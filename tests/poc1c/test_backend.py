import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "prototypes/poc1c/backend.py"
spec = importlib.util.spec_from_file_location("poc1c_backend", MOD)
backend = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(backend)

PROFILE = ROOT / "prototypes/poc1c/target_profiles.py"
profile_spec = importlib.util.spec_from_file_location("poc1c_profiles", PROFILE)
profiles = importlib.util.module_from_spec(profile_spec)
assert profile_spec.loader
profile_spec.loader.exec_module(profiles)

IR = ROOT / "examples/native-rv32i/safe_add_sub.specir.json"


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.ir = json.loads(IR.read_text())
        self.target = backend.validate_target_config(copy.deepcopy(profiles.RV32I_BAREMETAL))

    def test_codegen(self):
        fn = backend.validate_codegen_specir(self.ir)
        asm, state = backend.RV32ICodeGenerator(fn, self.target).generate()
        self.assertIn("add t0, a0, a1", asm)
        self.assertIn("sub a0, t0, a1", asm)
        self.assertEqual(1, state["temporary_pool_high_water_mark"])
        self.assertEqual(0, state["spill_count"])
        self.assertEqual("a0", state["abi_fixed_locations"]["arguments"]["a"])
        self.assertEqual("a1", state["abi_fixed_locations"]["arguments"]["b"])
        self.assertEqual("a0", state["abi_fixed_locations"]["return"])

    def test_mul_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["body"]["expr"] = {"op": "*", "args": ["a", "b"]}
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_UNSUPPORTED_OPERATION"):
            backend.validate_codegen_specir(ir)

    def test_target_field_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["target"] = "host-c"
        with self.assertRaisesRegex(backend.Poc1CError, "E_SPECIR_TARGET_LEAK"):
            backend.validate_codegen_specir(ir)

    def test_temporary_pool_exhaustion_rejected(self):
        pool = backend.RegisterPool()
        for _ in range(7):
            pool.acquire()
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_OUT_OF_REGISTERS"):
            pool.acquire()

    def test_ninth_argument_rejected(self):
        ir = copy.deepcopy(self.ir)
        template = copy.deepcopy(ir["function"]["inputs"][0])
        for i in range(2, 9):
            item = copy.deepcopy(template)
            item["id"] = f"x{i}"
            ir["function"]["inputs"].append(item)
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_ABI"):
            backend.validate_codegen_specir(ir)


if __name__ == "__main__":
    unittest.main()
