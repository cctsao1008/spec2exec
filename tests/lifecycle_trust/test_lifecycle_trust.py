from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "prototypes/lifecycle_trust/evaluate.py"
    spec = importlib.util.spec_from_file_location("lifecycle_trust", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_fixture(name: str) -> dict:
    path = ROOT / "examples/payment-retry/lifecycle" / name
    return json.loads(path.read_text(encoding="utf-8"))


class LifecycleTrustTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()
        cls.baseline = load_fixture("baseline-v7.json")
        cls.stale = load_fixture("contract-v8-stale.json")
        cls.revalidated = load_fixture("contract-v8-revalidated.json")

    def blocker_codes(self, document: dict) -> set[str]:
        return {x["code"] for x in self.mod.evaluate(document)["blockers"]}

    def fresh_policy_v2(self, document: dict, *, permissive_authority: bool = True) -> dict:
        policy = copy.deepcopy(document["projection_policies"][0])
        policy["revision"] = "2"
        policy["precedence"] = 200
        policy["supersedes_ref"] = "PP-PAY-RETRY@1"
        if permissive_authority:
            policy["permissive_change_authority_ref"] = "AUTH-PP-PERMISSIVE-1"
            policy["permissive_change_rationale"] = "Bounded POC policy revision approved for the gated experiment."
        return policy

    def test_p1_v7_baseline_is_current(self):
        result = self.mod.evaluate(copy.deepcopy(self.baseline))
        self.assertEqual(result["decision"], "CURRENT")
        self.assertEqual(result["dependency_completeness"]["status"], "ADEQUATE")
        self.assertEqual(result["projection_policy"]["ref"], "PP-PAY-RETRY@1")

    def test_p2_v7_to_v8_blocks_with_byte_identical_artifact(self):
        v7 = self.mod.evaluate(copy.deepcopy(self.baseline))
        v8 = self.mod.evaluate(copy.deepcopy(self.stale))
        self.assertEqual(v7["artifact"]["sha256"], v8["artifact"]["sha256"])
        self.assertEqual(v8["decision"], "BLOCKED")
        self.assertIn("E_ASSUMPTION_STALE", {x["code"] for x in v8["blockers"]})
        self.assertTrue(
            any(
                x["disposition"] == "ImpactDisposition.REVALIDATION_REQUIRED"
                for x in v8["impact_evaluations"]
            )
        )

    def test_p3_valid_revalidation_restores_only_current_relationship(self):
        result = self.mod.evaluate(copy.deepcopy(self.revalidated))
        self.assertEqual(result["decision"], "CURRENT")
        state = result["assumptions"][0]
        self.assertEqual(state["lifecycle"], "AssumptionLifecycle.BASIS_CURRENT")
        self.assertEqual(state["basis_ref"], "RV-API-IDEMPOTENCY-V8")
        self.assertIn("RV-API-IDEMPOTENCY-V8", result["revalidation_refs"])

    def test_p4_unrelated_historical_evidence_is_selectively_reusable(self):
        result = self.mod.evaluate(copy.deepcopy(self.stale))
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertIn("EV-CLIENT-ARTIFACT-001", result["historical_evidence_ids"])
        self.assertIn("EV-CLIENT-ARTIFACT-001", result["reusable_evidence_ids"])
        self.assertIn("EV-SEMANTIC-REVIEW-001", result["reusable_evidence_ids"])

    def test_p5_authorized_policy_revision_requires_fresh_projection(self):
        document = copy.deepcopy(self.baseline)
        policy_v2 = self.fresh_policy_v2(document)
        document["projection_policies"].append(policy_v2)
        fresh = self.mod.evaluate(copy.deepcopy(document))
        self.assertEqual(fresh["decision"], "CURRENT")
        self.assertEqual(fresh["projection_policy"]["ref"], "PP-PAY-RETRY@2")
        document["presented_projection"] = {
            "projection_policy_ref": "PP-PAY-RETRY@1",
            "evaluation_context_digest": self.mod.canonical_digest(document["evaluation_context"]),
            "artifact_sha256": document["artifact"]["sha256"],
            "basis_record_refs": [],
        }
        stale = self.mod.evaluate(document)
        self.assertEqual(stale["decision"], "BLOCKED")
        self.assertIn("E_STALE_PROJECTION_POLICY", {x["code"] for x in stale["blockers"]})

    def test_valid_no_material_effect_can_stop_one_event_edge(self):
        document = copy.deepcopy(self.baseline)
        document["invalidation_events"] = [
            {
                "event_id": "IE-TOOL-KNOWLEDGE",
                "kind": "KNOWLEDGE_CHANGE",
                "subject_ref": "TOOL-SEMANTIC-REVIEW-001",
                "prior_revision": "tool-v1",
                "new_revision": "tool-v1",
                "default_impact": "ImpactDisposition.UNKNOWN_IMPACT",
            }
        ]
        document["impact_assertions"] = [
            {
                "event_ref": "IE-TOOL-KNOWLEDGE",
                "edge_ref": "EDGE-TCB",
                "disposition": "ImpactDisposition.NO_MATERIAL_EFFECT",
                "evidence": {"status": "CHECKED", "method": "dependency-impact-check"},
            }
        ]
        result = self.mod.evaluate(document)
        self.assertEqual(result["decision"], "CURRENT")
        self.assertTrue(
            any(
                x["disposition"] == "ImpactDisposition.NO_MATERIAL_EFFECT"
                for x in result["impact_evaluations"]
            )
        )

    def test_n1_missing_projection_policy_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"] = []
        self.assertIn("E_POLICY_MISSING", self.blocker_codes(document))

    def test_n2_multiple_applicable_policies_without_precedence_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"][0].pop("precedence", None)
        policy2 = copy.deepcopy(document["projection_policies"][0])
        policy2["revision"] = "2"
        document["projection_policies"].append(policy2)
        self.assertIn("E_POLICY_AMBIGUOUS", self.blocker_codes(document))

    def test_n3_missing_policy_adoption_authority_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"][0]["adoption_authority_ref"] = "AUTH-NOT-THERE"
        self.assertIn("E_POLICY_AUTHORITY", self.blocker_codes(document))

    def test_n4_policy_cannot_silently_omit_established_assumes_dependency(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"][0]["required_dependency_kinds"].remove("ASSUMES")
        self.assertIn("E_POLICY_MATERIAL_OMISSION", self.blocker_codes(document))

    def test_n4b_policy_cannot_silently_omit_established_source_class(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"][0]["required_source_classes"].remove("AssumptionRecord")
        self.assertIn("E_POLICY_MATERIAL_OMISSION", self.blocker_codes(document))

    def test_n5_applicability_broadening_requires_permissive_change_authority(self):
        document = copy.deepcopy(self.revalidated)
        old = document["projection_policies"][0]
        old["applicability"] = {"api_contract_revision": ["v7"]}
        policy_v2 = copy.deepcopy(old)
        policy_v2["revision"] = "2"
        policy_v2["applicability"] = {"api_contract_revision": ["v7", "v8"]}
        policy_v2["precedence"] = 200
        policy_v2["supersedes_ref"] = "PP-PAY-RETRY@1"
        policy_v2.pop("permissive_change_authority_ref", None)
        policy_v2.pop("permissive_change_rationale", None)
        document["projection_policies"].append(policy_v2)
        self.assertIn("E_POLICY_PERMISSIVE_CHANGE_AUTHORITY", self.blocker_codes(document))

    def test_n6_cached_projection_bound_to_old_policy_is_rejected(self):
        document = copy.deepcopy(self.baseline)
        document["projection_policies"].append(self.fresh_policy_v2(document))
        document["presented_projection"] = {
            "projection_policy_ref": "PP-PAY-RETRY@1",
            "evaluation_context_digest": self.mod.canonical_digest(document["evaluation_context"]),
            "artifact_sha256": document["artifact"]["sha256"],
            "basis_record_refs": [],
        }
        self.assertIn("E_STALE_PROJECTION_POLICY", self.blocker_codes(document))

    def test_n7_missing_dependency_completeness_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["dependency_completeness"] = None
        self.assertIn("E_COMPLETENESS_MISSING", self.blocker_codes(document))

    def test_n8_policy_inadequate_completeness_coverage_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["dependency_completeness"]["covered_dependency_kinds"].remove("ASSUMES")
        self.assertIn("E_COMPLETENESS_COVERAGE", self.blocker_codes(document))

    def test_n9_missing_established_assumes_edge_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["dependencies"] = [
            x for x in document["dependencies"] if x["edge_id"] != "EDGE-ASSUMES-IDEMPOTENCY"
        ]
        self.assertIn("E_DEPENDENCY_EDGE_MISSING", self.blocker_codes(document))

    def test_n10_no_material_effect_without_required_basis_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["invalidation_events"] = [
            {
                "event_id": "IE-TOOL-KNOWLEDGE",
                "kind": "KNOWLEDGE_CHANGE",
                "subject_ref": "TOOL-SEMANTIC-REVIEW-001",
                "prior_revision": "tool-v1",
                "new_revision": "tool-v1",
                "default_impact": "ImpactDisposition.UNKNOWN_IMPACT",
            }
        ]
        document["impact_assertions"] = [
            {
                "event_ref": "IE-TOOL-KNOWLEDGE",
                "edge_ref": "EDGE-TCB",
                "disposition": "ImpactDisposition.NO_MATERIAL_EFFECT",
                "evidence": {"status": "HUMAN-DECLARED", "method": "dependency-impact-check"},
            }
        ]
        self.assertIn("E_IMPACT_BASIS", self.blocker_codes(document))

    def test_n11_accepted_residual_without_authority_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["defeaters"] = [
            {
                "defeater_id": "D-ENV",
                "kind": "ENVIRONMENT_LIMITATION",
                "disposition": "ACCEPTED_RESIDUAL",
                "review_trigger": "review before production deployment",
            }
        ]
        self.assertIn("E_RESIDUAL_AUTHORITY", self.blocker_codes(document))

    def test_n12_dependency_completeness_residual_not_generically_waivable(self):
        document = copy.deepcopy(self.baseline)
        document["dependency_completeness"]["unresolved_areas"] = ["provider-key-lifetime"]
        document["dependency_completeness"]["residual_authority_ref"] = "AUTH-COMP-RESIDUAL-1"
        document["dependency_completeness"]["mandatory_review_trigger"] = "before deployment"
        self.assertIn("E_COMPLETENESS_RESIDUAL", self.blocker_codes(document))

    def test_n13_materially_different_context_rejects_presented_projection(self):
        document = copy.deepcopy(self.baseline)
        document["presented_projection"] = {
            "projection_policy_ref": "PP-PAY-RETRY@1",
            "evaluation_context_digest": "0" * 64,
            "artifact_sha256": document["artifact"]["sha256"],
            "basis_record_refs": [],
        }
        self.assertIn("E_CONTEXT_MISMATCH", self.blocker_codes(document))

    def test_n14_knowledge_only_tcb_defect_invalidates_without_revision_change(self):
        document = copy.deepcopy(self.baseline)
        document["invalidation_events"] = [
            {
                "event_id": "IE-TOOL-DEFECT",
                "kind": "KNOWLEDGE_CHANGE",
                "subject_ref": "TOOL-SEMANTIC-REVIEW-001",
                "prior_revision": "tool-v1",
                "new_revision": "tool-v1",
                "default_impact": "ImpactDisposition.UNKNOWN_IMPACT",
            }
        ]
        result = self.mod.evaluate(document)
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertIn("E_ACTIVE_INVALIDATION", {x["code"] for x in result["blockers"]})

    def test_n15_record_supersession_stales_cached_projection(self):
        document = copy.deepcopy(self.baseline)
        document["record_supersessions"] = [
            {
                "supersession_id": "RS-EV-1",
                "prior_record_ref": "EV-SEMANTIC-REVIEW-001",
                "prior_revision": "1",
                "replacement_record_ref": "EV-SEMANTIC-REVIEW-002",
                "reason": "prior provenance was incomplete",
            }
        ]
        document["presented_projection"] = {
            "projection_policy_ref": "PP-PAY-RETRY@1",
            "evaluation_context_digest": self.mod.canonical_digest(document["evaluation_context"]),
            "artifact_sha256": document["artifact"]["sha256"],
            "basis_record_refs": ["EV-SEMANTIC-REVIEW-001"],
        }
        codes = self.blocker_codes(document)
        self.assertIn("E_SUPERSEDED_BASIS", codes)
        self.assertIn("E_ACTIVE_INVALIDATION", codes)

    def test_n16_evidentiary_self_support_cycle_fails_closed(self):
        document = copy.deepcopy(self.baseline)
        document["dependencies"].extend(
            [
                {
                    "edge_id": "EDGE-CYCLE-A",
                    "source_ref": "EVIDENCE-A",
                    "target_ref": "EVIDENCE-B",
                    "kind": "EVIDENCE_DEPENDS_ON",
                },
                {
                    "edge_id": "EDGE-CYCLE-B",
                    "source_ref": "EVIDENCE-B",
                    "target_ref": "EVIDENCE-A",
                    "kind": "VALIDATED_AGAINST",
                },
            ]
        )
        self.assertIn("E_EVIDENTIARY_SELF_SUPPORT", self.blocker_codes(document))

    def test_rfc0006_statuses_are_not_ranked(self):
        policy = self.baseline["projection_policies"][0]
        accepted = {
            (x["status"], x["method"])
            for x in policy["reuse_evidence_profiles"]["AssumptionLifecycle.BASIS_CURRENT"]
        }
        self.assertIn(("HUMAN-DECLARED", "provider-contract-fixture"), accepted)
        self.assertIn(("CHECKED", "contract-equivalence-check"), accepted)
        self.assertNotEqual("HUMAN-DECLARED", "CHECKED")

    def test_invalid_rfc0011_grant_kind_is_not_treated_as_authority(self):
        document = copy.deepcopy(self.baseline)
        auth = next(
            x for x in document["authority_records"] if x["authority_record_id"] == "AUTH-PP-ADOPT-1"
        )
        auth["grant_kind"] = "PROJECTION_POLICY_MAGIC"
        self.assertIn("E_POLICY_AUTHORITY", self.blocker_codes(document))

    def test_knowledge_defect_makes_affected_evidence_non_reusable(self):
        document = copy.deepcopy(self.baseline)
        document["invalidation_events"] = [
            {
                "event_id": "IE-TOOL-DEFECT-REUSE",
                "kind": "KNOWLEDGE_CHANGE",
                "subject_ref": "TOOL-SEMANTIC-REVIEW-001",
                "prior_revision": "tool-v1",
                "new_revision": "tool-v1",
                "default_impact": "ImpactDisposition.UNKNOWN_IMPACT",
            }
        ]
        result = self.mod.evaluate(document)
        self.assertNotIn("EV-SEMANTIC-REVIEW-001", result["reusable_evidence_ids"])
        self.assertIn("EV-CLIENT-ARTIFACT-001", result["reusable_evidence_ids"])

    def test_policy_adoption_authority_must_be_policy_and_property_scoped(self):
        document = copy.deepcopy(self.baseline)
        auth = next(
            x for x in document["authority_records"] if x["authority_record_id"] == "AUTH-PP-ADOPT-1"
        )
        auth["scope"] = ["projection-policy-adoption"]
        self.assertIn("E_POLICY_AUTHORITY", self.blocker_codes(document))

    def test_policy_revision_lineage_must_be_explicit(self):
        document = copy.deepcopy(self.baseline)
        policy_v2 = self.fresh_policy_v2(document)
        policy_v2.pop("supersedes_ref")
        document["projection_policies"].append(policy_v2)
        self.assertIn("E_POLICY_LINEAGE", self.blocker_codes(document))

    def test_result_is_property_scoped_not_artifact_wide_trust_label(self):
        result = self.mod.evaluate(copy.deepcopy(self.baseline))
        self.assertEqual(result["property"], "PAYMENT-RETRY-SAFETY")
        self.assertEqual(result["trust_claim"]["claim_id"], "CLAIM-PAYMENT-RETRY-SAFETY")
        self.assertNotIn("trust_score", result)
        self.assertNotIn("evidence_strength", result)


if __name__ == "__main__":
    unittest.main()
