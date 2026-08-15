import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "prototypes/poc1c/authority.py"
spec = importlib.util.spec_from_file_location("poc1c_authority", MODULE)
authority = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(authority)

SPEC = ROOT / "examples/optimization-preservation/specification.json"
MANIFEST = ROOT / "examples/optimization-preservation/authority/manifest.json"
AUTHORITY_DIR = MANIFEST.parent
TARGET = "rv32i-baremetal"


def load_records():
    spec_doc = json.loads(SPEC.read_text(encoding="utf-8"))
    bundle = authority.load_authority_bundle(MANIFEST)
    return spec_doc, copy.deepcopy(bundle)


def evaluate_records(spec_doc, bundle):
    return authority.evaluate_authority_records(
        spec_doc,
        bundle,
        TARGET,
        manifest_sha256="TEST-MANIFEST",
        specification_sha256="TEST-SPEC",
    )


def find_policy(bundle, policy_id):
    return next(item for item in bundle["policies"]["policies"] if item["policy_id"] == policy_id)


def find_obligation(bundle, obligation_id):
    return next(item for item in bundle["obligations"]["obligations"] if item["obligation_id"] == obligation_id)


class SemanticAuthorityTests(unittest.TestCase):
    def test_bound_authority_record_set_is_accepted(self):
        result = authority.evaluate_authority(SPEC, MANIFEST, TARGET)
        self.assertEqual("ACCEPTED", result["outcome"])
        self.assertEqual("AUTHORIZED", result["authority_validity"])
        self.assertEqual("CHECKED", result["evidence_claim"]["status"])
        self.assertEqual(3, len(result["closure"]["included_obligations"]))
        self.assertEqual([], result["closure"]["excluded_subjects"])

    def test_direct_value_and_delegated_value_set_are_both_exercised(self):
        spec_doc, bundle = load_records()
        result = evaluate_records(spec_doc, bundle)
        by_id = {item["obligation_id"]: item for item in result["obligation_evaluations"]}
        self.assertIn("POL-POC1C-OVERFLOW", by_id["AUTH-OVF-001"]["allowing_grants"])
        self.assertIn("POL-POC1C-INPUT-DOMAIN", by_id["AUTH-DOMAIN-A"]["allowing_grants"])
        self.assertIn("POL-POC1C-INPUT-DOMAIN", by_id["AUTH-DOMAIN-B"]["allowing_grants"])

    def test_closure_constraint_is_checked(self):
        spec_doc, bundle = load_records()
        result = evaluate_records(spec_doc, bundle)
        self.assertEqual(1, len(result["constraint_evaluations"]))
        self.assertEqual("CHECKED", result["constraint_evaluations"][0]["status"])
        self.assertEqual("deterministic-range-check", result["constraint_evaluations"][0]["method_class"])

    def test_manifest_hash_tamper_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "authority"
            shutil.copytree(AUTHORITY_DIR, dst)
            anchor = dst / "anchor.json"
            anchor.write_text(anchor.read_text(encoding="utf-8").replace("project-owner", "tampered-owner", 1),
                              encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_PROVENANCE"):
                authority.load_authority_bundle(dst / "manifest.json")

    def test_missing_anchor_is_rejected(self):
        spec_doc, bundle = load_records()
        bundle["manifest"]["anchor_set"] = []
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_NO_ANCHOR"):
            evaluate_records(spec_doc, bundle)

    def test_authority_cycle_is_rejected(self):
        spec_doc, bundle = load_records()
        policy = find_policy(bundle, "POL-POC1C-BUILD")
        policy["source_policy_id"] = policy["policy_id"]
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_CYCLE"):
            evaluate_records(spec_doc, bundle)

    def test_missing_bound_policy_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001")["authority_policy_id"] = "POL-MISSING"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_NO_POLICY"):
            evaluate_records(spec_doc, bundle)

    def test_value_outside_delegated_value_set_is_rejected(self):
        spec_doc, bundle = load_records()
        value = {"min": -75, "max": 75}
        spec_doc["function"]["inputs"][0]["range"] = copy.deepcopy(value)
        find_obligation(bundle, "AUTH-DOMAIN-A")["value"] = copy.deepcopy(value)
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_VALUE_OUT_OF_SET"):
            evaluate_records(spec_doc, bundle)

    def test_stale_policy_revision_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001")["policy_revision"] = "0"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_POTENTIALLY_STALE"):
            evaluate_records(spec_doc, bundle)

    def test_stale_anchor_revision_is_rejected(self):
        spec_doc, bundle = load_records()
        bundle["anchor"]["revision"] = "2"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_POTENTIALLY_STALE"):
            evaluate_records(spec_doc, bundle)

    def test_unresolved_obligation_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001")["resolution_state"] = "UNRESOLVED"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_UNRESOLVED"):
            evaluate_records(spec_doc, bundle)

    def test_semantic_conflict_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001")["resolution_state"] = "CONFLICT"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_CONFLICT"):
            evaluate_records(spec_doc, bundle)

    def test_scope_mismatch_is_rejected(self):
        spec_doc, bundle = load_records()
        find_policy(bundle, "POL-POC1C-OVERFLOW")["scope"]["build_ids"] = ["other-build"]
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_SCOPE"):
            evaluate_records(spec_doc, bundle)

    def test_missing_provenance_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001").pop("provenance")
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_PROVENANCE"):
            evaluate_records(spec_doc, bundle)

    def test_self_authorization_policy_violation_is_rejected(self):
        spec_doc, bundle = load_records()
        find_policy(bundle, "POL-POC1C-OVERFLOW")["self_authorization_allowed"] = False
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_SELF_AUTHORIZATION"):
            evaluate_records(spec_doc, bundle)

    def test_redelegation_is_rejected_in_mvi(self):
        spec_doc, bundle = load_records()
        policy = find_policy(bundle, "POL-POC1C-OVERFLOW")
        policy.pop("source_anchor_id")
        policy["source_policy_id"] = "POL-POC1C-BUILD"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_REDELEGATION"):
            evaluate_records(spec_doc, bundle)

    def test_missing_classification_basis_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-DOMAIN-A").pop("classification_basis")
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_CLASSIFICATION"):
            evaluate_records(spec_doc, bundle)

    def test_unbased_closure_exclusion_is_rejected(self):
        spec_doc, bundle = load_records()
        closure = bundle["closure"]
        closure["included_obligations"].remove("AUTH-DOMAIN-A")
        closure["excluded_subjects"] = ["AUTH-DOMAIN-A"]
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_CLOSURE"):
            evaluate_records(spec_doc, bundle)

    def test_selected_configuration_without_policy_is_rejected(self):
        spec_doc, bundle = load_records()
        bundle["closure"]["selected_build"]["authority_policy_id"] = "POL-MISSING"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_NO_POLICY"):
            evaluate_records(spec_doc, bundle)

    def test_conflicting_applicable_authority_grant_is_rejected(self):
        spec_doc, bundle = load_records()
        conflicting = copy.deepcopy(find_policy(bundle, "POL-POC1C-OVERFLOW"))
        conflicting["policy_id"] = "POL-POC1C-OVERFLOW-CONFLICT"
        conflicting["grant"]["value"] = "allowed"
        bundle["policies"]["policies"].append(conflicting)
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_AUTHORITY_CONFLICT"):
            evaluate_records(spec_doc, bundle)

    def test_potentially_stale_obligation_is_rejected(self):
        spec_doc, bundle = load_records()
        find_obligation(bundle, "AUTH-OVF-001")["authority_state"] = "POTENTIALLY_STALE"
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_POTENTIALLY_STALE"):
            evaluate_records(spec_doc, bundle)

    def test_closure_constraint_violation_is_rejected(self):
        spec_doc, bundle = load_records()
        value = {"min": -120, "max": 120}
        spec_doc["function"]["inputs"][0]["range"] = copy.deepcopy(value)
        find_obligation(bundle, "AUTH-DOMAIN-A")["value"] = copy.deepcopy(value)
        policy = find_policy(bundle, "POL-POC1C-INPUT-DOMAIN")
        policy["grant"]["allowed_values"].append(copy.deepcopy(value))
        with self.assertRaisesRegex(authority.AuthorityError, "E_AUTH_CONSTRAINT"):
            evaluate_records(spec_doc, bundle)


if __name__ == "__main__":
    unittest.main()
