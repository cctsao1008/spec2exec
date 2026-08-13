import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "prototypes/poc1c/run.py"
SPEC = ROOT / "examples/optimization-preservation/specification.json"
IR = ROOT / "examples/native-rv32i/safe_add_sub.specir.json"
HARNESS = ROOT / "tests/poc1c/runtime/safe_add_sub_harness.s"
LINKER_SCRIPT = ROOT / "tests/poc1c/runtime/rv32i_virt.ld"
AS = shutil.which("riscv64-unknown-elf-as")
LD = shutil.which("riscv64-unknown-elf-ld")
QEMU = shutil.which("qemu-system-riscv32")
TOOLS_AVAILABLE = all((AS, LD, QEMU))


@unittest.skipUnless(TOOLS_AVAILABLE, "RV32I binutils and QEMU are required")
class RuntimeOracleTests(unittest.TestCase):
    def _run_mutant(self, old: str, new: str) -> int:
        with tempfile.TemporaryDirectory() as tmp:
            build = Path(tmp)
            subprocess.run([
                sys.executable, str(RUN), "generate", str(IR),
                "--specification", str(SPEC),
                "--target-profile", "rv32i-baremetal",
                "--build-dir", str(build),
            ], cwd=ROOT, check=True)

            asm = build / "safe_add_sub.s"
            text = asm.read_text(encoding="utf-8")
            self.assertIn(old, text)
            asm.write_text(text.replace(old, new, 1), encoding="utf-8")

            obj = build / "safe_add_sub.o"
            harness_obj = build / "runtime-harness.o"
            elf = build / "safe_add_sub.elf"
            subprocess.run([AS, "-march=rv32i", "-mabi=ilp32", str(asm), "-o", str(obj)], check=True)
            subprocess.run([AS, "-march=rv32i", "-mabi=ilp32", str(HARNESS), "-o", str(harness_obj)], check=True)
            subprocess.run([
                LD, "-m", "elf32lriscv", "-T", str(LINKER_SCRIPT),
                str(harness_obj), str(obj), "-o", str(elf),
            ], check=True)
            proc = subprocess.run([
                QEMU, "-machine", "virt", "-nographic", "-bios", "none", "-kernel", str(elf),
            ], timeout=5, capture_output=True, text=True)
            return proc.returncode

    def test_non_equivalent_backend_mutations_fail_runtime_oracle(self):
        mutations = [
            ("    sub a0, t0, a1", "    add a0, t0, a1"),
            ("    add t0, a0, a1", "    sub t0, a0, a1"),
        ]
        for old, new in mutations:
            with self.subTest(mutation=f"{old.strip()} -> {new.strip()}"):
                self.assertNotEqual(0, self._run_mutant(old, new))


if __name__ == "__main__":
    unittest.main()
