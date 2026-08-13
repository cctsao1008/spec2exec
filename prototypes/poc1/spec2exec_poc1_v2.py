#!/usr/bin/env python3
"""Spec2Exec POC-1A v2: bounded integer semantics with model-scoped evidence.

This prototype intentionally excludes AI. It keeps P1/P2 deterministic checks,
lowers a straight-line bounded-integer expression to C, and performs P3-A
translation validation using a 32-bit bit-vector model. The P3-A claim is scoped
to the restricted emitted-expression model; complete C semantics are validated in
POC-1B with a C-aware model checker.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
import hashlib
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any

SPEC_VERSION = "spec2exec.specification/v0.1"
SPECIR_VERSION = "spec2exec.specir/v0.1"
SUPPORTED_TYPES = {"i32": (-(2**31), 2**31 - 1), "u32": (0, 2**32 - 1)}
ARITH_OPS = {"+", "-", "*"}
CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
BOOL_OPS = {"and", "or", "not"}
RESERVED_C_NAMES = {"INT32_MIN", "UINT32_C"}
BV_WIDTH = 32
EXT_WIDTH = 64


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


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_path(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


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
        _expect(_nonempty_string(name) and name not in names and name not in RESERVED_C_NAMES, "E_SPEC_INPUT", f"{where}.name must be unique/non-reserved")
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
    _expect(ovf.get("mode") == "forbidden", "E_SPEC_OVERFLOW", "POC-1 requires overflow_behavior.mode='forbidden'")
    clauses[ovf["clause_id"]] = {"kind": "overflow", "mode": "forbidden"}

    return {
        "id": fn["id"], "name": fn["name"], "inputs": inputs, "output": out,
        "behavior": behavior, "overflow": ovf, "clauses": clauses,
        "acceptance": acceptance,
    }


def _validate_expr(expr: Any, symbols: set[str], where: str) -> None:
    if isinstance(expr, bool): return
    if isinstance(expr, int): return
    if isinstance(expr, str):
        _expect(expr in symbols, "E_EXPR_SYMBOL", f"{where}: unknown symbol {expr}")
        return
    _expect(isinstance(expr, dict), "E_EXPR", f"{where}: expression must be symbol/int/object")
    op, args = expr.get("op"), expr.get("args")
    _expect(op in ARITH_OPS | CMP_OPS | BOOL_OPS, "E_EXPR_OP", f"{where}: unsupported op {op!r}")
    _expect(isinstance(args, list), "E_EXPR_ARGS", f"{where}: args must be list")
    if op == "not": _expect(len(args) == 1, "E_EXPR_ARITY", f"{where}: not expects 1 arg")
    else: _expect(len(args) >= 2, "E_EXPR_ARITY", f"{where}: {op} expects at least 2 args")
    for i, arg in enumerate(args): _validate_expr(arg, symbols, f"{where}.args[{i}]")


def _interval(expr: Any, ranges: dict[str, tuple[int, int]]) -> tuple[int, int]:
    if isinstance(expr, int) and not isinstance(expr, bool): return expr, expr
    if isinstance(expr, str): return ranges[expr]
    _expect(isinstance(expr, dict), "E_INTERVAL", "arithmetic expression required")
    op, args = expr.get("op"), expr.get("args")
    _expect(op in ARITH_OPS and isinstance(args, list) and len(args) == 2, "E_INTERVAL", "interval analysis supports binary + - * only")
    a, b = _interval(args[0], ranges), _interval(args[1], ranges)
    if op == "+": return a[0] + b[0], a[1] + b[1]
    if op == "-": return a[0] - b[1], a[1] - b[0]
    products = (a[0]*b[0], a[0]*b[1], a[1]*b[0], a[1]*b[1])
    return min(products), max(products)


def _overflow_code(type_name: str) -> str:
    return "E_SIGNED_OVERFLOW_UB" if type_name == "i32" else "E_UNSIGNED_WRAPAROUND"


def _check_all_arith_intermediates(expr: Any, ranges: dict[str, tuple[int, int]], type_name: str) -> tuple[int, int]:
    tlo, thi = SUPPORTED_TYPES[type_name]
    if isinstance(expr, (int, str)) and not isinstance(expr, bool):
        result = _interval(expr, ranges)
        _expect(tlo <= result[0] <= result[1] <= thi, _overflow_code(type_name), f"leaf range {result} exceeds {type_name}")
        return result
    _expect(isinstance(expr, dict) and expr.get("op") in ARITH_OPS, "E_OVERFLOW_EXPR", "body must be arithmetic expression")
    for arg in expr["args"]: _check_all_arith_intermediates(arg, ranges, type_name)
    result = _interval(expr, ranges)
    _expect(tlo <= result[0] <= result[1] <= thi, _overflow_code(type_name), f"intermediate {expr.get('op')} range {result} exceeds {type_name}")
    return result


def verify_specir(doc: Any, spec_info: dict[str, Any]) -> dict[str, Any]:
    _expect(isinstance(doc, dict), "E_ROOT", "SpecIR must be object")
    _expect(doc.get("specir_version") == SPECIR_VERSION, "E_VERSION", f"specir_version must be {SPECIR_VERSION}")
    fn = doc.get("function")
    _expect(isinstance(fn, dict), "E_FUNCTION", "function must be object")
    _expect(fn.get("name") == spec_info["name"], "E_SPEC_NAME_LINK", "SpecIR function.name differs from accepted specification")
    _expect(fn.get("target") == "host-c", "E_TARGET", "POC-1 supports host-c only")
    fn_trace = _trace_list(fn.get("trace"), "function.trace")
    _expect(spec_info["id"] in fn_trace, "E_SPEC_TRACE_LINK", "function.trace must include specification function requirement id")

    inputs = fn.get("inputs")
    _expect(isinstance(inputs, list) and len(inputs) == len(spec_info["inputs"]), "E_INPUTS", "SpecIR input count mismatch")
    spec_inputs_by_name = {x["name"]: x for x in spec_info["inputs"]}
    symbols: set[str] = set(); ranges: dict[str, tuple[int, int]] = {}; input_types: dict[str, str] = {}; seen: set[str] = set()
    for i, inp in enumerate(inputs):
        where = f"function.inputs[{i}]"; _expect(isinstance(inp, dict), "E_INPUT", f"{where} must be object")
        name = inp.get("id")
        _expect(_nonempty_string(name) and name not in symbols and name not in RESERVED_C_NAMES, "E_INPUT", f"{where}.id must be unique/non-reserved")
        symbols.add(name); _expect(name in spec_inputs_by_name, "E_SPEC_INPUT_LINK", f"SpecIR input {name} not in accepted specification")
        spec_in = spec_inputs_by_name[name]
        _expect(inp.get("type") == spec_in["type"], "E_SPEC_TYPE_LINK", f"type mismatch for input {name}")
        r = _check_range(inp.get("type"), inp.get("range"), where)
        _expect(r == (spec_in["range"]["min"], spec_in["range"]["max"]), "E_SPEC_RANGE_LINK", f"range mismatch for input {name}")
        tr = _trace_list(inp.get("trace"), f"{where}.trace")
        _expect(spec_in["clause_id"] in tr, "E_UNTRACEABLE_CONSTRAINT", f"input {name} range must trace to {spec_in['clause_id']}")
        seen.update(tr); ranges[name] = r; input_types[name] = inp["type"]

    output = fn.get("output"); _expect(isinstance(output, dict), "E_OUTPUT", "function.output must be object")
    _expect(output.get("type") == spec_info["output"]["type"], "E_SPEC_TYPE_LINK", "output type mismatch")
    out_range = _check_range(output.get("type"), output.get("range"), "function.output")
    expected_out_range = (spec_info["output"]["range"]["min"], spec_info["output"]["range"]["max"])
    _expect(out_range == expected_out_range, "E_SPEC_RANGE_LINK", "output range mismatch")
    out_trace = _trace_list(output.get("trace"), "function.output.trace")
    _expect(spec_info["output"]["clause_id"] in out_trace, "E_UNTRACEABLE_CONSTRAINT", "output range lacks accepted-spec trace"); seen.update(out_trace)

    _expect(fn.get("overflow_behavior") == "forbidden", "E_OVERFLOW_POLICY", "POC-1 requires overflow_behavior='forbidden'")
    ovf_trace = _trace_list(fn.get("overflow_trace"), "function.overflow_trace")
    _expect(spec_info["overflow"]["clause_id"] in ovf_trace, "E_UNTRACEABLE_CONSTRAINT", "overflow policy lacks accepted-spec trace"); seen.update(ovf_trace)

    preconditions = fn.get("preconditions"); _expect(isinstance(preconditions, list) and preconditions, "E_PRE", "preconditions must be non-empty list")
    for i, pre in enumerate(preconditions):
        _expect(isinstance(pre, dict), "E_PRE", f"preconditions[{i}] must be object")
        _trace_list(pre.get("trace"), f"preconditions[{i}].trace"); _validate_expr(pre.get("expr"), symbols, f"preconditions[{i}].expr"); seen.update(pre["trace"])
    expected_pre = []
    for inp in inputs:
        lo, hi = ranges[inp["id"]]
        expected_pre.append({"trace": inp["trace"], "expr": {"op": "and", "args": [
            {"op": ">=", "args": [inp["id"], lo]}, {"op": "<=", "args": [inp["id"], hi]}]}})
    _expect([{"trace": x["trace"], "expr": x["expr"]} for x in preconditions] == expected_pre, "E_PRE_LINK", "preconditions must be canonical accepted-range projection")

    body = fn.get("body"); _expect(isinstance(body, dict) and body.get("kind") == "expr", "E_BODY", "body.kind must be 'expr'")
    _validate_expr(body.get("expr"), symbols, "body.expr")
    body_trace = _trace_list(body.get("trace"), "body.trace")
    _expect(spec_info["behavior"]["clause_id"] in body_trace, "E_SPEC_BEHAVIOR_LINK", "body must trace to accepted behavior clause")
    _expect(body["expr"] == spec_info["behavior"]["expr"], "E_SPEC_BEHAVIOR_LINK", "body expression differs from accepted specification"); seen.update(body_trace)

    output_symbol = output.get("id"); postconditions = fn.get("postconditions")
    _expect(isinstance(postconditions, list) and postconditions, "E_POST", "postconditions must be non-empty list")
    post_symbols = symbols | {output_symbol}
    for i, post in enumerate(postconditions):
        _expect(isinstance(post, dict), "E_POST", f"postconditions[{i}] must be object")
        _trace_list(post.get("trace"), f"postconditions[{i}].trace"); _validate_expr(post.get("expr"), post_symbols, f"postconditions[{i}].expr"); seen.update(post["trace"])
    expected_post = {"op": "==", "args": [output_symbol, body["expr"]]}
    _expect(len(postconditions) == 1 and postconditions[0]["expr"] == expected_post, "E_POST_LINK", "POC-1 postcondition must equate output to body expression")
    _expect(spec_info["behavior"]["clause_id"] in postconditions[0]["trace"], "E_POST_LINK", "postcondition must trace to accepted behavior clause")

    required = set(spec_info["clauses"]); represented = set(fn_trace) | seen; missing = required - represented
    _expect(not missing, "E_SPEC_CLAUSE_MISSING", f"accepted specification clauses missing from SpecIR: {sorted(missing)}")

    common_type = output["type"]; _expect(all(t == common_type for t in input_types.values()), "E_MIXED_TYPE", "POC-1 forbids mixed integer types")
    expr_range = _check_all_arith_intermediates(body["expr"], ranges, common_type)
    _expect(out_range[0] <= expr_range[0] and expr_range[1] <= out_range[1], "E_OUTPUT_RANGE", f"body range {expr_range} not contained in output range {out_range}")
    p2_claim = "P2.no_signed_overflow_ub" if common_type == "i32" else "P2.no_unsigned_wraparound"
    return {
        "function": fn, "type": common_type, "input_ranges": ranges, "output_range": out_range, "body_range": expr_range,
        "p2_overflow_claim": p2_claim,
        "evidence": [
            {"claim": "P1.function_identity", "status": "CHECKED"},
            {"claim": "P1.constraint_traceability", "status": "CHECKED"},
            {"claim": "P1.range_linkage", "status": "CHECKED"},
            {"claim": "P1.behavior_linkage", "status": "CHECKED"},
            {"claim": "P2.fixed_width_type_domain", "status": "CHECKED"},
            {"claim": "P2.output_range_containment", "status": "CHECKED"},
            {"claim": p2_claim, "status": "CHECKED", "method": "sound interval analysis", "blocking": True},
        ],
    }


def eval_expr(expr: Any, env: dict[str, int]) -> Any:
    if isinstance(expr, bool): return expr
    if isinstance(expr, int): return expr
    if isinstance(expr, str): return env[expr]
    op, args = expr["op"], expr["args"]; vals = [eval_expr(x, env) for x in args]
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


def c_literal(value: int, type_name: str) -> str:
    _expect(isinstance(value, int) and not isinstance(value, bool), "E_C_LITERAL", "literal must be integer")
    lo, hi = SUPPORTED_TYPES[type_name]
    _expect(lo <= value <= hi, "E_C_LITERAL", f"literal {value} does not fit {type_name}")
    if type_name == "u32": return f"UINT32_C({value})"
    if value == -(2**31): return "INT32_MIN"
    if value < 0: return f"(-{abs(value)})"
    return str(value)


def c_expr(expr: Any, type_name: str) -> str:
    if isinstance(expr, int) and not isinstance(expr, bool): return c_literal(expr, type_name)
    if isinstance(expr, str): return expr
    op, args = expr["op"], expr["args"]
    _expect(op in ARITH_OPS and len(args) == 2, "E_C_EXPR", "C lowering supports binary + - * only")
    return f"({c_expr(args[0], type_name)} {op} {c_expr(args[1], type_name)})"


def lower_to_c(verified: dict[str, Any], out_path: Path, banner: str = "POC-1A-v2") -> None:
    fn, type_name = verified["function"], verified["type"]
    ctype = "int32_t" if type_name == "i32" else "uint32_t"
    params = ", ".join(f"{ctype} {x['id']}" for x in fn["inputs"])
    expr = c_expr(fn["body"]["expr"], type_name)
    traces = ",".join(fn["trace"] + fn["body"]["trace"])
    text = f'''/* Generated by Spec2Exec {banner}. Source of truth: accepted specification + SpecIR.\n * trace: {traces}\n */\n#include <stdint.h>\n#include <limits.h>\n\n#ifndef __CPROVER__\n_Static_assert(sizeof(int32_t) == 4, "int32_t must be 32-bit");\n_Static_assert(sizeof(uint32_t) == 4, "uint32_t must be 32-bit");\n_Static_assert(_Generic((int32_t)0, int: 1, default: 0), "host-c requires int32_t == int");\n_Static_assert(_Generic((uint32_t)0, unsigned int: 1, default: 0), "host-c requires uint32_t == unsigned int");\n#endif\n\n{ctype} {fn['name']}({params})\n{{\n    return {expr};\n}}\n'''
    out_path.parent.mkdir(parents=True, exist_ok=True); out_path.write_text(text, encoding="utf-8")


def _extract_c_return_expr(c_source: str) -> str:
    m = re.search(r"\breturn\s+(.+?)\s*;", c_source, re.DOTALL)
    _expect(m is not None, "E_P3_C_PARSE", "could not extract C return expression")
    return m.group(1).strip()


def _bv_val(z3: Any, value: int) -> Any:
    return z3.BitVecVal(value, BV_WIDTH)


def _restricted_ast_to_bv(node: ast.AST, symbols: dict[str, Any], type_name: str, z3: Any) -> Any:
    if isinstance(node, ast.Expression): return _restricted_ast_to_bv(node.body, symbols, type_name, z3)
    if isinstance(node, ast.Name):
        if node.id == "INT32_MIN" and type_name == "i32": return _bv_val(z3, -(2**31))
        _expect(node.id in symbols, "E_P3_SYMBOL", f"unknown emitted-expression symbol {node.id}")
        return symbols[node.id]
    if isinstance(node, ast.Constant) and isinstance(node.value, int): return _bv_val(z3, node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant) and isinstance(node.operand.value, int):
        return -_bv_val(z3, node.operand.value)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "UINT32_C" and type_name == "u32":
        _expect(len(node.args) == 1 and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, int), "E_P3_C_AST", "UINT32_C requires one integer literal")
        return _bv_val(z3, node.args[0].value)
    if isinstance(node, ast.BinOp):
        a = _restricted_ast_to_bv(node.left, symbols, type_name, z3); b = _restricted_ast_to_bv(node.right, symbols, type_name, z3)
        if isinstance(node.op, ast.Add): return a + b
        if isinstance(node.op, ast.Sub): return a - b
        if isinstance(node.op, ast.Mult): return a * b
    raise VerificationError(f"E_P3_C_AST: unsupported restricted emitted-expression node {type(node).__name__}")


def _builtin_safe(z3: Any, op: str, l: Any, r: Any, signed: bool) -> Any:
    if op == "+":
        return z3.And(z3.BVAddNoOverflow(l, r, True), z3.BVAddNoUnderflow(l, r)) if signed else z3.BVAddNoOverflow(l, r, False)
    if op == "-":
        return z3.And(z3.BVSubNoOverflow(l, r), z3.BVSubNoUnderflow(l, r, True)) if signed else z3.BVSubNoUnderflow(l, r, False)
    if op == "*":
        return z3.And(z3.BVMulNoOverflow(l, r, True), z3.BVMulNoUnderflow(l, r)) if signed else z3.BVMulNoOverflow(l, r, False)
    raise VerificationError(f"E_P3_OP: unsupported op {op}")


def _exact_safe(z3: Any, exact64: Any, signed: bool) -> Any:
    if signed:
        return z3.And(exact64 >= z3.BitVecVal(-(2**31), EXT_WIDTH), exact64 <= z3.BitVecVal(2**31 - 1, EXT_WIDTH))
    return z3.ULE(exact64, z3.BitVecVal(2**32 - 1, EXT_WIDTH))


def _encode_bv_expr(expr: Any, env: dict[str, Any], signed: bool, z3: Any, path: str = "body") -> tuple[Any, list[dict[str, Any]]]:
    if isinstance(expr, int) and not isinstance(expr, bool): return _bv_val(z3, expr), []
    if isinstance(expr, str): return env[expr], []
    _expect(isinstance(expr, dict) and expr.get("op") in ARITH_OPS and len(expr.get("args", [])) == 2, "E_P3_SPECIR_AST", "bit-vector encoder supports binary + - * only")
    op, args = expr["op"], expr["args"]
    l, lo = _encode_bv_expr(args[0], env, signed, z3, path + ".0"); r, ro = _encode_bv_expr(args[1], env, signed, z3, path + ".1")
    el = z3.SignExt(BV_WIDTH, l) if signed else z3.ZeroExt(BV_WIDTH, l)
    er = z3.SignExt(BV_WIDTH, r) if signed else z3.ZeroExt(BV_WIDTH, r)
    exact = {"+": el + er, "-": el - er, "*": el * er}[op]
    result = {"+": l + r, "-": l - r, "*": l * r}[op]
    obligation = {"path": path, "op": op, "exact_safe": _exact_safe(z3, exact, signed), "builtin_safe": _builtin_safe(z3, op, l, r, signed)}
    return result, lo + ro + [obligation]


def _precondition_terms(verified: dict[str, Any], env: dict[str, Any], z3: Any) -> list[Any]:
    signed = verified["type"] == "i32"; terms = []
    for name, (lo, hi) in verified["input_ranges"].items():
        v = env[name]
        if signed: terms.extend([v >= _bv_val(z3, lo), v <= _bv_val(z3, hi)])
        else: terms.extend([z3.UGE(v, _bv_val(z3, lo)), z3.ULE(v, _bv_val(z3, hi))])
    return terms


def _solver_result(solver: Any) -> tuple[str, float]:
    start = time.perf_counter(); result = solver.check(); ms = (time.perf_counter() - start) * 1000.0
    return str(result), round(ms, 3)


def translation_validate(verified: dict[str, Any], c_path: Path, specir_sha256: str | None = None, timeout_ms: int = 60_000) -> dict[str, Any]:
    try: import z3  # type: ignore
    except ImportError as exc: raise VerificationError("E_Z3_MISSING: install z3-solver for P3 translation validation") from exc

    fn, signed = verified["function"], verified["type"] == "i32"
    env = {x["id"]: z3.BitVec(x["id"], BV_WIDTH) for x in fn["inputs"]}
    P = _precondition_terms(verified, env, z3)
    ir_bv, obligations = _encode_bv_expr(fn["body"]["expr"], env, signed, z3)
    c_text = c_path.read_text(encoding="utf-8"); emitted = _extract_c_return_expr(c_text)
    try: c_ast = ast.parse(emitted, mode="eval")
    except SyntaxError as exc: raise VerificationError(f"E_P3_C_PARSE: restricted emitted expression is not parseable: {exc}") from exc
    c_bv = _restricted_ast_to_bv(c_ast, env, verified["type"], z3)

    def fresh() -> Any:
        s = z3.Solver(); s.set(timeout=timeout_ms); return s

    proof: list[dict[str, Any]] = []
    s = fresh(); s.add(*P); r, ms = _solver_result(s); proof.append({"id": "Q0.domain_non_vacuous", "expect": "sat", "result": r, "ms": ms})
    _expect(r == "sat", "E_P3_VACUOUS_DOMAIN", f"accepted function domain must be satisfiable, got {r}")

    exact_preds = [o["exact_safe"] for o in obligations]
    s = fresh(); s.add(*P); s.add(z3.Not(z3.And(*exact_preds)) if exact_preds else z3.BoolVal(False)); r, ms = _solver_result(s)
    proof.append({"id": "Q1.no_overflow_or_wrap", "expect": "unsat", "result": r, "ms": ms, "nodes": [o["path"] for o in obligations]})
    if r == "sat": raise VerificationError(f"{_overflow_code(verified['type'])}: P3 bit-vector model found unsafe arithmetic in accepted domain: {s.model()}")
    _expect(r == "unsat", "E_P3_UNRESOLVED", f"Q1 returned {r}")

    disagreements = [o["exact_safe"] != o["builtin_safe"] for o in obligations]
    s = fresh(); s.add(*P); s.add(z3.Or(*disagreements) if disagreements else z3.BoolVal(False)); r, ms = _solver_result(s)
    proof.append({"id": "Q2.encoder_cross_check", "expect": "unsat", "result": r, "ms": ms})
    if r == "sat": raise VerificationError(f"E_P3_ENCODING_DISAGREEMENT: extension and Z3 builtin overflow predicates disagree: {s.model()}")
    _expect(r == "unsat", "E_P3_UNRESOLVED", f"Q2 returned {r}")

    s = fresh(); s.add(*P); s.add(ir_bv != c_bv); r, ms = _solver_result(s)
    proof.append({"id": "Q3.result_equivalence", "expect": "unsat", "result": r, "ms": ms, "context": "fresh solver; Q1 safety predicates deliberately not asserted"})
    if r == "sat": raise VerificationError(f"E_P3_EQUIV: restricted emitted-expression model differs from SpecIR: {s.model()}")
    _expect(r == "unsat", "E_P3_UNRESOLVED", f"Q3 returned {r}")

    mutant = c_bv ^ _bv_val(z3, 1)
    s = fresh(); s.add(*P); s.add(ir_bv != mutant); r, ms = _solver_result(s)
    proof.append({"id": "Q4.harness_sensitivity", "expect": "sat", "result": r, "ms": ms, "mutation": "target_result XOR 1"})
    _expect(r == "sat", "E_P3_HARNESS", f"proof harness failed sensitivity self-test: {r}")

    c_sha = _sha256_bytes(c_text.encode("utf-8"))
    p2_claim = verified["p2_overflow_claim"]
    return {
        "claim": "P3A.restricted_emitted_expression_equivalence",
        "status": "SOLVER_PROVEN",
        "status_derivation": "all proof_obligations satisfied expected result",
        "semantic_model": {"id": "fixed-width-bitvector-v1", "width": 32, "signedness": "signed" if signed else "unsigned", "wrap_semantics": "excluded-by-obligation", "extension_width": 64},
        "target_model": {"id": "host-c-poc1", "required_static_assertions": ["int32_t == int", "uint32_t == unsigned int", "32-bit widths"], "literal_typing_gate": "INT32_MIN / int-compatible i32 literals / UINT32_C(u32)"},
        "proof_system": {"solver": "Z3", "logic": "QF_BV", "timeout_ms": timeout_ms},
        "scope": {"domain": "accepted input ranges", "granularity": "function return value", "target": "restricted emitted-expression model", "outside_domain": "no claim; signed C may exhibit UB" if signed else "no claim"},
        "subject_binding": {"emitted_c_sha256": c_sha, "specir_sha256": specir_sha256},
        "depends_on": ["P1.accepted_input_domain"],
        "cross_validates": [p2_claim],
        "divergence_policy": "P2/P3 safety disagreement rejects the claim",
        "proof_obligations": proof,
        "tcb": ["Z3 QF_BV implementation", "SpecIR-to-BitVec encoder", "restricted emitted-expression parser/encoder", "return-expression extractor", "64-bit extension lemma", "Python runtime"],
        "not_claimed": ["complete C source semantics", "compiler correctness", "machine-code equivalence", "behavior outside accepted preconditions", "human intent fidelity"],
    }


def build_shared(verified: dict[str, Any], c_path: Path, so_path: Path, *, compiler: str | None = None, optimization: str = "-O2", expected_source_sha256: str | None = None) -> dict[str, Any]:
    if expected_source_sha256 is not None:
        _expect(_sha256_path(c_path) == expected_source_sha256, "E_ARTIFACT_BINDING", "C source changed after P3 validation")
    cc = compiler or shutil.which("cc") or shutil.which("gcc") or shutil.which("clang")
    _expect(cc is not None, "E_CC", "no host C compiler found")
    so_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([cc, "-std=c11", optimization, "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC", str(c_path), "-o", str(so_path)], check=True)
    version = subprocess.run([cc, "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    return {"compiler": cc, "compiler_version": version, "optimization": optimization, "source_sha256": _sha256_path(c_path)}


def exhaustive_binary_check(verified: dict[str, Any], so_path: Path, *, compiler_info: dict[str, Any] | None = None, max_cases: int = 200_000) -> dict[str, Any]:
    fn = verified["function"]
    ranges = [range(verified["input_ranges"][x["id"]][0], verified["input_ranges"][x["id"]][1] + 1) for x in fn["inputs"]]
    cases = 1
    for r in ranges: cases *= len(r)
    _expect(cases <= max_cases, "E_P4_DOMAIN", f"declared domain has {cases} cases; exhaustive limit is {max_cases}; sampled evidence is not implemented")
    lib = ctypes.CDLL(str(so_path.resolve())); cfn = getattr(lib, fn["name"])
    ctype = ctypes.c_int32 if verified["type"] == "i32" else ctypes.c_uint32
    cfn.argtypes = [ctype for _ in fn["inputs"]]; cfn.restype = ctype
    for values in itertools.product(*ranges):
        env = {inp["id"]: value for inp, value in zip(fn["inputs"], values)}
        expected = eval_expr(fn["body"]["expr"], env); actual = int(cfn(*values))
        _expect(actual == expected, "E_P4_MISMATCH", f"binary mismatch inputs={env}: expected {expected}, got {actual}")
    claim = {"claim": "P4.binary_behavior_over_declared_domain", "status": "TESTED_EXHAUSTIVE", "method": "compiled shared-library invocation", "cases": cases}
    if compiler_info: claim.update(compiler_info)
    return claim


def run_all(spec_path: Path, specir_path: Path, build_dir: Path) -> dict[str, Any]:
    spec_info = verify_specification(_load(spec_path)); verified = verify_specir(_load(specir_path), spec_info)
    c_path = build_dir / "safe_add.c"; so_path = build_dir / "libsafe_add.so"
    lower_to_c(verified, c_path)
    p3 = translation_validate(verified, c_path, _sha256_path(specir_path))
    compiler_info = build_shared(verified, c_path, so_path, expected_source_sha256=p3["subject_binding"]["emitted_c_sha256"])
    p4 = exhaustive_binary_check(verified, so_path, compiler_info=compiler_info)
    evidence = {
        "experiment": "POC-1A-v2", "function": verified["function"]["name"], "claims": verified["evidence"] + [p3, p4],
        "explicit_nonclaims": ["human intent fidelity", "general specification completeness", "complete C source semantic equivalence", "C compiler correctness", "machine-code proof", "behavior outside accepted preconditions"],
        "pipeline_tcb": ["Python runtime", "POC-1A-v2 implementation", "Z3", "host OS", "host C compiler/linker", "ctypes/runtime loader"],
    }
    _write_json(build_dir / "evidence.json", evidence); return evidence


def cmd_verify(args: argparse.Namespace) -> None:
    info = verify_specification(_load(args.specification)); verified = verify_specir(_load(args.specir), info)
    print(json.dumps({"status": "PASS", "body_range": verified["body_range"], "evidence": verified["evidence"]}, indent=2))

def cmd_lower(args: argparse.Namespace) -> None:
    info = verify_specification(_load(args.specification)); verified = verify_specir(_load(args.specir), info); lower_to_c(verified, args.output); print(args.output)

def cmd_all(args: argparse.Namespace) -> None: print(json.dumps(run_all(args.specification, args.specir, args.build_dir), indent=2))

def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("verify", "lower", "all"):
        sp = sub.add_parser(name); sp.add_argument("specir", type=Path); sp.add_argument("--specification", required=True, type=Path)
        if name == "lower": sp.add_argument("-o", "--output", required=True, type=Path); sp.set_defaults(func=cmd_lower)
        elif name == "all": sp.add_argument("--build-dir", required=True, type=Path); sp.set_defaults(func=cmd_all)
        else: sp.set_defaults(func=cmd_verify)
    return p

def main() -> int:
    try:
        args = make_parser().parse_args(); args.func(args); return 0
    except (VerificationError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr); return 1

if __name__ == "__main__": raise SystemExit(main())
