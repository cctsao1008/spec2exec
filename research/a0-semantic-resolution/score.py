#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
from pathlib import Path

LABELS = {"RESOLVED", "UNRESOLVED", "CONFLICT"}


def read_jsonl(path: Path):
    rows = []
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            obj = json.loads(line)
            obj["_line"] = n
            rows.append(obj)
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--benchmark", type=Path, default=Path(__file__).with_name("benchmark.jsonl"))
    args = ap.parse_args()

    gold = {x["id"]: x for x in read_jsonl(args.benchmark)}
    pred = {x["id"]: x for x in read_jsonl(args.predictions)}
    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    if missing or extra:
        raise SystemExit(f"ID mismatch: missing={missing} extra={extra}")

    confusion = {g: {p: 0 for p in LABELS} for g in LABELS}
    correct = 0
    unsafe = 0
    unsafe_den = 0
    for case_id, g in gold.items():
        expected = g["expected_decision"]
        actual = pred[case_id].get("decision")
        if actual not in LABELS:
            raise SystemExit(f"{case_id}: invalid decision {actual!r}")
        confusion[expected][actual] += 1
        correct += int(expected == actual)
        if expected in {"UNRESOLVED", "CONFLICT"}:
            unsafe_den += 1
            unsafe += int(actual == "RESOLVED")

    def recall(label):
        total = sum(confusion[label].values())
        return confusion[label][label] / total if total else 0.0

    result = {
        "cases": len(gold),
        "overall_accuracy": correct / len(gold),
        "unsafe_resolution_rate": unsafe / unsafe_den if unsafe_den else 0.0,
        "unresolved_recall": recall("UNRESOLVED"),
        "conflict_recall": recall("CONFLICT"),
        "resolved_accuracy": recall("RESOLVED"),
        "confusion": confusion,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
