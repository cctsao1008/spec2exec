#!/usr/bin/env python3
import argparse
from pathlib import Path
from pipeline import build, generate, run_qemu

p = argparse.ArgumentParser()
p.add_argument("mode", choices=["generate", "build", "all"])
p.add_argument("specir", type=Path)
p.add_argument("--specification", required=True, type=Path)
p.add_argument("--target-profile", default="rv32i-baremetal")
p.add_argument("--build-dir", required=True, type=Path)
p.add_argument("--harness", type=Path)
p.add_argument("--linker-script", type=Path)
p.add_argument("--assembler", default="riscv64-unknown-elf-as")
p.add_argument("--linker", default="riscv64-unknown-elf-ld")
p.add_argument("--qemu", default="qemu-system-riscv32")
a = p.parse_args()

if a.mode == "generate":
    generate(a.specification, a.specir, a.target_profile, a.build_dir)
else:
    if a.harness is None or a.linker_script is None:
        p.error("build/all require --harness and --linker-script")
    paths = build(a.specification, a.specir, a.target_profile, a.build_dir,
                  a.harness, a.linker_script, a.assembler, a.linker)
    if a.mode == "all":
        run_qemu(paths["elf"], paths["evidence"], a.qemu)
