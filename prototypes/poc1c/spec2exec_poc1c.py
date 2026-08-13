#!/usr/bin/env python3
"""Spec2Exec POC-1C.A command line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

from backend import Poc1CError
from pipeline import build, generate, run_qemu


def common(p: argparse.ArgumentParser) -> None:
    p.add_argument("specir", type=Path)
    p.add_argument("--specification", required=True, type=Path)
    p.add_argument("--target", required=True, type=Path)
    p.add_argument("--build-dir", required=True, type=Path)


def make_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate")
    common(gen)

    bld = sub.add_parser("build")
    common(bld)
    bld.add_argument("--harness", required=True, type=Path)
    bld.add_argument("--linker-script", required=True, type=Path)
    bld.add_argument("--assembler", default="riscv64-unknown-elf-as")
    bld.add_argument("--linker", default="riscv64-unknown-elf-ld")

    all_cmd = sub.add_parser("all")
    common(all_cmd)
    all_cmd.add_argument("--harness", required=True, type=Path)
    all_cmd.add_argument("--linker-script", required=True, type=Path)
    all_cmd.add_argument("--assembler", default="riscv64-unknown-elf-as")
    all_cmd.add_argument("--linker", default="riscv64-unknown-elf-ld")
    all_cmd.add_argument("--qemu", default="qemu-system-riscv32")
    return p


def main() -> int:
    args = make_parser().parse_args()
    try:
        if args.command == "generate":
            generate(args.specification, args.specir, args.target, args.build_dir)
        else:
            paths = build(
                args.specification,
                args.specir,
                args.target,
                args.build_dir,
                args.harness,
                args.linker_script,
                args.assembler,
                args.linker,
            )
            if args.command == "all":
                run_qemu(paths["elf"], paths["evidence"], args.qemu)
        return 0
    except (Poc1CError, subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
