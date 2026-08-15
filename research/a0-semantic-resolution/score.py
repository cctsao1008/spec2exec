#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = ("RESOLVED", "UNRESOLVED", "CONFLICT")


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        case_id = obj.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise SystemExit(f"{path}:{n}: missing non-empty id")
        if case_id in seen:
            raise SystemExit(f"{path}:{n}: duplicate id {case_id}")
        seen.add(case_id)
        rows.append(obj)
    return rows


def score(gold_rows: list[dict], pred_rows: list[dict]) -> dict:
    gold = {x["id"]: x for x in gold_rows}
    pred = {x["id"]: x for x in pred_rows}
    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    if missing or extra:
        raise ValueError(f"ID mismatch: missing={missing} extra={extra}")

    versions = {x.get("benchmark_version") for x in gold_rows}
    if len(versions) != 1 or None in versions:
        raise ValueError(f"benchmark must contain exactly one benchmark_version, got {sorted(map(str, versions))}")
    benchmark_version = next(iter(versions))

    confusion = {g: {p: 0 for p in LABELS} for g in LABELS}
    correct = 0
    unsafe = 0
    unsafe_den = 0
    by_domain: dict[str, dict[str, int]] = {}

    for case_id, g in gold.items():
        expected = g.get("expected_decision")
        if expected not in LABELS:
            raise ValueError(f"{case_id}: invalid expected_decision {expected!r}")
        actual = pred[case_id].get("decision")
        if actual not in LABELS:
            raise ValueError(f"{case_id}: invalid decision {actual!r}")

        confusion[expected][actual] += 1
        correct += int(expected == actual)
        if expected in {"UNRESOLVED", "CONFLICT"}:
            unsafe_den += 1
            unsafe += int(actual == "RESOLVED")

        domain = g.get("domain", "unspecified")
        bucket = by_domain.setdefault(domain, {"cases": 0, "correct": 0, "unsafe_cases": 0, "unsafe_resolutions": 0})
        bucket["cases"] += 1
        bucket["correct"] += int(expected == actual)
        if expected in {"UNRESOLVED", "CONFLICT"}:
            bucket["unsafe_cases"] += 1
            bucket["unsafe_resolutions"] += int(actual == "RESOLVED")

    def recall(label: str) -> float:
        total = sum(confusion[label].values())
        return confusion[label][label] / total if total else 0.0

    domain_metrics = {}
    for domain, bucket in sorted(by_domain.items()):
        domain_metrics[domain] = {
            "cases": bucket["cases"],
            "accuracy": bucket["correct"] / bucket["cases"],
            "unsafe_resolution_rate": (
                bucket["unsafe_resolutions"] / bucket["unsafe_cases"] if bucket["unsafe_cases"] else 0.0
            ),
        }

    return {
        "benchmark_version": benchmark_version,
        "cases": len(gold),
        "overall_accuracy": correct / len(gold) if gold else 0.0,
        "unsafe_resolution_rate": unsafe / unsafe_den if unsafe_den else 0.0,
        "unsafe_resolution_denominator": unsafe_den,
        "unresolved_recall": recall("UNRESOLVED"),
        "conflict_recall": recall("CONFLICT"),
        "resolved_accuracy": recall("RESOLVED"),
        "confusion": confusion,
        "by_domain": domain_metrics,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions", type=Path)
    ap.add_argument("--benchmark", type=Path, default=Path(__file__).with_name("benchmark.jsonl"))
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    try:
        result = score(read_jsonl(args.benchmark), read_jsonl(args.predictions))
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
