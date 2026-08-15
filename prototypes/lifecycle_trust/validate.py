#!/usr/bin/env python3
"""Run the bounded RFC 0012 lifecycle validation fixtures and emit evidence."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "examples/payment-retry/lifecycle"
TEST_DIR = ROOT / "tests/lifecycle_trust"


def load_evaluator():
    path = ROOT / "prototypes/lifecycle_trust/evaluate.py"
    spec = importlib.util.spec_from_file_location("lifecycle_trust", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_revision() -> str:
    github_sha = os.environ.get("GITHUB_SHA")
    if github_sha:
        return github_sha
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def discovered_test_count() -> int:
    path = TEST_DIR / "test_lifecycle_trust.py"
    spec = importlib.util.spec_from_file_location("test_lifecycle_trust", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return unittest.defaultTestLoader.loadTestsFromModule(module).countTestCases()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-dir", type=Path, required=True)
    ap.add_argument("--summary", type=Path, required=True)
    args = ap.parse_args()

    mod = load_evaluator()
    scenarios = [
        ("baseline-v7.json", "CURRENT"),
        ("contract-v8-stale.json", "BLOCKED"),
        ("contract-v8-revalidated.json", "CURRENT"),
    ]

    args.build_dir.mkdir(parents=True, exist_ok=True)
    records = []
    artifact_hashes = set()

    for filename, expected in scenarios:
        input_path = FIXTURE_DIR / filename
        document = json.loads(input_path.read_text(encoding="utf-8"))
        result = mod.evaluate(document)
        if result["decision"] != expected:
            raise SystemExit(
                f"{filename}: expected {expected}, got {result['decision']}"
            )
        output_path = args.build_dir / filename.replace(".json", "-result.json")
        output_path.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        markdown_path = args.build_dir / filename.replace(".json", "-result.md")
        markdown_path.write_text(mod.render_markdown(result) + "\n", encoding="utf-8")
        artifact_hashes.add(document["artifact"]["sha256"])
        records.append(
            {
                "scenario_id": document["scenario_id"],
                "input_file": str(input_path.relative_to(ROOT)),
                "input_sha256": sha256_file(input_path),
                "expected_decision": expected,
                "actual_decision": result["decision"],
                "result_file": str(output_path),
                "result_sha256": sha256_file(output_path),
                "blocker_count": len(result["blockers"]),
                "reusable_evidence_ids": result["reusable_evidence_ids"],
            }
        )

    schema_paths = [
        ROOT / "spec/schemas/lifecycle-trust-input-v0.1.schema.json",
        ROOT / "spec/schemas/lifecycle-trust-result-v0.1.schema.json",
    ]
    for schema_path in schema_paths:
        json.loads(schema_path.read_text(encoding="utf-8"))

    summary = {
        "schema": "spec2exec.lifecycle-trust-validation/v0.1",
        "source_revision": source_revision(),
        "python_version": platform.python_version(),
        "evaluator": "prototypes/lifecycle_trust/evaluate.py",
        "evaluator_sha256": sha256_file(ROOT / "prototypes/lifecycle_trust/evaluate.py"),
        "schema_sha256": {
            str(path.relative_to(ROOT)): sha256_file(path) for path in schema_paths
        },
        "discovered_unit_test_count": discovered_test_count(),
        "scenario_count": len(records),
        "artifact_byte_identity_across_scenarios": len(artifact_hashes) == 1,
        "artifact_sha256_values": sorted(artifact_hashes),
        "scenarios": records,
        "claims": [
            "This summary records deterministic bounded POC observations, not formal proof.",
            "RFC 0011 authority records are consumed as imported inputs; the lifecycle evaluator does not create semantic authority.",
            "RFC 0006 evidence statuses are preserved without scalar ordering.",
        ],
    }

    if not summary["artifact_byte_identity_across_scenarios"]:
        raise SystemExit("expected all lifecycle scenarios to bind the same artifact SHA-256")

    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
