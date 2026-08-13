"""POC-1C.A pipeline, evidence, assembler/linker, and emulator integration."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
from typing import Any

from backend import Poc1CError, expect, validate_codegen_specir, validate_target_config, RV32ICodeGenerator

ROOT = Path(__file__).resolve().parents[2]
V2_PATH = ROOT / "prototypes" / "poc1" / "spec2exec_poc1_v2.py"
_v2_spec = importlib.util.spec_from_file_location("spec2exec_poc1_v2", V2_PATH)
v2 = importlib.util.module_from_spec(_v2_spec)
assert _v2_spec and _v2_spec.loader
_v2_spec.loader.exec_module(v2)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tool_version(tool: str) -> str:
    proc = subprocess.run([tool, "--version"], text=True, capture_output=True, check=True)
    return proc.stdout.splitlines()[0].strip()


def verify_machine_independent_specir(spec_doc: Any, ir_doc: Any) -> dict[str, Any]:
    expect(isinstance(ir_doc, dict) and isinstance(ir_doc.get("function"), dict),
           "E_SPECIR", "SpecIR function must be an object")
    expect("target" not in ir_doc["function"], "E_SPECIR_TARGET_LEAK",
           "machine-independent SpecIR must not contain function.target")
    compat = copy.deepcopy(ir_doc)
    compat["function"]["target"] = "host-c"
    try:
        verified = v2.verify_specir(compat, v2.verify_specification(spec_doc))
    except v2.VerificationError as exc:
        raise Poc1CError(str(exc)) from exc
    verified["function"] = ir_doc["function"]
    return verified


def generate(specification_path: Path, specir_path: Path, target_path: Path,
             build_dir: Path) -> dict[str, Path]:
    spec_doc, specir = load_json(specification_path), load_json(specir_path)
    target = validate_target_config(load_json(target_path))
    verified = verify_machine_independent_specir(spec_doc, specir)
    fn = validate_codegen_specir(specir)
    asm, state = RV32ICodeGenerator(fn, target).generate()

    build_dir.mkdir(parents=True, exist_ok=True)
    asm_path = build_dir / f"{fn['name']}.s"
    state_path = build_dir / "backend-state.json"
    evidence_path = build_dir / "evidence.json"
    asm_path.write_text(asm, encoding="utf-8")
    write_json(state_path, state)

    evidence = {
        "schema": "spec2exec.evidence/v0.1",
        "poc": "POC-1C.A",
        "subject": fn["name"],
        "claims": verified["evidence"] + [{
            "id": "P3.specir_to_rv32i_assembly",
            "status": "TESTED",
            "scope": "deterministic add/sub RV32I code-generation rules; not a formal equivalence proof",
            "subject_binding": {
                "specir_sha256": sha256(specir_path),
                "target_config_sha256": sha256(target_path),
                "assembly_sha256": sha256(asm_path),
                "backend_state_sha256": sha256(state_path),
            },
            "tcb": [
                "Python runtime",
                "POC-1C.A target generator",
                "POC-1A P1/P2 verifier compatibility path",
            ],
        }],
        "artifacts": {
            str(specification_path): sha256(specification_path),
            str(specir_path): sha256(specir_path),
            str(target_path): sha256(target_path),
            str(asm_path): sha256(asm_path),
            str(state_path): sha256(state_path),
        },
    }
    write_json(evidence_path, evidence)
    return {"asm": asm_path, "state": state_path, "evidence": evidence_path}


def build(specification_path: Path, specir_path: Path, target_path: Path,
          build_dir: Path, harness_path: Path, linker_script: Path,
          assembler: str, linker: str) -> dict[str, Path]:
    paths = generate(specification_path, specir_path, target_path, build_dir)
    fn = validate_codegen_specir(load_json(specir_path))
    obj = build_dir / f"{fn['name']}.o"
    harness_obj = build_dir / "runtime-harness.o"
    elf = build_dir / f"{fn['name']}.elf"

    as_path, ld_path = shutil.which(assembler), shutil.which(linker)
    expect(as_path is not None, "E_TOOLCHAIN", f"assembler not found: {assembler}")
    expect(ld_path is not None, "E_TOOLCHAIN", f"linker not found: {linker}")

    as_generated = [as_path, "-march=rv32i", "-mabi=ilp32", str(paths["asm"]), "-o", str(obj)]
    as_harness = [as_path, "-march=rv32i", "-mabi=ilp32", str(harness_path), "-o", str(harness_obj)]
    link_cmd = [ld_path, "-m", "elf32lriscv", "-T", str(linker_script),
                str(harness_obj), str(obj), "-o", str(elf)]
    subprocess.run(as_generated, check=True)
    subprocess.run(as_harness, check=True)
    subprocess.run(link_cmd, check=True)

    evidence = load_json(paths["evidence"])
    evidence["claims"].extend([
        {
            "id": "P4-A.assembly_to_object",
            "status": "TRUSTED",
            "tool": {"path": as_path, "version": tool_version(as_path)},
            "invocation": as_generated,
            "subject_binding": {
                "assembly_sha256": sha256(paths["asm"]),
                "object_sha256": sha256(obj),
            },
        },
        {
            "id": "P4-L.object_to_linked_elf",
            "status": "TRUSTED",
            "tool": {"path": ld_path, "version": tool_version(ld_path)},
            "invocation": link_cmd,
            "subject_binding": {
                "generated_object_sha256": sha256(obj),
                "harness_object_sha256": sha256(harness_obj),
                "linked_elf_sha256": sha256(elf),
            },
        },
    ])
    evidence["artifacts"].update({
        str(obj): sha256(obj),
        str(harness_obj): sha256(harness_obj),
        str(elf): sha256(elf),
    })
    write_json(paths["evidence"], evidence)
    return {**paths, "object": obj, "harness_object": harness_obj, "elf": elf}


def run_qemu(elf: Path, evidence_path: Path, qemu: str) -> None:
    qemu_path = shutil.which(qemu)
    expect(qemu_path is not None, "E_TOOLCHAIN", f"emulator not found: {qemu}")
    command = [qemu_path, "-machine", "virt", "-nographic", "-bios", "none", "-kernel", str(elf)]
    proc = subprocess.run(command, timeout=10)
    expect(proc.returncode == 0, "E_RUNTIME", f"QEMU returned {proc.returncode}")

    evidence = load_json(evidence_path)
    evidence["claims"].append({
        "id": "P4-R.linked_elf_runtime",
        "status": "TESTED_EXHAUSTIVE",
        "scope": "safe_add_sub a,b in [-100,100], 40,401 input pairs, assembly-only harness",
        "tool": {"path": qemu_path, "version": tool_version(qemu_path)},
        "invocation": command,
        "subject_binding": {"linked_elf_sha256": sha256(elf)},
        "cross_validates": ["P3.specir_to_rv32i_assembly"],
        "notes": "Runtime agreement does not discharge the P3 preservation obligation.",
    })
    write_json(evidence_path, evidence)
