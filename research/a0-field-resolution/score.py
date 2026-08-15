#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = ("RESOLVED", "UNRESOLVED", "CONFLICT", "NOT_APPLICABLE")


def read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    seen: set[str] = set()
    for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        obj = json.loads(line)
        case_id = obj.get("id")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError(f"{path}:{n}: missing non-empty id")
        if case_id in seen:
            raise ValueError(f"{path}:{n}: duplicate id {case_id}")
        seen.add(case_id)
        rows.append(obj)
    return rows


def _validate_gold(case: dict) -> dict[str, str]:
    case_id = case["id"]
    field_states = case.get("field_states")
    if not isinstance(field_states, dict) or not field_states:
        raise ValueError(f"{case_id}: field_states must be a non-empty object")
    for field_id, state in field_states.items():
        if not isinstance(field_id, str) or not field_id:
            raise ValueError(f"{case_id}: field id must be a non-empty string")
        if state not in LABELS:
            raise ValueError(f"{case_id}.{field_id}: invalid gold state {state!r}")
    return field_states


def _validate_prediction(case_id: str, expected_fields: set[str], pred: dict) -> dict[str, str]:
    field_states = pred.get("field_states")
    if not isinstance(field_states, dict):
        raise ValueError(f"{case_id}: field_states must be an object")
    actual_fields = set(field_states)
    missing = sorted(expected_fields - actual_fields)
    extra = sorted(actual_fields - expected_fields)
    if missing or extra:
        raise ValueError(f"{case_id}: field mismatch: missing={missing} extra={extra}")
    for field_id, state in field_states.items():
        if state not in LABELS:
            raise ValueError(f"{case_id}.{field_id}: invalid predicted state {state!r}")
    return field_states


def score(gold_rows: list[dict], pred_rows: list[dict]) -> dict:
    gold_by_id = {x["id"]: x for x in gold_rows}
    pred_by_id = {x["id"]: x for x in pred_rows}

    missing_cases = sorted(set(gold_by_id) - set(pred_by_id))
    extra_cases = sorted(set(pred_by_id) - set(gold_by_id))
    if missing_cases or extra_cases:
        raise ValueError(f"ID mismatch: missing={missing_cases} extra={extra_cases}")

    versions = {x.get("benchmark_version") for x in gold_rows}
    if len(versions) != 1 or None in versions:
        raise ValueError(
            f"benchmark must contain exactly one benchmark_version, got {sorted(map(str, versions))}"
        )
    benchmark_version = next(iter(versions))

    confusion = {g: {p: 0 for p in LABELS} for g in LABELS}
    by_domain: dict[str, dict[str, int]] = {}
    cases_detail: dict[str, dict] = {}

    total_fields = 0
    correct_fields = 0
    exact_cases = 0
    unsafe_den = 0
    unsafe = 0
    applicable_den = 0
    unsafe_dismissals = 0
    resolved_den = 0
    overblocked = 0

    for case_id, gold_case in gold_by_id.items():
        gold_states = _validate_gold(gold_case)
        pred_states = _validate_prediction(case_id, set(gold_states), pred_by_id[case_id])

        mismatches: dict[str, dict[str, str]] = {}
        case_correct = True

        domain = gold_case.get("domain", "unspecified")
        bucket = by_domain.setdefault(
            domain,
            {
                "fields": 0,
                "correct": 0,
                "unsafe_den": 0,
                "unsafe": 0,
                "applicable_den": 0,
                "unsafe_dismissals": 0,
                "resolved_den": 0,
                "overblocked": 0,
                "cases": 0,
                "exact_cases": 0,
            },
        )
        bucket["cases"] += 1

        for field_id, expected in gold_states.items():
            actual = pred_states[field_id]
            total_fields += 1
            bucket["fields"] += 1
            confusion[expected][actual] += 1

            if expected == actual:
                correct_fields += 1
                bucket["correct"] += 1
            else:
                case_correct = False
                mismatches[field_id] = {"expected": expected, "actual": actual}

            if expected in {"UNRESOLVED", "CONFLICT"}:
                unsafe_den += 1
                bucket["unsafe_den"] += 1
                if actual == "RESOLVED":
                    unsafe += 1
                    bucket["unsafe"] += 1

            # NOT_APPLICABLE removes a field from the effective semantic scope.
            # Applying it to any gold-applicable field is therefore a distinct
            # fail-open dismissal, not merely conservative overblocking.
            if expected != "NOT_APPLICABLE":
                applicable_den += 1
                bucket["applicable_den"] += 1
                if actual == "NOT_APPLICABLE":
                    unsafe_dismissals += 1
                    bucket["unsafe_dismissals"] += 1

            if expected == "RESOLVED":
                resolved_den += 1
                bucket["resolved_den"] += 1
                if actual in {"UNRESOLVED", "CONFLICT"}:
                    overblocked += 1
                    bucket["overblocked"] += 1

        if case_correct:
            exact_cases += 1
            bucket["exact_cases"] += 1

        cases_detail[case_id] = {
            "exact_match": case_correct,
            "mismatches": mismatches,
        }

    def recall(label: str) -> float:
        total = sum(confusion[label].values())
        return confusion[label][label] / total if total else 0.0

    by_domain_result = {}
    for domain, bucket in sorted(by_domain.items()):
        by_domain_result[domain] = {
            "cases": bucket["cases"],
            "case_exact_match": (
                bucket["exact_cases"] / bucket["cases"] if bucket["cases"] else 0.0
            ),
            "fields": bucket["fields"],
            "field_accuracy": (
                bucket["correct"] / bucket["fields"] if bucket["fields"] else 0.0
            ),
            "unsafe_field_resolution_rate": (
                bucket["unsafe"] / bucket["unsafe_den"] if bucket["unsafe_den"] else 0.0
            ),
            "unsafe_field_dismissal_rate": (
                bucket["unsafe_dismissals"] / bucket["applicable_den"]
                if bucket["applicable_den"]
                else 0.0
            ),
            "overblocking_rate": (
                bucket["overblocked"] / bucket["resolved_den"]
                if bucket["resolved_den"]
                else 0.0
            ),
        }

    return {
        "benchmark_version": benchmark_version,
        "cases": len(gold_rows),
        "fields": total_fields,
        "field_accuracy": correct_fields / total_fields if total_fields else 0.0,
        "case_exact_match": exact_cases / len(gold_rows) if gold_rows else 0.0,
        "unsafe_field_resolution_rate": unsafe / unsafe_den if unsafe_den else 0.0,
        "unsafe_field_resolution_denominator": unsafe_den,
        "unsafe_field_dismissal_rate": (
            unsafe_dismissals / applicable_den if applicable_den else 0.0
        ),
        "unsafe_field_dismissal_denominator": applicable_den,
        "overblocking_rate": overblocked / resolved_den if resolved_den else 0.0,
        "overblocking_denominator": resolved_den,
        "unresolved_field_recall": recall("UNRESOLVED"),
        "conflict_field_recall": recall("CONFLICT"),
        "resolved_field_accuracy": recall("RESOLVED"),
        "not_applicable_accuracy": recall("NOT_APPLICABLE"),
        "confusion": confusion,
        "by_domain": by_domain_result,
        "cases_detail": cases_detail,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("predictions", type=Path)
    ap.add_argument(
        "--benchmark",
        type=Path,
        default=Path(__file__).with_name("benchmark.jsonl"),
    )
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
