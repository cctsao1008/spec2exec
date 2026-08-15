"""Deterministic semantic-authority evaluation for the POC-1C MVI.

The evaluator consumes recorded AuthorityAnchors, policies, obligations, and an
explicit executable semantic closure. It computes authority validity and emits
an immutable acceptance record. It does not create semantic authority.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

MANIFEST_SCHEMA = "spec2exec.authority-manifest/v0.1"
ANCHOR_SCHEMA = "spec2exec.authority-anchor/v0.1"
POLICIES_SCHEMA = "spec2exec.authority-policies/v0.1"
OBLIGATIONS_SCHEMA = "spec2exec.semantic-obligations/v0.1"
CLOSURE_SCHEMA = "spec2exec.authority-closure/v0.1"
ACCEPTANCE_SCHEMA = "spec2exec.authority-acceptance/v0.1"

STALE_STATES = {"POTENTIALLY_STALE", "INVALIDATED", "REVOKED", "EXPIRED"}
SUPPORTED_GRANTS = {"VALUE", "VALUE_SET", "CONSTRAINT"}


class AuthorityError(Exception):
    pass


def expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(f"{code}: {message}")


def nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_pointer(document: Any, pointer: str) -> Any:
    expect(isinstance(pointer, str) and pointer.startswith("/"), "E_AUTH_PROVENANCE",
           f"invalid JSON pointer {pointer!r}")
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            expect(token.isdigit(), "E_AUTH_PROVENANCE", f"list pointer token must be an index: {token!r}")
            index = int(token)
            expect(0 <= index < len(current), "E_AUTH_PROVENANCE", f"list pointer index out of range: {index}")
            current = current[index]
        else:
            expect(isinstance(current, dict) and token in current, "E_AUTH_PROVENANCE",
                   f"JSON pointer token not found: {token!r}")
            current = current[token]
    return current


def _safe_component_path(base: Path, relative: str) -> Path:
    expect(nonempty_string(relative), "E_AUTH_PROVENANCE", "authority component path must be non-empty")
    candidate = (base / relative).resolve()
    expect(candidate == base.resolve() or base.resolve() in candidate.parents,
           "E_AUTH_PROVENANCE", f"authority component escapes manifest directory: {relative!r}")
    return candidate


def load_authority_bundle(manifest_path: Path) -> dict[str, Any]:
    manifest_path = manifest_path.resolve()
    manifest = load_json(manifest_path)
    expect(isinstance(manifest, dict) and manifest.get("schema") == MANIFEST_SCHEMA,
           "E_AUTH_PROVENANCE", f"authority manifest schema must be {MANIFEST_SCHEMA}")
    components = manifest.get("components")
    expect(isinstance(components, dict), "E_AUTH_PROVENANCE", "manifest.components must be an object")
    required = {"anchor", "policies", "obligations", "closure"}
    expect(required <= set(components), "E_AUTH_PROVENANCE",
           f"manifest missing components: {sorted(required - set(components))}")

    bundle: dict[str, Any] = {"manifest": manifest, "component_paths": {}, "component_hashes": {}}
    for name in sorted(required):
        record = components[name]
        expect(isinstance(record, dict), "E_AUTH_PROVENANCE", f"manifest.components.{name} must be object")
        path = _safe_component_path(manifest_path.parent, record.get("path"))
        expect(path.is_file(), "E_AUTH_PROVENANCE", f"authority component not found: {path}")
        actual = file_sha256(path)
        expected = record.get("sha256")
        expect(nonempty_string(expected) and actual == expected, "E_AUTH_PROVENANCE",
               f"authority component hash mismatch for {name}: expected {expected}, got {actual}")
        bundle[name] = load_json(path)
        bundle["component_paths"][name] = path
        bundle["component_hashes"][name] = actual

    expect(bundle["anchor"].get("schema") == ANCHOR_SCHEMA, "E_AUTH_PROVENANCE", "invalid anchor schema")
    expect(bundle["policies"].get("schema") == POLICIES_SCHEMA, "E_AUTH_PROVENANCE", "invalid policies schema")
    expect(bundle["obligations"].get("schema") == OBLIGATIONS_SCHEMA,
           "E_AUTH_PROVENANCE", "invalid obligations schema")
    expect(bundle["closure"].get("schema") == CLOSURE_SCHEMA, "E_AUTH_PROVENANCE", "invalid closure schema")
    bundle["manifest_path"] = manifest_path
    bundle["manifest_sha256"] = file_sha256(manifest_path)
    return bundle


def _index(records: list[Any], key: str, code: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        expect(isinstance(record, dict), code, f"record in {key} collection must be object")
        identity = record.get(key)
        expect(nonempty_string(identity), code, f"{key} must be non-empty")
        expect(identity not in result, code, f"duplicate {key}: {identity}")
        result[identity] = record
    return result


def _validate_policy_graph(policies: dict[str, dict[str, Any]]) -> None:
    graph: dict[str, str] = {}
    for policy_id, policy in policies.items():
        parent = policy.get("source_policy_id")
        if parent is not None:
            expect(nonempty_string(parent) and parent in policies, "E_AUTH_NO_POLICY",
                   f"policy {policy_id} references unknown source policy {parent!r}")
            graph[policy_id] = parent

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        expect(node not in visiting, "E_AUTH_CYCLE", f"authority policy cycle includes {node}")
        visiting.add(node)
        parent = graph.get(node)
        if parent is not None:
            visit(parent)
        visiting.remove(node)
        visited.add(node)

    for policy_id in policies:
        visit(policy_id)


def _validate_anchor(manifest: dict[str, Any], anchor: dict[str, Any]) -> dict[str, Any]:
    anchor_id = anchor.get("anchor_id")
    revision = anchor.get("revision")
    expect(nonempty_string(anchor_id) and nonempty_string(revision), "E_AUTH_NO_ANCHOR",
           "anchor id and revision are required")
    anchor_set = manifest.get("anchor_set")
    expect(isinstance(anchor_set, list) and anchor_set, "E_AUTH_NO_ANCHOR", "manifest anchor_set must be non-empty")
    entries = [entry for entry in anchor_set if isinstance(entry, dict) and entry.get("anchor_id") == anchor_id]
    expect(len(entries) == 1, "E_AUTH_NO_ANCHOR", f"anchor {anchor_id} must occur exactly once in manifest")
    expect(entries[0].get("revision") == revision, "E_AUTH_POTENTIALLY_STALE",
           f"manifest anchor revision {entries[0].get('revision')!r} != anchor revision {revision!r}")
    protection = anchor.get("protection")
    expect(isinstance(protection, dict) and nonempty_string(protection.get("mechanism")),
           "E_AUTH_NO_ANCHOR", "anchor protection/declaration mechanism must be explicit")
    expect(nonempty_string(protection.get("evidence_status")), "E_AUTH_NO_ANCHOR",
           "anchor protection evidence status must be explicit")
    scope = anchor.get("scope")
    expect(isinstance(scope, dict) and isinstance(scope.get("subjects"), list),
           "E_AUTH_SCOPE", "anchor scope.subjects must be a list")
    return entries[0]


def _policy_build_matches(policy: dict[str, Any], build_id: str) -> bool:
    scope = policy.get("scope")
    return isinstance(scope, dict) and build_id in scope.get("build_ids", [])


def _policy_subject_matches(policy: dict[str, Any], subject: str) -> bool:
    return subject in policy.get("subjects", [])


def _validate_policy_source(policy: dict[str, Any], anchor: dict[str, Any],
                            policies: dict[str, dict[str, Any]]) -> None:
    policy_id = policy.get("policy_id", "<unknown>")
    if policy.get("source_policy_id") is not None:
        parent_id = policy["source_policy_id"]
        parent = policies.get(parent_id)
        expect(parent is not None, "E_AUTH_NO_POLICY", f"unknown source policy {parent_id!r}")
        expect(parent.get("redelegation_allowed") is True, "E_AUTH_REDELEGATION",
               f"policy {parent_id} does not permit redelegation to {policy_id}")
        raise AuthorityError(f"E_AUTH_REDELEGATION: POC-1C MVI does not support delegated policy depth > 1 ({policy_id})")

    expect(policy.get("source_anchor_id") == anchor.get("anchor_id"), "E_AUTH_NO_ANCHOR",
           f"policy {policy_id} is not rooted at the declared POC anchor")
    expect(policy.get("source_revision") == anchor.get("revision"), "E_AUTH_POTENTIALLY_STALE",
           f"policy {policy_id} source anchor revision is stale")
    anchor_subjects = set(anchor.get("scope", {}).get("subjects", []))
    policy_subjects = set(policy.get("subjects", []))
    expect(bool(policy_subjects) and policy_subjects <= anchor_subjects, "E_AUTH_SCOPE",
           f"policy {policy_id} exceeds anchor subject scope")


def _attribution_ok(record: dict[str, Any], policy: dict[str, Any]) -> bool:
    requirement = policy.get("attribution_requirement", {})
    allowed = requirement.get("allowed_mechanisms", []) if isinstance(requirement, dict) else []
    attribution = record.get("attribution")
    mechanism = attribution.get("mechanism") if isinstance(attribution, dict) else None
    return nonempty_string(mechanism) and mechanism in allowed


def _validate_exercise(record: dict[str, Any], policy: dict[str, Any]) -> None:
    policy_id = policy["policy_id"]
    agent = record.get("authority_agent")
    expect(agent in policy.get("allowed_authority_agents", []), "E_AUTH_SCOPE",
           f"authority agent {agent!r} is not permitted by {policy_id}")
    expect(_attribution_ok(record, policy), "E_AUTH_ATTRIBUTION",
           f"attribution mechanism does not satisfy {policy_id}")
    proposer = record.get("proposer")
    if proposer is not None and proposer == agent:
        expect(policy.get("self_authorization_allowed") is True, "E_AUTH_SELF_AUTHORIZATION",
               f"policy {policy_id} does not permit proposer == authority_agent")


def _grant_allows(policy: dict[str, Any], value: Any) -> bool:
    kind = policy.get("grant_kind")
    expect(kind in SUPPORTED_GRANTS, "E_AUTH_GRANT_KIND", f"unsupported POC authority grant kind: {kind!r}")
    grant = policy.get("grant")
    expect(isinstance(grant, dict), "E_AUTH_GRANT_KIND", f"policy {policy.get('policy_id')} grant must be object")
    if kind == "VALUE":
        return value == grant.get("value")
    if kind == "VALUE_SET":
        values = grant.get("allowed_values")
        expect(isinstance(values, list) and values, "E_AUTH_GRANT_KIND", "VALUE_SET must contain allowed_values")
        return value in values
    return True


def _excluded_ids(closure: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
    result: list[str] = []
    normalized: list[dict[str, Any]] = []
    for item in closure.get("excluded_subjects", []):
        if isinstance(item, str):
            raise AuthorityError(f"E_AUTH_CLOSURE: excluded subject {item!r} lacks an authorized/deterministic basis")
        expect(isinstance(item, dict) and nonempty_string(item.get("obligation_id")),
               "E_AUTH_CLOSURE", "excluded subject must identify obligation_id")
        basis = item.get("basis")
        expect(isinstance(basis, dict) and basis.get("kind") in {"authorized", "deterministic"},
               "E_AUTH_CLOSURE", f"excluded subject {item['obligation_id']} lacks valid exclusion basis")
        expect(nonempty_string(basis.get("method") or basis.get("policy_id")), "E_AUTH_CLOSURE",
               f"excluded subject {item['obligation_id']} exclusion basis must identify method/policy")
        result.append(item["obligation_id"])
        normalized.append(item)
    return result, normalized


def _validate_closure(closure: dict[str, Any], obligations: dict[str, dict[str, Any]]) -> dict[str, Any]:
    candidates = closure.get("candidate_subjects")
    included = closure.get("included_obligations")
    expect(isinstance(candidates, list) and all(nonempty_string(x) for x in candidates),
           "E_AUTH_CLOSURE", "candidate_subjects must be a string list")
    expect(isinstance(included, list) and all(nonempty_string(x) for x in included),
           "E_AUTH_CLOSURE", "included_obligations must be a string list")
    excluded_ids, excluded_records = _excluded_ids(closure)
    expect(len(candidates) == len(set(candidates)), "E_AUTH_CLOSURE", "duplicate candidate subject")
    expect(len(included) == len(set(included)), "E_AUTH_CLOSURE", "duplicate included obligation")
    expect(len(excluded_ids) == len(set(excluded_ids)), "E_AUTH_CLOSURE", "duplicate excluded obligation")
    expect(set(candidates) == set(obligations), "E_AUTH_CLOSURE",
           "candidate_subjects must enumerate every semantic-obligation record")
    expect(set(included).isdisjoint(excluded_ids), "E_AUTH_CLOSURE", "included and excluded sets overlap")
    expect(set(candidates) == set(included) | set(excluded_ids), "E_AUTH_CLOSURE",
           "closure inclusion/exclusion must cover every candidate subject")
    for obligation_id in included:
        expect(obligation_id in obligations, "E_AUTH_CLOSURE", f"unknown included obligation {obligation_id}")
    return {"included": list(included), "excluded": excluded_records, "candidates": list(candidates)}


def _validate_selected_build(closure: dict[str, Any], policies: dict[str, dict[str, Any]],
                             anchor: dict[str, Any], target_profile: str) -> dict[str, Any]:
    selected = closure.get("selected_build")
    expect(isinstance(selected, dict), "E_AUTH_SCOPE", "closure.selected_build must be object")
    expect(selected.get("target_profile") == target_profile, "E_AUTH_SCOPE",
           f"selected target {selected.get('target_profile')!r} != requested {target_profile!r}")
    build_id = selected.get("build_id")
    configuration = selected.get("configuration")
    expect(nonempty_string(build_id) and nonempty_string(configuration), "E_AUTH_SCOPE",
           "selected build id/configuration are required")
    policy_id = selected.get("authority_policy_id")
    policy = policies.get(policy_id)
    expect(policy is not None, "E_AUTH_NO_POLICY", f"selected build policy not found: {policy_id!r}")
    _validate_policy_source(policy, anchor, policies)
    expect(policy.get("revision") == selected.get("policy_revision"), "E_AUTH_POTENTIALLY_STALE",
           "selected-build policy revision is stale")
    expect(_policy_subject_matches(policy, "selected-build") and _policy_build_matches(policy, build_id),
           "E_AUTH_SCOPE", "selected-build policy scope does not cover this build")
    expected_value = f"{build_id}|{target_profile}|{configuration}"
    expect(_grant_allows(policy, expected_value), "E_AUTH_SCOPE", "selected build/configuration is not authorized")
    _validate_exercise(selected, policy)
    return dict(selected)


def _obligation_precheck(obligation: dict[str, Any], spec_doc: dict[str, Any],
                         expected_source_artifact: str | None) -> None:
    obligation_id = obligation.get("obligation_id", "<unknown>")
    state = obligation.get("resolution_state")
    if state == "UNRESOLVED":
        raise AuthorityError(f"E_AUTH_UNRESOLVED: {obligation_id} is unresolved")
    if state == "CONFLICT":
        raise AuthorityError(f"E_AUTH_CONFLICT: {obligation_id} has unresolved candidate conflict")
    expect(state == "RESOLVED", "E_AUTH_UNRESOLVED", f"{obligation_id} has invalid resolution state {state!r}")
    expect(obligation.get("applicability") == "APPLICABLE", "E_AUTH_SCOPE",
           f"in-closure obligation {obligation_id} must be APPLICABLE")
    authority_state = obligation.get("authority_state", "CURRENT")
    if authority_state in STALE_STATES:
        raise AuthorityError(f"E_AUTH_POTENTIALLY_STALE: {obligation_id} authority dependency is {authority_state}")
    expect(authority_state == "CURRENT", "E_AUTH_POTENTIALLY_STALE",
           f"{obligation_id} authority dependency state must be CURRENT")
    basis = obligation.get("classification_basis")
    expect(isinstance(basis, dict) and basis.get("kind") in {"authorized", "deterministic"},
           "E_AUTH_CLASSIFICATION", f"{obligation_id} lacks authority-relevant classification basis")
    expect(nonempty_string(basis.get("method") or basis.get("policy_id")), "E_AUTH_CLASSIFICATION",
           f"{obligation_id} classification basis must identify method/policy")
    provenance = obligation.get("provenance")
    expect(isinstance(provenance, dict) and nonempty_string(provenance.get("source_artifact")) and
           nonempty_string(provenance.get("source_locator")),
           "E_AUTH_PROVENANCE", f"{obligation_id} provenance is incomplete")
    if expected_source_artifact is not None:
        expect(provenance.get("source_artifact") == expected_source_artifact, "E_AUTH_PROVENANCE",
               f"{obligation_id} provenance points at unexpected source artifact")
    locator = obligation.get("spec_locator")
    expect(nonempty_string(locator) and locator == provenance.get("source_locator"), "E_AUTH_PROVENANCE",
           f"{obligation_id} spec locator/provenance locator mismatch")
    expect(json_pointer(spec_doc, locator) == obligation.get("value"), "E_AUTH_PROVENANCE",
           f"{obligation_id} value does not match exact specification locator")


def _evaluate_obligation(obligation: dict[str, Any], policies: dict[str, dict[str, Any]],
                         anchor: dict[str, Any], build_id: str) -> dict[str, Any]:
    subject = obligation.get("subject")
    expect(nonempty_string(subject), "E_AUTH_SCOPE", "semantic obligation subject is required")
    provided_id = obligation.get("authority_policy_id")
    provided = policies.get(provided_id)
    expect(provided is not None, "E_AUTH_NO_POLICY", f"bound policy not found for {subject}: {provided_id!r}")
    expect(provided.get("revision") == obligation.get("policy_revision"), "E_AUTH_POTENTIALLY_STALE",
           f"bound policy revision is stale for {subject}")
    expect(_policy_subject_matches(provided, subject) and _policy_build_matches(provided, build_id),
           "E_AUTH_SCOPE", f"bound policy {provided_id} does not cover {subject}/{build_id}")
    _validate_policy_source(provided, anchor, policies)
    _validate_exercise(obligation, provided)

    evaluated: list[str] = []
    applicable: list[str] = []
    rejected: list[dict[str, str]] = []
    allowed: list[str] = []
    contradictory: list[str] = []

    for policy_id in sorted(policies):
        policy = policies[policy_id]
        evaluated.append(policy_id)
        if policy.get("grant_kind") == "CONSTRAINT":
            rejected.append({"policy_id": policy_id, "basis": "constraint-evaluated-separately"})
            continue
        if not _policy_subject_matches(policy, subject):
            rejected.append({"policy_id": policy_id, "basis": "subject-not-covered"})
            continue
        if not _policy_build_matches(policy, build_id):
            rejected.append({"policy_id": policy_id, "basis": "build-scope-not-covered"})
            continue
        _validate_policy_source(policy, anchor, policies)
        applicable.append(policy_id)
        if _grant_allows(policy, obligation.get("value")):
            allowed.append(policy_id)
        else:
            contradictory.append(policy_id)

    expect(applicable, "E_AUTH_NO_POLICY", f"no applicable policy discovered for {subject}")
    if allowed and contradictory:
        raise AuthorityError(
            f"E_AUTH_AUTHORITY_CONFLICT: applicable policies disagree for {subject}: "
            f"allow={allowed}, contradict={contradictory}"
        )
    expect(allowed, "E_AUTH_VALUE_OUT_OF_SET", f"no applicable authority grant permits value for {subject}")
    expect(provided_id in allowed, "E_AUTH_NO_POLICY", f"bound policy {provided_id} is not an allowing grant")

    return {
        "obligation_id": obligation["obligation_id"],
        "subject": subject,
        "authority_bindings_used": [provided_id],
        "authority_grants_evaluated": evaluated,
        "authority_grants_applicable": applicable,
        "authority_grants_rejected_as_inapplicable": rejected,
        "allowing_grants": allowed,
        "contradictory_grants": contradictory,
        "authority_validity": "AUTHORIZED",
    }


def _discover_constraints(policies: dict[str, dict[str, Any]], included_subjects: set[str],
                          build_id: str) -> set[str]:
    result: set[str] = set()
    for policy_id, policy in policies.items():
        if policy.get("grant_kind") != "CONSTRAINT" or not _policy_build_matches(policy, build_id):
            continue
        if included_subjects & set(policy.get("subjects", [])):
            result.add(policy_id)
    return result


def _evaluate_constraint(policy: dict[str, Any], obligations: dict[str, dict[str, Any]],
                         included_ids: list[str], anchor: dict[str, Any],
                         policies: dict[str, dict[str, Any]]) -> dict[str, Any]:
    _validate_policy_source(policy, anchor, policies)
    evidence_profile = policy.get("evidence_profile")
    expect(isinstance(evidence_profile, dict), "E_AUTH_CONSTRAINT", "constraint evidence profile is required")
    expect("CHECKED" in evidence_profile.get("allowed_statuses", []), "E_AUTH_CONSTRAINT",
           "POC constraint requires CHECKED to be an allowed evidence status")
    expect(evidence_profile.get("required_method_class") == "deterministic-range-check", "E_AUTH_CONSTRAINT",
           "unsupported constraint evidence method class")
    rule = policy.get("grant", {}).get("rule", {})
    expect(rule.get("kind") == "input_ranges_within", "E_AUTH_CONSTRAINT", "unsupported constraint rule")
    lo, hi = rule.get("min"), rule.get("max")
    expect(isinstance(lo, int) and isinstance(hi, int) and lo <= hi,
           "E_AUTH_CONSTRAINT", "constraint range must be valid integers")
    checked: list[str] = []
    policy_subjects = set(policy.get("subjects", []))
    for obligation_id in included_ids:
        obligation = obligations[obligation_id]
        if obligation.get("subject") not in policy_subjects:
            continue
        value = obligation.get("value")
        expect(isinstance(value, dict) and isinstance(value.get("min"), int) and isinstance(value.get("max"), int),
               "E_AUTH_CONSTRAINT", f"constraint subject {obligation_id} must carry min/max range")
        expect(lo <= value["min"] <= value["max"] <= hi, "E_AUTH_CONSTRAINT",
               f"{obligation_id} range {value} violates [{lo}, {hi}] constraint")
        checked.append(obligation_id)
    expect(checked, "E_AUTH_CONSTRAINT", f"constraint {policy['policy_id']} matched no in-closure obligations")
    return {
        "policy_id": policy["policy_id"],
        "status": "CHECKED",
        "method_class": "deterministic-range-check",
        "subjects_checked": checked,
        "rule": rule,
    }


def evaluate_authority_records(spec_doc: dict[str, Any], bundle: dict[str, Any], target_profile: str,
                               *, manifest_sha256: str = "UNBOUND",
                               specification_sha256: str = "UNBOUND",
                               expected_source_artifact: str | None = None) -> dict[str, Any]:
    manifest = bundle.get("manifest")
    anchor = bundle.get("anchor")
    policies_doc = bundle.get("policies")
    obligations_doc = bundle.get("obligations")
    closure = bundle.get("closure")
    expect(isinstance(manifest, dict) and manifest.get("schema") == MANIFEST_SCHEMA,
           "E_AUTH_PROVENANCE", "invalid authority manifest")
    expect(isinstance(anchor, dict) and anchor.get("schema") == ANCHOR_SCHEMA,
           "E_AUTH_NO_ANCHOR", "invalid AuthorityAnchor record")
    expect(isinstance(policies_doc, dict) and policies_doc.get("schema") == POLICIES_SCHEMA,
           "E_AUTH_NO_POLICY", "invalid authority-policies record")
    expect(isinstance(obligations_doc, dict) and obligations_doc.get("schema") == OBLIGATIONS_SCHEMA,
           "E_AUTH_CLOSURE", "invalid semantic-obligations record")
    expect(isinstance(closure, dict) and closure.get("schema") == CLOSURE_SCHEMA,
           "E_AUTH_CLOSURE", "invalid ClosureRecord")

    _validate_anchor(manifest, anchor)
    policies = _index(policies_doc.get("policies", []), "policy_id", "E_AUTH_NO_POLICY")
    obligations = _index(obligations_doc.get("obligations", []), "obligation_id", "E_AUTH_CLOSURE")
    _validate_policy_graph(policies)

    selected_build = _validate_selected_build(closure, policies, anchor, target_profile)
    build_id = selected_build["build_id"]
    closure_state = _validate_closure(closure, obligations)

    obligation_results: list[dict[str, Any]] = []
    for obligation_id in closure_state["included"]:
        obligation = obligations[obligation_id]
        _obligation_precheck(obligation, spec_doc, expected_source_artifact)
        obligation_results.append(_evaluate_obligation(obligation, policies, anchor, build_id))

    included_subjects = {obligations[item]["subject"] for item in closure_state["included"]}
    discovered_constraints = _discover_constraints(policies, included_subjects, build_id)
    declared_constraints = set(closure.get("constraint_policy_ids", []))
    expect(discovered_constraints == declared_constraints, "E_AUTH_CONSTRAINT",
           f"closure constraint set incomplete/mismatched: discovered={sorted(discovered_constraints)}, "
           f"declared={sorted(declared_constraints)}")
    constraint_results = [
        _evaluate_constraint(policies[policy_id], obligations, closure_state["included"], anchor, policies)
        for policy_id in sorted(discovered_constraints)
    ]

    component_hashes = bundle.get("component_hashes", {})
    anchor_hash = component_hashes.get("anchor", canonical_json_sha256(anchor))
    anchor_entry = {
        "anchor_id": anchor["anchor_id"],
        "revision": anchor["revision"],
        "sha256": anchor_hash,
        "protection": anchor["protection"],
    }
    anchor_set_hash = canonical_json_sha256([anchor_entry])

    return {
        "schema": ACCEPTANCE_SCHEMA,
        "outcome": "ACCEPTED",
        "acceptance_state": "ACCEPTED",
        "authority_validity": "AUTHORIZED",
        "evaluation_method": "deterministic-authority-gate-v0.1",
        "record_set_id": manifest.get("record_set_id"),
        "manifest_sha256": manifest_sha256,
        "specification_sha256": specification_sha256,
        "selected_build": selected_build,
        "authority_tcb": {
            "anchors": [anchor_entry],
            "anchor_set_sha256": anchor_set_hash,
            "protection_authentication": "unauthenticated",
        },
        "closure": {
            "closure_id": closure.get("closure_id"),
            "method": closure.get("method"),
            "method_version": closure.get("method_version"),
            "included_obligations": closure_state["included"],
            "excluded_subjects": closure_state["excluded"],
            "candidate_subjects": closure_state["candidates"],
            "constraint_policy_ids": sorted(discovered_constraints),
        },
        "obligation_evaluations": obligation_results,
        "constraint_evaluations": constraint_results,
        "attribution_limitations": [
            "AuthorityAnchor and repository protection are HUMAN-DECLARED / unauthenticated in this POC",
            "Git authorship or repository write access is not cryptographic identity proof",
        ],
        "evidence_claim": {
            "id": "A1.semantic_authority_gate",
            "status": "CHECKED",
            "method": "deterministic-authority-gate-v0.1",
            "property": "all in-closure semantic obligations and authority constraints satisfy the bound POC authority model",
            "assumptions": [
                "declared AuthorityAnchor and repository protection mechanism are trusted governance inputs",
                "explicit POC closure enumeration contains every authority-relevant candidate subject",
            ],
        },
    }


def evaluate_authority(specification_path: Path, manifest_path: Path, target_profile: str) -> dict[str, Any]:
    specification_path = specification_path.resolve()
    manifest_path = manifest_path.resolve()
    spec_doc = load_json(specification_path)
    acceptance = spec_doc.get("acceptance")
    expect(isinstance(acceptance, dict), "E_AUTH_PROVENANCE", "specification acceptance record is required")
    manifest_ref = acceptance.get("authority_manifest")
    expect(nonempty_string(manifest_ref), "E_AUTH_PROVENANCE", "specification acceptance must bind authority_manifest")
    expected_manifest = (specification_path.parent / manifest_ref).resolve()
    expect(expected_manifest == manifest_path, "E_AUTH_PROVENANCE",
           "authority manifest path does not match specification acceptance binding")

    bundle = load_authority_bundle(manifest_path)
    return evaluate_authority_records(
        spec_doc,
        bundle,
        target_profile,
        manifest_sha256=file_sha256(manifest_path),
        specification_sha256=file_sha256(specification_path),
        expected_source_artifact=rel(specification_path),
    )
