import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "prototypes/poc1c/backend.py"
spec = importlib.util.spec_from_file_location("poc1c_backend_hardening", MOD)
backend = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(backend)

PROFILE = ROOT / "prototypes/poc1c/target_profiles.py"
profile_spec = importlib.util.spec_from_file_location("poc1c_profiles_hardening", PROFILE)
profiles = importlib.util.module_from_spec(profile_spec)
assert profile_spec.loader
profile_spec.loader.exec_module(profiles)

IR = ROOT / "examples/native-rv32i/safe_add_sub.specir.json"


class BackendHardeningTests(unittest.TestCase):
    def setUp(self):
        self.ir = json.loads(IR.read_text())
        self.target = backend.validate_target_config(copy.deepcopy(profiles.RV32I_BAREMETAL))

    def _generate(self, ir):
        fn = backend.validate_codegen_specir(ir)
        return backend.RV32ICodeGenerator(fn, self.target).generate()

    def test_integer_literal_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["body"]["expr"] = {"op": "+", "args": ["a", 1]}
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_UNSUPPORTED_LITERAL"):
            backend.validate_codegen_specir(ir)

    def test_non_binary_operation_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["body"]["expr"] = {"op": "+", "args": ["a", "b", "a"]}
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_UNSUPPORTED_OPERATION"):
            backend.validate_codegen_specir(ir)

    def test_non_expression_body_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["body"] = {"kind": "block", "ops": []}
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_UNSUPPORTED_OPERATION"):
            backend.validate_codegen_specir(ir)

    def test_mixed_integer_types_rejected(self):
        ir = copy.deepcopy(self.ir)
        ir["function"]["inputs"][1]["type"] = "u32"
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_ABI"):
            backend.validate_codegen_specir(ir)

    def test_expression_tree_exhaustion_rejected_by_codegen(self):
        ir = copy.deepcopy(self.ir)
        expr = {"op": "+", "args": ["a", "b"]}
        for _ in range(8):
            expr = {"op": "+", "args": [{"op": "+", "args": ["a", "b"]}, expr]}
        ir["function"]["body"]["expr"] = expr
        fn = backend.validate_codegen_specir(ir)
        with self.assertRaisesRegex(backend.Poc1CError, "E_TARGET_OUT_OF_REGISTERS"):
            backend.RV32ICodeGenerator(fn, self.target).generate()

    def test_root_symbol_result_is_position_independent(self):
        first = copy.deepcopy(self.ir)
        first["function"]["body"]["expr"] = "a"
        asm_first, _ = self._generate(first)
        self.assertIn("    ret", asm_first)

        second = copy.deepcopy(self.ir)
        second["function"]["body"]["expr"] = "b"
        asm_second, _ = self._generate(second)
        self.assertIn("add a0, a1, zero", asm_second)
        self.assertIn("    ret", asm_second)

    def test_u32_codegen_uses_rv32i_integer_instructions(self):
        ir = copy.deepcopy(self.ir)
        for inp in ir["function"]["inputs"]:
            inp["type"] = "u32"
        ir["function"]["output"]["type"] = "u32"
        asm, state = self._generate(ir)
        self.assertIn("add t0, a0, a1", asm)
        self.assertIn("sub a0, t0, a1", asm)
        self.assertEqual(0, state["spill_count"])

    def test_callee_saved_register_use_is_rejected_without_save_restore(self):
        original = list(backend.TEMP_REGS)
        backend.TEMP_REGS[:] = ["s0", *original[1:]]
        try:
            with self.assertRaisesRegex(backend.Poc1CError, "E_BACKEND_ABI_CLOBBER"):
                self._generate(copy.deepcopy(self.ir))
        finally:
            backend.TEMP_REGS[:] = original

    def test_generated_state_records_abi_preservation_policy(self):
        _, state = self._generate(copy.deepcopy(self.ir))
        self.assertEqual("forbidden-without-explicit-save-restore", state["callee_saved_policy"])
        self.assertIn("s0", state["forbidden_unsaved_registers"])
        self.assertEqual("root-only", state["preferred_dest_policy"])

    def test_preferred_destination_is_root_only(self):
        fn = backend.validate_codegen_specir(copy.deepcopy(self.ir))
        generator = backend.RV32ICodeGenerator(fn, self.target)
        with self.assertRaisesRegex(backend.Poc1CError, "E_BACKEND_STATE"):
            generator.compile_expr({"op": "+", "args": ["a", "b"]}, preferred_dest="a0")


if __name__ == "__main__":
    unittest.main()
