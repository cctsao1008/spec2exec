# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **Next architecture experiment:** POC-1C.A — Pico 2 Hazard3 / RV32I Native Pipeline Validation
- **Following architecture stress experiment:** POC-1C.B — Hazard3 Native Backend Stress
- **Later portability experiment:** POC-1D — Pico 2 Cortex-M33 Cross-Target Generation
- **Next semantic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Adversarial Semantic Resolution

## Primary architecture

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

C and LLVM remain optional reference/comparison paths.

## POC-1C Target Profile — Pico 2 Hazard3 / RV32I subset

The first native backend targets the Hazard3 RISC-V cores in RP2350 on Raspberry Pi Pico 2 while deliberately constraining generated semantics to RV32I base integer.

```text
Hardware:       Raspberry Pi Pico 2 / RP2350
Core:           Hazard3 RISC-V
ISA subset:     RV32I
M/C/A/F/D:      OFF
Privileged ISA: outside the semantic target
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

The physical Hazard3 core may implement more than this profile; those extra capabilities are intentionally outside POC-1C.

## POC-1C.A — Native Pipeline Validation

Initial scope is straight-line bounded integer expressions such as `safe_add_sub`.

```text
Verified SpecIR
      ↓
Hazard3/RV32I Target Code Generator
      ↓
RV32I Assembly
      ↓
Assembler
      ↓
ELF32 Object
      ↓
Linker
      ↓
RV32I ELF
      ↓
Emulator and/or Pico 2 hardware evidence
```

Initial operation whitelist:

```text
add
sub
```

`mul` and every other unsupported operation fail closed. Register exhaustion also fails closed; POC-1C.A does not silently spill or reuse live registers.

The initial ABI subset is intentionally narrow:

```text
integer inputs  → a0, a1, ...
integer return  → a0
return          → ret
```

The backend uses a bounded temporary-register pool and emits machine-readable bookkeeping evidence containing target-profile identity, value→location mapping, ABI-fixed locations, temporary-register pool, high-water mark, and spill count.

Evidence boundaries remain separate:

```text
P3    SpecIR → RV32I assembly
P4-A  RV32I assembly → ELF32 object
P4-L  object → linked ELF
P4-R  linked ELF → runtime/hardware observation
```

Runtime, emulator, or hardware agreement does not discharge P3.

## POC-1C.B — Hazard3 Native Backend Stress

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive function call
```

These cases test when local machine bookkeeping becomes too complex and should be promoted into an explicit TargetIR/MachineIR-style representation.

## POC-1D — Pico 2 Cortex-M33 Cross-Target Generation

After the Hazard3 backend is validated, the same verified SpecIR is generated for the Arm Cortex-M33 cores in the same RP2350/Pico 2 platform.

```text
POC-1C  Pico 2 / RP2350 / Hazard3 RISC-V / RV32I subset
POC-1D  Pico 2 / RP2350 / Cortex-M33 / Armv8-M Mainline
```

The initial Cortex-M33 profile keeps floating-point, TrustZone/security-state behavior, DSP-specific operations, and other target-specific features outside the experiment unless explicitly enabled later.

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

This deliberately changes CPU architecture while keeping the physical development platform largely constant. Target semantics remain in Target Profiles; RP2350/Pico 2 board and memory/image details remain in the Platform Profile.

See `docs/target-profiles.md` and RFC 0009.

## POC-2 — State Machine

POC-2 remains the next semantic-complexity experiment. It introduces persistent finite-state behavior without simultaneously adding timing or hardware semantics.

## POC-3 — Thermal Motor Protection

POC-3 remains the first domain-significant embedded/control experiment.

## A0 — Semantic Resolution

A0 remains independent from executable generation.
