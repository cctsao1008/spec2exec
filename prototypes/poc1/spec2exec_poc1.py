#!/usr/bin/env python3
"""Spec2Exec POC-1A: bounded integer semantics and preservation evidence.

This prototype intentionally excludes AI. It validates an accepted arithmetic
specification and a small SpecIR v0.1 subset, proves static no-overflow for the
accepted domain using interval analysis, lowers a straight-line expression to C,
performs translation validation against the exact emitted C return expression
with Z3 when available, compiles a shared library, and exhaustively checks binary
behavior over the declared finite input domain.

The proof claims are intentionally narrow. POC-1A does not prove the C compiler,
Python runtime, Z3, host OS, or human intent correct.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

SPEC_VERSION = "spec2exec.specification/v0.1"
SPECIR_VERSION = "spec2exec.specir/v0.1"
SUPPORTED_TYPES = {"i32": (-(2**31), 2**31 - 1), "u32": (0, 2**32 - 1)}
ARITH_OPS = {"+", "-", "*"}
CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
BOOL_OPS = {"and", "or", "not"}


class VerificationError(Exception):
    pass


def _expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise VerificationError(f"{code}: {message}")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_range(type_name: str, r: Any, where: str) -> tuple[int, int]:
    _expect(type_name in SUPPORTED_TYPES, "E_TYPE", f"{where}.type must be one of {sorted(SUPPORTED_TYPES)}")
    _expect(isinstance(r, dict), "E_RANGE", f"{where}.range must be an object")
    lo, hi = r.get("min"), r.get("max")
    _expect(isinstance(lo, int) and not isinstance(lo, bool), "E_RANGE", f"{where}.range.min must be integer")
    _expect(isinstance(hi, int) and not isinstance(hi, bool), "E_RANGE", f"{where}.range.max must be integer")
    _expect(lo <= hi, "E_RANGE", f"{where}.range.min must be <= max")
    tlo, thi = SUPPORTED_TYPES[type_name]
    _expect(tlo <= lo <= hi <= thi, "E_RANGE_TYPE", f"{where}.range must fit {type_name}")
    return lo, hi


def _trace_list(value: Any, where: str) -> list[str]:
    _expect(isinstance(value, list) and value, "E_TRACE", f"{where} must be a non-empty list")
    for i, item in enumerate(value):
        _expect(_nonempty_string(item), "E_TRACE", f"{where}[{i}] must be non-empty string")
    return value


def verify_specification(spec: Any) -> dict[str, Any]:
    _expect(isinstance(spec, dict), "E_SPEC_ROOT", "specification must be object")
    _expect(spec.get("specification_version") == SPEC_VERSION, "E_SPEC_VERSION", f"specification_version must be {SPEC_VERSION}")
    acceptance = spec.get("acceptance")
    _expect(isinstance(acceptance, dict), "E_SPEC_ACCEPT", "acceptance must be object")
    _expect(acceptance.get("status") == "accepted-for-poc", "E_SPEC_ACCEPT", "specification must be accepted-for-poc")
    _expect(_nonempty_string(acceptance.get("authority_role")), "E_SPEC_ACCEPT", "authority_role must be non-empty")

    fn = spec.get("function")
    _expect(isinstance(fn, dict), "E_SPEC_FUNCTION", "function must be object")
    _expect(_nonempty_string(fn.get("id")), "E_SPEC_FUNCTION", "function.id required")
    _expect(_nonempty_string(fn.get("name")), "E_SPEC_FUNCTION", "function.name required")
    inputs = fn.get("inputs")
    _expect(isinstance(inputs, list) and inputs, "E_SPEC_INPUTS", "function.inputs must be non-empty list")
    clauses: dict[str, dict[str, Any]] = {}
    names: set[str] = set()
    for i, inp in enumerate(inputs):
        where = f"function.inputs[{i}]"
        _expect(isinstance(inp, dict), "E_SPEC_INPUT", f"{where} must be object")
        clause_id = inp.get("clause_id")
        name = inp.get("name")
        _expect(_nonempty_string(clause_id), "E_SPEC_CLAUSE", f"{where}.clause_id required")
        _expect(clause_id not in clauses, "E_SPEC_CLAUSE", f"duplicate clause_id {clause_id}")
        _expect(_nonempty_string(name) and name not in names, "E_SPEC_INPUT", f"{where}.name must be unique")
        names.add(name)
        r = _check_range(inp.get("type"), inp.get("range"), where)
        clauses[clause_id] = {"kind": "input", "name": name, "type": inp["type"], "range": r}

    out = fn.get("output")
    _expect(isinstance(out, dict), "E_SPEC_OUTPUT", "function.output must be object")
    out_clause = out.get("clause_id")
    _expect(_nonempty_string(out_clause), "E_SPEC_CLAUSE", "output.clause_id required")
    out_range = _check_range(out.get("type"), out.get("range"), "function.output")
    clauses[out_clause] = {"kind": "output", "name": out.get("name"), "type": out["type"], "range": out_range}

    behavior = fn.get("behavior")
    _expect(isinstance(behavior, dict) and _nonempty_string(behavior.get("clause_id")), "E_SPEC_BEHAVIOR", "function.behavior clause required")
    clauses[behavior["clause_id"]] = {"kind": "behavior", "expr": behavior.get("expr")}

    ovf = fn.get("overflow_behavior")
    _expect(isinstance(ovf, dict) and _nonempty_string(ovf.get("clause_id")), "E_SPEC_OVERFLOW", "overflow_behavior clause required")
    _expect(ovf.get("mode") == "forbidden", "E_SPEC_OVERFLOW", "POC-1A requires overflow_behavior.mode='forbidden'")
    clauses[ovf["clause_id"]] = {"kind": "overflow", "mode": "forbidden"}

    return {
        "id": fn["id"],
        "name": fn["name"],
        "inputs": inputs,
        "output": out,
        "behavior": behavior,
        "overflow": ovf,
        "clauses": clauses,
        "acceptance": acceptance,
    }


def _validate_expr(expr: Any, symbols: set[str], where: str) -> None:
    if isinstance(expr, bool):
        return
    if isinstance(expr, int):
        return
    if isinstance(expr, str):
        _expect(expr in symbols, "E_EXPR_SYMBOL", f"{where}: unknown symbol {expr}")
        return
    _expect(isinstance(expr, dict), "E_EXPR", f"{where}: expression must be symbol/int/object")
    op = expr.get("op")
    args = expr.get("args")
    _expect(op in ARITH_OPS | CMP_OPS | BOOL_OPS, "E_EXPR_OP", f"{where}: unsupported op {op!r}")
    _expect(isinstance(args, list), "E_EXPR_ARGS", f"{where}: args must be list")
    if op == "not":
        _expect(len(args) == 1, "E_EXPR_ARITY", f"{where}: not expects 1 arg")
    else:
        _expect(len(args) >= 2, "E_EXPR_ARITY", f"{where}: {op} expects at least 2 args")
    for i, arg in enumerate(args):
        _validate_expr(arg, symbols, f"{where}.args[{i}]")


def _interval(expr: Any, ranges: dict[str, tuple[int, int]]) -> tuple[int, int]:
    if isinstance(expr, int) and not isinstance(expr, bool):
        return expr, expr
    if isinstance(expr, str):
        return ranges[expr]
    _expect(isinstance(expr, dict), "E_INTERVAL", "arithmetic expression required")
    op = expr.get("op")
    args = expr.get("args")
    _expect(op in ARITH_OPS and isinstance(args, list) and len(args) == 2, "E_INTERVAL", "interval analysis supports binary + - * only")
    a = _interval(args[0], ranges)
    b = _interval(args[1], ranges)
    if op == "+":
        return a[0] + b[0], a[1] + b[1]
    if op == "-":
        return a[0] - b[1], a[1] - b[0]
    products = (a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1])
    return min(products), max(products)


def _check_all_arith_intermediates(expr: Any, ranges: dict[str, tuple[int, int]], tlo: int, thi: int) -> tuple[int, int]:
    if isinstance(expr, (int, str)) and not isinstance(expr, bool):
        result = _interval(expr, ranges)
        _expect(tlo <= result[0] <= result[1] <= thi, "E_OVERFLOW", f"leaf range {result} exceeds machine type")
        return result
    _expect(isinstance(expr, dict) and expr.get("op") in ARITH_OPS, "E_OVERFLOW_EXPR", "body must be arithmetic expression")
    for arg in expr["args"]:
        _check_all_arith_intermediates(arg, ranges, tlo, thi)
    result = _interval(expr, ranges)
    _expect(tlo <= result[0] <= result[1] <= thi, "E_OVERFLOW", f"intermediate {expr.get('op')} range {result} exceeds machine type")
    return result


def verify_specir(doc: Any, spec_info: dict[str, Any]) -> dict[str, Any]:
    _expect(isinstance(doc, dict), "E_ROOT", "SpecIR must be object")
    _expect(doc.get("specir_version") == SPECIR_VERSION, "E_VERSION", f"specir_version must be {SPECIR_VERSION}")
    fn = doc.get("function")
    _expect(isinstance(fn, dict), "E_FUNCTION", "function must be object")
    _expect(fn.get("name") == spec_info["name"], "E_SPEC_NAME_LINK", "SpecIR function.name differs from accepted specification")
    _expect(fn.get("target") == "host-c", "E_TARGET", "POC-1A supports host-c only")
    fn_trace = _trace_list(fn.get("trace"), "function.trace")
    _expect(spec_info["id"] in fn_trace, "E_SPEC_TRACE_LINK", "function.trace must include specification function requirement id")

    inputs = fn.get("inputs")
    _expect(isinstance(inputs, list) and len(inputs) == len(spec_info["inputs"]), "E_INPUTS", "SpecIR input count mismatch")
    spec_inputs_by_name = {x["name"]: x for x in spec_info["inputs"]}
    symbols: set[str] = set()
    ranges: dict[str, tuple[int, int]] = {}
    input_types: dict[str, str] = {}
    seen_constraint_traces: set[str] = set()
    for i, inp in enumerate(inputs):
        where = f"function.inputs[{i}]"
        _expect(isinstance(inp, dict), "E_INPUT", f"{where} must be object")
        name = inp.get("id")
        _expect(_nonempty_string(name) and name not in symbols, "E_INPUT", f"{where}.id must be unique")
        symbols.add(name)
        _expect(name in spec_inputs_by_name, "E_SPEC_INPUT_LINK", f"SpecIR input {name} not in accepted specification")
        spec_in = spec_inputs_by_name[name]
        _expect(inp.get("type") == spec_in["type"], "E_SPEC_TYPE_LINK", f"type mismatch for input {name}")
        r = _check_range(inp.get("type"), inp.get("range"), where)
        _expect(r == (spec_in["range"]["min"], spec_in["range"]["max"]), "E_SPEC_RANGE_LINK", f"range mismatch for input {name}")
        tr = _trace_list(inp.get("trace"), f"{where}.trace")
        _expect(spec_in["clause_id"] in tr, "E_UNTRACEABLE_CONSTRAINT", f"input {name} range must trace to {spec_in['clause_id']}")
        seen_constraint_traces.update(tr)
        ranges[name] = r
        input_types[name] = inp["type"]

    output = fn.get("output")
    _expect(isinstance(output, dict), "E_OUTPUT", "function.output must be object")
    _expect(output.get("type") == spec_info["output"]["type"], "E_SPEC_TYPE_LINK", "output type mismatch")
    out_range = _check_range(output.get("type"), output.get("range"), "function.output")
    expected_out_range = (spec_info["output"]["range"]["min"], spec_info["output"]["range"]["max"])
    _expect(out_range == expected_out_range, "E_SPEC_RANGE_LINK", "output range mismatch")
    out_trace = _trace_list(output.get("trace"), "function.output.trace")
    _expect(spec_info["output"]["clause_id"] in out_trace, "E_UNTRACEABLE_CONSTRAINT", "output range lacks accepted-spec trace")
    seen_constraint_traces.update(out_trace)

    _expect(fn.get("overflow_behavior") == "forbidden", "E_OVERFLOW_POLICY", "POC-1A requires overflow_behavior='forbidden'")
    ovf_trace = _trace_list(fn.get("overflow_trace"), "function.overflow_trace")
    _expect(spec_info["overflow"]["clause_id"] in ovf_trace, "E_UNTRACEABLE_CONSTRAINT", "overflow policy lacks accepted-spec trace")
    seen_constraint_traces.update(ovf_trace)

    preconditions = fn.get("preconditions")
    _expect(isinstance(preconditions, list) and preconditions, "E_PRE", "preconditions must be non-empty list")
    for i, pre in enumerate(preconditions):
        _expect(isinstance(pre, dict), "E_PRE", f"preconditions[{i}] must be object")
        _trace_list(pre.get("trace"), f"preconditions[{i}].trace")
        _validate_expr(pre.get("expr"), symbols, f"preconditions[{i}].expr")
        seen_constraint_traces.update(pre["trace"])

    expected_preconditions = []
    for inp in inputs:
        lo, hi = ranges[inp["id"]]
        expected_preconditions.append({
            "trace": inp["trace"],
            "expr": {"op": "and", "args": [
                {"op": ">=", "args": [inp["id"], lo]},
                {"op": "<=", "args": [inp["id"], hi]},
            ]},
        })
    actual_preconditions = [{"trace": x["trace"], "expr": x["expr"]} for x in preconditions]
    _expect(actual_preconditions == expected_preconditions, "E_PRE_LINK", "preconditions must be the canonical projection of accepted input ranges")

    body = fn.get("body")
    _expect(isinstance(body, dict) and body.get("kind") == "expr", "E_BODY", "body.kind must be 'expr'")
    _validate_expr(body.get("expr"), symbols, "body.expr")
    body_trace = _trace_list(body.get("trace"), "body.trace")
    _expect(spec_info["behavior"]["clause_id"] in body_trace, "E_SPEC_BEHAVIOR_LINK", "body must trace to accepted behavior clause")
    _expect(body["expr"] == spec_info["behavior"]["expr"], "E_SPEC_BEHAVIOR_LINK", "body expression differs from accepted specification")
    seen_constraint_traces.update(body_trace)

    output_symbol = output.get("id")
    postconditions = fn.get("postconditions")
    _expect(isinstance(postconditions, list) and postconditions, "E_POST", "postconditions must be non-empty list")
    post_symbols = symbols | {output_symbol}
    for i, post in enumerate(postconditions):
        _expect(isinstance(post, dict), "E_POST", f"postconditions[{i}] must be object")
        _trace_list(post.get("trace"), f"postconditions[{i}].trace")
        _validate_expr(post.get("expr"), post_symbols, f"postconditions[{i}].expr")
        seen_constraint_traces.update(post["trace"])
    expected_post = {"op": "==", "args": [output_symbol, body["expr"]]}
    _expect(len(postconditions) == 1 and postconditions[0]["expr"] == expected_post, "E_POST_LINK", "POC-1A postcondition must equate output to body expression")
    _expect(spec_info["behavior"]["clause_id"] in postconditions[0]["trace"], "E_POST_LINK", "postcondition must trace to accepted behavior clause")

    required_clauses = set(spec_info["clauses"])
    represented = set(fn_trace) | seen_constraint_traces
    missing = required_clauses - represented
    _expect(not missing, "E_SPEC_CLAUSE_MISSING", f"accepted specification clauses missing from SpecIR: {sorted(missing)}")

    common_type = output["type"]
    _expect(all(t == common_type for t in input_types.values()), "E_MIXED_TYPE", "POC-1A forbids mixed integer types")
    tlo, thi = SUPPORTED_TYPES[common_type]
    expr_range = _check_all_arith_intermediates(body["expr"], ranges, tlo, thi)
    _expect(out_range[0] <= expr_range[0] and expr_range[1] <= out_range[1], "E_OUTPUT_RANGE", f"body range {expr_range} not contained in declared output range {out_range}")

    return {
        "function": fn,
        "type": common_type,
        "input_ranges": ranges,
        "output_range": out_range,
        "body_range": expr_range,
        "evidence": [
            {"claim": "P1.function_identity", "status": "CHECKED"},
            {"claim": "P1.constraint_traceability", "status": "CHECKED"},
            {"claim": "P1.range_linkage", "status": "CHECKED"},
            {"claim": "P1.behavior_linkage", "status": "CHECKED"},
            {"claim": "P2.fixed_width_type_domain", "status": "CHECKED"},
            {"claim": "P2.output_range_containment", "status": "CHECKED"},
            {"claim": "P2.static_overflow_exclusion", "status": "CHECKED", "method": "sound interval analysis"},
        ],
    }


def eval_expr(expr: Any, env: dict[str, int]) -> Any:
    if isinstance(expr, bool): return expr
    if isinstance(expr, int): return expr
    if isinstance(expr, str): return env[expr]
    op, args = expr["op"], expr["args"]
    vals = [eval_expr(x, env) for x in args]
    if op == "+": return vals[0] + vals[1]
    if op == "-": return vals[0] - vals[1]
    if op == "*": return vals[0] * vals[1]
    if op == "==": return vals[0] == vals[1]
    if op == "!=": return vals[0] != vals[1]
    if op == "<": return vals[0] < vals[1]
    if op == "<=": return vals[0] <= vals[1]
    if op == ">": return vals[0] > vals[1]
    if op == ">=": return vals[0] >= vals[1]
    if op == "and": return all(vals)
    if op == "or": return any(vals)
    if op == "not": return not vals[0]
    raise VerificationError(f"E_EVAL: unsupported op {op}")


def c_expr(expr: Any) -> str:
    if isinstance(expr, int) and not isinstance(expr, bool): return str(expr)
    if isinstance(expr, str): return expr
    op, args = expr["op"], expr["args"]
    _expect(op in ARITH_OPS and len(args) == 2, "E_C_EXPR", "POC-1A C lowering supports binary arithmetic body only")
    return f"({c_expr(args[0])} {op} {c_expr(args[1])})"


def lower_to_c(verified: dict[str, Any], out_path: Path) -> None:
    fn = verified["function"]
    ctype = "int32_t" if verified["type"] == "i32" else "uint32_t"
    params = ", ".join(f"{ctype} {x['id']}" for x in fn["inputs"])
    expr = c_expr(fn["body"]["expr"])
    traces = ",".join(fn["trace"] + fn["body"]["trace"])
    text = f'''/* Generated by Spec2Exec POC-1A. Source of truth: accepted specification + SpecIR.\n * trace: {traces}\n */\n#include <stdint.h>\n\n{ctype} {fn['name']}({params})\n{{\n    return {expr};\n}}\n'''
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")


def _extract_c_return_expr(c_source: str) -> str:
    m = re.search(r"\breturn\s+(.+?)\s*;", c_source, re.DOTALL)
    _expect(m is not None, "E_P3_C_PARSE", "could not extract C return expression")
    return m.group(1).strip()


def _pyast_to_z3(node: ast.AST, symbols: dict[str, Any]) -> Any:
    try:
        import z3  # type: ignore
    except ImportError as exc:
        raise VerificationError("E_Z3_MISSING: install z3-solver for P3 translation validation") from exc
    if isinstance(node, ast.Expression): return _pyast_to_z3(node.body, symbols)
    if isinstance(node, ast.Name):
        _expect(node.id in symbols, "E_P3_SYMBOL", f"unknown C expression symbol {node.id}")
        return symbols[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, int): return z3.IntVal(node.value)
    if isinstance(node, ast.BinOp):
        a = _pyast_to_z3(node.left, symbols)
        b = _pyast_to_z3(node.right, symbols)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
    raise VerificationError(f"E_P3_C_AST: unsupported emitted C expression AST node {type(node).__name__}")


def _specir_to_z3(expr: Any, symbols: dict[str, Any]) -> Any:
    try:
        import z3  # type: ignore
    except ImportError as exc:
        raise VerificationError("E_Z3_MISSING: install z3-solver for P3 translation validation") from exc
    if isinstance(expr, int) and not isinstance(expr, bool): return z3.IntVal(expr)
    if isinstance(expr, str): return symbols[expr]
    op, args = expr["op"], expr["args"]
    a = _specir_to_z3(args[0], symbols)
    b = _specir_to_z3(args[1], symbols)
    if op == "+": return a + b
    if op == "-": return a - b
    if op == "*": return a * b
    raise VerificationError(f"E_P3_SPECIR_AST: unsupported SpecIR arithmetic op {op}")


def translation_validate(verified: dict[str, Any], c_path: Path) -> dict[str, Any]:
    try:
        import z3  # type: ignore
    except ImportError as exc:
        raise VerificationError("E_Z3_MISSING: install z3-solver for P3 translation validation") from exc
    fn = verified["function"]
    symbols = {x["id"]: z3.Int(x["id"]) for x in fn["inputs"]}
    solver = z3.Solver()
    for name, (lo, hi) in verified["input_ranges"].items():
        solver.add(symbols[name] >= lo, symbols[name] <= hi)
    ir_result = _specir_to_z3(fn["body"]["expr"], symbols)
    emitted = _extract_c_return_expr(c_path.read_text(encoding="utf-8"))
    c_result = _pyast_to_z3(ast.parse(emitted, mode="eval"), symbols)
    solver.add(ir_result != c_result)
    result = solver.check()
    _expect(result == z3.unsat, "E_P3_EQUIV", f"translation equivalence failed: solver returned {result}")
    return {
        "claim": "P3.function_output_equivalence",
        "status": "PROVEN",
        "method": "SMT translation validation over exact emitted C return expression",
        "granularity": "function contract boundary / return value",
        "assumptions": [
            "accepted input precondition/ranges hold",
            "static overflow exclusion evidence is valid",
            "C expression parser covers the emitted POC-1A subset",
            "Z3 solver is trusted",
        ],
    }


def build_shared(verified: dict[str, Any], c_path: Path, so_path: Path) -> None:
    cc = shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    _expect(cc is not None, "E_CC", "no host C compiler found")
    so_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([cc, "-std=c11", "-O2", "-shared", "-fPIC", str(c_path), "-o", str(so_path)], check=True)


def exhaustive_binary_check(verified: dict[str, Any], so_path: Path, max_cases: int = 200_000) -> dict[str, Any]:
    fn = verified["function"]
    ranges = [range(verified["input_ranges"][x["id"]][0], verified["input_ranges"][x["id"]][1] + 1) for x in fn["inputs"]]
    cases = 1
    for r in ranges: cases *= len(r)
    _expect(cases <= max_cases, "E_P4_DOMAIN", f"declared domain has {cases} cases, exceeds exhaustive limit {max_cases}")
    lib = ctypes.CDLL(str(so_path.resolve()))
    cfn = getattr(lib, fn["name"])
    ctype = ctypes.c_int32 if verified["type"] == "i32" else ctypes.c_uint32
    cfn.argtypes = [ctype for _ in fn["inputs"]]
    cfn.restype = ctype
    for values in itertools.product(*ranges):
        env = {inp["id"]: value for inp, value in zip(fn["inputs"], values)}
        expected = eval_expr(fn["body"]["expr"], env)
        actual = int(cfn(*values))
        _expect(actual == expected, "E_P4_MISMATCH", f"binary mismatch inputs={env}: expected {expected}, got {actual}")
    return {
        "claim": "P4.binary_behavior_over_declared_domain",
        "status": "TESTED_EXHAUSTIVE",
        "method": "compiled shared-library invocation",
        "cases": cases,
        "compiler_optimization": "-O2",
    }


def run_all(spec_path: Path, specir_path: Path, build_dir: Path) -> dict[str, Any]:
    spec_info = verify_specification(_load(spec_path))
    verified = verify_specir(_load(specir_path), spec_info)
    c_path = build_dir / "safe_add.c"
    so_path = build_dir / "libsafe_add.so"
    lower_to_c(verified, c_path)
    p3 = translation_validate(verified, c_path)
    build_shared(verified, c_path, so_path)
    p4 = exhaustive_binary_check(verified, so_path)
    evidence = {
        "experiment": "POC-1A",
        "function": verified["function"]["name"],
        "claims": verified["evidence"] + [p3, p4],
        "explicit_nonclaims": [
            "human intent fidelity",
            "general specification completeness",
            "C compiler correctness",
            "machine-code proof",
            "behavior outside accepted preconditions",
        ],
        "tcb": ["Python runtime", "POC-1A implementation", "Z3", "host OS", "host C compiler/linker", "ctypes/runtime loader"],
    }
    _write_json(build_dir / "evidence.json", evidence)
    return evidence


def cmd_verify(args: argparse.Namespace) -> None:
    info = verify_specification(_load(args.specification))
    verified = verify_specir(_load(args.specir), info)
    print(json.dumps({"status": "PASS", "body_range": verified["body_range"], "evidence": verified["evidence"]}, indent=2))


def cmd_lower(args: argparse.Namespace) -> None:
    info = verify_specification(_load(args.specification))
    verified = verify_specir(_load(args.specir), info)
    lower_to_c(verified, args.output)
    print(args.output)


def cmd_all(args: argparse.Namespace) -> None:
    print(json.dumps(run_all(args.specification, args.specir, args.build_dir), indent=2))


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("verify", "lower", "all"):
        sp = sub.add_parser(name)
        sp.add_argument("specir", type=Path)
        sp.add_argument("--specification", required=True, type=Path)
        if name == "lower":
            sp.add_argument("-o", "--output", required=True, type=Path)
            sp.set_defaults(func=cmd_lower)
        elif name == "all":
            sp.add_argument("--build-dir", required=True, type=Path)
            sp.set_defaults(func=cmd_all)
        else:
            sp.set_defaults(func=cmd_verify)
    return p


def main() -> int:
    try:
        args = make_parser().parse_args()
        args.func(args)
        return 0
    except (VerificationError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
