from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class A0ScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module("a0_score", ROOT / "research/a0-semantic-resolution/score.py")
        cls.gold = cls.mod.read_jsonl(ROOT / "research/a0-semantic-resolution/benchmark.jsonl")

    def test_negative_control_exposes_unsafe_resolution(self):
        pred = cls_pred = self.mod.read_jsonl(
            ROOT / "research/a0-semantic-resolution/baselines/unsafe-always-resolve.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["benchmark_version"], "a0/v1")
        self.assertGreater(result["unsafe_resolution_rate"], 0.5)
        self.assertEqual(result["resolved_accuracy"], 1.0)
        self.assertEqual(len(cls_pred), len(self.gold))

    def test_prediction_id_mismatch_fails(self):
        pred = [{"id": self.gold[0]["id"], "decision": "RESOLVED"}]
        with self.assertRaises(ValueError):
            self.mod.score(self.gold, pred)

    def test_measured_claude_opus_5_high_baseline_matches_recorded_score(self):
        baseline = ROOT / "research/a0-semantic-resolution/baselines"
        pred = self.mod.read_jsonl(
            baseline / "claude-opus-5-high-20260816.predictions.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        recorded = json.loads(
            (baseline / "claude-opus-5-high-20260816.score.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(result, recorded)
        self.assertEqual(result["cases"], 24)
        self.assertEqual(result["overall_accuracy"], 1.0)
        self.assertEqual(result["unsafe_resolution_rate"], 0.0)
        self.assertEqual(result["unresolved_recall"], 1.0)
        self.assertEqual(result["conflict_recall"], 1.0)
        self.assertEqual(result["resolved_accuracy"], 1.0)


class A0FFieldResolutionScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module(
            "a0f_score", ROOT / "research/a0-field-resolution/score.py"
        )
        cls.gold = cls.mod.read_jsonl(
            ROOT / "research/a0-field-resolution/benchmark.jsonl"
        )

    def test_oracle_fixture_scores_perfectly(self):
        pred = self.mod.read_jsonl(
            ROOT / "research/a0-field-resolution/baselines/oracle-fixture.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["benchmark_version"], "a0f/v1")
        self.assertEqual(result["cases"], 24)
        self.assertEqual(result["fields"], 114)
        self.assertEqual(result["field_accuracy"], 1.0)
        self.assertEqual(result["case_exact_match"], 1.0)
        self.assertEqual(result["unsafe_field_resolution_rate"], 0.0)
        self.assertEqual(result["unsafe_field_dismissal_rate"], 0.0)
        self.assertEqual(result["overblocking_rate"], 0.0)
        self.assertEqual(result["unresolved_field_recall"], 1.0)
        self.assertEqual(result["conflict_field_recall"], 1.0)
        self.assertEqual(result["resolved_field_accuracy"], 1.0)
        self.assertEqual(result["not_applicable_accuracy"], 1.0)

    def test_unsafe_always_resolve_control_is_detected(self):
        pred = self.mod.read_jsonl(
            ROOT
            / "research/a0-field-resolution/baselines/unsafe-always-resolve.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["unsafe_field_resolution_rate"], 1.0)
        self.assertEqual(result["unsafe_field_dismissal_rate"], 0.0)
        self.assertEqual(result["resolved_field_accuracy"], 1.0)
        self.assertLess(result["field_accuracy"], 0.7)

    def test_unsafe_all_not_applicable_control_is_detected(self):
        pred = self.mod.read_jsonl(
            ROOT
            / "research/a0-field-resolution/baselines/unsafe-all-not-applicable.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["unsafe_field_resolution_rate"], 0.0)
        self.assertEqual(result["unsafe_field_dismissal_rate"], 1.0)
        self.assertEqual(result["not_applicable_accuracy"], 1.0)
        self.assertLess(result["field_accuracy"], 0.1)

    def test_overconservative_control_is_detected(self):
        pred = self.mod.read_jsonl(
            ROOT
            / "research/a0-field-resolution/baselines/overconservative-all-unresolved.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["unsafe_field_resolution_rate"], 0.0)
        self.assertEqual(result["unsafe_field_dismissal_rate"], 0.0)
        self.assertEqual(result["overblocking_rate"], 1.0)
        self.assertEqual(result["unresolved_field_recall"], 1.0)
        self.assertEqual(result["resolved_field_accuracy"], 0.0)

    def test_field_set_mismatch_fails(self):
        pred = [
            {
                "id": case["id"],
                "field_states": dict(case["field_states"]),
            }
            for case in self.gold
        ]
        pred[0]["field_states"].pop(next(iter(pred[0]["field_states"])))
        with self.assertRaises(ValueError):
            self.mod.score(self.gold, pred)

    def test_invalid_field_state_fails(self):
        pred = [
            {
                "id": case["id"],
                "field_states": dict(case["field_states"]),
            }
            for case in self.gold
        ]
        first_field = next(iter(pred[0]["field_states"]))
        pred[0]["field_states"][first_field] = "MAYBE"
        with self.assertRaises(ValueError):
            self.mod.score(self.gold, pred)


class CompletenessScoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module(
            "c0_score", ROOT / "research/semantic-obligation-completeness/score.py"
        )
        cls.gold = cls.mod.read_jsonl(
            ROOT / "research/semantic-obligation-completeness/benchmark.jsonl"
        )

    def test_oracle_fixture_scores_perfectly(self):
        pred = self.mod.read_jsonl(
            ROOT / "research/semantic-obligation-completeness/baselines/oracle-fixture.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertEqual(result["benchmark_version"], "c0/v1")
        self.assertEqual(result["obligation_recall"], 1.0)
        self.assertEqual(result["unsafe_omission_rate"], 0.0)
        self.assertEqual(result["spurious_obligation_rate"], 0.0)
        self.assertEqual(result["high_impact_recall"], 1.0)

    def test_naive_fixture_exposes_omissions(self):
        pred = self.mod.read_jsonl(
            ROOT / "research/semantic-obligation-completeness/baselines/naive-first-obligation.jsonl"
        )
        result = self.mod.score(self.gold, pred)
        self.assertLess(result["obligation_recall"], 0.5)
        self.assertGreater(result["unsafe_omission_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
