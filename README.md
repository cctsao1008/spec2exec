# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec is not another AI coding tool. It is a software development architecture that explores specification as the primary interface between human intent and executable software.

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
Specification
    ↓
Semantic Synthesis
    ↓
SpecIR
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

## Architectural principles

1. **Specification first** — specifications, not generated source code, are the primary engineering artifact.
2. **Semantic preservation** — engineering meaning must survive synthesis and lowering.
3. **AI for synthesis, not authority** — probabilistic systems may propose; deterministic verifiers decide.
4. **Explicit contracts** — timing, units, ranges, safety, resources, interfaces, and invariants should be first-class when the domain requires them.
5. **Backend reuse** — reuse LLVM/MLIR and other mature compiler infrastructure instead of rebuilding machine-code backends.
6. **Traceability** — requirement → SpecIR → verification evidence → executable behavior should remain traceable.
7. **Reproducibility** — verified intermediate artifacts should support deterministic builds.
8. **Human inspectability** — SpecIR is machine-oriented, but the system must remain reviewable and debuggable.

## What Spec2Exec is not

- Not an LLM wrapper that emits C/C++/Rust source.
- Not a new human-oriented programming language.
- Not an attempt to replace LLVM, GCC, linkers, ABIs, loaders, or ISAs.
- Not a claim that programming languages will disappear.
- Not a system in which AI output is accepted without deterministic validation.

## Repository status

**Phase 0 — Architecture Definition**

The project is intentionally architecture-first. The first milestone is to define the contracts between specification, semantic synthesis, SpecIR, verification, lowering, and executable generation before implementing a compiler.

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
│   └── 0004-verification-model.md
├── spec/
│   ├── specir/
│   └── schemas/
├── examples/
│   ├── hello/
│   └── embedded-control/
├── prototypes/
└── tests/
```

## Initial proof-of-concept direction

The first implementation should remain deliberately small:

```text
Specification
    ↓
SpecIR
    ↓
Verifier
    ↓
C or LLVM IR lowering
    ↓
Existing compiler backend
    ↓
Linux ELF executable
```

The initial examples should progress from:

1. Hello World
2. Pure function / arithmetic
3. State machine
4. Explicit constraints and invariants
5. Timing-aware model
6. Embedded/control-system example

## Name

**Spec2Exec** is the project name. The earlier shorthand **S2E** is intentionally not used because it collides with the established S²E selective symbolic execution project.

## License

License selection is intentionally pending. It should be chosen explicitly before the first public code release.
