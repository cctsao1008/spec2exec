# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **POC-1C.A:** CLOSED / PASS for the RV32I native emulator baseline; physical hardware validation pending
- **POC-1C.B entry hardening:** complete
- **Current backend experiment:** POC-1C.B B1 — multiple live values / forced spill
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

The native emulator baseline is closed after hostile implementation review and closure re-review.

```text
Accepted Specification
        ↓
Target-neutral verification
        ↓
Machine-independent SpecIR
        ↓
RV32I Target Code Generator
        ↓
RV32I assembly
        ↓
GNU assembler (-march=rv32i -mabi=ilp32)
        ↓
Generated object
        ↓
Trusted validation harness
        ↓
GNU linker
        ↓
Validation ELF
        ↓
QEMU rv32 virt
        ↓
40,401 exhaustive accepted-contract observations
```

The generated target object remains RV32I-only. The trusted bare-metal harness uses Zicsr only to install `mtvec` for the diagnostic trap path; this is validation infrastructure, not an expansion of the architectural target.

Evidence boundaries:

```text
P1/P2             specification / SpecIR obligations       CHECKED
P3                SpecIR → generated RV32I assembly        TESTED
P4-A              generated assembly → generated object    TRUSTED
P4-H              harness assembly → harness object        TRUSTED
P4-L              objects + linker script → validation ELF TRUSTED
P4-R              ELF → accepted contract                  TESTED_EXHAUSTIVE
P4-R.sensitivity  known-bad controls → failure channel     TESTED
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

The B0 entry-hardening gate is complete. It established:

```text
mechanically bound runtime case counting
normalized harness integrity checks
callee-saved register guard
root-only preferred destination invariant
verified runtime contract traceability
runtime-oracle sensitivity evidence
source/toolchain evidence hardening
reserved stack and initialized sp
observable synchronous trap/failure path
```

Current sequence:

```text
B1  multiple live values / forced spill       UNLOCKED / NEXT
B2  single branch + single merge              PLANNED
B3  single non-recursive call                 PLANNED
```

These experiments determine whether local backend bookkeeping remains adequate or should be promoted into an explicit TargetIR/MachineIR-style representation. A named MachineIR is not introduced merely because spilling exists; the implementation evidence must justify that transition.

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
