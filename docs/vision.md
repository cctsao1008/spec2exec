# Vision

## The problem

Modern software development assumes that programming-language source code is the primary bridge between human intent and executable software. AI changes that assumption.

Programming languages historically solve several human problems: expressing algorithms, managing complexity, constraining mistakes, enabling reuse, and making machine behavior understandable. Once a program has become target machine code, the processor no longer knows whether the behavior originated in C, Rust, assembly, or another source representation.

Spec2Exec asks whether source code must remain the primary human-facing artifact when semantic synthesis and deterministic verification can operate on a specification-oriented formal representation.

## The proposed shift

From:

```text
Requirement → Human-authored source → Compiler → Executable
```

Toward:

```text
Intent
  ↓
Accepted Specification
  ↓
SpecIR
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

C, LLVM IR, and other programming/compiler representations may remain useful as reference, interoperability, debugging, or comparison paths, but they are not mandatory stages of the primary architecture.

## Machine independence

SpecIR remains machine-independent. Target-specific semantics enter through a selected Target Profile after verification.

This makes a long-term cross-target experiment possible:

```text
same Verified SpecIR
        │
        ├── RV32I target
        └── Cortex-M target
```

SoC/board-specific layout remains a separate Platform Profile rather than part of SpecIR.

## Long-term hypothesis

Programming languages may remain important, but their role may change from the mandatory primary interface for humans to one of several implementation, interoperability, debugging, or legacy representations.

The source of truth may move from source code toward accepted specifications, formal semantic representations, verification evidence, and traceability metadata.

## Success criterion

Spec2Exec succeeds only if specification-centric development is demonstrably better for at least some real engineering domains in correctness, traceability, maintainability, portability, or development efficiency. Generating code faster is insufficient.
