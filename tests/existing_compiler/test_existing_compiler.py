from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_module():
    path = ROOT / "prototypes/existing_compiler/run.py"
    spec = importlib.util.spec_from_file_location("existing_compiler", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExistingCompilerUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod = load_module()

    def test_mutation_changes_fixture_payload(self):
        source = 'int main(void) { puts("Hello, world!"); }\n'
        mutated = self.mod.mutate_generated_c(source, "Hello, world!\n")
        self.assertIn("MUTATED-WORLD", mutated)
        self.assertNotEqual(source, mutated)

    def test_find_cc_resolves_available_compiler(self):
        cc = self.mod.find_cc(None)
        self.assertTrue(Path(cc).is_file())


if __name__ == "__main__":
    unittest.main()
