import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
PROTO = ROOT / "prototypes/poc1c"
sys.path.insert(0, str(PROTO))

import pipeline  # noqa: E402

SPEC = ROOT / "examples/optimization-preservation/specification.json"
IR = ROOT / "examples/native-rv32i/safe_add_sub.specir.json"
HARNESS = ROOT / "tests/poc1c/runtime/safe_add_sub_harness.s"


class PipelineHardeningTests(unittest.TestCase):
    def setUp(self):
        self.spec_doc = json.loads(SPEC.read_text())
        self.ir_doc = json.loads(IR.read_text())
        self.verified = pipeline.verify_machine_independent_specir(self.spec_doc, self.ir_doc)

    def _validate_text(self, text):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "harness.s"
            path.write_text(text, encoding="utf-8")
            return pipeline.validate_runtime_harness(path, self.spec_doc, self.verified)

    def test_baseline_harness_binds_all_expected_cases(self):
        binding = pipeline.validate_runtime_harness(HARNESS, self.spec_doc, self.verified)
        self.assertEqual(40401, binding["expected_cases"])
        self.assertEqual("addi s2, zero, 0", binding["case_counter_binding"]["initialize"])
        self.assertEqual("addi s2, s2, 1", binding["case_counter_binding"]["increment"])
        self.assertEqual("bne s2, t2, .L_fail", binding["case_counter_binding"]["assertion"])

    def test_case_counter_lines_are_mandatory(self):
        baseline = HARNESS.read_text(encoding="utf-8")
        for line in (
            "    addi s2, zero, 0\n",
            "    addi s2, s2, 1\n",
            "    bne s2, t2, .L_fail\n",
        ):
            with self.subTest(line=line.strip()):
                self.assertIn(line, baseline)
                with self.assertRaisesRegex(pipeline.Poc1CError, "E_P4_DOMAIN"):
                    self._validate_text(baseline.replace(line, "", 1))

    def test_comment_text_cannot_satisfy_instruction_binding(self):
        baseline = HARNESS.read_text(encoding="utf-8")
        live = "    addi s2, s2, 1\n"
        modified = baseline.replace(live, "    addi s2, s2, 2\n", 1)
        modified += "\n    # addi s2, s2, 1\n"
        with self.assertRaisesRegex(pipeline.Poc1CError, "E_P4_DOMAIN"):
            self._validate_text(modified)

    def test_toolchain_binding_includes_assembly_dialect(self):
        target = pipeline.resolve_target_profile("rv32i-baremetal")
        binding = pipeline.resolve_gnu_toolchain_binding(target)
        self.assertIn("-march=rv32i", binding["assembler_flags"])

        incompatible = copy.deepcopy(target)
        incompatible["execution_profile"]["assembly_dialect"] = "other-riscv"
        with self.assertRaisesRegex(pipeline.Poc1CError, "E_TARGET_PROFILE"):
            pipeline.resolve_gnu_toolchain_binding(incompatible)

    def test_source_binding_includes_entrypoint_and_workflow(self):
        bound = {pipeline.rel(path) for path in pipeline.POC1C_SOURCE_FILES}
        self.assertIn("prototypes/poc1c/run.py", bound)
        self.assertIn(".github/workflows/poc1c.yml", bound)

    def test_working_tree_cleanliness_is_explicitly_reportable(self):
        self.assertIn(pipeline.working_tree_clean(), (True, False, None))


if __name__ == "__main__":
    unittest.main()
