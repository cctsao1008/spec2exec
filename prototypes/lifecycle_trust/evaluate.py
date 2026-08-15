#!/usr/bin/env python3
"""Bounded RFC 0012 lifecycle-trust evaluator for payment-retry issue #62.

RFC 0011 authority results and RFC 0006 evidence records are inputs. This
prototype does not create authority, rank evidence classes, or infer arbitrary
repository dependencies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

INPUT_SCHEMA = "spec2exec.lifecycle-trust-input/v0.1"
RESULT_SCHEMA = "spec2exec.lifecycle-trust-result/v0.1"

EVIDENCE_STATUSES = {
    "PROVEN", "CHECKED", "TESTED", "TESTED_EXHAUSTIVE", "MEASURED",
    "ESTIMATED", "HUMAN-DECLARED", "HUMAN-ACCEPTED", "TRUSTED",
    "ASSUMED", "ADVISORY", "UNRESOLVED",
}
GRANT_KINDS = {"VALUE", "VALUE_SET", "CONSTRAINT", "PROCEDURE", "SOURCE", "DISCRETION"}
SELF_SUPPORT_KINDS = {"EVIDENCE_DEPENDS_ON", "VALIDATED_AGAINST"}
RESTRICTIVE_IMPACTS = {
    "ImpactDisposition.REVALIDATION_REQUIRED",
    "ImpactDisposition.INVALIDATED",
    "ImpactDisposition.UNKNOWN_IMPACT",
}


class LifecycleError(Exception):
    pass


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise LifecycleError(f"{path}: root must be an object")
    return value


def canonical_digest(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def policy_ref(policy: dict[str, Any]) -> str:
    return f"{policy['projection_policy_id']}@{policy['revision']}"


def req_str(obj: dict[str, Any], key: str, where: str) -> str:
    value = obj.get(key)
    if not isinstance(value, str) or not value:
        raise LifecycleError(f"{where}.{key} must be a non-empty string")
    return value


def req_list(obj: dict[str, Any], key: str, where: str) -> list[Any]:
    value = obj.get(key)
    if not isinstance(value, list):
        raise LifecycleError(f"{where}.{key} must be an array")
    return value


def index(records: Iterable[dict[str, Any]], key: str, where: str) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            raise LifecycleError(f"{where} entries must be objects")
        ident = req_str(record, key, where)
        if ident in out:
            raise LifecycleError(f"{where}: duplicate {key}={ident}")
        out[ident] = record
    return out


def evidence_key(evidence: dict[str, Any]) -> tuple[str, str]:
    status, method = evidence.get("status"), evidence.get("method")
    if status not in EVIDENCE_STATUSES:
        raise LifecycleError(f"unsupported RFC 0006 evidence status: {status!r}")
    if not isinstance(method, str) or not method:
        raise LifecycleError("evidence.method must be a non-empty string")
    return status, method


def profile_allowed(policy: dict[str, Any], conclusion: str, evidence: dict[str, Any]) -> bool:
    actual = evidence_key(evidence)
    profiles = policy.get("reuse_evidence_profiles", {}).get(conclusion, [])
    if not isinstance(profiles, list):
        raise LifecycleError(f"policy reuse profile {conclusion} must be an array")
    return any(
        isinstance(p, dict) and (p.get("status"), p.get("method")) == actual
        for p in profiles
    )


def completeness_profile_allowed(policy: dict[str, Any], evidence: dict[str, Any]) -> bool:
    actual = evidence_key(evidence)
    profiles = policy.get("completeness_evidence_profiles", [])
    if not isinstance(profiles, list):
        raise LifecycleError("completeness_evidence_profiles must be an array")
    return any(
        isinstance(p, dict) and (p.get("status"), p.get("method")) == actual
        for p in profiles
    )


def context_matches(spec: dict[str, Any], context: dict[str, Any]) -> bool:
    for key, expected in spec.items():
        actual = context.get(key)
        if isinstance(expected, list):
            if actual not in expected:
                return False
        elif actual != expected:
            return False
    return True


def authority_check(
    records: dict[str, dict[str, Any]], ref: Any, required_scopes: str | Iterable[str]
) -> tuple[bool, str]:
    if not isinstance(ref, str) or not ref:
        return False, "authority reference is missing"
    record = records.get(ref)
    if record is None:
        return False, f"authority record {ref!r} does not exist"
    if record.get("authority_validity") != "AUTHORIZED":
        return False, f"authority record {ref!r} is not AUTHORIZED"
    if record.get("grant_kind") not in GRANT_KINDS:
        return False, f"authority record {ref!r} does not use an RFC 0011 grant kind"
    for field in ("anchor_id", "authority_policy_id", "authority_policy_revision"):
        if not isinstance(record.get(field), str) or not record[field]:
            return False, f"authority record {ref!r} lacks {field}"
    scopes = record.get("scope")
    if not isinstance(scopes, list):
        return False, f"authority record {ref!r}.scope must be an array"
    required = [required_scopes] if isinstance(required_scopes, str) else list(required_scopes)
    missing = [x for x in required if x not in scopes]
    return (
        (False, f"authority record {ref!r} does not cover required scopes {missing}")
        if missing else
        (True, "authorized by imported RFC 0011 result")
    )


def policy_applies(policy: dict[str, Any], doc: dict[str, Any]) -> bool:
    return (
        policy.get("gated_action") == doc["gated_action"]
        and policy.get("property") == doc["property"]
        and context_matches(policy.get("applicability", {}), doc["evaluation_context"])
    )


def select_policy(doc: dict[str, Any], blockers: list[dict[str, str]]) -> dict[str, Any] | None:
    applicable = [p for p in doc["projection_policies"] if policy_applies(p, doc)]
    if not applicable:
        blockers.append({"code": "E_POLICY_MISSING", "message": "no ProjectionPolicy applies"})
        return None
    if len(applicable) == 1:
        return applicable[0]
    values = [p.get("precedence") for p in applicable]
    if not all(isinstance(x, int) and not isinstance(x, bool) for x in values):
        blockers.append({
            "code": "E_POLICY_AMBIGUOUS",
            "message": "multiple ProjectionPolicies apply without deterministic precedence",
        })
        return None
    top = max(values)
    winners = [p for p in applicable if p.get("precedence") == top]
    if len(winners) != 1:
        blockers.append({
            "code": "E_POLICY_AMBIGUOUS",
            "message": "multiple ProjectionPolicies share highest precedence",
        })
        return None
    return winners[0]


def applicability_broadened(old: dict[str, Any], new: dict[str, Any]) -> bool:
    old_app, new_app = old.get("applicability", {}), new.get("applicability", {})
    for key, old_value in old_app.items():
        if key not in new_app:
            return True
        new_value = new_app[key]
        if isinstance(old_value, list) and isinstance(new_value, list):
            if set(new_value) > set(old_value):
                return True
        elif old_value != new_value:
            return True
    return False


def removed(old: dict[str, Any], new: dict[str, Any], field: str) -> bool:
    return not set(old.get(field, [])).issubset(set(new.get(field, [])))


def profiles_added(old: dict[str, Any], new: dict[str, Any]) -> bool:
    before, after = old.get("reuse_evidence_profiles", {}), new.get("reuse_evidence_profiles", {})
    for conclusion, entries in after.items():
        old_keys = {
            (x.get("status"), x.get("method"))
            for x in before.get(conclusion, []) if isinstance(x, dict)
        }
        new_keys = {
            (x.get("status"), x.get("method"))
            for x in entries if isinstance(x, dict)
        }
        if not new_keys.issubset(old_keys):
            return True
    return False


def permissive_changes(old: dict[str, Any], new: dict[str, Any]) -> list[str]:
    out = []
    if applicability_broadened(old, new):
        out.append("applicability")
    for field in ("required_dependency_kinds", "required_source_classes", "non_waivable_defeater_kinds"):
        if removed(old, new, field):
            out.append(field)
    if old.get("allow_dependency_completeness_residual") is False and new.get(
        "allow_dependency_completeness_residual"
    ) is True:
        out.append("dependency_completeness_residual")
    if isinstance(old.get("precedence"), int) and isinstance(new.get("precedence"), int):
        if new["precedence"] > old["precedence"]:
            out.append("precedence")
    if profiles_added(old, new):
        out.append("reuse_evidence_profiles")
    return sorted(set(out))


def find_cycle(edges: list[dict[str, Any]]) -> list[str] | None:
    graph: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("kind") in SELF_SUPPORT_KINDS:
            graph.setdefault(edge["source_ref"], []).append(edge["target_ref"])
    state: dict[str, int] = {}
    stack: list[str] = []

    def dfs(node: str) -> list[str] | None:
        state[node] = 1
        stack.append(node)
        for nxt in graph.get(node, []):
            if state.get(nxt, 0) == 0:
                found = dfs(nxt)
                if found:
                    return found
            elif state.get(nxt) == 1:
                i = stack.index(nxt)
                return stack[i:] + [nxt]
        stack.pop()
        state[node] = 2
        return None

    for node in sorted(graph):
        if state.get(node, 0) == 0:
            found = dfs(node)
            if found:
                return found
    return None


def matching_revalidation(
    claims: list[dict[str, Any]],
    target_ref: str,
    context: dict[str, Any],
    event_ref: str | None,
    policy: dict[str, Any],
) -> dict[str, Any] | None:
    for claim in claims:
        if claim.get("target_ref") != target_ref:
            continue
        binding = claim.get("context_binding")
        if not isinstance(binding, dict) or not context_matches(binding, context):
            continue
        if event_ref is not None and event_ref not in claim.get("event_refs", []):
            continue
        evidence = claim.get("evidence")
        if not isinstance(evidence, dict) or claim.get("method") != evidence.get("method"):
            continue
        if profile_allowed(policy, "AssumptionLifecycle.BASIS_CURRENT", evidence):
            return claim
    return None


def validate_document(doc: dict[str, Any]) -> None:
    if doc.get("schema") != INPUT_SCHEMA:
        raise LifecycleError("unsupported lifecycle-trust input schema")
    for field in ("scenario_id", "subject", "gated_action", "property"):
        req_str(doc, field, "input")
    artifact, context, claim = doc.get("artifact"), doc.get("evaluation_context"), doc.get("trust_claim")
    if not isinstance(artifact, dict) or not isinstance(context, dict) or not isinstance(claim, dict):
        raise LifecycleError("artifact, evaluation_context, and trust_claim must be objects")
    for field in ("artifact_id", "revision", "sha256"):
        req_str(artifact, field, "artifact")
    if len(artifact["sha256"]) != 64:
        raise LifecycleError("artifact.sha256 must be a 64-character SHA-256")
    for field in ("context_id", "revision", "api_contract_revision", "endpoint", "operation", "idempotency_key_scope"):
        req_str(context, field, "evaluation_context")
    req_str(claim, "claim_id", "trust_claim")
    if claim.get("property") != doc["property"]:
        raise LifecycleError("trust_claim.property must match input.property")

    arrays = (
        "authority_records", "projection_policies", "assumptions", "evidence_records",
        "dependencies", "established_material_relations", "defeaters",
        "invalidation_events", "impact_assertions", "revalidations", "record_supersessions",
    )
    for name in arrays:
        req_list(doc, name, "input")
    if doc.get("dependency_completeness") is not None and not isinstance(
        doc["dependency_completeness"], dict
    ):
        raise LifecycleError("dependency_completeness must be object or null")
    if doc.get("presented_projection") is not None and not isinstance(
        doc["presented_projection"], dict
    ):
        raise LifecycleError("presented_projection must be object or null")

    for evidence in doc["evidence_records"]:
        req_str(evidence, "evidence_id", "evidence_records")
        evidence_key({"status": evidence.get("status"), "method": evidence.get("method")})
        req_list(evidence, "dependency_refs", "evidence_records")
    for policy in doc["projection_policies"]:
        for field in ("projection_policy_id", "revision", "gated_action", "property"):
            req_str(policy, field, "projection_policies")
        for field in (
            "required_dependency_kinds", "required_source_classes",
            "completeness_evidence_profiles", "allowed_residual_defeater_kinds",
            "non_waivable_defeater_kinds",
        ):
            req_list(policy, field, "projection_policies")
        if not isinstance(policy.get("reuse_evidence_profiles"), dict):
            raise LifecycleError("reuse_evidence_profiles must be an object")


def dedupe(blockers: list[dict[str, str]]) -> list[dict[str, str]]:
    seen, out = set(), []
    for item in blockers:
        key = (item["code"], item["message"])
        if key not in seen:
            seen.add(key)
            out.append(item)
    return sorted(out, key=lambda x: (x["code"], x["message"]))


def evaluate(doc: dict[str, Any]) -> dict[str, Any]:
    validate_document(doc)
    blockers: list[dict[str, str]] = []
    context, claim = doc["evaluation_context"], doc["trust_claim"]
    context_hash, claim_id = canonical_digest(context), claim["claim_id"]
    authorities = index(doc["authority_records"], "authority_record_id", "authority_records")
    assumptions = index(doc["assumptions"], "assumption_id", "assumptions")
    evidence_records = index(doc["evidence_records"], "evidence_id", "evidence_records")
    edges = index(doc["dependencies"], "edge_id", "dependencies")
    edge_values = list(edges.values())
    policies = {policy_ref(p): p for p in doc["projection_policies"]}
    if len(policies) != len(doc["projection_policies"]):
        raise LifecycleError("ProjectionPolicy id/revision pairs must be unique")

    selected = select_policy(doc, blockers)
    selected_ref = policy_ref(selected) if selected else None

    if selected:
        siblings = [
            p for p in doc["projection_policies"]
            if p["projection_policy_id"] == selected["projection_policy_id"]
            and p["revision"] != selected["revision"]
        ]
        selected_is_ancestor = any(p.get("supersedes_ref") == selected_ref for p in siblings)
        if siblings and not selected_is_ancestor and not isinstance(selected.get("supersedes_ref"), str):
            blockers.append({
                "code": "E_POLICY_LINEAGE",
                "message": "selected newer ProjectionPolicy revision has no explicit supersedes_ref",
            })

        ok, reason = authority_check(
            authorities,
            selected.get("adoption_authority_ref"),
            [
                "projection-policy-adoption",
                f"policy:{selected['projection_policy_id']}",
                f"property:{doc['property']}",
            ],
        )
        if not ok:
            blockers.append({"code": "E_POLICY_AUTHORITY", "message": reason})

        prior_ref = selected.get("supersedes_ref")
        if prior_ref is not None:
            prior = policies.get(prior_ref)
            if prior is None:
                blockers.append({
                    "code": "E_POLICY_SUPERSEDES_UNKNOWN",
                    "message": f"selected policy supersedes unknown policy {prior_ref!r}",
                })
            else:
                changes = permissive_changes(prior, selected)
                if changes:
                    ok, reason = authority_check(
                        authorities,
                        selected.get("permissive_change_authority_ref"),
                        [
                            "projection-policy-permissive-change",
                            f"policy:{selected['projection_policy_id']}",
                            f"property:{doc['property']}",
                        ],
                    )
                    rationale = selected.get("permissive_change_rationale")
                    if not ok or not isinstance(rationale, str) or not rationale:
                        blockers.append({
                            "code": "E_POLICY_PERMISSIVE_CHANGE_AUTHORITY",
                            "message": f"permissive changes {changes} lack RFC 0011 authority/rationale: {reason}",
                        })

        gated = [r for r in doc["established_material_relations"] if r.get("gates_property") is True]
        req_kinds, req_classes = set(selected["required_dependency_kinds"]), set(selected["required_source_classes"])
        missing_kinds = sorted({r["kind"] for r in gated if r.get("kind") not in req_kinds})
        missing_classes = sorted({r["source_class"] for r in gated if r.get("source_class") not in req_classes})
        if missing_kinds or missing_classes:
            narrowing, authorized = selected.get("permissive_narrowing"), False
            if isinstance(narrowing, dict):
                ok, _ = authority_check(
                    authorities,
                    narrowing.get("authority_ref"),
                    [
                        "projection-policy-permissive-change",
                        f"policy:{selected['projection_policy_id']}",
                        f"property:{doc['property']}",
                    ],
                )
                authorized = (
                    set(missing_kinds).issubset(set(narrowing.get("omitted_material_dependency_kinds", [])))
                    and set(missing_classes).issubset(set(narrowing.get("omitted_material_source_classes", [])))
                    and isinstance(narrowing.get("rationale"), str)
                    and bool(narrowing["rationale"])
                    and ok
                )
            if not authorized:
                blockers.append({
                    "code": "E_POLICY_MATERIAL_OMISSION",
                    "message": f"policy omits established material coverage kinds={missing_kinds} source_classes={missing_classes}",
                })

    for rel in doc["established_material_relations"]:
        for field in ("source_ref", "target_ref", "kind", "source_class"):
            req_str(rel, field, "established_material_relations")
        represented = any(
            e.get("source_ref") == rel["source_ref"]
            and e.get("target_ref") == rel["target_ref"]
            and e.get("kind") == rel["kind"]
            for e in edge_values
        )
        if not represented:
            blockers.append({
                "code": "E_DEPENDENCY_EDGE_MISSING",
                "message": f"material relation {rel['source_ref']} -[{rel['kind']}]-> {rel['target_ref']} is absent",
            })

    completeness_out = {
        "status": "MISSING", "record_id": None, "covered_dependency_kinds": [],
        "covered_source_classes": [], "evidence": None,
    }
    completeness = doc.get("dependency_completeness")
    if selected:
        if completeness is None:
            blockers.append({
                "code": "E_COMPLETENESS_MISSING",
                "message": "DependencyCompletenessClaim is required",
            })
        else:
            cid = req_str(completeness, "completeness_claim_id", "dependency_completeness")
            covered_kinds = set(req_list(completeness, "covered_dependency_kinds", "dependency_completeness"))
            covered_classes = set(req_list(completeness, "covered_source_classes", "dependency_completeness"))
            evidence = completeness.get("evidence")
            adequate = True
            if not isinstance(evidence, dict) or not completeness_profile_allowed(selected, evidence):
                adequate = False
                blockers.append({
                    "code": "E_COMPLETENESS_EVIDENCE",
                    "message": "completeness evidence does not satisfy ProjectionPolicy",
                })
            if not set(selected["required_dependency_kinds"]).issubset(covered_kinds) or not set(
                selected["required_source_classes"]
            ).issubset(covered_classes):
                adequate = False
                blockers.append({
                    "code": "E_COMPLETENESS_COVERAGE",
                    "message": "completeness coverage is below ProjectionPolicy requirements",
                })
            unresolved = completeness.get("unresolved_areas", [])
            exclusions = completeness.get("known_exclusions", [])
            if not isinstance(unresolved, list) or not isinstance(exclusions, list):
                raise LifecycleError("completeness unresolved/exclusion fields must be arrays")
            if unresolved or exclusions:
                if not selected.get("allow_dependency_completeness_residual", False):
                    adequate = False
                    blockers.append({
                        "code": "E_COMPLETENESS_RESIDUAL",
                        "message": "dependency completeness uncertainty is non-waivable",
                    })
                else:
                    ok, reason = authority_check(
                        authorities,
                        completeness.get("residual_authority_ref"),
                        ["dependency-completeness-residual", f"property:{doc['property']}"],
                    )
                    trigger = completeness.get("mandatory_review_trigger")
                    if not ok or not isinstance(trigger, str) or not trigger:
                        adequate = False
                        blockers.append({
                            "code": "E_COMPLETENESS_RESIDUAL_AUTHORITY",
                            "message": f"completeness residual lacks specific authority/review trigger: {reason}",
                        })
            completeness_out = {
                "status": "ADEQUATE" if adequate else "INADEQUATE",
                "record_id": cid,
                "covered_dependency_kinds": sorted(covered_kinds),
                "covered_source_classes": sorted(covered_classes),
                "evidence": evidence,
            }

    active_defeaters = []
    if selected:
        for d in doc["defeaters"]:
            did, kind, disposition = (
                req_str(d, "defeater_id", "defeaters"),
                req_str(d, "kind", "defeaters"),
                req_str(d, "disposition", "defeaters"),
            )
            bad = False
            if disposition == "OPEN":
                bad = True
                blockers.append({"code": "E_DEFEATER_OPEN", "message": f"{did} ({kind}) is OPEN"})
            elif disposition == "RESOLVED":
                ev = d.get("evidence")
                if not isinstance(ev, dict) or not profile_allowed(selected, "DefeaterDisposition.RESOLVED", ev):
                    bad = True
                    blockers.append({
                        "code": "E_DEFEATER_RESOLUTION_BASIS",
                        "message": f"{did} lacks policy-accepted resolution evidence",
                    })
            elif disposition == "ACCEPTED_RESIDUAL":
                allowed = kind in set(selected.get("allowed_residual_defeater_kinds", []))
                ok, reason = authority_check(
                    authorities, d.get("authority_ref"),
                    ["residual-disposition", f"property:{doc['property']}"],
                )
                if kind == "DEPENDENCY_COMPLETENESS":
                    allowed = bool(selected.get("allow_dependency_completeness_residual"))
                    ok2, reason2 = authority_check(
                        authorities, d.get("authority_ref"),
                        ["dependency-completeness-residual", f"property:{doc['property']}"],
                    )
                    ok = ok and ok2
                    if not ok2:
                        reason = reason2
                if not allowed or not ok or not isinstance(d.get("review_trigger"), str):
                    bad = True
                    blockers.append({
                        "code": "E_RESIDUAL_AUTHORITY",
                        "message": f"{did} residual is not validly authorized/policy-permitted: {reason}",
                    })
            else:
                raise LifecycleError(f"unsupported DefeaterDisposition: {disposition}")
            if bad:
                active_defeaters.append(did)

    revalidations = doc["revalidations"]
    assumption_states, stale_assumptions = [], set()
    if selected:
        for assumption in assumptions.values():
            aid = assumption["assumption_id"]
            basis = assumption.get("basis_context")
            evidence = assumption.get("evidence")
            if not isinstance(basis, dict) or not isinstance(evidence, dict):
                raise LifecycleError("assumption basis_context/evidence must be objects")
            violated = any(
                isinstance(x, dict) and context_matches(x, context)
                for x in assumption.get("violated_contexts", [])
            )
            if violated:
                lifecycle, basis_ref = "AssumptionLifecycle.VIOLATED", None
                stale_assumptions.add(aid)
                blockers.append({"code": "E_ASSUMPTION_VIOLATED", "message": f"{aid} is violated"})
            elif context_matches(basis, context):
                lifecycle, basis_ref = "AssumptionLifecycle.BASIS_CURRENT", aid
                if not profile_allowed(selected, lifecycle, evidence):
                    blockers.append({"code": "E_ASSUMPTION_BASIS", "message": f"{aid} basis is not policy-accepted"})
            else:
                rv = matching_revalidation(revalidations, aid, context, None, selected)
                if rv:
                    lifecycle, basis_ref = "AssumptionLifecycle.BASIS_CURRENT", rv["revalidation_id"]
                else:
                    lifecycle, basis_ref = "AssumptionLifecycle.BASIS_STALE", None
                    stale_assumptions.add(aid)
                    blockers.append({"code": "E_ASSUMPTION_STALE", "message": f"{aid} basis is stale"})
            assumption_states.append({
                "assumption_id": aid, "lifecycle": lifecycle, "basis_ref": basis_ref, "evidence": evidence,
            })

    cycle = find_cycle(edge_values)
    if cycle:
        blockers.append({
            "code": "E_EVIDENTIARY_SELF_SUPPORT",
            "message": "evidentiary self-support cycle: " + " -> ".join(cycle),
        })

    event_map = index(doc["invalidation_events"], "event_id", "invalidation_events")
    roots: list[tuple[str, str, str]] = []
    event_out = []
    for event in event_map.values():
        eid = event["event_id"]
        subject = req_str(event, "subject_ref", "invalidation_events")
        impact = event.get("default_impact", "ImpactDisposition.UNKNOWN_IMPACT")
        if impact not in RESTRICTIVE_IMPACTS:
            raise LifecycleError(f"unsupported event default impact: {impact}")
        resolved = bool(
            selected
            and subject in assumptions
            and matching_revalidation(revalidations, subject, context, eid, selected)
        )
        event_out.append({
            "event_id": eid, "kind": req_str(event, "kind", "invalidation_events"),
            "subject_ref": subject, "prior_revision": event.get("prior_revision"),
            "new_revision": event.get("new_revision"), "resolved_by_revalidation": resolved,
        })
        if not resolved:
            roots.append((eid, subject, impact))

    for aid in sorted(stale_assumptions):
        if not any(root[1] == aid for root in roots):
            eid = f"DERIVED-ASSUMPTION-STALE:{aid}"
            roots.append((eid, aid, "ImpactDisposition.REVALIDATION_REQUIRED"))
            event_out.append({
                "event_id": eid, "kind": "CONTEXT_CHANGE", "subject_ref": aid,
                "prior_revision": None, "new_revision": context["api_contract_revision"],
                "resolved_by_revalidation": False,
            })

    supersessions = index(doc["record_supersessions"], "supersession_id", "record_supersessions")
    superseded = set()
    for record in supersessions.values():
        prior = req_str(record, "prior_record_ref", "record_supersessions")
        superseded.add(prior)
        eid = f"RECORD_CORRECTION:{record['supersession_id']}"
        roots.append((eid, prior, "ImpactDisposition.REVALIDATION_REQUIRED"))
        event_out.append({
            "event_id": eid, "kind": "RECORD_CORRECTION", "subject_ref": prior,
            "prior_revision": record.get("prior_revision"),
            "new_revision": record.get("replacement_record_ref"),
            "resolved_by_revalidation": False,
        })

    presented = doc.get("presented_projection")
    if presented is not None:
        if selected_ref and presented.get("projection_policy_ref") != selected_ref:
            blockers.append({
                "code": "E_STALE_PROJECTION_POLICY",
                "message": "presented projection uses a non-governing ProjectionPolicy revision",
            })
        if presented.get("evaluation_context_digest") != context_hash:
            blockers.append({"code": "E_CONTEXT_MISMATCH", "message": "presented projection context is stale/different"})
        if presented.get("artifact_sha256") != doc["artifact"]["sha256"]:
            blockers.append({"code": "E_ARTIFACT_MISMATCH", "message": "presented projection artifact differs"})
        basis_refs = req_list(presented, "basis_record_refs", "presented_projection")
        stale_basis = sorted(set(basis_refs) & superseded)
        if stale_basis:
            blockers.append({
                "code": "E_SUPERSEDED_BASIS",
                "message": "presented projection uses superseded records: " + ", ".join(stale_basis),
            })

    assertions = {}
    for item in doc["impact_assertions"]:
        key = (req_str(item, "event_ref", "impact_assertions"), req_str(item, "edge_ref", "impact_assertions"))
        if key in assertions:
            raise LifecycleError(f"duplicate impact assertion {key}")
        assertions[key] = item

    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edge_values:
        for field in ("source_ref", "target_ref", "kind"):
            req_str(edge, field, "dependencies")
        adjacency.setdefault(edge["source_ref"], []).append(edge)

    impacts, affected = [], set()
    for eid, source, default_impact in roots:
        queue, visited = [(source, default_impact)], set()
        while queue:
            node, impact = queue.pop(0)
            if (eid, node) in visited:
                continue
            visited.add((eid, node))
            affected.add(node)
            for edge in sorted(adjacency.get(node, []), key=lambda x: x["edge_id"]):
                disposition, basis = impact, None
                assertion = assertions.get((eid, edge["edge_id"]))
                if assertion:
                    asserted = assertion.get("disposition")
                    if asserted == "ImpactDisposition.NO_MATERIAL_EFFECT":
                        ev = assertion.get("evidence")
                        if selected and isinstance(ev, dict) and profile_allowed(
                            selected, "ImpactDisposition.NO_MATERIAL_EFFECT", ev
                        ):
                            disposition, basis = asserted, ev
                        else:
                            disposition = "ImpactDisposition.UNKNOWN_IMPACT"
                            blockers.append({
                                "code": "E_IMPACT_BASIS",
                                "message": f"NO_MATERIAL_EFFECT for {eid}/{edge['edge_id']} lacks policy basis",
                            })
                    elif asserted in RESTRICTIVE_IMPACTS:
                        disposition = asserted
                    else:
                        raise LifecycleError(f"unsupported impact assertion: {asserted}")
                impacts.append({
                    "event_ref": eid, "edge_ref": edge["edge_id"],
                    "source_ref": edge["source_ref"], "target_ref": edge["target_ref"],
                    "property": doc["property"], "evaluation_context_digest": context_hash,
                    "disposition": disposition, "basis": basis,
                })
                if disposition == "ImpactDisposition.NO_MATERIAL_EFFECT":
                    continue
                queue.append((edge["target_ref"], disposition))
                if edge["target_ref"] == claim_id:
                    blockers.append({
                        "code": "E_ACTIVE_INVALIDATION",
                        "message": f"{eid} reaches {claim_id} as {disposition}",
                    })
    if any(source == claim_id for _, source, _ in roots):
        blockers.append({"code": "E_ACTIVE_INVALIDATION", "message": f"{claim_id} is an invalidation root"})

    historical = sorted(evidence_records)
    reusable = []
    for evidence in evidence_records.values():
        eid, deps = evidence["evidence_id"], evidence["dependency_refs"]
        if eid in superseded or eid in affected:
            continue
        if any(ref in affected or ref in superseded for ref in deps):
            continue
        reusable.append(eid)

    blockers = dedupe(blockers)
    return {
        "schema": RESULT_SCHEMA,
        "scenario_id": doc["scenario_id"],
        "subject": doc["subject"],
        "gated_action": doc["gated_action"],
        "property": doc["property"],
        "artifact": doc["artifact"],
        "evaluation_context": {
            "context_id": context["context_id"], "revision": context["revision"],
            "digest_sha256": context_hash,
            "api_contract_revision": context["api_contract_revision"],
        },
        "projection_policy": None if not selected else {
            "projection_policy_id": selected["projection_policy_id"],
            "revision": selected["revision"], "ref": selected_ref,
            "adoption_authority_ref": selected.get("adoption_authority_ref"),
        },
        "trust_claim": {"claim_id": claim_id, "property": claim["property"]},
        "dependency_completeness": completeness_out,
        "assumptions": sorted(assumption_states, key=lambda x: x["assumption_id"]),
        "active_defeaters": sorted(active_defeaters),
        "invalidation_events": sorted(event_out, key=lambda x: x["event_id"]),
        "impact_evaluations": sorted(impacts, key=lambda x: (x["event_ref"], x["edge_ref"])),
        "revalidation_refs": sorted(
            x["revalidation_id"] for x in revalidations if isinstance(x.get("revalidation_id"), str)
        ),
        "historical_evidence_ids": historical,
        "reusable_evidence_ids": sorted(reusable),
        "decision": "CURRENT" if not blockers else "BLOCKED",
        "blockers": blockers,
        "limitations": [
            "RFC 0011 authority records are imported already-evaluated inputs; this prototype does not create semantic authority.",
            "RFC 0006 evidence statuses remain typed labels; no scalar strength ordering is introduced.",
            "Dependency completeness is bounded to the payment-retry experiment, not universal real-world completeness.",
            "CURRENT is one property/context projection, not an artifact-wide trust label.",
        ],
    }


def render_markdown(result: dict[str, Any]) -> str:
    policy = result.get("projection_policy")
    lines = [
        "# Spec2Exec Lifecycle Trust Projection", "",
        f"**Scenario:** `{result['scenario_id']}`  ",
        f"**Property:** `{result['property']}`  ",
        f"**ProjectionPolicy:** `{'none' if policy is None else policy['ref']}`  ",
        f"**CURRENT TRUST:** **{result['decision']}**", "",
        "## Dependency completeness", "",
        f"- Status: `{result['dependency_completeness']['status']}`",
        f"- Claim: `{result['dependency_completeness']['record_id']}`", "",
        "## Assumptions", "",
    ]
    lines += [
        f"- `{x['assumption_id']}` — `{x['lifecycle']}`"
        for x in result.get("assumptions", [])
    ]
    lines += ["", "## Blockers", ""]
    lines += (
        [f"- `{x['code']}` — {x['message']}" for x in result["blockers"]]
        if result["blockers"] else ["- none"]
    )
    lines += [
        "", "## Evidence reuse", "",
        "- Historical evidence retained: " + ", ".join(f"`{x}`" for x in result["historical_evidence_ids"]),
        "- Selectively reusable evidence: " + ", ".join(f"`{x}`" for x in result["reusable_evidence_ids"]),
        "",
        "> Historical evidence retention does not imply that the current property projection is CURRENT.",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--markdown-output", type=Path)
    ap.add_argument("--expect", choices=["CURRENT", "BLOCKED"])
    args = ap.parse_args()
    try:
        result = evaluate(load_json(args.input))
    except (OSError, json.JSONDecodeError, LifecycleError) as exc:
        print(f"lifecycle_trust: ERROR: {exc}")
        return 3
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    if args.expect and result["decision"] != args.expect:
        return 4
    return 0 if result["decision"] == "CURRENT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
