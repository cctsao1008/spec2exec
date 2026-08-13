import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "prototypes/poc1b/spec2exec_poc1b.py"
spec = importlib.util.spec_from_file_location("spec2exec_poc1b", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)

SPEC_PATH = ROOT / "examples/optimization-preservation/specification.json"
IR_PATH = ROOT / "examples/optimization-preservation/safe_add_sub.specir.json"


class Poc1BTests(unittest.TestCase):
    def setUp(self):
        self.spec_doc = json.loads(SPEC_PATH.read_text())
        self.ir_doc = json.loads(IR_PATH.read_text())
        self.spec_info = mod.v2.verify_specification(self.spec_doc)
        self.verified = mod.v2.verify_specir(self.ir_doc, self.spec_info)

    def test_contract_and_conservative_interval(self):
        contract = mod.verify_poc1b_contract(self.spec_doc, self.verified)
        self.assertEqual("REQ-OPT-001-EQ", contract["clause_id"])
        self.assertEqual("a", contract["expr"])
        self.assertEqual((-300, 300), self.verified["body_range"])

    def test_harness_contains_contract_trace(self):
        contract = mod.verify_poc1b_contract(self.spec_doc, self.verified)
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target.c"
            harness = Path(td) / "verification_harness.c"
            mod.v2.lower_to_c(self.verified, target, banner="POC-1B-test")
            mod.generate_cbmc_harness(self.verified, contract, target, harness)
            text = harness.read_text()
            self.assertIn("TRACE: REQ-OPT-001-EQ", text)
            self.assertIn("__CPROVER_assume", text)
            self.assertIn("result == a", text)

    def test_optimization_destroys_add_sub_when_clang_available(self):
        if not mod.shutil.which("clang"):
            self.skipTest("clang not installed")
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "target.c"
            mod.v2.lower_to_c(self.verified, target, banner="POC-1B-test")
            evidence = mod.optimization_destruction(target, self.verified["function"]["name"], Path(td))
            self.assertGreaterEqual(evidence["o0_arithmetic_instructions"], 2)
            self.assertEqual(0, evidence["o2_arithmetic_instructions"])


if __name__ == "__main__":
    unittest.main()
