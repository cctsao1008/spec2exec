"""Authority-gated entrypoint for the POC-1C native pipeline.

The existing pipeline module remains the target-generation/runtime substrate.
This wrapper enforces RFC-0011 authority acceptance before any P1/P2/SpecIR
verification or target generation is entered through the supported CLI path,
then binds the authority acceptance record into evidence.json.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import authority
import pipeline as base

ROOT = Path(__file__).resolve().parents[2]
AUTHORITY_SOURCE_FILES = [
    ROOT / "prototypes" / "poc1c" / "authority.py",
    ROOT / "prototypes" / "poc1c" / "pipeline_authority.py",
    ROOT / "spec" / "schemas" / "authority-v0.1.schema.json",
]


def _manifest_path(specification_path: Path) -> Path:
    spec_doc = base.load_json(specification_path)
    acceptance = spec_doc.get("acceptance")
    base.expect(isinstance(acceptance, dict), "E_AUTH_PROVENANCE", "specification acceptance record is required")
    manifest_ref = acceptance.get("authority_manifest")
    base.expect(isinstance(manifest_ref, str) and bool(manifest_ref.strip()),
                "E_AUTH_PROVENANCE", "specification acceptance must bind authority_manifest")
    return (specification_path.resolve().parent / manifest_ref).resolve()


def _evaluate(specification_path: Path, target_profile: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    manifest_path = _manifest_path(specification_path)
    try:
        acceptance = authority.evaluate_authority(specification_path, manifest_path, target_profile)
        bundle = authority.load_authority_bundle(manifest_path)
    except authority.AuthorityError as exc:
        raise base.Poc1CError(str(exc)) from exc
    return acceptance, bundle, manifest_path


def _bind_authority_evidence(paths: dict[str, Path], specification_path: Path,
                             acceptance: dict[str, Any], bundle: dict[str, Any],
                             manifest_path: Path) -> None:
    evidence = base.load_json(paths["evidence"])
    component_hashes = dict(bundle["component_hashes"])
    component_bindings = {
        name: {
            "path": base.rel(bundle["component_paths"][name]),
            "sha256": digest,
        }
        for name, digest in sorted(component_hashes.items())
    }
    authority_binding = {
        "specification_sha256": base.sha256(specification_path),
        "authority_manifest_sha256": base.sha256(manifest_path),
        "authority_components": component_bindings,
        "authority_acceptance_sha256": authority.canonical_json_sha256(acceptance),
    }

    claim = dict(acceptance["evidence_claim"])
    claim.update({
        "subject": evidence.get("subject", "safe_add_sub"),
        "producer": "poc1c-authority-gate-v0.1",
        "source_revision": evidence.get("source_revision", "UNAVAILABLE"),
        "trace": ["REQ-OPT-001-OVF", "REQ-OPT-001-A", "REQ-OPT-001-B"],
        "subject_binding": authority_binding,
        "tcb": [
            "declared POC-1C AuthorityAnchor",
            "repository write-access governance for authority records",
            "Python runtime executing the deterministic authority evaluator",
            "POC-1C authority evaluator implementation",
        ],
    })

    evidence["authority_acceptance"] = acceptance
    evidence["claims"].insert(0, claim)
    evidence["artifacts"][base.rel(manifest_path)] = base.sha256(manifest_path)
    for name, path in bundle["component_paths"].items():
        evidence["artifacts"][base.rel(path)] = bundle["component_hashes"][name]
    for path in AUTHORITY_SOURCE_FILES:
        evidence["artifacts"][base.rel(path)] = base.sha256(path)

    base.normalize_claim_schema(evidence)
    base.write_json(paths["evidence"], evidence)


def generate(specification_path: Path, specir_path: Path, target_profile: str,
             build_dir: Path) -> dict[str, Path]:
    acceptance, bundle, manifest_path = _evaluate(specification_path, target_profile)
    paths = base.generate(specification_path, specir_path, target_profile, build_dir)
    _bind_authority_evidence(paths, specification_path, acceptance, bundle, manifest_path)
    return paths


def build(specification_path: Path, specir_path: Path, target_profile: str,
          build_dir: Path, harness_path: Path, linker_script: Path,
          assembler: str, linker: str) -> dict[str, Path]:
    acceptance, bundle, manifest_path = _evaluate(specification_path, target_profile)
    paths = base.build(
        specification_path, specir_path, target_profile, build_dir,
        harness_path, linker_script, assembler, linker,
    )
    _bind_authority_evidence(paths, specification_path, acceptance, bundle, manifest_path)
    return paths


def run_qemu(elf: Path, evidence_path: Path, qemu: str) -> None:
    base.run_qemu(elf, evidence_path, qemu)


def run_runtime_sensitivity(asm_path: Path, evidence_path: Path, harness_path: Path,
                            linker_script: Path, assembler: str, linker: str,
                            qemu: str) -> None:
    base.run_runtime_sensitivity(
        asm_path, evidence_path, harness_path, linker_script, assembler, linker, qemu,
    )
