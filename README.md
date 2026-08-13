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

Spec2Exec explores a specification-centric model:

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

The central question is not whether AI can generate code. It already can. The question is whether manually authored programming-language source code must remain the primary interface between human intent and executable software.

Spec2Exec does **not** claim that this question has already been answered. The project exists to test the hypothesis with explicit semantics, working prototypes, verification evidence, and end-to-end examples.

## Three correctness boundaries

Spec2Exec separates three questions that must not be conflated:

1. **Intent fidelity** — does the accepted specification represent what the human/domain authority actually intends?
2. **Specification / SpecIR correctness** — is the formal representation internally consistent and compliant with declared contracts?
3. **Implementation conformance** — does the executable preserve the verified SpecIR semantics through lowering and compilation?

A deterministic verifier can establish only the properties it actually checks. It cannot generally prove that an incorrect specification matches human intent.

## Architectural principles

1. **Specification first** — specifications, not generated source code, are the primary engineering artifact.
2. **Explicit specification acceptance** — intent fidelity requires accountable human/domain review where the domain requires it.
3. **Semantic preservation** — engineering meaning must survive synthesis and lowering.
4. **AI for synthesis, not authority** — semantic synthesis is untrusted candidate generation; deterministic mechanisms verify named properties.
5. **Explicit uncertainty** — assumptions, unresolved semantics, derived facts, accepted requirements, and verified properties must remain distinguishable.
6. **Explicit contracts** — timing, units, ranges, safety, resources, interfaces, and invariants should be first-class when the domain requires them.
7. **Backend reuse** — reuse LLVM/MLIR and other mature compiler infrastructure instead of rebuilding machine-code backends.
8. **Traceability** — requirement → accepted specification → SpecIR → verification evidence → executable behavior should remain traceable.
9. **Reproducibility** — verified intermediate artifacts should support deterministic builds.
10. **Human inspectability** — SpecIR is machine-oriented, but the system must remain reviewable and debuggable.

## What Spec2Exec is not

- Not an LLM wrapper that emits C/C++/Rust source.
- Not a new human-authored general-purpose programming language.
- Not an attempt to replace LLVM, GCC, linkers, ABIs, loaders, or ISAs.
- Not a claim that programming languages will disappear.
- Not a claim that AI can automatically determine human intent.
- Not a claim that general specification completeness can be automatically proven.
- Not a system in which AI output is accepted without explicit acceptance or deterministic validation appropriate to the property.

## SpecIR

SpecIR is a **formal, machine-oriented intermediate representation** between semantic synthesis and deterministic verification/lowering.

It may have formal syntax and semantics; that is necessary for deterministic processing. The design constraint is different: SpecIR must not become the mandatory manually authored general-purpose source language.

```text
General-purpose source language
    optimized for human → implementation

SpecIR
    optimized for synthesis → verification → lowering
```

## Trust model

```text
Accepted Specification
    ↓
Semantic Synthesis
    ↓
Candidate SpecIR

──── deterministic trust boundary ────

Verification
    ↓
Verified-for-declared-properties SpecIR
    ↓
Lowering
    ↓
Executable
```

**Semantic synthesis is untrusted.** A verifier PASS applies only to named properties under named assumptions.

## Repository status

**Phase 0 — Architecture Definition**

The project is intentionally architecture-first. The current work defines the contracts between specification, human/domain acceptance, semantic synthesis, SpecIR, verification, lowering, and executable generation before implementing the first compiler prototype.

## Repository layout

```text
spec2exec/
├── README.md
├── CONTRIBUTING.md
├── docs/
│   ├── vision.md
│   ├── architecture.md
│   ├── terminology.md
│   ├── design-principles.md
│   ├── non-goals.md
│   └── research-landscape.md
├── rfcs/
│   ├── 0001-spec2exec-architecture.md
│   ├── 0002-specification-model.md
│   ├── 0003-specir.md
│   ├── 0004-verification-model.md
│   └── 0005-trust-intent-fidelity-and-specification-acceptance.md
├── spec/
│   ├── specir/
│   └── schemas/
├── examples/
│   ├── hello/
│   └── embedded-control/
├── prototypes/
└── tests/
```

## Phase 1 proof-of-concept direction

The first implementation deliberately excludes AI so that the deterministic lower half can be tested independently:

```text
Manually Constructed Minimal SpecIR
    ↓
Parser / Loader
    ↓
Deterministic Verifier
    ↓
C or LLVM IR Lowering
    ↓
Existing Compiler Backend
    ↓
Linux ELF Executable
```

AI semantic synthesis is introduced only after this path is independently testable.

The initial examples should progress from:

1. **Hello World** — toolchain plumbing only.
2. **Bounded arithmetic** — types, ranges, pre/postconditions.
3. **State machine** — states and invalid transition rejection.
4. **Thermal motor protection** — units, thresholds, timing, fail-safe behavior, provenance, and unresolved requirements.
5. **Timing-aware embedded model** — timing/resource contracts.
6. **Embedded/control-system example** — broader system integration.

## Research stance

The project treats the following as open questions rather than settled claims:

- Can specification complexity remain lower than equivalent implementation complexity?
- Can SpecIR remain machine-oriented without becoming another mandatory human programming language?
- Can uncertainty and provenance be preserved well enough to prevent AI-derived assumptions from becoming executable truth?
- Can deterministic verification provide useful guarantees without making the specification model impractically restrictive?
- Can requirement-to-runtime traceability remain usable at realistic system scale?

## Name

**Spec2Exec** is the project name. The earlier shorthand **S2E** is intentionally not used because it collides with the established S²E selective symbolic execution project.

## License

License selection is intentionally pending. It should be chosen explicitly before the first public code release.
