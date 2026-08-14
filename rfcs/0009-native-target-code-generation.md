# RFC 0009 — Native Target Code Generation

- **Status:** Accepted / Architecture Baseline
- **Scope:** Primary executable-generation path
- **Review status:** Architecture closure complete; POC-1C.A closed after hostile implementation review; POC-1C.B entry hardening complete

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

A CPU core is also not identical to an ISA. Hazard3 is a concrete RISC-V core planned for physical validation of an RV32I subset. Cortex-M33 is a concrete Arm core planned for physical validation of an Armv8-M Mainline target.

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
P3                SpecIR → Target Assembly
P4-A              Target Assembly → Generated Object
P4-H              Runtime Harness Assembly → Harness Object
P4-L              Objects + Linker Script → Validation Executable
P4-R              Validation Executable → Runtime Observation
P4-R.sensitivity  Known-bad controls → Observable Failure
```

No single PASS may collapse these boundaries. Runtime or hardware agreement does not discharge P3.

Runtime observation is a semantic observation, not a requirement for structural identity between SpecIR expression trees and target instruction sequences. A target program may be optimized or structurally different while preserving the accepted observable semantics.

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

### POC-1C.A implementation status

POC-1C.A is **CLOSED / PASS** for the declared emulator baseline. The completed validation binding is:

```text
Validation kind: emulator
Emulator:        qemu-system-riscv32
Machine:         virt
```

The validated generated-code path is:

```text
Accepted Specification
    ↓
Target-neutral P1/P2 verification
    ↓
machine-independent SpecIR
    ↓
RV32I target code generation
    ↓
GNU assembler (-march=rv32i -mabi=ilp32)
    ↓
Generated ELF32 RISC-V object
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

POC-1C.A supports `add` and `sub`. Unsupported operations, ABI shapes, machine-specific fields, literals, temporary-register exhaustion, and backend-state violations fail closed. The backend emits machine-readable bookkeeping for value locations, ABI-fixed locations, temporary-register pressure, spill count, and explicit ABI/placement invariants.

### Runtime evidence and trace hardening

The current runtime evidence includes these safeguards:

- the SiFive test-finisher FAIL word produces QEMU exit code `1`;
- negative controls require the exact expected failure status, not merely any non-zero result;
- the harness cannot reach PASS without the mechanically bound case-counter initialization, per-case increment, and final expected-count assertion;
- harness matching strips comments, normalizes instruction lines, and checks the required execution skeleton in order;
- the accepted `result == a` contract is a neutral verified specification clause (`REQ-OPT-001-EQ`) and a traced SpecIR postcondition;
- P4-R consumes that already-verified contract rather than an unverified side field;
- two deliberately non-equivalent target-code mutations and one explicit trap probe are assembled, linked, executed, and required to exit `1`;
- sensitivity results are first-class `P4-R.sensitivity` evidence;
- runtime observation remains an accepted-contract observation and does not upgrade P3 to a proof.

For the current subject:

```text
input domain:       a,b ∈ [-100,100]
expected cases:     40,401
runtime contract:   result == a
contract trace:     REQ-OPT-001-EQ
runtime evidence:   TESTED_EXHAUSTIVE
```

### Target/profile binding hardening

The validated Target Configuration selects the toolchain binding used by the pipeline, and `assembly_dialect` is part of that lookup key:

```text
rv32i + bare-metal + ilp32-integer-subset + gnu-riscv + elf32-riscv
    ↓
generated object assembler: -march=rv32i -mabi=ilp32
linker:                     -m elf32lriscv
```

Unsupported profile/toolchain combinations fail closed instead of silently reusing unrelated flags.

### Validation-harness ISA boundary

The bare-metal validation harness is trusted downstream infrastructure, not generated Spec2Exec target code. To make synchronous faults observable before forced-spill experiments, it installs `mtvec` and therefore uses Zicsr:

```text
Generated Spec2Exec target object
    -march=rv32i -mabi=ilp32

Trusted validation harness object
    -march=rv32i_zicsr -mabi=ilp32
    Zicsr use: mtvec installation only
```

This does **not** add Zicsr to the Spec2Exec architectural target accepted by the RV32I Target Code Generator. Evidence keeps P4-A (generated object) and P4-H (harness object) separate so this distinction remains auditable.

### Verification boundary hardening

POC-1C no longer injects a synthetic `target: host-c` field or routes P1/P2 through the previous host-C compatibility path. The target-neutral verifier checks specification/SpecIR linkage, ranges, behavior, overflow policy, and the accepted runtime contract before the target boundary.

### Backend ABI and placement invariants

For the current no-save/restore direct backend:

```text
argument registers      a0..a7
return register         a0
temporary registers     t0..t6
callee-saved registers  forbidden until explicit save/restore exists
preferred_dest          root-only
```

Generated use of `s0..s11`, `sp`, `gp`, or `tp` fails with `E_BACKEND_ABI_CLOBBER`. Non-root preferred destinations fail with `E_BACKEND_STATE`. These restrictions are deliberate entry safeguards, not permanent architecture rules; later backends may use callee-saved registers only with explicit ABI-preserving save/restore.

### Evidence-record hardening

Evidence strength remains boundary-specific:

```text
P1/P2             CHECKED
P3                TESTED
P4-A              TRUSTED
P4-H              TRUSTED
P4-L              TRUSTED
P4-R              TESTED_EXHAUSTIVE
P4-R.sensitivity  TESTED
```

Every current POC-1C evidence claim carries the normalized audit fields:

```text
id
subject
property
status
assumptions
producer
source_revision
trace
subject_binding
```

The evidence artifact set binds the accepted specification, SpecIR, target configuration, generated assembly, backend state, backend/pipeline/entrypoint/profile/verifier sources, runtime harness, linker script, Makefile, CI workflow, generated object, harness object, linked ELF, source revision, working-tree cleanliness, and named external-tool versions/invocations.

`P3` remains TESTED, not formally proven. `P4-R` means exhaustive accepted-contract observation over the mechanically bound declared domain; it does not establish a compiler-correctness theorem.

### POC-1C.B entry gate

The entry hardening required before forced spills is now complete:

```text
stack region reserved                 COMPLETE
sp initialized                        COMPLETE
minimal mtvec trap path installed     COMPLETE
trap failure observable as exit 1     COMPLETE
trap path dynamically exercised       COMPLETE
callee-saved clobber guard            COMPLETE
root-only destination invariant       COMPLETE
runtime harness integrity binding     COMPLETE
runtime sensitivity evidence          COMPLETE
contract traceability                 COMPLETE
source/toolchain evidence hardening   COMPLETE
```

The bare-metal linker script reserves a 4096-byte aligned stack and exports `__stack_top`. The harness initializes `sp` before executing generated code. A deliberate `ebreak` mutation proves the synchronous trap path reaches the same expected exit-1 failure channel.

POC-1C.B may therefore proceed to B1 multiple-live-value / forced-spill experiments. Spill support itself is **not** claimed complete by this entry work.

Planned physical validation remains separate:

```text
Validation kind: hardware
CPU core:        Hazard3 RISC-V
SoC:             RP2350
Board:           Raspberry Pi Pico 2
```

Physical Hazard3/RP2350 execution is not part of the completed emulator evidence set. Pico 2 remains validation hardware, not an architectural target.

See `docs/poc1c-results.md` for the concrete CI result, tool versions, artifact hashes, runtime sensitivity observations, and evidence classifications.

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

Planned physical validation binding:

```text
CPU core:       Arm Cortex-M33
SoC:             RP2350
Board:           Raspberry Pi Pico 2
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
- Generated-target semantics and trusted validation-harness capabilities must remain separately evidenced.
- A named TargetIR/MachineIR remains optional; machine bookkeeping must stay explicit and testable.
- Unsupported operations, incompatible target-profile combinations, resource exhaustion, ABI-clobber risks, runtime-domain mismatch, and runtime-oracle mismatch fail closed.
- Native evidence must distinguish semantic checking from assembler, linker, ABI, emulator, operating-system, loader/runtime, platform, and hardware assumptions.
- Runtime contract observation does not imply structural preservation and does not discharge the P3 semantic-preservation obligation.
- Reuse mature assembler/linker and platform tooling rather than reimplementing it inside Target Code Generation.
- When literals enter a target subset, immediate/constant legalization remains an explicit Target Code Generator responsibility even though final binary instruction encoding remains the assembler's responsibility.
