# RFC 0009 — Native Target Code Generation

- **Status:** Accepted / Architecture Baseline
- **Scope:** Primary executable-generation path
- **Review status:** Hardened after independent formal/backend hostile review

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

`Target Assembly` means the assembly language of the selected ISA. An assembler may be replaced by an equivalent mature object emitter when that is the better target-toolchain interface.

## Decision

### 1. Native target generation is the primary path

Spec2Exec targets machine semantics directly. Native target code generation is therefore the primary path from verified SpecIR toward an executable artifact.

The target code generator maps verified SpecIR semantics into target-specific instruction semantics and emits target assembly or an equivalent machine-oriented artifact.

C and LLVM remain useful reference and comparison paths, but they are not required architectural intermediates.

### 2. No mandatory `Lowering` architecture stage

The transformation from SpecIR to target instructions necessarily performs lowering in the compiler-theory sense, but `Lowering` is not a mandatory top-level architecture component.

The top-level boundary remains intentionally simple:

```text
Verified SpecIR
      ↓
Target Code Generation
      ↓
Target Assembly
```

A named `TargetIR` or `MachineIR` is optional. Machine-oriented bookkeeping is not optional once the backend needs it.

Even a minimal backend may need explicit state such as:

```text
SpecIR value → physical register / stack slot
available temporary-register pool
live temporary ownership
ABI argument / return locations
labels / symbolic branch targets
```

For POC-scale backends this state may remain an internal, small, testable code-generator data structure rather than a named IR stage.

A backend should promote that bookkeeping into an explicit TargetIR/MachineIR-style representation when one or more of the following become general requirements:

- live values routinely exceed the available physical registers;
- spill/reload placement requires non-local reasoning;
- multi-block control-flow graphs with merge points are supported;
- loops require cross-block liveness reasoning;
- multiple call sites require persistent ABI-aware value placement;
- backend state can no longer be validated cleanly as local tables/rules.

Promotion is driven by demonstrated complexity, not by compiler convention alone.

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

SpecIR remains machine-independent. ISA, ABI, register, calling-convention, stack-frame, instruction-selection, legalization, relocation-facing, and assembly-dialect concerns begin at the target boundary.

### 4. Backend roles

```text
Native target backend
    primary Spec2Exec executable-generation path

C backend
    bootstrap / reference / differential-validation path

LLVM backend
    optional optimization / code-generation / comparison path
```

A target does not need a C compiler to be a valid Spec2Exec target.

### 5. Responsibility split

#### Target Code Generator — Spec2Exec responsibility

The target code generator owns, when required by the supported subset:

- SpecIR operation → target instruction selection;
- legalization when one SpecIR operation requires multiple target instructions;
- immediate/constant legalization and materialization;
- register/value placement policy;
- ABI argument and return-value placement;
- caller/callee-save handling when calls are supported;
- stack-frame and spill-slot construction when stack use is supported;
- control-flow labels and branch selection when control flow is supported;
- syntactically valid target-assembly emission.

A deliberately narrow POC may use fixed or greedy policies, but those policies must be explicit and must not be presented as general register allocation or general ABI support.

#### Assembler — external target-toolchain responsibility

The assembler or equivalent object emitter owns:

- assembly syntax parsing;
- instruction encoding;
- assembly directives;
- symbol-table construction;
- relocation-record generation;
- target object-file emission.

#### Linker — external target-toolchain responsibility

The linker owns:

- cross-object and cross-section symbol resolution;
- relocation application;
- section and memory placement;
- entry-point/image construction;
- final ELF/firmware image generation according to the selected target profile.

#### Hard scope guardrail

The Target Code Generator must not silently grow into an assembler or linker.

Without a future explicit architecture decision it must not implement:

```text
raw opcode / instruction binary encoding
ELF/object-file serialization
relocation encoding/application
cross-object symbol resolution
linking
```

### 6. Minimal target infrastructure and TCB

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

For the primary native path, the assembler and linker are explicit downstream trusted or separately checked components unless Spec2Exec provides independent evidence for those boundaries.

Spec2Exec must not let `Verified SpecIR` imply that assembler, linker, ABI, object-format, or hardware correctness has automatically been proven.

### 7. Semantic-preservation and downstream evidence boundaries

The native semantic-preservation obligation is target-boundary equivalence rather than source-language equivalence:

```text
Accepted Preconditions
        ⇒
SpecIR Observable Semantics
        =
Target ISA Observable Semantics
```

The exact proof/checking mechanism is target-profile dependent. Evidence must remain model-scoped and identify the target assembly artifact to which it is bound.

The native semantic-preservation claim terminates at Target Assembly unless assembler/linker transformations are separately validated.

Executable-level evidence is a distinct downstream claim and must identify its toolchain and artifact bindings. A future evidence chain may therefore distinguish concepts such as:

```text
SpecIR → Target Assembly     semantic-preservation evidence
Target Assembly → Object     assembly/toolchain evidence
Object → Linked ELF          link/image-construction evidence
ELF execution                emulator/runtime behavior evidence
```

No single PASS may collapse these boundaries.

## First native target profile — POC-1C

Independent backend review converged on RV32I as the least incidental-complexity target for the first native experiment.

POC-1C therefore selects this experimental profile:

```text
ISA:            RISC-V RV32I base integer
M extension:    OFF
C extension:    OFF
A extension:    OFF
F/D extensions: OFF
Privileged ISA: outside the semantic target
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

This is a POC target-profile decision, not a restriction embedded into SpecIR. Cortex-M/Thumb remains a strong later target for portability and embedded relevance.

## POC-1C experimental split

### POC-1C.A — Native Pipeline Proof

POC-1C.A answers one question only:

> Can verified SpecIR produce correct native target assembly and an executable artifact without requiring C, LLVM IR, or another high-level-language compiler stage?

It reuses the current bounded-arithmetic semantic core and begins with `safe_add_sub`-class straight-line arithmetic.

Required properties:

```text
Verified SpecIR
      ↓
RV32I Target Code Generator
      ↓
RV32I Assembly
      ↓
unmodified assembler
      ↓
ELF32 object
      ↓
unmodified linker
      ↓
RV32I ELF
      ↓
emulator / execution evidence
```

The code generator must use a minimal register-resource model rather than hard-coded per-example instruction templates. At minimum it should model argument registers, return register, and a temporary-register pool.

POC-1C.A does not require a general register allocator, spilling, control flow, calls, loops, or a named TargetIR/MachineIR.

### POC-1C.B — Native Backend Stress

After POC-1C.A passes, POC-1C.B should deliberately stress the assumptions that made the direct backend small.

Planned stress classes are:

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive call
```

POC-1C.B exists to measure when backend bookkeeping should be promoted into an explicit TargetIR/MachineIR-style representation.

The experiment must not prejudge that result. If the direct representation becomes fragile or non-local, promotion is the intended architectural response rather than a failure to preserve the top-level Spec2Exec pipeline.

## Relationship to POC-1A / POC-1B

POC-1A and POC-1B intentionally used generated C to bootstrap and stress the deterministic preservation/evidence architecture. Those experiments remain valid within their recorded scope.

Their role is now explicitly reference-oriented:

```text
SpecIR → generated C → CBMC / compiler → executable
```

is an experimental reference path, not the required final Spec2Exec architecture.

The C experiments are valuable precisely because they exposed the additional semantic and trusted-computing-base burden introduced by a high-level source-language intermediary.

## Consequences

This decision moves Spec2Exec beyond a specification frontend for conventional compilers. A native backend makes Spec2Exec responsible for target code-generation decisions that a traditional compiler backend would otherwise own.

The architecture accepts that responsibility deliberately while keeping backend-internal machinery proportional to demonstrated complexity.

## Guardrails

- SpecIR must not absorb ISA-specific details merely to simplify a backend.
- Target-specific semantics begin at the Target Code Generation boundary.
- `Lowering` remains a transformation concept, not a mandatory architecture box.
- A named TargetIR/MachineIR is optional; required machine-oriented bookkeeping must still be explicit and testable.
- C, LLVM IR, TargetIR, or MachineIR must not become mandatory stages without an explicit future architecture decision.
- Native backend evidence must distinguish semantic proof/checking from assembler, linker, ABI, object-format, emulator, and hardware assumptions.
- Target Code Generation must not reimplement instruction encoding, object writing, relocation processing, or linking without a separate architecture decision.
- A backend should reuse the lowest trustworthy target infrastructure available rather than require a larger compiler stack by default.
