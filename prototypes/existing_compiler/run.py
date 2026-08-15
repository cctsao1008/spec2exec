#!/usr/bin/env python3
"""Evidence wrapper for the existing-compiler realization experiment.

The experiment deliberately reuses the historical POC-0 SpecIR -> C lowering
and delegates C -> executable realization to an installed host compiler.
The compiler is named as TRUSTED infrastructure; this script does not claim
compiler verification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]


class ExperimentError(Exception):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ExperimentError(f"{path}: JSON root must be an object")
    return value


def compiler_version(cc: str) -> str:
    completed = subprocess.run([cc, "--version"], capture_output=True, text=True, check=True)
    text = (completed.stdout or completed.stderr).splitlines()
    return text[0] if text else "unknown"


def find_cc(explicit: str | None) -> str:
    if explicit:
        found = shutil.which(explicit)
        if not found:
            raise ExperimentError(f"compiler not found: {explicit}")
        return found
    for candidate in ("cc", "gcc", "clang"):
        found = shutil.which(candidate)
        if found:
            return found
    raise ExperimentError("no host C compiler found")


def run_executable(executable: Path) -> tuple[int, str, str]:
    completed = subprocess.run([str(executable)], capture_output=True, text=True)
    return completed.returncode, completed.stdout, completed.stderr


def mutate_generated_c(source: str, expected_stdout: str) -> str:
    needle = "Hello, world!"
    if needle not in source or expected_stdout != "Hello, world!\n":
        raise ExperimentError("sensitivity mutation is defined only for the current hello fixture")
    return source.replace(needle, "MUTATED-WORLD", 1)


def run_experiment(specification: Path, specir: Path, build_dir: Path, cc: str) -> dict[str, Any]:
    build_dir.mkdir(parents=True, exist_ok=True)
    poc0 = ROOT / "prototypes/poc0/spec2exec_poc0.py"
    command = [
        sys.executable,
        str(poc0),
        "all",
        str(specir),
        "--specification",
        str(specification),
        "--build-dir",
        str(build_dir),
        "--cc",
        cc,
    ]
    subprocess.run(command, cwd=ROOT, check=True)

    generated_c = build_dir / "generated.c"
    executable = build_dir / "hello"
    verification = build_dir / "verification.json"
    for path in (generated_c, executable, verification):
        if not path.is_file():
            raise ExperimentError(f"expected artifact missing: {path}")

    spec_doc = read_json(specification)
    behavior = spec_doc.get("behavior")
    if not isinstance(behavior, dict):
        raise ExperimentError("specification.behavior must be an object")
    expected_stdout = behavior.get("stdout")
    expected_exit = behavior.get("exit_status")
    if not isinstance(expected_stdout, str) or not isinstance(expected_exit, int):
        raise ExperimentError("specification behavior must define stdout and integer exit_status")

    returncode, stdout, stderr = run_executable(executable)
    if returncode != expected_exit or stdout != expected_stdout:
        raise ExperimentError(
            f"compiled executable violates accepted behavior: rc={returncode}, stdout={stdout!r}, stderr={stderr!r}"
        )

    mutated_c = build_dir / "generated.mutated.c"
    mutated_exe = build_dir / "hello-mutated"
    mutated_c.write_text(
        mutate_generated_c(generated_c.read_text(encoding="utf-8"), expected_stdout),
        encoding="utf-8",
    )
    mutation_command = [cc, "-std=c11", "-Wall", "-Wextra", "-Werror", str(mutated_c), "-o", str(mutated_exe)]
    subprocess.run(mutation_command, check=True)
    m_rc, m_out, _ = run_executable(mutated_exe)
    mutation_detected = m_rc != expected_exit or m_out != expected_stdout
    if not mutation_detected:
        raise ExperimentError("runtime oracle failed to detect known-bad generated-C mutation")

    version = compiler_version(cc)
    evidence = {
        "schema": "spec2exec.existing-compiler-evidence/v0.1",
        "experiment": "poc0-host-c",
        "claim_boundaries": [
            {
                "claim_id": "CGEN.specir_to_c",
                "status": "TESTED",
                "subject": "SpecIR -> generated C",
                "method": "poc0 deterministic lowering plus specification/runtime regression",
                "limitations": ["No formal lowering-equivalence proof is claimed."],
            },
            {
                "claim_id": "CC.c_to_executable",
                "status": "TRUSTED",
                "subject": "generated C -> host executable",
                "method": "external host C compiler",
                "tool": {"path": cc, "version": version, "invocation": command},
                "limitations": ["The host C compiler is trusted, not verified by Spec2Exec."],
            },
            {
                "claim_id": "CRUN.runtime_observation",
                "status": "TESTED",
                "subject": "host executable -> accepted stdout/exit contract",
                "method": "direct process execution",
                "observation": {"exit_status": returncode, "stdout": stdout},
            },
            {
                "claim_id": "CRUN.sensitivity",
                "status": "TESTED",
                "subject": "known-bad generated-C mutation -> runtime oracle",
                "method": "replace hello payload, rebuild, execute, require mismatch",
                "observation": {"mutation_detected": mutation_detected, "exit_status": m_rc, "stdout": m_out},
            },
        ],
        "artifacts": {
            "specification": {"path": str(specification), "sha256": sha256(specification)},
            "specir": {"path": str(specir), "sha256": sha256(specir)},
            "generated_c": {"path": str(generated_c), "sha256": sha256(generated_c)},
            "executable": {"path": str(executable), "sha256": sha256(executable)},
            "poc0_verification": {"path": str(verification), "sha256": sha256(verification)},
            "mutated_c": {"path": str(mutated_c), "sha256": sha256(mutated_c)},
            "mutated_executable": {"path": str(mutated_exe), "sha256": sha256(mutated_exe)},
        },
        "overall_statement": (
            "Spec2Exec can preserve explicit evidence boundaries while delegating realization to a conventional "
            "C compiler. This experiment does not claim the compiler is formally verified."
        ),
    }
    return evidence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specification", type=Path, default=ROOT / "examples/hello/specification.json")
    ap.add_argument("--specir", type=Path, default=ROOT / "examples/hello/hello.specir.json")
    ap.add_argument("--build-dir", type=Path, default=ROOT / "build/existing-compiler")
    ap.add_argument("--cc")
    ap.add_argument("--evidence")
    args = ap.parse_args()

    try:
        cc = find_cc(args.cc)
        evidence = run_experiment(args.specification, args.specir, args.build_dir, cc)
    except (OSError, json.JSONDecodeError, subprocess.CalledProcessError, ExperimentError) as exc:
        print(f"existing_compiler: FAIL: {exc}", file=sys.stderr)
        return 2

    output = Path(args.evidence) if args.evidence else args.build_dir / "evidence.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
