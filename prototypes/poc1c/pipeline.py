"""POC-1C.A pipeline, evidence, assembler/linker, and emulator integration."""

from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any

from backend import Poc1CError, expect, validate_codegen_specir, validate_target_config, RV32ICodeGenerator
from target_profiles import RV32I_BAREMETAL
import verification as verifier

ROOT = Path(__file__).resolve().parents[2]
POC1C_SOURCE_FILES = [
    ROOT / "prototypes" / "poc1c" / "backend.py",
    ROOT / "prototypes" / "poc1c" / "pipeline.py",
    ROOT / "prototypes" / "poc1c" / "target_profiles.py",
    ROOT / "prototypes" / "poc1c" / "verification.py",
    ROOT / "Makefile",
]

CLAIM_PROPERTIES = {
    "P1.function_identity": "SpecIR function identity matches the accepted specification",
    "P1.constraint_traceability": "accepted constraints remain traceable in SpecIR",
    "P1.range_linkage": "SpecIR input/output ranges match accepted ranges",
    "P1.behavior_linkage": "SpecIR behavior expression matches accepted behavior",
    "P2.fixed_width_type_domain": "declared values remain inside the fixed-width integer type domain",
    "P2.output_range_containment": "computed body range is contained in the declared output range",
    "P2.no_signed_overflow_ub": "no signed overflow occurs within declared input ranges",
    "P2.no_unsigned_wraparound": "no unsigned wraparound occurs within declared input ranges",
    "P3.specir_to_rv32i_assembly": "target assembly preserves the accepted SpecIR semantics for the tested subset",
    "P4-A.assembly_to_object": "external assembler transforms target assembly into an ELF32 RISC-V object",
    "P4-H.harness_assembly": "external assembler transforms the runtime harness into an ELF32 RISC-V object",
    "P4-L.object_to_linked_elf": "external linker constructs the linked RV32I ELF from the bound objects and linker script",
    "P4-R.linked_elf_runtime": "linked ELF satisfies the accepted runtime contract over the declared test domain",
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


def tool_version(tool: str) -> str:
    proc = subprocess.run([tool, "--version"], text=True, capture_output=True, check=True)
    return proc.stdout.splitlines()[0].strip()


def source_revision() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    return proc.stdout.strip() if proc.returncode == 0 and proc.stdout.strip() else "UNAVAILABLE"


def collect_trace_ids(fn: dict[str, Any]) -> list[str]:
    result: set[str] = set()
    for item in fn.get("trace", []):
        if isinstance(item, str):
            result.add(item)
    for inp in fn.get("inputs", []):
        for item in inp.get("trace", []):
            if isinstance(item, str):
                result.add(item)
    for field in ("output", "body"):
        value = fn.get(field)
        if isinstance(value, dict):
            for item in value.get("trace", []):
                if isinstance(item, str):
                    result.add(item)
    for item in fn.get("overflow_trace", []):
        if isinstance(item, str):
            result.add(item)
    for field in ("preconditions", "postconditions"):
        for entry in fn.get(field, []):
            if isinstance(entry, dict):
                for item in entry.get("trace", []):
                    if isinstance(item, str):
                        result.add(item)
    return sorted(result)


def normalize_claim_schema(evidence: dict[str, Any]) -> None:
    """Ensure every evidence claim satisfies the RFC-0006 audit fields."""
    revision = evidence.get("source_revision", "UNAVAILABLE")
    default_subject = evidence.get("subject", "unknown")
    default_trace = evidence.get("trace_context", [])
    for claim in evidence.get("claims", []):
        claim_id = claim.get("id")
        expect(isinstance(claim_id, str) and claim_id, "E_EVIDENCE_SCHEMA", "claim.id is required")
        claim.setdefault("subject", default_subject)
        claim.setdefault("property", CLAIM_PROPERTIES.get(claim_id, claim_id))
        claim.setdefault("producer", "UNSPECIFIED")
        claim.setdefault("assumptions", [])
        claim.setdefault("source_revision", revision)
        claim.setdefault("trace", list(default_trace))
        claim.setdefault("subject_binding", {})


def resolve_target_profile(name: str) -> dict[str, Any]:
    profiles = {"rv32i-baremetal": RV32I_BAREMETAL}
    expect(name in profiles, "E_TARGET_PROFILE", f"unknown target profile {name!r}")
    return validate_target_config(copy.deepcopy(profiles[name]))


def resolve_gnu_toolchain_binding(target: dict[str, Any]) -> dict[str, list[str]]:
    """Translate a validated target configuration into GNU binutils options."""
    isa = target["isa_profile"]
    exe = target["execution_profile"]
    key = (
        isa["architecture"],
        isa["isa"],
        tuple(isa["extensions"]),
        exe["environment"],
        exe["abi"],
        exe["object_model"],
    )
    bindings = {
        ("riscv", "rv32i", (), "bare-metal", "ilp32-integer-subset", "elf32-riscv"): {
            "assembler_flags": ["-march=rv32i", "-mabi=ilp32"],
            "linker_flags": ["-m", "elf32lriscv"],
        }
    }
    expect(key in bindings, "E_TARGET_PROFILE", f"no GNU toolchain binding for target {key!r}")
    return copy.deepcopy(bindings[key])


def verify_machine_independent_specir(spec_doc: Any, ir_doc: Any) -> dict[str, Any]:
    try:
        spec_info = verifier.verify_specification(spec_doc)
        return verifier.verify_specir(ir_doc, spec_info)
    except verifier.VerificationError as exc:
        raise Poc1CError(str(exc)) from exc


def normalized_verifier_claims(verified: dict[str, Any], specification_path: Path,
                               specir_path: Path) -> list[dict[str, Any]]:
    binding = {
        "specification_sha256": sha256(specification_path),
        "specir_sha256": sha256(specir_path),
    }
    result = []
    for claim in verified["evidence"]:
        item = dict(claim)
        item["producer"] = "poc1c-target-neutral-verifier"
        item["assumptions"] = ["bounded integer model; declared input ranges are preconditions"]
        item["subject_binding"] = dict(binding)
        result.append(item)
    return result


def expected_case_count(ranges: dict[str, tuple[int, int]]) -> int:
    cases = 1
    for lo, hi in ranges.values():
        cases *= hi - lo + 1
    return cases


def split_lui_addi(value: int) -> tuple[int, int]:
    upper = (value + 0x800) >> 12
    lower = value - (upper << 12)
    expect(-2048 <= lower <= 2047, "E_P4_DOMAIN", "internal LUI/ADDI split is invalid")
    return upper, lower


def validate_runtime_harness(harness_path: Path, spec_doc: dict[str, Any],
                             verified: dict[str, Any]) -> dict[str, Any]:
    """Mechanically bind the hand-written harness to the verified domain/oracle."""
    text = harness_path.read_text(encoding="utf-8")
    inputs = verified["function"]["inputs"]
    expect(len(inputs) == 2 and [item["id"] for item in inputs] == ["a", "b"],
           "E_P4_DOMAIN", "POC-1C.A runtime harness supports exactly inputs a,b")
    ranges = verified["input_ranges"]
    a_lo, a_hi = ranges["a"]
    b_lo, b_hi = ranges["b"]

    required_counts = Counter([
        f"addi s0, zero, {a_lo}",
        f"addi s1, zero, {b_lo}",
        f"addi t0, zero, {b_hi + 1}",
        f"addi t0, zero, {a_hi + 1}",
    ])
    for instruction, count in required_counts.items():
        actual = text.count(instruction)
        expect(actual == count, "E_P4_DOMAIN",
               f"runtime harness domain binding mismatch for {instruction!r}: expected {count}, found {actual}")

    cases = expected_case_count(ranges)
    upper, lower = split_lui_addi(cases)
    expect(text.count(f"lui t2, 0x{upper:x}") == 1 and text.count(f"addi t2, t2, {lower}") == 1,
           "E_P4_DOMAIN", "runtime harness case-count check does not match verified domain")

    contract = spec_doc.get("function", {}).get("poc1b_contract", {})
    expect(contract.get("expr") == "a", "E_P4_ORACLE",
           "POC-1C.A harness currently supports the accepted result == a contract only")
    expect(text.count("bne a0, s0, .L_fail") == 1, "E_P4_ORACLE",
           "runtime harness oracle does not uniquely implement result == a")

    contract_trace = []
    if isinstance(contract.get("clause_id"), str):
        contract_trace.append(contract["clause_id"])
    return {
        "input_ranges": {name: [lo, hi] for name, (lo, hi) in ranges.items()},
        "expected_cases": cases,
        "oracle": "result == a",
        "oracle_kind": "accepted-contract-observation",
        "trace": contract_trace,
    }


def base_artifacts(specification_path: Path, specir_path: Path, target_path: Path,
                   asm_path: Path, state_path: Path) -> dict[str, str]:
    artifacts = {
        rel(specification_path): sha256(specification_path),
        rel(specir_path): sha256(specir_path),
        rel(target_path): sha256(target_path),
        rel(asm_path): sha256(asm_path),
        rel(state_path): sha256(state_path),
    }
    for path in POC1C_SOURCE_FILES:
        artifacts[rel(path)] = sha256(path)
    return artifacts


def generate(specification_path: Path, specir_path: Path, target_profile: str,
             build_dir: Path) -> dict[str, Path]:
    spec_doc, specir = load_json(specification_path), load_json(specir_path)
    target = resolve_target_profile(target_profile)
    verified = verify_machine_independent_specir(spec_doc, specir)
    fn = validate_codegen_specir(specir)
    asm, state = RV32ICodeGenerator(fn, target).generate()

    build_dir.mkdir(parents=True, exist_ok=True)
    asm_path = build_dir / f"{fn['name']}.s"
    state_path = build_dir / "backend-state.json"
    target_path = build_dir / "target-config.json"
    evidence_path = build_dir / "evidence.json"
    asm_path.write_text(asm, encoding="utf-8")
    write_json(state_path, state)
    write_json(target_path, target)

    evidence = {
        "schema": "spec2exec.evidence/v0.1",
        "poc": "POC-1C.A",
        "subject": fn["name"],
        "target_profile": target_profile,
        "source_revision": source_revision(),
        "trace_context": collect_trace_ids(verified["function"]),
        "claims": normalized_verifier_claims(verified, specification_path, specir_path) + [{
            "id": "P3.specir_to_rv32i_assembly",
            "status": "TESTED",
            "producer": "rv32i-direct-v0.1",
            "scope": "POC-1C.A accepted add/sub expression subset; semantic preservation is not formally proven",
            "semantic_model": {
                "model": "fixed-width-bitvector-v1",
                "width": 32,
                "type": verified["type"],
                "overflow_behavior": "forbidden within declared input ranges",
            },
            "target_model": {
                "isa": "rv32i",
                "xlen": 32,
                "integer_width_binding": "i32/u32 storage width equals XLEN for this POC",
            },
            "assumptions": ["P1/P2 declared-range obligations hold"],
            "subject_binding": {
                "specir_sha256": sha256(specir_path),
                "target_config_sha256": sha256(target_path),
                "assembly_sha256": sha256(asm_path),
                "backend_state_sha256": sha256(state_path),
            },
            "tcb": [
                f"Python runtime {sys.version.split()[0]}",
                "POC-1C.A target generator",
                "POC-1C target-neutral P1/P2 verifier",
            ],
        }],
        "artifacts": base_artifacts(specification_path, specir_path, target_path, asm_path, state_path),
    }
    normalize_claim_schema(evidence)
    write_json(evidence_path, evidence)
    return {"asm": asm_path, "state": state_path, "target": target_path, "evidence": evidence_path}


def build(specification_path: Path, specir_path: Path, target_profile: str,
          build_dir: Path, harness_path: Path, linker_script: Path,
          assembler: str, linker: str) -> dict[str, Path]:
    paths = generate(specification_path, specir_path, target_profile, build_dir)
    spec_doc, specir = load_json(specification_path), load_json(specir_path)
    verified = verify_machine_independent_specir(spec_doc, specir)
    fn = validate_codegen_specir(specir)
    target = resolve_target_profile(target_profile)
    toolchain = resolve_gnu_toolchain_binding(target)
    runtime_validation = validate_runtime_harness(harness_path, spec_doc, verified)
    runtime_validation["harness_artifact"] = rel(harness_path)
    runtime_validation["linker_script_artifact"] = rel(linker_script)

    obj = build_dir / f"{fn['name']}.o"
    harness_obj = build_dir / "runtime-harness.o"
    elf = build_dir / f"{fn['name']}.elf"

    as_path, ld_path = shutil.which(assembler), shutil.which(linker)
    expect(as_path is not None, "E_TOOLCHAIN", f"assembler not found: {assembler}")
    expect(ld_path is not None, "E_TOOLCHAIN", f"linker not found: {linker}")

    as_generated = [as_path, *toolchain["assembler_flags"], str(paths["asm"]), "-o", str(obj)]
    as_harness = [as_path, *toolchain["assembler_flags"], str(harness_path), "-o", str(harness_obj)]
    link_cmd = [ld_path, *toolchain["linker_flags"], "-T", str(linker_script),
                str(harness_obj), str(obj), "-o", str(elf)]
    subprocess.run(as_generated, check=True)
    subprocess.run(as_harness, check=True)
    subprocess.run(link_cmd, check=True)

    evidence = load_json(paths["evidence"])
    evidence["runtime_validation"] = runtime_validation
    evidence["toolchain_binding"] = toolchain
    evidence["claims"].extend([
        {
            "id": "P4-A.assembly_to_object",
            "status": "TRUSTED",
            "producer": "GNU assembler",
            "assumptions": ["assembler correctly implements declared RV32I/ILP32 options"],
            "tool": {"path": as_path, "version": tool_version(as_path)},
            "invocation": as_generated,
            "subject_binding": {
                "assembly_sha256": sha256(paths["asm"]),
                "object_sha256": sha256(obj),
                "target_config_sha256": sha256(paths["target"]),
            },
        },
        {
            "id": "P4-H.harness_assembly",
            "status": "TRUSTED",
            "producer": "GNU assembler",
            "assumptions": ["runtime harness source implements the mechanically checked domain/oracle"],
            "tool": {"path": as_path, "version": tool_version(as_path)},
            "invocation": as_harness,
            "subject_binding": {
                "harness_source_sha256": sha256(harness_path),
                "harness_object_sha256": sha256(harness_obj),
            },
        },
        {
            "id": "P4-L.object_to_linked_elf",
            "status": "TRUSTED",
            "producer": "GNU linker",
            "assumptions": ["linker and linker script correctly realize the declared ELF32 layout"],
            "tool": {"path": ld_path, "version": tool_version(ld_path)},
            "invocation": link_cmd,
            "subject_binding": {
                "generated_object_sha256": sha256(obj),
                "harness_object_sha256": sha256(harness_obj),
                "linker_script_sha256": sha256(linker_script),
                "linked_elf_sha256": sha256(elf),
            },
        },
    ])
    evidence["artifacts"].update({
        rel(harness_path): sha256(harness_path),
        rel(linker_script): sha256(linker_script),
        rel(obj): sha256(obj),
        rel(harness_obj): sha256(harness_obj),
        rel(elf): sha256(elf),
    })
    normalize_claim_schema(evidence)
    write_json(paths["evidence"], evidence)
    return {**paths, "object": obj, "harness_object": harness_obj, "elf": elf}


def run_qemu(elf: Path, evidence_path: Path, qemu: str) -> None:
    qemu_path = shutil.which(qemu)
    expect(qemu_path is not None, "E_TOOLCHAIN", f"emulator not found: {qemu}")
    command = [qemu_path, "-machine", "virt", "-nographic", "-bios", "none", "-kernel", str(elf)]
    proc = subprocess.run(command, timeout=10, text=True, capture_output=True)
    detail = (proc.stderr or proc.stdout or "").strip()
    expect(proc.returncode == 0, "E_RUNTIME",
           f"QEMU returned {proc.returncode}" + (f": {detail[-500:]}" if detail else ""))

    evidence = load_json(evidence_path)
    runtime_validation = evidence["runtime_validation"]
    harness_key = runtime_validation["harness_artifact"]
    linker_key = runtime_validation["linker_script_artifact"]
    evidence["claims"].append({
        "id": "P4-R.linked_elf_runtime",
        "status": "TESTED_EXHAUSTIVE",
        "producer": "POC-1C assembly runtime harness under QEMU",
        "scope": {
            "kind": "accepted-contract-observation",
            "input_ranges": runtime_validation["input_ranges"],
            "expected_cases": runtime_validation["expected_cases"],
            "oracle": runtime_validation["oracle"],
        },
        "trace": runtime_validation.get("trace", []),
        "assumptions": [
            "QEMU rv32 virt models the exercised RV32I behavior correctly",
            "SiFive test finisher maps PASS to exit 0 and FAIL to non-zero exit",
            "runtime harness case-count assertion completes before PASS",
        ],
        "tool": {"path": qemu_path, "version": tool_version(qemu_path)},
        "invocation": command,
        "subject_binding": {
            "linked_elf_sha256": sha256(elf),
            "harness_source_sha256": evidence["artifacts"][harness_key],
            "linker_script_sha256": evidence["artifacts"][linker_key],
        },
        "tcb": [
            "QEMU rv32 virt machine model",
            "QEMU SiFive test finisher protocol at 0x100000",
            "POC-1C assembly runtime harness",
            "POC-1C linker script",
        ],
        "notes": "This is exhaustive contract observation over the declared domain, not a structural comparison of the generated instruction sequence and not a formal P3 proof.",
    })
    normalize_claim_schema(evidence)
    write_json(evidence_path, evidence)
