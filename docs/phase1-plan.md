# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **Next architecture experiment:** POC-1C.A — RV32I Bare-Metal Native Pipeline Validation
- **Following backend experiment:** POC-1C.B — RV32 Backend Complexity
- **Later portability experiment:** POC-1D — Armv8-M Mainline Bare-Metal Cross-Target Generation
- **Later hosted portability experiment:** POC-1E — Hosted ISA / OS Expansion
- **Next semantic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Semantic Resolution

## Target model

A Spec2Exec architectural target is defined by its ISA and execution semantics. The CPU core and board used to validate that target are recorded separately.

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
Validation Binding    = CPU core + board or host used for evidence
```

## POC-1C — RV32I Bare Metal

```text
ISA:            RV32I
Execution:      bare metal
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

Initial validation binding uses the RISC-V core in RP2350 on Raspberry Pi Pico 2. Pico 2 is validation hardware, not the architectural target.

POC-1C.A begins with straight-line `add` and `sub`. Unsupported operations and register exhaustion fail closed. The backend uses a bounded temporary-register pool and emits machine-readable bookkeeping evidence.

POC-1C.B later exercises multiple live values, one branch/merge, and one non-recursive call.

## POC-1D — Armv8-M Mainline Bare Metal

```text
ISA/profile:    Armv8-M Mainline
Execution:      bare metal
ABI subset:     AAPCS integer subset
Assembly:       GNU Arm syntax
Object model:   ELF32 Arm
```

Initial validation binding uses the Cortex-M33 cores in the same RP2350/Pico 2 platform. Reusing the board reduces unrelated hardware variation while changing CPU architecture; it does not make Pico 2 part of the target definition.

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

See `docs/target-profiles.md` and RFC 0009.
