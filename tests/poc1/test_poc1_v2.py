import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = ROOT / "prototypes/poc1/spec2exec_poc1_v2.py"
spec = importlib.util.spec_from_file_location("spec2exec_poc1_v2", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(mod)

SPEC_PATH = ROOT / "examples/bounded-arithmetic/specification.json"
IR_PATH = ROOT / "examples/bounded-arithmetic/safe_add.specir.json"


class Poc1V2Tests(unittest.TestCase):
    def setUp(self):
        spec_doc = json.loads(SPEC_PATH.read_text())
        ir_doc = json.loads(IR_PATH.read_text())
        self.verified = mod.verify_specir(ir_doc, mod.verify_specification(spec_doc))

    def test_literal_forms(self):
        self.assertEqual("INT32_MIN", mod.c_literal(-(2**31), "i32"))
        self.assertEqual("UINT32_C(4294967295)", mod.c_literal(2**32 - 1, "u32"))

    def test_model_scoped_obligations(self):
        try:
            import z3  # noqa: F401
        except ImportError:
            self.skipTest("z3-solver not installed")
        with tempfile.TemporaryDirectory() as td:
            c_path = Path(td) / "generated.c"
            mod.lower_to_c(self.verified, c_path)
            evidence = mod.translation_validate(self.verified, c_path, "fixture")
            self.assertEqual("SOLVER_PROVEN", evidence["status"])
            self.assertEqual(["sat", "unsat", "unsat", "unsat", "sat"], [q["result"] for q in evidence["proof_obligations"]])

    def test_large_input_domain_is_rejected_by_p3_safety_query(self):
        try:
            import z3  # noqa: F401
        except ImportError:
            self.skipTest("z3-solver not installed")
        changed = copy.deepcopy(self.verified)
        changed["input_ranges"] = {
            "a": (2_000_000_000, 2_000_000_000),
            "b": (2_000_000_000, 2_000_000_000),
        }
        with tempfile.TemporaryDirectory() as td:
            c_path = Path(td) / "generated.c"
            mod.lower_to_c(changed, c_path)
            with self.assertRaisesRegex(mod.VerificationError, "E_SIGNED_OVERFLOW_UB"):
                mod.translation_validate(changed, c_path)


if __name__ == "__main__":
    unittest.main()
