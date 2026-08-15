#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


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


def _ids(items: list[dict], case_id: str) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            raise ValueError(f"{case_id}: every gold obligation needs a non-empty id")
        if item["id"] in result:
            raise ValueError(f"{case_id}: duplicate gold obligation {item['id']}")
        result[item["id"]] = item
    return result


def score(gold_rows: list[dict], pred_rows: list[dict]) -> dict:
    gold_by_id = {x["id"]: x for x in gold_rows}
    pred_by_id = {x["id"]: x for x in pred_rows}
    missing_cases = sorted(set(gold_by_id) - set(pred_by_id))
    extra_cases = sorted(set(pred_by_id) - set(gold_by_id))
    if missing_cases or extra_cases:
        raise ValueError(f"ID mismatch: missing={missing_cases} extra={extra_cases}")

    versions = {x.get("benchmark_version") for x in gold_rows}
    if len(versions) != 1 or None in versions:
        raise ValueError(f"benchmark must contain exactly one benchmark_version, got {versions!r}")
    version = next(iter(versions))

    total_gold = found_gold = total_pred = spurious = 0
    high_total = high_found = 0
    by_domain: dict[str, dict[str, int]] = {}
    case_results: dict[str, dict] = {}

    for case_id, case in gold_by_id.items():
        gold = _ids(case.get("gold_obligations", []), case_id)
        pred_items = pred_by_id[case_id].get("obligations")
        if not isinstance(pred_items, list) or not all(isinstance(x, str) and x for x in pred_items):
            raise ValueError(f"{case_id}: obligations must be a list of non-empty strings")
        if len(pred_items) != len(set(pred_items)):
            raise ValueError(f"{case_id}: duplicate predicted obligation")
        pred = set(pred_items)
        gold_ids = set(gold)
        found = gold_ids & pred
        omitted = gold_ids - pred
        extra = pred - gold_ids

        total_gold += len(gold_ids)
        found_gold += len(found)
        total_pred += len(pred)
        spurious += len(extra)

        high_ids = {k for k, v in gold.items() if v.get("impact") in {"HIGH", "CRITICAL"}}
        high_total += len(high_ids)
        high_found += len(high_ids & pred)

        domain = case.get("domain", "unspecified")
        bucket = by_domain.setdefault(domain, {"gold": 0, "found": 0, "predicted": 0, "spurious": 0})
        bucket["gold"] += len(gold_ids)
        bucket["found"] += len(found)
        bucket["predicted"] += len(pred)
        bucket["spurious"] += len(extra)

        case_results[case_id] = {
            "found": sorted(found),
            "omitted": sorted(omitted),
            "spurious": sorted(extra),
            "obligation_recall": len(found) / len(gold_ids) if gold_ids else 1.0,
        }

    by_domain_result = {}
    for domain, b in sorted(by_domain.items()):
        by_domain_result[domain] = {
            "obligation_recall": b["found"] / b["gold"] if b["gold"] else 1.0,
            "unsafe_omission_rate": (b["gold"] - b["found"]) / b["gold"] if b["gold"] else 0.0,
            "spurious_obligation_rate": b["spurious"] / b["predicted"] if b["predicted"] else 0.0,
        }

    return {
        "benchmark_version": version,
        "cases": len(gold_rows),
        "gold_obligations": total_gold,
        "predicted_obligations": total_pred,
        "obligation_recall": found_gold / total_gold if total_gold else 1.0,
        "unsafe_omission_rate": (total_gold - found_gold) / total_gold if total_gold else 0.0,
        "spurious_obligation_rate": spurious / total_pred if total_pred else 0.0,
        "high_impact_recall": high_found / high_total if high_total else 1.0,
        "by_domain": by_domain_result,
        "cases_detail": case_results,
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
