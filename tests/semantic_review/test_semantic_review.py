from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_review_module():
    path = ROOT / "prototypes/semantic_review/review.py"
    spec = importlib.util.spec_from_file_location("semantic_review", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SemanticReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_review_module()
        base = ROOT / "examples/payment-retry"
        cls.policy = json.loads((base / "authority-policy.json").read_text(encoding="utf-8"))
        cls.unsafe = json.loads((base / "unsafe-candidate.json").read_text(encoding="utf-8"))
        cls.accepted = json.loads((base / "accepted-candidate.json").read_text(encoding="utf-8"))
        cls.codeowners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8")

    def test_unsafe_candidate_blocks_with_unauthorized_and_unresolved(self):
        result = self.mod.review(self.policy, self.unsafe, self.codeowners)
        self.assertEqual(result["outcome"], "BLOCKED")
        by_id = {x["obligation_id"]: x for x in result["obligations"]}
        self.assertEqual(by_id["retry_count"]["status"], "UNAUTHORIZED")
        self.assertEqual(by_id["retry_on_http_500"]["status"], "AUTHORIZED")
        self.assertEqual(by_id["retry_on_timeout"]["status"], "UNRESOLVED")

    def test_accepted_candidate_passes(self):
        result = self.mod.review(self.policy, self.accepted, self.codeowners)
        self.assertEqual(result["outcome"], "ACCEPTED")
        self.assertEqual(result["blocking_findings"], 0)
        self.assertTrue(all(x["status"] == "AUTHORIZED" for x in result["obligations"]))
        self.assertTrue(all(x["status"] == "CHECKED" for x in result["constraints"]))

    def test_missing_codeowner_fails_closed(self):
        with self.assertRaises(self.mod.ReviewError):
            self.mod.review(self.policy, self.accepted, "# no owners\n")

    def test_ambiguous_codeowner_fails_closed(self):
        ambiguous = "/examples/payment-retry/ @cctsao1008 @other-owner\n"
        with self.assertRaises(self.mod.ReviewError):
            self.mod.review(self.policy, self.accepted, ambiguous)

    def test_unknown_semantic_obligation_is_unauthorized(self):
        candidate = copy.deepcopy(self.accepted)
        candidate["values"]["invented_retry_jitter"] = True
        result = self.mod.review(self.policy, candidate, self.codeowners)
        self.assertEqual(result["outcome"], "BLOCKED")
        row = next(x for x in result["obligations"] if x["obligation_id"] == "invented_retry_jitter")
        self.assertEqual(row["status"], "UNAUTHORIZED")

    def test_constraint_violation_blocks(self):
        candidate = copy.deepcopy(self.accepted)
        candidate["values"]["idempotency_requirement"] = False
        result = self.mod.review(self.policy, candidate, self.codeowners)
        self.assertEqual(result["outcome"], "BLOCKED")
        self.assertEqual(result["constraints"][0]["status"], "FAILED")

    def test_markdown_is_reviewable(self):
        result = self.mod.review(self.policy, self.unsafe, self.codeowners)
        markdown = self.mod.render_markdown(result)
        self.assertIn("MERGE GATE:** **BLOCKED", markdown)
        self.assertIn("`retry_count`", markdown)
        self.assertIn("**UNAUTHORIZED**", markdown)
        self.assertIn("CODEOWNERS is an adapter", markdown)


if __name__ == "__main__":
    unittest.main()
