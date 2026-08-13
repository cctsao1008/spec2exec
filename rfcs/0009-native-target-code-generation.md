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

SpecIR remains machine-independent. Target-specific ISA, ABI, register, calling-convention, legalization, and assembly concerns begin at Target Code Generation.

A Target Profile selects architecture/ISA, core/profile, enabled semantic subset/extensions, ABI subset, assembly dialect, and object model. A Platform Profile carries execution-environment details: bare-metal SoC/board and processor mode, or hosted operating-system and loader/runtime context.

A single ISA may therefore require multiple Target Profiles when ABI or object-format semantics differ across execution environments.

```text
SpecIR semantics != Target Profile != Platform Profile
```

See `docs/target-profiles.md`.

## Backend boundary

The Target Code Generator owns instruction selection, legalization, register/value placement, ABI mapping, and assembly emission for the supported subset. The external assembler owns instruction encoding and object emission; the linker owns relocation/symbol resolution and final image construction.

Without a future RFC, Target Code Generation must not implement instruction binary encoding, object-file serialization, relocation processing, or linking.

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
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

The physical core may implement additional capabilities; they are not automatically part of the Spec2Exec Target Profile.

POC-1C.A initially supports `add` and `sub`. Unsupported operations, including `mul` under this profile, fail closed. Register exhaustion also fails closed. The minimal ABI subset uses `a0`, `a1`, ... for integer inputs, `a0` for the return value, and `ret` for return.

The backend emits machine-readable bookkeeping evidence for target profile, value locations, ABI-fixed locations, temporary-register pool, high-water mark, and spill count.

POC-1C.B later stresses spilling, branch/merge handling, and one non-recursive call.

## POC-1D — Pico 2 Cortex-M33 cross-target validation

POC-1D uses the same RP2350/Pico 2 platform switched to its Arm Cortex-M33 cores.

```text
POC-1C  Pico 2 / RP2350 / Hazard3 RISC-V / RV32I subset
POC-1D  Pico 2 / RP2350 / Cortex-M33 / Armv8-M Mainline
```

Initial POC-1D profile:

```text
Core:           Arm Cortex-M33
ISA/profile:    Armv8-M Mainline
Endianness:     little
ABI subset:     AAPCS integer subset
Floating point: outside initial semantics
TrustZone:      outside initial semantics
Assembly:       GNU Arm syntax
Object model:   ELF32 Arm
```

The CPU architecture changes while the physical development platform remains largely constant. RP2350/Pico 2 board details stay in the Platform Profile rather than SpecIR.

## POC-1E — x86_64 hosted platform matrix

POC-1E adds x86_64 as a third representative ISA family and explicitly validates that hosted operating-system conventions are part of the target boundary rather than hidden behind the ISA name.

Initial matrix:

```text
x86_64 / Linux    SysV AMD64 integer subset      ELF64
x86_64 / Windows  Microsoft x64 integer subset   COFF + PE32+
x86_64 / macOS    Darwin x86_64 integer subset   Mach-O
```

These profiles share the x86_64 ISA but are not interchangeable: ABI, object-format, symbol, linker, loader, and executable-environment assumptions remain explicit.

POC-1E should begin with the same narrow straight-line arithmetic semantics used for the first native validation experiments. Its purpose is to test cross-ISA and cross-hosted-platform preservation, not to implement a general x86 optimizer or complete platform runtime.

The representative architecture matrix becomes:

```text
                           same Verified SpecIR
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
      Hazard3 / RV32I    Cortex-M33 / Armv8-M       x86_64
              │                   │                   │
              ▼                   ▼        ┌──────────┼──────────┐
       RISC-V assembly        Arm assembly  ▼          ▼          ▼
              │                   │       Linux     Windows     macOS
              ▼                   ▼       ELF64     PE/COFF     Mach-O
          Pico 2              Pico 2
```

This is representative architectural coverage rather than complete ISA or OS coverage. A later AArch64/arm64 hosted target may be introduced independently and must not be conflated with x86_64 macOS.

## Guardrails

- SpecIR must not absorb ISA-specific details.
- A named TargetIR/MachineIR remains optional; machine bookkeeping must stay explicit and testable.
- Unsupported operations and resource exhaustion fail closed.
- Native evidence must distinguish semantic checking from assembler, linker, ABI, emulator, operating-system, loader/runtime, and hardware assumptions.
- Reuse mature assembler/linker infrastructure rather than reimplementing it inside Target Code Generation.
