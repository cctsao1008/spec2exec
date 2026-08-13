# Vision

## The problem

Modern software development assumes that programming-language source code is the primary bridge between human intent and executable software. AI changes that assumption.

Programming languages historically solve several human problems: expressing algorithms, managing complexity, constraining mistakes, enabling reuse, and making machine behavior understandable. Once a program has been lowered to a particular ISA, the CPU no longer knows whether the behavior originated in C, Rust, Go, assembly, or another source language.

Spec2Exec asks whether source code must remain the primary human-facing artifact when an AI system can perform semantic synthesis.

## The proposed shift

From:

```text
Requirement → Human-authored source → Compiler → Executable
```

Toward:

```text
Intent
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
Executable
```

## Long-term hypothesis

Programming languages may remain important, but their role may change from the mandatory primary interface for humans to one of several implementation, interoperability, debugging, or legacy representations.

The source of truth may move from source code toward:

- specifications;
- formal semantic representations;
- verification evidence;
- traceability metadata.

## Success criterion

Spec2Exec succeeds only if specification-centric development is demonstrably better for at least some real engineering domains in correctness, traceability, maintainability, portability, or development efficiency. Generating code faster is insufficient.
