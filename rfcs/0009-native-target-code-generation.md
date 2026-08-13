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

SpecIR remains machine-independent. Target-specific ISA, ABI, register, calling-convention, legalization, assembly, object, loader, and runtime concerns begin at Target Code Generation or later target-toolchain boundaries.

A concrete target configuration is composed from three dimensions:

```text
ISA Profile
    architecture / ISA / core profile / enabled features

Execution Profile
    OS or bare-metal environment
    ABI / calling convention
    assembly dialect
    object / executable model
    loader / runtime conventions

Platform Profile (optional)
    SoC / board / machine identity
    processor mode
    memory map / startup / image layout
    firmware packaging / signing where applicable
```

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
```

This decomposition prevents one operating system, ABI, object format, or board from becoming an implicit property of an ISA or of SpecIR.

Not every ISA × OS combination is meaningful. A combination is valid only when its ISA, ABI, object/executable model, toolchain, runtime, and platform assumptions are defined.

See `docs/target-profiles.md`.

## Architecture coverage goal

Spec2Exec is intended to be implementable across major CPU ISA families and major execution environments rather than being architecturally tied to a finite POC target list.

Initial architecture families include:

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
    Android
    bare metal
    selected RTOS profiles
```

Additional valid ISA/OS/platform combinations may be introduced without changing machine-independent SpecIR or the primary pipeline.

This is an extensibility requirement, not a requirement to implement every Cartesian-product pair before the architecture is useful.

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

## POC-1C — Pico 2 Hazard3 / RV32I subset

The first native backend uses the Hazard3 RISC-V cores in RP2350 on Raspberry Pi Pico 2 while deliberately constraining Spec2Exec code generation to the RV32I base-integer subset.

```text
Hardware:       Raspberry Pi Pico 2 / RP2350
Core:           Hazard3 RISC-V
ISA subset:     RV32I
M/C/A/F/D:      OFF
Hazard3 custom: outside initial semantics
Execution:      bare metal
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

The physical core may implement additional capabilities; they are not automatically part of the Spec2Exec ISA Profile.

POC-1C.A initially supports `add` and `sub`. Unsupported operations, including `mul` under this profile, fail closed. Register exhaustion also fails closed. The minimal ABI subset uses `a0`, `a1`, ... for integer inputs, `a0` for the return value, and `ret` for return.

The backend emits machine-readable bookkeeping evidence for target configuration, value locations, ABI-fixed locations, temporary-register pool, high-water mark, and spill count.

POC-1C.B later stresses spilling, branch/merge handling, and one non-recursive call.

## POC-1D — Pico 2 Cortex-M33 cross-target validation

POC-1D uses the same RP2350/Pico 2 platform switched to its Arm Cortex-M33 cores.

```text
POC-1C  Pico 2 / RP2350 / Hazard3 RISC-V / RV32I subset
POC-1D  Pico 2 / RP2350 / Cortex-M33 / Armv8-M Mainline
```

Initial POC-1D target configuration:

```text
Core:           Arm Cortex-M33
ISA/profile:    Armv8-M Mainline
Endianness:     little
Execution:      bare metal
ABI subset:     AAPCS integer subset
Floating point: outside initial semantics
TrustZone:      outside initial semantics
Assembly:       GNU Arm syntax
Object model:   ELF32 Arm
```

The CPU architecture changes while the physical development platform remains largely constant.

## POC-1E — Hosted ISA / OS expansion

POC-1E begins hosted target validation using composable ISA and Execution Profiles rather than tying a desktop OS to one ISA.

Initial validation configurations:

```text
x86_64 + Linux
x86_64 + Windows
AArch64 + Linux
AArch64 + macOS
```

Follow-on valid configurations should include, when practical:

```text
AArch64 + Windows
AArch64 + Android
RV64 + Linux
```

Hosted portability therefore tests two independent questions:

```text
same SpecIR across different ISA families
same ISA family across different execution environments
```

The purpose is not to build all hosted backends at once. The purpose is to ensure the architecture does not contain assumptions that prevent major ISA or operating-system families from being implemented.

## Guardrails

- SpecIR must not absorb ISA-, OS-, ABI-, object-format-, or board-specific details.
- ISA Profile, Execution Profile, and Platform Profile remain explicit target dimensions.
- A named TargetIR/MachineIR remains optional; machine bookkeeping must stay explicit and testable.
- Unsupported operations, incompatible target-profile combinations, and resource exhaustion fail closed.
- Native evidence must distinguish semantic checking from assembler, linker, ABI, emulator, operating-system, loader/runtime, signing/packaging, and hardware assumptions.
- Reuse mature assembler/linker and platform tooling rather than reimplementing it inside Target Code Generation.
