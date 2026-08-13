# Architecture

## Primary pipeline

```text
Human Intent
    ↓
Draft Specification
    ↓
Semantic Resolution
    ↓
Human / Domain Specification Gate
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

The primary Spec2Exec path targets machine semantics directly. C, Rust, LLVM IR, and similar representations are optional paths rather than mandatory architecture stages.

## Target boundary

SpecIR remains machine-independent. ISA, ABI, registers, calling convention, instruction encoding, relocation, and object-format concerns begin at Target Code Generation.

```text
MACHINE-INDEPENDENT
Accepted Specification → SpecIR → Deterministic Verification → Verified SpecIR

================ TARGET BOUNDARY ================

TARGET-SPECIFIC
Target Code Generation → Target Assembly → Assembler → Object → Linker → Executable
```

## No mandatory Lowering component

Lowering exists as a transformation concept, but it is not a required top-level architecture component. A target backend may internally introduce TargetIR, MachineIR, instruction selection, register allocation, stack-frame construction, or target-specific optimization when concrete implementation complexity justifies them.

For a simple backend, the mapping may be direct:

```text
SpecIR operation
    ↓
Target code-generation rule
    ↓
Target assembly instruction sequence
```

## Backend roles

```text
Native target backend
    primary executable-generation path

C backend
    bootstrap / reference / differential-validation path

LLVM backend
    optional optimization / code-generation / comparison path
```

POC-1A and POC-1B used the C path intentionally. Their evidence remains valid within its declared scope, but C is not a required stage of the final architecture.

## Correctness boundaries

Spec2Exec separates three questions:

1. Intent fidelity.
2. Specification / SpecIR correctness.
3. Implementation conformance.

For the native path, the long-term implementation-conformance obligation is:

```text
Accepted Preconditions
    ⇒
SpecIR Observable Semantics
    =
Target ISA Observable Semantics
```

Assembler, object emission, linking, ABI, and hardware behavior remain separate downstream evidence or trust boundaries.

## Traceability

```text
Executable behavior
    ↑
Object / linked artifact
    ↑
Target assembly / target evidence
    ↑
Verified SpecIR
    ↑
Accepted specification clause
    ↑
Requirement / decision / assumption
```

Traceability does not require one-to-one structural identity.

See RFC 0009 for the native target-code-generation decision.
