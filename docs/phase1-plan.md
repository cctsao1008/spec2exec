# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **POC-1C.A:** RV32I native/emulator baseline complete; physical hardware validation pending
- **Next architecture experiment:** POC-1C.B — RV32 Backend Complexity
- **Later portability experiment:** POC-1D — Armv8-M Mainline Bare-Metal Cross-Target Generation
- **Later hosted portability experiment:** POC-1E — Hosted ISA / OS Expansion
- **Next semantic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Semantic Resolution

## Target model

A Spec2Exec architectural target is defined by its ISA and execution semantics. The CPU core, board, emulator, or host used to validate that target are recorded separately.

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
Validation Binding    = CPU core + board, emulator, or host used for evidence
```

## POC-1C — RV32I Bare Metal

```text
ISA:            RV32I
Execution:      bare metal
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

### POC-1C.A — Native Pipeline Validation

The first native implementation baseline is complete in CI.

```text
Machine-independent SpecIR
        ↓
RV32I Target Code Generator
        ↓
RV32I assembly
        ↓
GNU assembler
        ↓
ELF32 object
        ↓
GNU linker
        ↓
RV32I ELF
        ↓
QEMU rv32 virt
        ↓
40,401 exhaustive runtime cases
```

Initial scope remains straight-line `add` and `sub`. Unsupported operations, unsupported ABI shapes, machine-specific fields in SpecIR, and temporary-register exhaustion fail closed. The backend uses a bounded temporary-register pool and emits machine-readable bookkeeping evidence.

Successful baseline evidence:

```text
P1/P2  specification / SpecIR obligations       CHECKED
P3     SpecIR → RV32I assembly                  TESTED
P4-A   RV32I assembly → ELF32 object            TRUSTED
P4-L   object → linked RV32I ELF                TRUSTED
P4-R   linked ELF → runtime observation         TESTED_EXHAUSTIVE
```

The completed CI validation binding is:

```text
emulator: qemu-system-riscv32
machine:  virt
```

Planned physical hardware validation remains:

```text
CPU core: Hazard3 RISC-V
SoC:      RP2350
board:    Raspberry Pi Pico 2
```

Pico 2 is validation hardware, not the architectural target. See `docs/poc1c-results.md` for tool versions, artifact hashes, and exact evidence boundaries.

### POC-1C.B — RV32 Backend Complexity

POC-1C.B is the next architecture/backend experiment after the 1C.A baseline.

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive call
```

These experiments determine whether local backend bookkeeping remains adequate or should be promoted into an explicit TargetIR/MachineIR-style representation.

## POC-1D — Armv8-M Mainline Bare Metal

```text
ISA/profile:    Armv8-M Mainline
Execution:      bare metal
ABI subset:     AAPCS integer subset
Assembly:       GNU Arm syntax
Object model:   ELF32 Arm
```

The planned initial hardware validation binding uses Cortex-M33 cores in RP2350/Pico 2. Reusing the board reduces unrelated hardware variation while changing CPU architecture; it does not make Pico 2 part of the target definition.

## POC-1E — Hosted ISA / OS Expansion

Initial configurations:

```text
x86_64 + Linux
x86_64 + Windows
AArch64 + Linux
AArch64 + macOS
```

Follow-on configurations, when practical:

```text
AArch64 + Windows
RV64 + Linux
```

Current architecture coverage:

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

The same machine-independent SpecIR should remain reusable across supported configurations.

See `docs/target-profiles.md`, `docs/poc1c-results.md`, and RFC 0009.
