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

A Target Profile selects architecture/ISA, core/profile, enabled semantic subset/extensions, ABI subset, assembly dialect, and object model. An optional Platform Profile carries SoC/board details, processor mode, memory map, startup/image conventions, and linker layout.

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

The intended portability experiment is:

```text
                     same Verified SpecIR
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
       Hazard3 / RV32I        Cortex-M33 / Armv8-M
                 │                     │
                 ▼                     ▼
          RISC-V assembly          Arm assembly
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    same RP2350 / Pico 2
```

The CPU architecture changes while the physical development platform remains largely constant. RP2350/Pico 2 board details stay in the Platform Profile rather than SpecIR.

## Guardrails

- SpecIR must not absorb ISA-specific details.
- A named TargetIR/MachineIR remains optional; machine bookkeeping must stay explicit and testable.
- Unsupported operations and resource exhaustion fail closed.
- Native evidence must distinguish semantic checking from assembler, linker, ABI, emulator, and hardware assumptions.
- Reuse mature assembler/linker infrastructure rather than reimplementing it inside Target Code Generation.
