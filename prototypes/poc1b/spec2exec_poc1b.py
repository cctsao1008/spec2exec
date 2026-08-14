#!/usr/bin/env python3
"""Spec2Exec POC-1B: C-aware contract validation and optimization destruction."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
V2_PATH = ROOT / "prototypes" / "poc1" / "spec2exec_poc1_v2.py"
spec = importlib.util.spec_from_file_location("spec2exec_poc1_v2", V2_PATH)
v2 = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(v2)


class Poc1BError(Exception):
    pass


def _expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise Poc1BError(f"{code}: {message}")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def verify_poc1b_contract(spec_doc: dict[str, Any], verified: dict[str, Any]) -> dict[str, Any]:
    contract = spec_doc.get("function", {}).get("contract")
    _expect(isinstance(contract, dict), "E_POC1B_CONTRACT", "function.contract is required")
    clause_id = contract.get("clause_id")
    expr = contract.get("expr")
    _expect(isinstance(clause_id, str) and clause_id, "E_POC1B_CONTRACT", "contract.clause_id required")
    symbols = {x["id"] for x in verified["function"]["inputs"]}
    _expect(isinstance(expr, (str, int, dict)), "E_POC1B_CONTRACT", "contract.expr required")
    v2._validate_expr(expr, symbols, "function.contract.expr")
    return {"clause_id": clause_id, "expr": expr}


def _contract_c_expr(expr: Any, type_name: str) -> str:
    if isinstance(expr, int) and not isinstance(expr, bool):
        return v2.c_literal(expr, type_name)
    if isinstance(expr, str):
        return expr
    _expect(isinstance(expr, dict), "E_POC1B_CONTRACT_EXPR", "contract expression must be arithmetic")
    op, args = expr.get("op"), expr.get("args")
    _expect(op in {"+", "-", "*"} and isinstance(args, list) and len(args) == 2, "E_POC1B_CONTRACT_EXPR", "contract emitter supports binary + - *")
    return f"({_contract_c_expr(args[0], type_name)} {op} {_contract_c_expr(args[1], type_name)})"


def generate_cbmc_harness(verified: dict[str, Any], contract: dict[str, Any], target_path: Path, harness_path: Path) -> None:
    fn = verified["function"]
    type_name = verified["type"]
    ctype = "int32_t" if type_name == "i32" else "uint32_t"
    nondet_name = "nondet_i32" if type_name == "i32" else "nondet_u32"
    lines = ["#include <stdint.h>", "#include <limits.h>", f'#include "{target_path.name}"', "", f"extern {ctype} {nondet_name}(void);", "", "void spec2exec_p3_validation(void)", "{"]
    for inp in fn["inputs"]:
        lines.append(f"    {ctype} {inp['id']} = {nondet_name}();")
    for inp in fn["inputs"]:
        lo, hi = verified["input_ranges"][inp["id"]]
        lines.append(f"    __CPROVER_assume({inp['id']} >= {v2.c_literal(lo, type_name)} && {inp['id']} <= {v2.c_literal(hi, type_name)});")
    args = ", ".join(x["id"] for x in fn["inputs"])
    lines.append(f"    {ctype} result = {fn['name']}({args});")
    lines.append(f'    __CPROVER_assert(result == {_contract_c_expr(contract["expr"], type_name)}, "TRACE: {contract["clause_id"]}");')
    lines.append("}")
    harness_path.parent.mkdir(parents=True, exist_ok=True)
    harness_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cbmc_validate(verified: dict[str, Any], contract: dict[str, Any], target_path: Path, harness_path: Path) -> dict[str, Any]:
    cbmc = shutil.which("cbmc")
    _expect(cbmc is not None, "E_CBMC_MISSING", "cbmc is required for POC-1B")
    generate_cbmc_harness(verified, contract, target_path, harness_path)
    version = subprocess.run([cbmc, "--version"], capture_output=True, text=True, check=True).stdout.strip()
    show = subprocess.run([cbmc, harness_path.name, "--function", "spec2exec_p3_validation", "--show-properties"], cwd=harness_path.parent, capture_output=True, text=True)
    _expect(show.returncode == 0, "E_CBMC_PROPERTIES", show.stdout + show.stderr)
    _expect(contract["clause_id"] in show.stdout + show.stderr, "E_CBMC_TRACE", "contract trace id not visible in CBMC property listing")
    overflow_flag = "--signed-overflow-check" if verified["type"] == "i32" else "--unsigned-overflow-check"
    flags = ["--function", "spec2exec_p3_validation", overflow_flag]
    run = subprocess.run([cbmc, harness_path.name, *flags], cwd=harness_path.parent, capture_output=True, text=True)
    output = run.stdout + run.stderr
    _expect(run.returncode == 0 and "VERIFICATION SUCCESSFUL" in output, "E_CBMC_VERIFY", output)
    return {
        "claim": "P3B.c_source_contract_conformance",
        "status": "MODEL_CHECKED",
        "tool": version,
        "method": "CBMC C semantic model checking",
        "scope": "function boundary over accepted input ranges; straight-line function",
        "contract_trace": [contract["clause_id"]],
        "subject_binding": {"emitted_c_sha256": v2._sha256_path(target_path), "harness_sha256": v2._sha256_path(harness_path)},
        "checks": [overflow_flag],
        "not_claimed": ["compiler optimization correctness", "machine-code equivalence", "target ABI/hardware behavior"],
    }


def _llvm_arith_count(text: str) -> int:
    return len(re.findall(r"^\s*%[A-Za-z0-9_.]+\s*=\s*(?:add|sub)\b.*\bi32\b", text, re.MULTILINE))


def optimization_destruction(target_path: Path, fn_name: str, build_dir: Path) -> dict[str, Any]:
    clang = shutil.which("clang")
    _expect(clang is not None, "E_CLANG_MISSING", "clang is required for POC-1B optimization observation")
    o0 = build_dir / "target.O0.ll"
    o2 = build_dir / "target.O2.ll"
    subprocess.run([clang, "-std=c11", "-O0", "-S", "-emit-llvm", str(target_path), "-o", str(o0)], check=True)
    subprocess.run([clang, "-std=c11", "-O2", "-S", "-emit-llvm", str(target_path), "-o", str(o2)], check=True)
    o0_text, o2_text = o0.read_text(encoding="utf-8"), o2.read_text(encoding="utf-8")
    o0_count, o2_count = _llvm_arith_count(o0_text), _llvm_arith_count(o2_text)
    _expect(o0_count >= 2, "E_POC1B_STRUCTURE", f"expected visible add/sub structure at -O0, found {o0_count}")
    _expect(o2_count == 0, "E_POC1B_STRUCTURE", f"expected add/sub structure destroyed at -O2, found {o2_count}")
    _expect(re.search(rf"define\b.*@{re.escape(fn_name)}\b", o2_text) is not None, "E_POC1B_STRUCTURE", "optimized function missing")
    version = subprocess.run([clang, "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    return {
        "claim": "POC1B.optimization_structural_destruction",
        "status": "CHECKED",
        "compiler": version,
        "observation": "add/sub instructions visible at -O0 and absent at -O2",
        "o0_arithmetic_instructions": o0_count,
        "o2_arithmetic_instructions": o2_count,
        "artifacts": {"o0_llvm_sha256": v2._sha256_path(o0), "o2_llvm_sha256": v2._sha256_path(o2)},
        "semantic_claim": "none; this claim only demonstrates structural identity was destroyed",
    }


def run_all(spec_path: Path, specir_path: Path, build_dir: Path) -> dict[str, Any]:
    spec_doc, ir_doc = _load(spec_path), _load(specir_path)
    spec_info = v2.verify_specification(spec_doc)
    verified = v2.verify_specir(ir_doc, spec_info)
    contract = verify_poc1b_contract(spec_doc, verified)
    build_dir.mkdir(parents=True, exist_ok=True)
    target = build_dir / "target.c"
    harness = build_dir / "verification_harness.c"
    so = build_dir / "libtarget.so"
    v2.lower_to_c(verified, target, banner="POC-1B")
    p3a = v2.translation_validate(verified, target, v2._sha256_path(specir_path))
    p3b = cbmc_validate(verified, contract, target, harness)
    structural = optimization_destruction(target, verified["function"]["name"], build_dir)
    clang = shutil.which("clang")
    compiler_info = v2.build_shared(verified, target, so, compiler=clang, optimization="-O2", expected_source_sha256=p3b["subject_binding"]["emitted_c_sha256"])
    p4 = v2.exhaustive_binary_check(verified, so, compiler_info=compiler_info)
    evidence = {
        "experiment": "POC-1B",
        "function": verified["function"]["name"],
        "contract_trace": [contract["clause_id"]],
        "claims": verified["evidence"] + [p3a, p3b, structural, p4],
        "result": "PASS",
        "explicit_nonclaims": ["ARM/target ABI semantics", "LLVM optimization proof", "compiler correctness", "machine-code proof", "human intent fidelity"],
    }
    _write_json(build_dir / "evidence.json", evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("specir", type=Path)
    parser.add_argument("--specification", required=True, type=Path)
    parser.add_argument("--build-dir", required=True, type=Path)
    try:
        args = parser.parse_args()
        print(json.dumps(run_all(args.specification, args.specir, args.build_dir), indent=2))
        return 0
    except (Poc1BError, v2.VerificationError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
