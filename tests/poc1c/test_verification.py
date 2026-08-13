import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "prototypes/poc1c/verification.py"
spec = importlib.util.spec_from_file_location("poc1c_verification", MODULE)
verification = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(verification)

SPEC = ROOT / "examples/optimization-preservation/specification.json"
IR = ROOT / "examples/native-rv32i/safe_add_sub.specir.json"


def rename_symbol(value, old, new):
    if isinstance(value, str):
        return new if value == old else value
    if isinstance(value, list):
        return [rename_symbol(item, old, new) for item in value]
    if isinstance(value, dict):
        return {key: rename_symbol(item, old, new) for key, item in value.items()}
    return value


class TargetNeutralVerificationTests(unittest.TestCase):
    def test_no_c_target_field_is_required(self):
        spec_doc = json.loads(SPEC.read_text())
        ir_doc = json.loads(IR.read_text())
        verified = verification.verify_specir(ir_doc, verification.verify_specification(spec_doc))
        self.assertEqual("safe_add_sub", verified["function"]["name"])

    def test_c_specific_reserved_identifier_is_not_a_native_restriction(self):
        spec_doc = rename_symbol(json.loads(SPEC.read_text()), "a", "INT32_MIN")
        ir_doc = rename_symbol(json.loads(IR.read_text()), "a", "INT32_MIN")
        verified = verification.verify_specir(ir_doc, verification.verify_specification(spec_doc))
        self.assertIn("INT32_MIN", verified["input_ranges"])

    def test_machine_target_leak_is_rejected(self):
        spec_doc = json.loads(SPEC.read_text())
        ir_doc = copy.deepcopy(json.loads(IR.read_text()))
        ir_doc["function"]["target"] = "rv32i"
        with self.assertRaisesRegex(verification.VerificationError, "E_SPECIR_TARGET_LEAK"):
            verification.verify_specir(ir_doc, verification.verify_specification(spec_doc))


if __name__ == "__main__":
    unittest.main()
