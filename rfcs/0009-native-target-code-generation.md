# RFC 0009 — Native Target Code Generation

- **Status:** Accepted / Architecture Baseline
- **Scope:** Primary executable-generation path

## Summary

Spec2Exec shall not require a human-oriented programming language or a full C/C++ compiler stack as a mandatory stage between verified SpecIR and executable software.

The primary architecture path is:

```text
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

`Target Assembly` means the assembly language of the selected ISA. An assembler may be replaced by an equivalent object emitter when that is the better target toolchain interface.

## Decision

### 1. Native target generation is the primary path

Spec2Exec targets machine semantics directly. The architecture therefore treats native target code generation as the primary path from verified SpecIR toward an executable artifact.

The target code generator is responsible for mapping verified SpecIR semantics into target-specific instruction semantics and emitting target assembly or an equivalent machine-oriented artifact.

### 2. No mandatory `Lowering` architecture stage

The transformation from SpecIR to target instructions necessarily performs lowering in the compiler-theory sense, but `Lowering` is not a mandatory top-level architecture component.

A target backend may internally use `TargetIR`, `MachineIR`, instruction selection, register allocation, stack-frame construction, or target-specific optimization when engineering evidence shows they are useful. These are backend implementation techniques, not required Spec2Exec architectural stages.

The top-level boundary is intentionally simpler:

```text
Verified SpecIR
      ↓
Target Code Generation
      ↓
Target Assembly
```

### 3. Machine-independent / target-specific boundary

```text
          MACHINE-INDEPENDENT
────────────────────────────────────
Accepted Specification
        ↓
      SpecIR
        ↓
Deterministic Verification
        ↓
   Verified SpecIR

════════════ TARGET BOUNDARY ════════════

        ↓
Target Code Generation
        ↓
Target Assembly
────────────────────────────────────
            TARGET-SPECIFIC
        ↓
Assembler / Object Emitter
        ↓
Object
        ↓
Linker
        ↓
Executable / Firmware
```

SpecIR remains machine-independent. ISA, ABI, register, calling-convention, instruction-encoding, relocation, and target object-format concerns begin at the target boundary.

### 4. C and LLVM are optional paths

C and LLVM remain useful, but they are not mandatory architectural intermediates.

```text
Native target backend
    primary Spec2Exec executable-generation path

C backend
    bootstrap / reference / differential-validation path

LLVM backend
    optional optimization / code-generation / comparison path
```

A target does not need a C compiler to be a valid Spec2Exec target.

### 5. Minimal target infrastructure

A new executable target must ultimately define instruction semantics and encoding. Practical target support therefore requires enough information and tooling for:

```text
ISA semantics and instruction encoding
ABI / calling convention when applicable
memory / register conventions required by the target profile
object and relocation model when object linking is used
assembler or equivalent object emitter
linker / image construction when required
```

A full high-level-language compiler is not an inherent prerequisite.

### 6. Semantic-preservation obligation

The long-term native preservation obligation is target-boundary equivalence rather than source-language equivalence:

```text
Accepted Preconditions
        ⇒
SpecIR Observable Semantics
        =
Target ISA Observable Semantics
```

The exact proof/checking mechanism is target-profile dependent. Evidence must remain model-scoped and identify the target artifact to which it is bound.

Assembler/object emission and linking remain explicit transformation boundaries. Their correctness must not be silently implied by a SpecIR-level proof.

## Relationship to POC-1A / POC-1B

POC-1A and POC-1B intentionally used generated C to bootstrap and stress the deterministic preservation/evidence architecture. Those experiments remain valid within their recorded scope.

Their role is now explicitly historical/reference-oriented:

```text
SpecIR → generated C → CBMC / compiler → executable
```

is an experimental reference path, not the required final Spec2Exec architecture.

The C experiments are valuable precisely because they exposed the additional semantic and trusted-computing-base burden introduced by a high-level source-language intermediary.

## Consequences

This decision moves Spec2Exec beyond a specification frontend for conventional compilers. A native backend makes Spec2Exec responsible for target code-generation decisions that a traditional compiler backend would otherwise own.

The architecture accepts that responsibility deliberately, while keeping backend-internal machinery optional until concrete complexity requires it.

## Guardrails

- SpecIR must not absorb ISA-specific details merely to simplify a backend.
- Target-specific semantics begin at the target-code-generation boundary.
- C, LLVM IR, TargetIR, or MachineIR must not become mandatory stages without an explicit future architecture decision.
- Native backend evidence must distinguish semantic proof/checking from assembler, linker, ABI, object-format, and hardware assumptions.
- A backend should reuse the lowest trustworthy target infrastructure available rather than require a larger compiler stack by default.
