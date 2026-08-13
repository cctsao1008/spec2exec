# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec is not another AI coding tool. It is a software development architecture and research hypothesis that explores specification as the primary interface between human intent and executable software.

## Core thesis

Traditional software development is programming-language-centric:

```text
Human Intent
    ↓
Programming Language
    ↓
Source Code
    ↓
Compiler
    ↓
Executable
```

Spec2Exec investigates a specification-centric model:

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
Lowering
    ↓
Compiler Backend
    ↓
Executable
```

The question is not whether AI can generate code. The question is whether manually authored programming-language source must remain the primary interface between human intent and executable software.

Spec2Exec does **not** claim that this has already been proven. The project exists to test the hypothesis through explicit semantics, working prototypes, evidence, and end-to-end examples.

## Correctness boundaries

Spec2Exec separates three questions:

1. **Intent fidelity** — does the accepted specification represent what the human/domain authority intends?
2. **Specification / SpecIR correctness** — is the formal representation internally consistent and compliant with declared contracts?
3. **Implementation conformance** — does the executable preserve the relevant SpecIR semantics through lowering and compilation?

No verifier PASS is allowed to silently collapse these into one claim.

## Architectural principles

1. **Specification first** — accepted specifications, not generated source code, are the primary engineering artifact.
2. **Explicit specification acceptance** — intent fidelity requires accountable human/domain acceptance where appropriate.
3. **Semantic preservation** — each transformation boundary must identify what semantics it claims to preserve.
4. **AI for synthesis, not authority** — semantic synthesis is untrusted candidate generation.
5. **Explicit uncertainty and evidence** — assumptions, unresolved semantics, accepted requirements, checked properties, and trusted components remain distinguishable.
6. **Explicit contracts** — timing, units, ranges, safety, resources, interfaces, and invariants become first-class when a domain requires them.
7. **Backend reuse** — reuse mature compiler infrastructure instead of rebuilding machine-code backends.
8. **Traceability** — requirement → accepted specification → SpecIR → evidence → executable behavior should remain traceable.
9. **Reproducibility** — verified/intermediate artifacts should support deterministic, repeatable builds where practical.
10. **Human inspectability** — SpecIR is machine-oriented, but the system must remain reviewable and debuggable.

## What Spec2Exec is not

- Not an LLM wrapper that emits C/C++/Rust source.
- Not a new mandatory human-authored general-purpose programming language.
- Not an attempt to replace LLVM, GCC, linkers, ABIs, loaders, or ISAs.
- Not a claim that programming languages will disappear.
- Not a claim that AI can automatically determine human intent.
- Not a claim that general specification completeness can be automatically proven.
- Not a claim that every transformation is already formally verified.

## SpecIR

SpecIR is a **formal, machine-oriented intermediate representation** between semantic synthesis and deterministic verification/lowering.

It may have formal syntax and semantics. The design constraint is that it must not become the mandatory manually authored general-purpose source language.

```text
General-purpose source language
    optimized for human → implementation

SpecIR
    optimized for synthesis → verification → lowering
```

## Trust and evidence model

**Semantic synthesis is untrusted.** Human/domain authorities accept intent-bearing specifications. Deterministic systems verify only the formal properties they actually support. Lowering and compiler stages carry separate semantic-preservation obligations.

Evidence is property-oriented rather than a single undifferentiated PASS. See RFC 0005 and RFC 0006.

## Project status

**Phase 1 — Minimal SpecIR and Deterministic Pipeline**

Phase 0 established the initial architecture, trust boundaries, specification model, SpecIR direction, verification model, and semantic-preservation/evidence model.

POC-0 now provides the first working deterministic path without AI:

```text
Accepted Hello Specification
    ↓
Experimental SpecIR v0
    ↓
Deterministic Verifier
    ↓
C Lowering
    ↓
Host C Compiler
    ↓
Executable
    ↓
Runtime Check
```

## Run POC-0

Requirements:

- Python 3
- `make`
- a host C compiler available as `cc`, `gcc`, or `clang`

From the repository root:

```bash
make test
make poc0
```

POC-0 currently uses only the Python standard library and the host C toolchain.

## Current POC sequence

```text
POC-0  Hello / deterministic plumbing
POC-1  Bounded arithmetic / contracts
POC-2  State machine / behavioral invariants
POC-3  Thermal motor protection / units, timing, safety, provenance
```

AI semantic synthesis is intentionally deferred until the deterministic lower half is independently testable.

## Key documents

```text
docs/architecture.md
rfcs/0001-spec2exec-architecture.md
rfcs/0002-specification-model.md
rfcs/0003-specir.md
rfcs/0004-verification-model.md
rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md
rfcs/0006-semantic-preservation-and-evidence-model.md
docs/phase1-plan.md
```

## License

License selection remains intentionally pending before a public code release is declared stable or reusable.
