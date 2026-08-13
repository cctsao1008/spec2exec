import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "prototypes" / "poc0" / "spec2exec_poc0.py"
spec = importlib.util.spec_from_file_location("spec2exec_poc0", MODULE_PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)

VALID_PATH = ROOT / "examples" / "hello" / "hello.specir.json"
SPECIFICATION_PATH = ROOT / "examples" / "hello" / "specification.json"


class Poc0VerificationTests(unittest.TestCase):
    def valid(self):
        return json.loads(VALID_PATH.read_text(encoding="utf-8"))

    def specification(self):
        return json.loads(SPECIFICATION_PATH.read_text(encoding="utf-8"))

    def assert_rejected(self, doc, code, specification=None):
        with self.assertRaises(mod.VerificationError) as ctx:
            mod.verify_specir(doc, specification)
        self.assertTrue(str(ctx.exception).startswith(code + ":"), str(ctx.exception))

    def test_valid_document_passes(self):
        evidence = mod.verify_specir(self.valid(), self.specification())
        self.assertEqual(evidence["result"], "PASS")

    def test_wrong_version_rejected(self):
        doc = self.valid()
        doc["specir_version"] = "spec2exec.specir/v999"
        self.assert_rejected(doc, "E_VERSION")

    def test_unknown_operation_rejected(self):
        doc = self.valid()
        doc["program"]["operations"][0]["kind"] = "network.send"
        self.assert_rejected(doc, "E_OPERATION_KIND")

    def test_duplicate_operation_id_rejected(self):
        doc = self.valid()
        doc["program"]["operations"].append(copy.deepcopy(doc["program"]["operations"][0]))
        self.assert_rejected(doc, "E_DUPLICATE_ID")

    def test_exit_status_out_of_range_rejected(self):
        doc = self.valid()
        doc["program"]["exit_status"] = 256
        self.assert_rejected(doc, "E_EXIT_RANGE")

    def test_trace_scope_rejected(self):
        doc = self.valid()
        doc["program"]["operations"][0]["trace"] = ["REQ-OTHER-001"]
        self.assert_rejected(doc, "E_TRACE_SCOPE")

    def test_specification_stdout_mismatch_rejected(self):
        doc = self.valid()
        specification = self.specification()
        specification["behavior"]["stdout"] = "Different\n"
        self.assert_rejected(doc, "E_SPEC_STDOUT_LINK", specification)

    def test_unaccepted_specification_rejected(self):
        specification = self.specification()
        specification["acceptance"]["status"] = "draft"
        with self.assertRaises(mod.VerificationError) as ctx:
            mod.verify_specir(self.valid(), specification)
        self.assertTrue(str(ctx.exception).startswith("E_SPEC_ACCEPT:"), str(ctx.exception))

    def test_lowering_contains_trace_and_behavior(self):
        doc = self.valid()
        c = mod.lower_to_c(doc)
        self.assertIn("REQ-HELLO-001", c)
        self.assertIn("Hello, world!", c)
        self.assertIn("return 0;", c)


if __name__ == "__main__":
    unittest.main()
