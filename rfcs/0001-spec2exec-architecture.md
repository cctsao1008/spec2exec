# RFC 0001 — Spec2Exec Architecture

- **Status:** Draft
- **Scope:** Foundational architecture

## Summary

Spec2Exec is a specification-centric software development architecture and research hypothesis. It investigates whether specifications can become the primary engineering artifact between human intent and executable software without requiring manually authored general-purpose source code as the mandatory interface.

The primary architecture path is:

```text
Human Intent
    ↓
Draft Specification
    ↓
Semantic Resolution
    ↓
Human / Domain Specification Acceptance
    ↓
Accepted Specification
    ↓
Semantic Synthesis
    ↓
Candidate SpecIR
    ↓
Deterministic Verification
    ↓
Verified SpecIR
    ↓
Target Code Generation
    ↓
Target Assembly
    ↓
Assembler
    ↓
Object
    ↓
Linker
    ↓
Executable / Firmware
```

## Motivation

AI coding tools usually insert AI before a conventional programming language:

```text
Intent → AI → C/Rust/Python → Compiler → Executable
```

This leaves a human-oriented programming language as a mandatory intermediate semantic layer.

Spec2Exec instead investigates whether an accepted specification plus machine-oriented SpecIR can proceed directly toward target-machine semantics.

## Trust model

Spec2Exec separates three distinct correctness questions:

1. **Intent fidelity** — does the accepted specification represent what the human/domain authority actually intends?
2. **Specification / SpecIR correctness** — is the formal representation internally consistent and compliant with declared contracts?
3. **Implementation conformance** — does target code generation preserve verified SpecIR semantics into the executable artifact?

These questions have different authorities. Deterministic verification cannot prove that an incorrect specification matches human intent.

## Decision

The architecture shall:

1. distinguish Intent, Draft Specification, Accepted Specification, SpecIR, and Executable;
2. make unresolved ambiguity and assumptions explicit rather than silently invent requirements;
3. include a human/domain specification acceptance gate where intent fidelity matters;
4. treat AI semantic synthesis as untrusted candidate generation;
5. place deterministic verification before target-specific code generation;
6. distinguish solver-proven, model-checked, checked, tested, measured, estimated, advisory, assumed, and unresolved claims;
7. keep SpecIR machine-independent;
8. use native target code generation as the primary executable-generation path;
9. treat C and LLVM as optional bootstrap/reference/comparison paths rather than mandatory stages;
10. avoid making `Lowering`, TargetIR, MachineIR, instruction selection, or register allocation mandatory top-level architecture components; backends may introduce them internally when justified;
11. retain requirement-to-runtime traceability and provenance;
12. keep assembler/object emission and linking as explicit downstream evidence or trust boundaries.

## Native target path

The machine-independent/target-specific boundary is:

```text
Accepted Specification → SpecIR → Verification → Verified SpecIR

================ TARGET BOUNDARY ================

Target Code Generation → Target Assembly → Assembler → Object → Linker → Executable
```

A full C compiler is not an inherent prerequisite for a Spec2Exec target. Practical target support requires sufficient ISA, ABI, instruction-encoding, object/relocation, assembler-or-equivalent-emitter, and linking information.

## Optional paths

```text
Native target backend
    primary path

C backend
    bootstrap / reference / differential-validation path

LLVM backend
    optional optimization / code-generation / comparison path
```

POC-1A and POC-1B used C intentionally as a reference path. Their evidence remains valid within its recorded scope.

## Non-claim

Spec2Exec does not claim to solve the general intent problem, prove specification completeness, or already prove every native backend transformation. Its goal is to make unresolved semantics, assumptions, authority, target-specific transformations, and verification evidence explicit and auditable.

## Open questions

- What is the minimum semantic core of SpecIR?
- Which properties must be deterministic versus advisory?
- What target profile should be used for the first native assembly backend?
- What is the smallest useful native target code generator?
- How should SpecIR-to-target-ISA semantic preservation be checked?
- When does backend complexity justify an internal TargetIR or MachineIR?
- What is the debug model when no primary human-authored source exists?

See RFC 0009 for the accepted native target-code-generation architecture decision.
