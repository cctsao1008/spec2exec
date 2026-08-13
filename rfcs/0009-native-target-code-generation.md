# RFC 0009 — Native Target Code Generation

- **Status:** Accepted / Architecture Baseline
- **Scope:** Primary executable-generation path
- **Review status:** Closure review complete; no architecture blockers

## Primary path

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

C and LLVM remain optional reference/comparison paths. `Lowering` is a transformation concept, not a mandatory top-level component.

## Target boundary

SpecIR remains machine-independent. A concrete architectural target is composed from:

```text
ISA Profile
    architecture / ISA / enabled features

Execution Profile
    OS or bare-metal environment
    ABI / calling convention
    assembly dialect
    object / executable model
    loader / runtime conventions

Platform Profile (optional)
    SoC / board / machine identity
    memory map / startup / image layout
```

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
```

A separate **Validation Binding** identifies the concrete CPU core, SoC, board, emulator, or host used to gather evidence for a target configuration.

```text
Target Configuration != Validation Binding
```

A CPU core is also not identical to an ISA. Hazard3 is a concrete RISC-V core used to validate an RV32I subset. Cortex-M33 is a concrete Arm core used to validate an Armv8-M Mainline target.

## Architecture coverage goal

Current architecture families are:

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

Android and generic RTOS coverage are intentionally outside the current implementation roadmap. Additional environments may be introduced later only through explicit target decisions.

The goal is extensibility across valid target configurations, not implementation of every ISA × OS Cartesian-product pair.

## Backend boundary

The Target Code Generator owns instruction selection, legalization, register/value placement, ABI mapping, and assembly emission for the supported subset. The external assembler owns instruction encoding and object emission; the linker owns relocation/symbol resolution and final image construction.

Without a future RFC, Target Code Generation must not implement instruction binary encoding, object-file serialization, relocation processing, or linking.

Reusable backend structure should separate ISA-dependent instruction semantics from Execution-Profile-dependent ABI/object/runtime conventions when that separation is technically meaningful.

## Evidence boundaries

```text
P3    SpecIR → Target Assembly
P4-A  Target Assembly → Object
P4-L  Object → Linked Executable
P4-R  Linked Executable → Runtime Observation
```

No single PASS may collapse these boundaries. Runtime or hardware agreement does not discharge P3.

## POC-1C — RV32I bare-metal native validation

Architectural target:

```text
ISA:            RISC-V RV32I
M/C/A/F/D:      OFF
Execution:      bare metal
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

Initial validation binding:

```text
CPU core:       Hazard3 RISC-V
SoC:            RP2350
Board:          Raspberry Pi Pico 2
```

The physical Hazard3 core may implement more capabilities than the selected RV32I subset. Those capabilities are not automatically part of the Spec2Exec target semantics.

POC-1C.A initially supports `add` and `sub`. Unsupported operations, including `mul` under this profile, fail closed. Register exhaustion also fails closed. The backend emits machine-readable bookkeeping evidence for target configuration, value locations, ABI-fixed locations, temporary-register pool, high-water mark, and spill count.

POC-1C.B later stresses spilling, branch/merge handling, and one non-recursive call.

## POC-1D — Armv8-M Mainline bare-metal cross-target validation

Architectural target:

```text
ISA/profile:    Armv8-M Mainline
Execution:      bare metal
ABI subset:     AAPCS integer subset
Floating point: outside initial semantics
TrustZone:      outside initial semantics
Assembly:       GNU Arm syntax
Object model:   ELF32 Arm
```

Initial validation binding:

```text
CPU core:       Arm Cortex-M33
SoC:            RP2350
Board:          Raspberry Pi Pico 2
```

Using the same RP2350/Pico 2 platform is a validation strategy that reduces unrelated hardware variation while changing CPU architecture. Pico 2 is not an architectural target.

## POC-1E — Hosted ISA / OS expansion

Initial validation configurations:

```text
x86_64 + Linux
x86_64 + Windows
AArch64 + Linux
AArch64 + macOS
```

Follow-on valid configurations, when practical:

```text
AArch64 + Windows
RV64 + Linux
```

Hosted portability tests both the same SpecIR across different ISA families and the same ISA family across different execution environments.

## Guardrails

- SpecIR must not absorb ISA-, OS-, ABI-, object-format-, CPU-core-, or board-specific details.
- ISA Profile, Execution Profile, Platform Profile, and Validation Binding remain distinct concepts.
- A named TargetIR/MachineIR remains optional; machine bookkeeping must stay explicit and testable.
- Unsupported operations, incompatible target-profile combinations, and resource exhaustion fail closed.
- Native evidence must distinguish semantic checking from assembler, linker, ABI, emulator, operating-system, loader/runtime, platform, and hardware assumptions.
- Reuse mature assembler/linker and platform tooling rather than reimplementing it inside Target Code Generation.
