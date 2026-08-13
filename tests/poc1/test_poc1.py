import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "prototypes/poc1/spec2exec_poc1.py"
spec = importlib.util.spec_from_file_location("spec2exec_poc1", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)

SPEC_PATH = ROOT / "examples/bounded-arithmetic/specification.json"
IR_PATH = ROOT / "examples/bounded-arithmetic/safe_add.specir.json"


def load(path):
    return json.loads(path.read_text())


class Poc1Tests(unittest.TestCase):
    def setUp(self):
        self.spec_doc = load(SPEC_PATH)
        self.ir_doc = load(IR_PATH)
        self.spec_info = mod.verify_specification(self.spec_doc)

    def test_valid(self):
        verified = mod.verify_specir(self.ir_doc, self.spec_info)
        self.assertEqual((0, 200), verified["body_range"])

    def test_range_drift_rejected(self):
        doc = copy.deepcopy(self.ir_doc)
        doc["function"]["inputs"][0]["range"]["max"] = 99
        with self.assertRaisesRegex(mod.VerificationError, "E_SPEC_RANGE_LINK"):
            mod.verify_specir(doc, self.spec_info)

    def test_orphan_constraint_rejected(self):
        doc = copy.deepcopy(self.ir_doc)
        doc["function"]["inputs"][0]["trace"] = ["REQ-NOT-REAL"]
        with self.assertRaisesRegex(mod.VerificationError, "E_UNTRACEABLE_CONSTRAINT"):
            mod.verify_specir(doc, self.spec_info)

    def test_missing_spec_clause_rejected(self):
        doc = copy.deepcopy(self.ir_doc)
        doc["function"]["postconditions"][0]["trace"] = ["REQ-ARITH-001"]
        doc["function"]["body"]["trace"] = ["REQ-ARITH-001"]
        with self.assertRaisesRegex(mod.VerificationError, "E_SPEC_BEHAVIOR_LINK"):
            mod.verify_specir(doc, self.spec_info)

    def test_output_range_too_small_rejected(self):
        spec_doc = copy.deepcopy(self.spec_doc)
        spec_doc["function"]["output"]["range"] = {"min": 0, "max": 100}
        ir_doc = copy.deepcopy(self.ir_doc)
        ir_doc["function"]["output"]["range"] = {"min": 0, "max": 100}
        spec_info = mod.verify_specification(spec_doc)
        with self.assertRaisesRegex(mod.VerificationError, "E_OUTPUT_RANGE"):
            mod.verify_specir(ir_doc, spec_info)

    def test_overflow_rejected(self):
        spec_doc = copy.deepcopy(self.spec_doc)
        ir_doc = copy.deepcopy(self.ir_doc)
        big = 2_000_000_000
        for i in range(2):
            spec_doc["function"]["inputs"][i]["range"] = {"min": big, "max": big}
            ir_doc["function"]["inputs"][i]["range"] = {"min": big, "max": big}
            name = ir_doc["function"]["inputs"][i]["id"]
            ir_doc["function"]["preconditions"][i]["expr"] = {"op": "and", "args": [
                {"op": ">=", "args": [name, big]},
                {"op": "<=", "args": [name, big]}
            ]}
        spec_doc["function"]["output"]["range"] = {"min": 0, "max": 2_147_483_647}
        ir_doc["function"]["output"]["range"] = {"min": 0, "max": 2_147_483_647}
        spec_info = mod.verify_specification(spec_doc)
        with self.assertRaisesRegex(mod.VerificationError, "E_OVERFLOW"):
            mod.verify_specir(ir_doc, spec_info)

    def test_tampered_c_expression_rejected_by_p3_when_z3_available(self):
        try:
            import z3  # noqa: F401
        except ImportError:
            self.skipTest("z3-solver not installed")
        verified = mod.verify_specir(self.ir_doc, self.spec_info)
        with tempfile.TemporaryDirectory() as td:
            c_path = Path(td) / "tampered.c"
            c_path.write_text("#include <stdint.h>\nint32_t safe_add(int32_t a, int32_t b){ return (a - b); }\n")
            with self.assertRaisesRegex(mod.VerificationError, "E_P3_EQUIV"):
                mod.translation_validate(verified, c_path)


if __name__ == "__main__":
    unittest.main()
