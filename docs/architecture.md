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

SpecIR remains machine-independent. Target-specific concerns begin at Target Code Generation or later target-toolchain boundaries.

A concrete target configuration is composed from:

```text
ISA Profile
    architecture / ISA / enabled features

Execution Profile
    OS or bare-metal environment
    ABI / calling convention
    assembly dialect
    object / executable model

Platform Profile (optional)
    SoC / board / machine-specific layout and startup conventions
```

A separate Validation Binding records the concrete CPU core, board, emulator, or host used to gather implementation evidence.

```text
SpecIR semantics
    != ISA Profile
    != Execution Profile
    != Platform Profile
    != Validation Binding
```

A CPU core is not identical to an ISA, and a development board is not an architectural target merely because it is used for validation.

## Architecture coverage goal

Current target families are:

```text
ISA families
    x86_64
    AArch64 / Arm64
    RISC-V RV32 / RV64
    Arm M-profile

Execution environments
    Linux
    Windows
    macOS
    bare metal
```

Android and generic RTOS coverage are outside the current implementation roadmap.

## Validation strategy

The initial embedded hardware validation uses RP2350/Pico 2 because it provides two different CPU-core families on the same physical platform:

```text
RV32I / bare metal
    validated on Hazard3

Armv8-M Mainline / bare metal
    validated on Cortex-M33

Hazard3 and Cortex-M33
    both available in RP2350 / Pico 2
```

Pico 2 is validation hardware, not an architectural target. Replacing it with another compatible platform must not require redefining machine-independent SpecIR.

## No mandatory Lowering component

Lowering exists as a transformation concept, but it is not a required top-level architecture component.

A named TargetIR/MachineIR is optional. Machine-oriented bookkeeping is not. A direct backend may maintain explicit internal state such as SpecIR-value locations, temporary registers, ABI locations, and labels.

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

Instruction encoding, object-file serialization, relocation processing, and linking remain responsibilities of the external assembler/object emitter and linker unless a future RFC explicitly changes that boundary.

## Correctness and trust boundaries

Spec2Exec separates intent fidelity, specification/SpecIR correctness, and implementation conformance.

For the native path, the long-term implementation-conformance obligation is:

```text
Accepted Preconditions
    ⇒
SpecIR Observable Semantics
    =
Target ISA Observable Semantics
```

The native semantic-preservation claim terminates at Target Assembly unless downstream transformations are separately validated.

```text
SpecIR → Target Assembly     semantic-preservation evidence
Target Assembly → Object     assembler/toolchain evidence
Object → Linked Artifact     link/image-construction evidence
Artifact execution           runtime/emulator/hardware evidence
```

No single PASS collapses these boundaries.

See RFC 0009 and `docs/target-profiles.md` for the current target architecture and validation model.
