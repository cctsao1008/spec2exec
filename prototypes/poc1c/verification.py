"""Target-neutral P1/P2 verification for POC-1C.

This module deliberately contains no C target field, C identifier restriction,
or native ISA detail. It verifies the accepted specification/SpecIR linkage and
bounded-integer obligations used before the Spec2Exec target boundary.
"""

from __future__ import annotations

from typing import Any

SPEC_VERSION = "spec2exec.specification/v0.1"
SPECIR_VERSION = "spec2exec.specir/v0.1"
SUPPORTED_TYPES = {"i32": (-(2**31), 2**31 - 1), "u32": (0, 2**32 - 1)}
ARITH_OPS = {"+", "-", "*"}
CMP_OPS = {"==", "!=", "<", "<=", ">", ">="}
BOOL_OPS = {"and", "or", "not"}


class VerificationError(Exception):
    pass


def expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise VerificationError(f"{code}: {message}")


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def check_range(type_name: str, value: Any, where: str) -> tuple[int, int]:
    expect(type_name in SUPPORTED_TYPES, "E_TYPE", f"{where}.type must be one of {sorted(SUPPORTED_TYPES)}")
    expect(isinstance(value, dict), "E_RANGE", f"{where}.range must be an object")
    lo, hi = value.get("min"), value.get("max")
    expect(isinstance(lo, int) and not isinstance(lo, bool), "E_RANGE", f"{where}.range.min must be integer")
    expect(isinstance(hi, int) and not isinstance(hi, bool), "E_RANGE", f"{where}.range.max must be integer")
    expect(lo <= hi, "E_RANGE", f"{where}.range.min must be <= max")
    tlo, thi = SUPPORTED_TYPES[type_name]
    expect(tlo <= lo <= hi <= thi, "E_RANGE_TYPE", f"{where}.range must fit {type_name}")
    return lo, hi


def trace_list(value: Any, where: str) -> list[str]:
    expect(isinstance(value, list) and value, "E_TRACE", f"{where} must be a non-empty list")
    for index, item in enumerate(value):
        expect(nonempty_string(item), "E_TRACE", f"{where}[{index}] must be non-empty string")
    return value


def validate_expr(expr: Any, symbols: set[str], where: str) -> None:
    if isinstance(expr, bool) or (isinstance(expr, int) and not isinstance(expr, bool)):
        return
    if isinstance(expr, str):
        expect(expr in symbols, "E_EXPR_SYMBOL", f"{where}: unknown symbol {expr}")
        return
    expect(isinstance(expr, dict), "E_EXPR", f"{where}: expression must be symbol/int/object")
    op, args = expr.get("op"), expr.get("args")
    expect(op in ARITH_OPS | CMP_OPS | BOOL_OPS, "E_EXPR_OP", f"{where}: unsupported op {op!r}")
    expect(isinstance(args, list), "E_EXPR_ARGS", f"{where}: args must be list")
    if op == "not":
        expect(len(args) == 1, "E_EXPR_ARITY", f"{where}: not expects 1 arg")
    else:
        expect(len(args) >= 2, "E_EXPR_ARITY", f"{where}: {op} expects at least 2 args")
    for index, arg in enumerate(args):
        validate_expr(arg, symbols, f"{where}.args[{index}]")


def interval(expr: Any, ranges: dict[str, tuple[int, int]]) -> tuple[int, int]:
    if isinstance(expr, int) and not isinstance(expr, bool):
        return expr, expr
    if isinstance(expr, str):
        return ranges[expr]
    expect(isinstance(expr, dict), "E_INTERVAL", "arithmetic expression required")
    op, args = expr.get("op"), expr.get("args")
    expect(op in ARITH_OPS and isinstance(args, list) and len(args) == 2,
           "E_INTERVAL", "interval analysis supports binary + - * only")
    left, right = interval(args[0], ranges), interval(args[1], ranges)
    if op == "+":
        return left[0] + right[0], left[1] + right[1]
    if op == "-":
        return left[0] - right[1], left[1] - right[0]
    products = (
        left[0] * right[0], left[0] * right[1],
        left[1] * right[0], left[1] * right[1],
    )
    return min(products), max(products)


def overflow_code(type_name: str) -> str:
    return "E_SIGNED_OVERFLOW_UB" if type_name == "i32" else "E_UNSIGNED_WRAPAROUND"


def check_all_arith_intermediates(expr: Any, ranges: dict[str, tuple[int, int]],
                                  type_name: str) -> tuple[int, int]:
    tlo, thi = SUPPORTED_TYPES[type_name]
    if isinstance(expr, (int, str)) and not isinstance(expr, bool):
        result = interval(expr, ranges)
        expect(tlo <= result[0] <= result[1] <= thi, overflow_code(type_name),
               f"leaf range {result} exceeds {type_name}")
        return result
    expect(isinstance(expr, dict) and expr.get("op") in ARITH_OPS,
           "E_OVERFLOW_EXPR", "body must be arithmetic expression")
    for arg in expr["args"]:
        check_all_arith_intermediates(arg, ranges, type_name)
    result = interval(expr, ranges)
    expect(tlo <= result[0] <= result[1] <= thi, overflow_code(type_name),
           f"intermediate {expr.get('op')} range {result} exceeds {type_name}")
    return result


def verify_specification(spec: Any) -> dict[str, Any]:
    expect(isinstance(spec, dict), "E_SPEC_ROOT", "specification must be object")
    expect(spec.get("specification_version") == SPEC_VERSION,
           "E_SPEC_VERSION", f"specification_version must be {SPEC_VERSION}")
    acceptance = spec.get("acceptance")
    expect(isinstance(acceptance, dict), "E_SPEC_ACCEPT", "acceptance must be object")
    expect(acceptance.get("status") == "accepted-for-poc", "E_SPEC_ACCEPT",
           "specification must be accepted-for-poc")
    expect(nonempty_string(acceptance.get("authority_role")), "E_SPEC_ACCEPT",
           "authority_role must be non-empty")

    fn = spec.get("function")
    expect(isinstance(fn, dict), "E_SPEC_FUNCTION", "function must be object")
    expect(nonempty_string(fn.get("id")), "E_SPEC_FUNCTION", "function.id required")
    expect(nonempty_string(fn.get("name")), "E_SPEC_FUNCTION", "function.name required")
    inputs = fn.get("inputs")
    expect(isinstance(inputs, list) and inputs, "E_SPEC_INPUTS", "function.inputs must be non-empty list")

    clauses: dict[str, dict[str, Any]] = {}
    names: set[str] = set()
    for index, inp in enumerate(inputs):
        where = f"function.inputs[{index}]"
        expect(isinstance(inp, dict), "E_SPEC_INPUT", f"{where} must be object")
        clause_id, name = inp.get("clause_id"), inp.get("name")
        expect(nonempty_string(clause_id), "E_SPEC_CLAUSE", f"{where}.clause_id required")
        expect(clause_id not in clauses, "E_SPEC_CLAUSE", f"duplicate clause_id {clause_id}")
        expect(nonempty_string(name) and name not in names, "E_SPEC_INPUT",
               f"{where}.name must be unique")
        names.add(name)
        item_range = check_range(inp.get("type"), inp.get("range"), where)
        clauses[clause_id] = {"kind": "input", "name": name, "type": inp["type"], "range": item_range}

    out = fn.get("output")
    expect(isinstance(out, dict), "E_SPEC_OUTPUT", "function.output must be object")
    out_clause = out.get("clause_id")
    expect(nonempty_string(out_clause), "E_SPEC_CLAUSE", "output.clause_id required")
    expect(out_clause not in clauses, "E_SPEC_CLAUSE", f"duplicate clause_id {out_clause}")
    out_range = check_range(out.get("type"), out.get("range"), "function.output")
    clauses[out_clause] = {"kind": "output", "name": out.get("name"), "type": out["type"], "range": out_range}

    behavior = fn.get("behavior")
    expect(isinstance(behavior, dict) and nonempty_string(behavior.get("clause_id")),
           "E_SPEC_BEHAVIOR", "function.behavior clause required")
    expect(behavior["clause_id"] not in clauses, "E_SPEC_CLAUSE",
           f"duplicate clause_id {behavior['clause_id']}")
    clauses[behavior["clause_id"]] = {"kind": "behavior", "expr": behavior.get("expr")}

    overflow = fn.get("overflow_behavior")
    expect(isinstance(overflow, dict) and nonempty_string(overflow.get("clause_id")),
           "E_SPEC_OVERFLOW", "overflow_behavior clause required")
    expect(overflow.get("mode") == "forbidden", "E_SPEC_OVERFLOW",
           "POC-1C requires overflow_behavior.mode='forbidden'")
    expect(overflow["clause_id"] not in clauses, "E_SPEC_CLAUSE",
           f"duplicate clause_id {overflow['clause_id']}")
    clauses[overflow["clause_id"]] = {"kind": "overflow", "mode": "forbidden"}

    return {
        "id": fn["id"],
        "name": fn["name"],
        "inputs": inputs,
        "output": out,
        "behavior": behavior,
        "overflow": overflow,
        "clauses": clauses,
        "acceptance": acceptance,
    }


def verify_specir(doc: Any, spec_info: dict[str, Any]) -> dict[str, Any]:
    expect(isinstance(doc, dict), "E_ROOT", "SpecIR must be object")
    expect(doc.get("specir_version") == SPECIR_VERSION,
           "E_VERSION", f"specir_version must be {SPECIR_VERSION}")
    fn = doc.get("function")
    expect(isinstance(fn, dict), "E_FUNCTION", "function must be object")
    expect("target" not in fn, "E_SPECIR_TARGET_LEAK",
           "machine-independent SpecIR must not contain function.target")
    expect(fn.get("name") == spec_info["name"], "E_SPEC_NAME_LINK",
           "SpecIR function.name differs from accepted specification")

    fn_trace = trace_list(fn.get("trace"), "function.trace")
    expect(spec_info["id"] in fn_trace, "E_SPEC_TRACE_LINK",
           "function.trace must include specification function requirement id")

    inputs = fn.get("inputs")
    expect(isinstance(inputs, list) and len(inputs) == len(spec_info["inputs"]),
           "E_INPUTS", "SpecIR input count mismatch")
    spec_inputs = {item["name"]: item for item in spec_info["inputs"]}
    symbols: set[str] = set()
    ranges: dict[str, tuple[int, int]] = {}
    input_types: dict[str, str] = {}
    seen: set[str] = set()

    for index, inp in enumerate(inputs):
        where = f"function.inputs[{index}]"
        expect(isinstance(inp, dict), "E_INPUT", f"{where} must be object")
        name = inp.get("id")
        expect(nonempty_string(name) and name not in symbols, "E_INPUT",
               f"{where}.id must be unique/non-empty")
        symbols.add(name)
        expect(name in spec_inputs, "E_SPEC_INPUT_LINK", f"SpecIR input {name} not in accepted specification")
        spec_input = spec_inputs[name]
        expect(inp.get("type") == spec_input["type"], "E_SPEC_TYPE_LINK", f"type mismatch for input {name}")
        item_range = check_range(inp.get("type"), inp.get("range"), where)
        expect(item_range == (spec_input["range"]["min"], spec_input["range"]["max"]),
               "E_SPEC_RANGE_LINK", f"range mismatch for input {name}")
        item_trace = trace_list(inp.get("trace"), f"{where}.trace")
        expect(spec_input["clause_id"] in item_trace, "E_UNTRACEABLE_CONSTRAINT",
               f"input {name} range must trace to {spec_input['clause_id']}")
        seen.update(item_trace)
        ranges[name] = item_range
        input_types[name] = inp["type"]

    output = fn.get("output")
    expect(isinstance(output, dict), "E_OUTPUT", "function.output must be object")
    expect(output.get("type") == spec_info["output"]["type"], "E_SPEC_TYPE_LINK", "output type mismatch")
    out_range = check_range(output.get("type"), output.get("range"), "function.output")
    expected_out_range = (spec_info["output"]["range"]["min"], spec_info["output"]["range"]["max"])
    expect(out_range == expected_out_range, "E_SPEC_RANGE_LINK", "output range mismatch")
    out_trace = trace_list(output.get("trace"), "function.output.trace")
    expect(spec_info["output"]["clause_id"] in out_trace, "E_UNTRACEABLE_CONSTRAINT",
           "output range lacks accepted-spec trace")
    seen.update(out_trace)

    expect(fn.get("overflow_behavior") == "forbidden", "E_OVERFLOW_POLICY",
           "POC-1C requires overflow_behavior='forbidden'")
    overflow_trace = trace_list(fn.get("overflow_trace"), "function.overflow_trace")
    expect(spec_info["overflow"]["clause_id"] in overflow_trace, "E_UNTRACEABLE_CONSTRAINT",
           "overflow policy lacks accepted-spec trace")
    seen.update(overflow_trace)

    preconditions = fn.get("preconditions")
    expect(isinstance(preconditions, list) and preconditions, "E_PRE", "preconditions must be non-empty list")
    for index, pre in enumerate(preconditions):
        expect(isinstance(pre, dict), "E_PRE", f"preconditions[{index}] must be object")
        trace_list(pre.get("trace"), f"preconditions[{index}].trace")
        validate_expr(pre.get("expr"), symbols, f"preconditions[{index}].expr")
        seen.update(pre["trace"])
    expected_pre = []
    for inp in inputs:
        lo, hi = ranges[inp["id"]]
        expected_pre.append({
            "trace": inp["trace"],
            "expr": {"op": "and", "args": [
                {"op": ">=", "args": [inp["id"], lo]},
                {"op": "<=", "args": [inp["id"], hi]},
            ]},
        })
    expect([{"trace": item["trace"], "expr": item["expr"]} for item in preconditions] == expected_pre,
           "E_PRE_LINK", "preconditions must be canonical accepted-range projection")

    body = fn.get("body")
    expect(isinstance(body, dict) and body.get("kind") == "expr", "E_BODY", "body.kind must be 'expr'")
    validate_expr(body.get("expr"), symbols, "body.expr")
    body_trace = trace_list(body.get("trace"), "body.trace")
    expect(spec_info["behavior"]["clause_id"] in body_trace, "E_SPEC_BEHAVIOR_LINK",
           "body must trace to accepted behavior clause")
    expect(body["expr"] == spec_info["behavior"]["expr"], "E_SPEC_BEHAVIOR_LINK",
           "body expression differs from accepted specification")
    seen.update(body_trace)

    output_symbol = output.get("id")
    expect(nonempty_string(output_symbol), "E_OUTPUT", "function.output.id required")
    postconditions = fn.get("postconditions")
    expect(isinstance(postconditions, list) and postconditions, "E_POST", "postconditions must be non-empty list")
    post_symbols = symbols | {output_symbol}
    for index, post in enumerate(postconditions):
        expect(isinstance(post, dict), "E_POST", f"postconditions[{index}] must be object")
        trace_list(post.get("trace"), f"postconditions[{index}].trace")
        validate_expr(post.get("expr"), post_symbols, f"postconditions[{index}].expr")
        seen.update(post["trace"])
    expected_post = {"op": "==", "args": [output_symbol, body["expr"]]}
    expect(len(postconditions) == 1 and postconditions[0]["expr"] == expected_post,
           "E_POST_LINK", "POC-1C postcondition must equate output to body expression")
    expect(spec_info["behavior"]["clause_id"] in postconditions[0]["trace"], "E_POST_LINK",
           "postcondition must trace to accepted behavior clause")

    required = set(spec_info["clauses"])
    represented = set(fn_trace) | seen
    missing = required - represented
    expect(not missing, "E_SPEC_CLAUSE_MISSING",
           f"accepted specification clauses missing from SpecIR: {sorted(missing)}")

    common_type = output["type"]
    expect(all(item_type == common_type for item_type in input_types.values()),
           "E_MIXED_TYPE", "POC-1C forbids mixed integer types")
    expr_range = check_all_arith_intermediates(body["expr"], ranges, common_type)
    expect(out_range[0] <= expr_range[0] and expr_range[1] <= out_range[1],
           "E_OUTPUT_RANGE", f"body range {expr_range} not contained in output range {out_range}")
    p2_claim = "P2.no_signed_overflow_ub" if common_type == "i32" else "P2.no_unsigned_wraparound"

    return {
        "function": fn,
        "type": common_type,
        "input_ranges": ranges,
        "output_range": out_range,
        "body_range": expr_range,
        "p2_overflow_claim": p2_claim,
        "evidence": [
            {"id": "P1.function_identity", "status": "CHECKED"},
            {"id": "P1.constraint_traceability", "status": "CHECKED"},
            {"id": "P1.range_linkage", "status": "CHECKED"},
            {"id": "P1.behavior_linkage", "status": "CHECKED"},
            {"id": "P2.fixed_width_type_domain", "status": "CHECKED"},
            {"id": "P2.output_range_containment", "status": "CHECKED"},
            {"id": p2_claim, "status": "CHECKED", "method": "sound interval analysis", "blocking": True},
        ],
    }
