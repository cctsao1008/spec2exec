#!/usr/bin/env python3
"""Minimal deterministic Spec2Exec POC-0 pipeline.

POC-0 intentionally excludes AI. It checks an accepted example specification,
validates a tiny SpecIR v0 subset, checks observable spec-to-SpecIR linkage,
lowers SpecIR to C, compiles with the host C compiler, runs the executable, and
emits explicit verification evidence.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

SPECIFICATION_VERSION = "spec2exec.specification/v0"
SPECIR_VERSION = "spec2exec.specir/v0"
ALLOWED_TOP_LEVEL = {"specir_version", "program"}
ALLOWED_PROGRAM_KEYS = {"id", "name", "target", "trace", "operations", "exit_status"}
ALLOWED_OPERATION_KEYS = {"id", "kind", "text", "trace"}


class VerificationError(Exception):
    pass


def _expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise VerificationError(f"{code}: {message}")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _verify_trace(trace: Any, where: str) -> None:
    _expect(isinstance(trace, list) and len(trace) > 0, "E_TRACE", f"{where}.trace must be a non-empty list")
    for i, item in enumerate(trace):
        _expect(_is_nonempty_string(item), "E_TRACE", f"{where}.trace[{i}] must be a non-empty string")


def verify_specification(specification: Any) -> dict[str, Any]:
    _expect(isinstance(specification, dict), "E_SPEC_ROOT", "specification must be an object")
    _expect(specification.get("specification_version") == SPECIFICATION_VERSION, "E_SPEC_VERSION", f"specification_version must be {SPECIFICATION_VERSION}")
    _expect(_is_nonempty_string(specification.get("requirement_id")), "E_SPEC_REQ", "requirement_id must be a non-empty string")

    behavior = specification.get("behavior")
    _expect(isinstance(behavior, dict), "E_SPEC_BEHAVIOR", "behavior must be an object")
    _expect(isinstance(behavior.get("stdout"), str), "E_SPEC_STDOUT", "behavior.stdout must be a string")
    exit_status = behavior.get("exit_status")
    _expect(isinstance(exit_status, int) and not isinstance(exit_status, bool), "E_SPEC_EXIT", "behavior.exit_status must be an integer")
    _expect(0 <= exit_status <= 255, "E_SPEC_EXIT", "behavior.exit_status must be in [0, 255]")

    acceptance = specification.get("acceptance")
    _expect(isinstance(acceptance, dict), "E_SPEC_ACCEPT", "acceptance must be an object")
    _expect(acceptance.get("status") == "accepted-for-poc", "E_SPEC_ACCEPT", "acceptance.status must be 'accepted-for-poc'")
    _expect(_is_nonempty_string(acceptance.get("authority_role")), "E_SPEC_ACCEPT", "acceptance.authority_role must be a non-empty string")

    return {
        "requirement_id": specification["requirement_id"],
        "stdout": behavior["stdout"],
        "exit_status": behavior["exit_status"],
        "acceptance_status": acceptance["status"],
        "authority_role": acceptance["authority_role"]
    }


def verify_specir(doc: Any, specification: Any | None = None) -> dict[str, Any]:
    _expect(isinstance(doc, dict), "E_ROOT", "SpecIR document must be an object")
    unknown = set(doc) - ALLOWED_TOP_LEVEL
    _expect(not unknown, "E_ROOT_KEY", f"unsupported top-level keys: {sorted(unknown)}")
    _expect(doc.get("specir_version") == SPECIR_VERSION, "E_VERSION", f"specir_version must be {SPECIR_VERSION}")

    program = doc.get("program")
    _expect(isinstance(program, dict), "E_PROGRAM", "program must be an object")
    unknown = set(program) - ALLOWED_PROGRAM_KEYS
    _expect(not unknown, "E_PROGRAM_KEY", f"unsupported program keys: {sorted(unknown)}")

    _expect(_is_nonempty_string(program.get("id")), "E_PROGRAM_ID", "program.id must be a non-empty string")
    _expect(_is_nonempty_string(program.get("name")), "E_PROGRAM_NAME", "program.name must be a non-empty string")
    _expect(program.get("target") == "host-c", "E_TARGET", "POC-0 supports only target='host-c'")
    _verify_trace(program.get("trace"), "program")

    exit_status = program.get("exit_status")
    _expect(isinstance(exit_status, int) and not isinstance(exit_status, bool), "E_EXIT_TYPE", "program.exit_status must be an integer")
    _expect(0 <= exit_status <= 255, "E_EXIT_RANGE", "program.exit_status must be in [0, 255]")

    operations = program.get("operations")
    _expect(isinstance(operations, list) and len(operations) > 0, "E_OPERATIONS", "program.operations must be a non-empty list")

    seen_ids: set[str] = set()
    program_trace = set(program["trace"])
    for index, op in enumerate(operations):
        where = f"program.operations[{index}]"
        _expect(isinstance(op, dict), "E_OPERATION", f"{where} must be an object")
        unknown = set(op) - ALLOWED_OPERATION_KEYS
        _expect(not unknown, "E_OPERATION_KEY", f"{where} has unsupported keys: {sorted(unknown)}")
        op_id = op.get("id")
        _expect(_is_nonempty_string(op_id), "E_OPERATION_ID", f"{where}.id must be a non-empty string")
        _expect(op_id not in seen_ids, "E_DUPLICATE_ID", f"duplicate operation id: {op_id}")
        seen_ids.add(op_id)
        _expect(op.get("kind") == "stdout.write", "E_OPERATION_KIND", f"{where}.kind must be 'stdout.write'")
        _expect(isinstance(op.get("text"), str), "E_TEXT", f"{where}.text must be a string")
        _verify_trace(op.get("trace"), where)
        _expect(set(op["trace"]).issubset(program_trace), "E_TRACE_SCOPE", f"{where}.trace must be covered by program.trace")

    evidence = [
        {"property": "document_structure", "status": "CHECKED"},
        {"property": "supported_version", "status": "CHECKED"},
        {"property": "operation_ids_unique", "status": "CHECKED"},
        {"property": "operation_kinds_supported", "status": "CHECKED"},
        {"property": "traceability_scope", "status": "CHECKED"},
        {"property": "exit_status_range", "status": "CHECKED"}
    ]

    if specification is not None:
        spec = verify_specification(specification)
        actual_stdout = "".join(op["text"] for op in operations)
        _expect(spec["requirement_id"] in program_trace, "E_SPEC_TRACE", "accepted requirement_id is not present in program.trace")
        _expect(actual_stdout == spec["stdout"], "E_SPEC_STDOUT_LINK", "SpecIR stdout behavior differs from accepted specification")
        _expect(program["exit_status"] == spec["exit_status"], "E_SPEC_EXIT_LINK", "SpecIR exit status differs from accepted specification")
        evidence.extend([
            {"property": "specification_acceptance_record_present", "status": "HUMAN-DECLARED"},
            {"property": "requirement_trace_linkage", "status": "CHECKED"},
            {"property": "observable_stdout_linkage", "status": "CHECKED"},
            {"property": "observable_exit_status_linkage", "status": "CHECKED"}
        ])

    return {
        "result": "PASS",
        "specir_version": SPECIR_VERSION,
        "program_id": program["id"],
        "evidence": evidence,
        "not_verified": [
            "human_intent_fidelity",
            "general_specification_completeness",
            "lowering_equivalence_proof",
            "C_compiler_correctness",
            "machine_code_semantic_equivalence"
        ]
    }


def _c_string_literal(text: str) -> str:
    encoded = text.encode("utf-8")
    parts = ['"']
    for b in encoded:
        if b == 0x22:
            parts.append('\\"')
        elif b == 0x5C:
            parts.append('\\\\')
        elif b == 0x0A:
            parts.append('\\n')
        elif b == 0x0D:
            parts.append('\\r')
        elif b == 0x09:
            parts.append('\\t')
        elif 0x20 <= b <= 0x7E:
            parts.append(chr(b))
        else:
            parts.append(f"\\{b:03o}")
    parts.append('"')
    return "".join(parts)


def lower_to_c(doc: dict[str, Any]) -> str:
    program = doc["program"]
    lines = [
        "/* Generated by Spec2Exec POC-0. Do not edit as source of truth. */",
        f"/* program.id: {program['id']} */",
        f"/* trace: {', '.join(program['trace'])} */",
        "#include <stdio.h>",
        "",
        "int main(void)",
        "{",
    ]
    for op in program["operations"]:
        lines.append(f"    /* {op['id']} | trace: {', '.join(op['trace'])} */")
        lines.append(f"    if (fputs({_c_string_literal(op['text'])}, stdout) == EOF) return 111;")
    lines.append(f"    return {program['exit_status']};")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"E_INPUT: {exc}") from exc


def load_optional_specification(path: Path | None) -> Any | None:
    return None if path is None else load_json(path)


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def cmd_verify(args: argparse.Namespace) -> int:
    doc = load_json(args.specir)
    specification = load_optional_specification(args.specification)
    evidence = verify_specir(doc, specification)
    if args.evidence:
        write_json(args.evidence, evidence)
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


def cmd_lower(args: argparse.Namespace) -> int:
    doc = load_json(args.specir)
    specification = load_optional_specification(args.specification)
    evidence = verify_specir(doc, specification)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(lower_to_c(doc), encoding="utf-8")
    if args.evidence:
        write_json(args.evidence, evidence)
    print(f"lowered: {args.output}")
    return 0


def find_cc(explicit: str | None) -> str:
    if explicit:
        return explicit
    for candidate in (os.environ.get("CC"), "cc", "gcc", "clang"):
        if candidate and shutil.which(candidate):
            return candidate
    raise VerificationError("E_TOOLCHAIN: no C compiler found (set CC or pass --cc)")


def cmd_build(args: argparse.Namespace) -> int:
    doc = load_json(args.specir)
    specification = load_optional_specification(args.specification)
    evidence = verify_specir(doc, specification)
    args.build_dir.mkdir(parents=True, exist_ok=True)
    c_path = args.build_dir / "generated.c"
    exe_path = args.build_dir / "hello"
    evidence_path = args.build_dir / "verification.json"
    c_path.write_text(lower_to_c(doc), encoding="utf-8")
    write_json(evidence_path, evidence)
    cc = find_cc(args.cc)
    subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(c_path), "-o", str(exe_path)], check=True)
    print(f"compiler: {cc}")
    print(f"executable: {exe_path}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    doc = load_json(args.specir)
    specification = load_optional_specification(args.specification)
    verify_specir(doc, specification)
    program = doc["program"]
    expected_stdout = "".join(op["text"] for op in program["operations"] if op["kind"] == "stdout.write")
    expected_exit = program["exit_status"]
    completed = subprocess.run([str(args.executable)], capture_output=True, text=True)
    _expect(completed.stdout == expected_stdout, "E_RUNTIME_STDOUT", f"stdout mismatch: {completed.stdout!r} != {expected_stdout!r}")
    _expect(completed.returncode == expected_exit, "E_RUNTIME_EXIT", f"exit status mismatch: {completed.returncode} != {expected_exit}")
    print("runtime_check: PASS")
    return 0


def cmd_all(args: argparse.Namespace) -> int:
    build_args = argparse.Namespace(specir=args.specir, specification=args.specification, build_dir=args.build_dir, cc=args.cc)
    cmd_build(build_args)
    run_args = argparse.Namespace(specir=args.specir, specification=args.specification, executable=args.build_dir / "hello")
    return cmd_run(run_args)


def add_common_specification_argument(command: argparse.ArgumentParser) -> None:
    command.add_argument("--specification", type=Path)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Spec2Exec deterministic POC-0")
    sub = p.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify")
    verify.add_argument("specir", type=Path)
    add_common_specification_argument(verify)
    verify.add_argument("--evidence", type=Path)
    verify.set_defaults(func=cmd_verify)

    lower = sub.add_parser("lower")
    lower.add_argument("specir", type=Path)
    add_common_specification_argument(lower)
    lower.add_argument("-o", "--output", type=Path, required=True)
    lower.add_argument("--evidence", type=Path)
    lower.set_defaults(func=cmd_lower)

    build = sub.add_parser("build")
    build.add_argument("specir", type=Path)
    add_common_specification_argument(build)
    build.add_argument("--build-dir", type=Path, default=Path("build/poc0"))
    build.add_argument("--cc")
    build.set_defaults(func=cmd_build)

    run = sub.add_parser("run")
    run.add_argument("specir", type=Path)
    add_common_specification_argument(run)
    run.add_argument("executable", type=Path)
    run.set_defaults(func=cmd_run)

    all_cmd = sub.add_parser("all")
    all_cmd.add_argument("specir", type=Path)
    add_common_specification_argument(all_cmd)
    all_cmd.add_argument("--build-dir", type=Path, default=Path("build/poc0"))
    all_cmd.add_argument("--cc")
    all_cmd.set_defaults(func=cmd_all)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except VerificationError as exc:
        print(f"verification: FAIL\n{exc}", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"toolchain: FAIL\n{exc}", file=sys.stderr)
        return exc.returncode or 3


if __name__ == "__main__":
    raise SystemExit(main())
