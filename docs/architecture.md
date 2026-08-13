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

SpecIR remains machine-independent. ISA, ABI, registers, calling convention, stack conventions, instruction selection/legalization, assembly syntax, relocation-facing behavior, and object-format assumptions begin at Target Code Generation.

```text
MACHINE-INDEPENDENT
Accepted Specification → SpecIR → Deterministic Verification → Verified SpecIR

================ TARGET BOUNDARY ================

TARGET-SPECIFIC
Target Code Generation → Target Assembly → Assembler → Object → Linker → Executable
```

## No mandatory Lowering component

Lowering exists as a transformation concept, but it is not a required top-level architecture component.

For a simple backend, the mapping may be direct:

```text
SpecIR operation
    ↓
Target code-generation rule
    ↓
Target assembly instruction sequence
```

A named TargetIR/MachineIR is optional. Machine-oriented bookkeeping is not. A direct backend may still maintain explicit internal state such as SpecIR-value locations, available temporary registers, ABI argument/return locations, and labels.

That bookkeeping should be promoted into an explicit TargetIR/MachineIR-style representation when backend complexity becomes non-local: general spilling, multi-block CFG merges, loops/cross-block liveness, repeated call sites, or machine state that can no longer be validated cleanly as local rules.

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

## Target Code Generator responsibilities

When required by the supported subset, Target Code Generation owns instruction selection, legalization, constant/immediate materialization, register/value placement, ABI argument/return handling, save/restore rules, stack/spill handling, branch/label generation, and target-assembly syntax emission.

For a POC, fixed or greedy policies are acceptable when explicitly scoped. They must not be presented as general register allocation or general ABI support.

Instruction encoding, object-file serialization, relocation processing, and linking remain responsibilities of the external assembler/object emitter and linker unless a future RFC explicitly changes that boundary.

## Correctness and trust boundaries

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

The native semantic-preservation claim terminates at Target Assembly unless assembler/linker transformations are separately validated.

Assembler, object emission, linking, ABI, emulator/runtime, and hardware behavior remain separate downstream evidence or trust boundaries. Executable-level claims must identify their toolchain and artifact bindings rather than inherit a SpecIR proof automatically.

A conceptual evidence chain may distinguish:

```text
SpecIR → Target Assembly     semantic-preservation evidence
Target Assembly → Object     assembler/toolchain evidence
Object → Linked ELF          link/image-construction evidence
ELF execution                runtime/emulator evidence
```

No single PASS collapses these boundaries.

## First native target profile

POC-1C uses RV32I as the first native architecture experiment:

```text
RISC-V RV32I base integer
no M / C / A / F / D extensions
integer argument/return ABI subset
GNU RISC-V assembly syntax
ELF32 RISC-V object path
```

This is an experiment-specific target profile. It is not encoded into machine-independent SpecIR.

Cortex-M/Thumb remains a later portability target with higher embedded relevance and higher ISA/ABI incidental complexity.

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

See RFC 0009 for the native target-code-generation decision and the POC-1C.A / POC-1C.B split.
