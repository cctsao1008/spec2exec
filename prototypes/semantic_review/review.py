#!/usr/bin/env python3
"""Deterministic semantic-diff review for the GitHub workflow POC.

This module consumes a bounded semantic-review policy plus a candidate.
It does not create semantic authority. CODEOWNERS is treated as a repository
ownership/attribution adapter into the policy, not as the RFC 0011 authority
model itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


class ReviewError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReviewError(f"{path}: root must be an object")
    return value


def parse_codeowners(text: str) -> list[tuple[str, list[str]]]:
    entries: list[tuple[str, list[str]]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            raise ReviewError(f"invalid CODEOWNERS entry: {raw!r}")
        entries.append((parts[0], parts[1:]))
    return entries


def _normalize_repo_path(path: str) -> str:
    return path.lstrip("/")


def _pattern_matches(pattern: str, repo_path: str) -> bool:
    pattern = _normalize_repo_path(pattern)
    repo_path = _normalize_repo_path(repo_path)
    if pattern.endswith("/"):
        return repo_path == pattern[:-1] or repo_path.startswith(pattern)
    if "*" not in pattern and "?" not in pattern and "[" not in pattern:
        return repo_path == pattern
    import fnmatch
    return fnmatch.fnmatchcase(repo_path, pattern)


def owners_for_path(entries: list[tuple[str, list[str]]], repo_path: str) -> list[str]:
    owners: list[str] = []
    for pattern, candidate_owners in entries:
        if _pattern_matches(pattern, repo_path):
            owners = candidate_owners
    return owners


def verify_codeowner(policy: dict[str, Any], codeowners_text: str) -> dict[str, Any]:
    target = policy.get("codeowners_path")
    required_owner = policy.get("required_owner")
    if not isinstance(target, str) or not target:
        raise ReviewError("policy.codeowners_path must be non-empty")
    if not isinstance(required_owner, str) or not required_owner.startswith("@"):
        raise ReviewError("policy.required_owner must be an @owner")
    owners = owners_for_path(parse_codeowners(codeowners_text), target)
    if not owners:
        raise ReviewError(f"E_GH_OWNER_MISSING: no CODEOWNERS mapping for {target}")
    if len(owners) != 1:
        raise ReviewError(
            f"E_GH_OWNER_AMBIGUOUS: POC requires exactly one owner for {target}; owners={owners}"
        )
    if required_owner not in owners:
        raise ReviewError(
            f"E_GH_OWNER_MISMATCH: {required_owner} is not an owner for {target}; owners={owners}"
        )
    assurance = policy.get("attribution_assurance")
    if not isinstance(assurance, dict):
        raise ReviewError("policy.attribution_assurance must be explicit")
    return {
        "path": target,
        "owners": owners,
        "required_owner": required_owner,
        "attribution_assurance": assurance,
    }


def _any_retry_enabled(values: dict[str, Any]) -> bool:
    count = values.get("retry_count")
    return bool(
        (isinstance(count, int) and not isinstance(count, bool) and count > 0)
        or values.get("retry_on_http_500") is True
        or values.get("retry_on_timeout") is True
    )


def review(policy: dict[str, Any], candidate: dict[str, Any], codeowners_text: str) -> dict[str, Any]:
    if policy.get("schema") != "spec2exec.semantic-review-policy/v0.1":
        raise ReviewError("unsupported semantic-review policy schema")
    if candidate.get("schema") != "spec2exec.semantic-candidate/v0.1":
        raise ReviewError("unsupported semantic candidate schema")

    owner_binding = verify_codeowner(policy, codeowners_text)
    declared = policy.get("obligations")
    if not isinstance(declared, dict) or not declared:
        raise ReviewError("policy.obligations must be a non-empty object")
    values = candidate.get("values")
    if not isinstance(values, dict):
        raise ReviewError("candidate.values must be an object")

    rows: list[dict[str, Any]] = []
    blocking = 0

    for obligation_id, rule in declared.items():
        if not isinstance(rule, dict):
            raise ReviewError(f"policy obligation {obligation_id} must be an object")
        allowed = rule.get("allowed_values")
        if not isinstance(allowed, list) or not allowed:
            raise ReviewError(f"policy obligation {obligation_id} must declare allowed_values")

        if obligation_id not in values or values[obligation_id] is None:
            status = "UNRESOLVED"
            value = None
            blocking += 1
        else:
            value = values[obligation_id]
            if value in allowed:
                status = "AUTHORIZED"
            else:
                status = "UNAUTHORIZED"
                blocking += 1

        rows.append(
            {
                "obligation_id": obligation_id,
                "value": value,
                "status": status,
                "impact": rule.get("impact", "UNSPECIFIED"),
                "authority_basis": rule.get("authority_basis"),
                "allowed_values": allowed,
            }
        )

    for obligation_id in sorted(set(values) - set(declared)):
        rows.append(
            {
                "obligation_id": obligation_id,
                "value": values[obligation_id],
                "status": "UNAUTHORIZED",
                "impact": "UNSPECIFIED",
                "authority_basis": None,
                "allowed_values": [],
                "reason": "candidate introduced a semantic obligation with no governing policy",
            }
        )
        blocking += 1

    constraint_results: list[dict[str, Any]] = []
    for constraint in policy.get("constraints", []):
        if not isinstance(constraint, dict):
            raise ReviewError("constraint must be an object")
        constraint_id = constraint.get("constraint_id")
        condition = constraint.get("when", {})
        required = constraint.get("require", {})
        applies = condition.get("any_retry_enabled") is True and _any_retry_enabled(values)
        ok = True
        if applies:
            for key, expected in required.items():
                if values.get(key) != expected:
                    ok = False
                    break
        if applies and not ok:
            blocking += 1
        constraint_results.append(
            {
                "constraint_id": constraint_id,
                "applies": applies,
                "status": "CHECKED" if (not applies or ok) else "FAILED",
                "method": "deterministic-semantic-review",
            }
        )

    outcome = "ACCEPTED" if blocking == 0 else "BLOCKED"
    return {
        "schema": "spec2exec.semantic-review-result/v0.1",
        "subject": policy.get("subject"),
        "candidate_id": candidate.get("candidate_id"),
        "outcome": outcome,
        "blocking_findings": blocking,
        "authority_adapter": owner_binding,
        "obligations": rows,
        "constraints": constraint_results,
        "limitations": [
            "CODEOWNERS is a repository-declared attribution/ownership input, not proof of real-world organizational authority.",
            "This workflow POC does not provide cryptographic identity, quorum approval, or production payment assurance.",
        ],
    }


def display_value(value: Any) -> str:
    if value is None:
        return "?"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Spec2Exec Semantic Review",
        "",
        f"**Subject:** `{result.get('subject')}`  ",
        f"**Candidate:** `{result.get('candidate_id')}`  ",
        f"**MERGE GATE:** **{result.get('outcome')}**",
        "",
        "| Semantic obligation | Candidate value | Status | Impact |",
        "|---|---:|---|---|",
    ]
    for row in result.get("obligations", []):
        lines.append(
            f"| `{row['obligation_id']}` | `{display_value(row.get('value'))}` | "
            f"**{row['status']}** | {row.get('impact', 'UNSPECIFIED')} |"
        )

    lines.extend(["", "## Constraint checks", ""])
    for item in result.get("constraints", []):
        lines.append(
            f"- `{item.get('constraint_id')}` — **{item.get('status')}** "
            f"(applies={str(bool(item.get('applies'))).lower()})"
        )

    adapter = result.get("authority_adapter", {})
    assurance = adapter.get("attribution_assurance", {})
    lines.extend(
        [
            "",
            "## Authority adapter",
            "",
            f"- CODEOWNERS path: `{adapter.get('path')}`",
            f"- Required owner: `{adapter.get('required_owner')}`",
            f"- Repository owners: `{', '.join(adapter.get('owners', []))}`",
            f"- Attribution: `{assurance.get('status')}` / `{assurance.get('authentication')}`",
            "",
            "> CODEOWNERS is an adapter into the RFC 0011 authority model, not semantic authority by itself.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--candidate", type=Path, required=True)
    ap.add_argument("--codeowners", type=Path, required=True)
    ap.add_argument("--json-output", type=Path)
    ap.add_argument("--markdown-output", type=Path)
    ap.add_argument("--expect", choices=["ACCEPTED", "BLOCKED"])
    args = ap.parse_args()

    try:
        result = review(
            load_json(args.policy),
            load_json(args.candidate),
            args.codeowners.read_text(encoding="utf-8"),
        )
    except (OSError, json.JSONDecodeError, ReviewError) as exc:
        print(f"semantic_review: ERROR: {exc}")
        return 3

    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)

    if args.expect and result["outcome"] != args.expect:
        print(f"semantic_review: expected {args.expect}, got {result['outcome']}")
        return 4
    return 0 if result["outcome"] == "ACCEPTED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
