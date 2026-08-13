# POC-1C.A — RV32I Native Pipeline Validation Results

- **Status:** Emulator baseline PASS after hostile implementation review hardening
- **Target configuration:** RV32I + bare metal
- **Physical hardware validation:** pending
- **Successful implementation commit:** `c0f7f66e4cb433a21cc6ba3cbef50dd0504c2976`
- **GitHub Actions run:** `31730932788`

## What was validated

POC-1C.A exercises the native Spec2Exec executable-generation path without generated C, LLVM IR, or another high-level-language compiler stage:

```text
Accepted Specification
        ↓
Machine-independent SpecIR
        ↓
Target-neutral deterministic P1/P2 checks
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
40,401-case exhaustive contract observation
```

The native runtime harness is assembly-only. C remains available elsewhere in the project as a reference/comparison path, but POC-1C.A no longer routes its P1/P2 verification through the earlier host-C compatibility shim.

## Test subject

```text
safe_add_sub(a, b) = (a + b) - b

a,b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
```

The generated target code for the successful run is:

```asm
    .section .text
    .option norvc
    .globl safe_add_sub
    .type safe_add_sub, @function
safe_add_sub:
    add t0, a0, a1
    sub a0, t0, a1
    ret
    .size safe_add_sub, .-safe_add_sub
```

Runtime validation observes the accepted contract. It does not require the final instruction sequence to preserve the syntactic structure of the SpecIR expression. A semantically equivalent optimized target program would still be valid under the declared preconditions.

## Backend bookkeeping

The generated backend-state evidence records:

```text
a      → a0
b      → a1
expr:0 → t0   add
expr:1 → a0   sub
result → a0

temporary register pool = t0..t6
high-water mark          = 1
spill count              = 0
```

This is explicit backend decision evidence, not a mandatory MachineIR.

## Hostile-review hardening

Independent hostile reviews were used as implementation attacks rather than as automatic authorities. Findings were accepted only when confirmed against the current implementation or external tool semantics.

The post-review baseline includes these corrections and hardening measures:

- the QEMU SiFive finisher failure word now carries a non-zero process exit code;
- two deliberately non-equivalent generated-assembly mutations are assembled, linked, executed, and required to fail the runtime oracle;
- the runtime harness counts completed cases and cannot reach PASS unless all 40,401 expected cases complete;
- the hand-written harness domain is mechanically checked against the verified SpecIR ranges before `TESTED_EXHAUSTIVE` may be emitted;
- the runtime oracle is explicitly classified as an accepted-contract observation, not a structural comparison or formal P3 proof;
- P1/P2 use a target-neutral POC-1C verifier with no injected `target: host-c` field;
- GNU assembler/linker flags are selected through the validated Target Configuration binding rather than independently at call sites;
- harness source, linker script, backend/pipeline/verifier sources, source revision, tools, versions, invocations, and generated artifacts are bound into the evidence record;
- evidence claims now use a uniform record shape with `id`, `subject`, `property`, `status`, `assumptions`, `producer`, `source_revision`, `trace`, and `subject_binding`;
- actual expression-tree register exhaustion is tested through code generation, not only by directly exhausting the RegisterPool;
- root-symbol returns are position-independent and u32 code generation has explicit test coverage.

## CI tests

The successful run executes 16 unit/integration tests and the full native pipeline. The tests cover:

```text
normal code generation / bookkeeping                      PASS
unsupported mul                                            REJECTED
ninth integer argument                                     REJECTED
machine-specific function.target leakage                   REJECTED
raw temporary-pool exhaustion                              REJECTED
real expression-tree register exhaustion                   REJECTED
integer literal outside POC-1C.A                           REJECTED
mixed integer input types                                  REJECTED
non-binary arithmetic operation                            REJECTED
non-expression body                                        REJECTED
root-symbol result in a0 / another argument register       PASS
u32 add/sub target-code generation                         PASS
non-equivalent native assembly mutations                   DETECTED AS RUNTIME FAILURE
target-neutral verifier accepts non-C native identifiers   PASS
machine target leak at verification boundary               REJECTED
no host-C target field required by P1/P2 verifier          PASS
```

The fail-closed policy includes:

```text
unsupported operation       → E_TARGET_UNSUPPORTED_OPERATION
unsupported literal         → E_TARGET_UNSUPPORTED_LITERAL
unsupported ABI shape       → E_TARGET_ABI
register exhaustion         → E_TARGET_OUT_OF_REGISTERS
machine detail in SpecIR    → E_SPECIR_TARGET_LEAK
target/tool binding mismatch→ E_TARGET_PROFILE
runtime-domain mismatch     → E_P4_DOMAIN
runtime-oracle mismatch     → E_P4_ORACLE
native runtime failure      → E_RUNTIME
```

POC-1C.A does not silently spill, silently reuse live registers, emulate unsupported operations, or silently widen its target semantics.

## Evidence boundaries

The result deliberately does not collapse the native pipeline into one PASS:

```text
P1/P2  specification / SpecIR obligations       CHECKED
P3     SpecIR → RV32I assembly                  TESTED
P4-A   RV32I assembly → ELF32 object            TRUSTED
P4-H   harness assembly → harness object        TRUSTED
P4-L   objects + linker script → RV32I ELF      TRUSTED
P4-R   linked ELF → accepted contract           TESTED_EXHAUSTIVE
```

`P3` is not a formal equivalence proof. `P4-R` means that the linked executable satisfied the accepted `result == a` contract for every input pair in the mechanically bound `[-100,100] × [-100,100]` domain. It is not evidence that the generated assembly must have a particular instruction structure, and it does not discharge the P3 preservation obligation.

The negative-control mutations demonstrate that the current runtime oracle has a functioning failure channel for known non-equivalent target-code changes.

## Toolchain and target binding

Successful CI environment:

```text
GitHub runner OS       Ubuntu 24.04.4
Python                 3.12.3
GNU assembler          2.42 (2.42-1ubuntu1+6)
GNU linker             2.42 (2.42-1ubuntu1+6)
QEMU                    8.2.2 (Debian 1:8.2.2+ds-0ubuntu1.18)
```

The validated target configuration selects the current GNU binding:

```text
ISA Profile            riscv / rv32i / extensions=[]
Execution Profile      bare-metal / ilp32-integer-subset / elf32-riscv

assembler flags        -march=rv32i -mabi=ilp32
linker flags           -m elf32lriscv
```

Unsupported profile/toolchain combinations fail closed instead of silently reusing these flags.

## Runtime-domain binding

Before building the runtime evidence, the pipeline checks that the assembly harness encodes the verified input ranges and expected case count. For this baseline:

```text
a range                 [-100,100]
b range                 [-100,100]
expected cases          40,401
runtime oracle          result == a
runtime oracle kind     accepted-contract-observation
trace                    REQ-OPT-001-EQ
```

The harness also maintains a runtime case counter and verifies `40,401` before writing the PASS finisher value.

## Artifact bindings

Successful-run SHA-256 values:

```text
target-config.json
9160ba245268499fd22d4537efb586d61eceb9719290670553d6bf4a393d750b

safe_add_sub.s
9e78282830b5e9e87a69b22dc0c358bd07bcff248f04f2709792f45973892a6b

safe_add_sub.o
027486b5efe99dfc21356d26620f9523316db0e32b1a5266396b96f62f799b7d

safe_add_sub.elf
fec6e6bbab3de0ef2e5cfa7b0f255458959d3c31a43f26bdc785988e11802029

backend-state.json
10cc1a8d81019dfb565ffd272ce63d688b7c7c47eb18866e09e8ca8c1e9762ef

evidence.json
b4c990a7220d4960b6e6e763c8b1a69695698f7635d894cd60ac9d3bf864a03f
```

Source / trusted-input bindings recorded by the evidence include:

```text
safe_add_sub.specir.json
d45f6b02bf484fdd69de4c62473405487ab8e93b6f9f9f7beb64ec92dd5cabeb

specification.json
faedcfe74e01547fde7bca2ea46251f826579e5a55099b895b64b4ad80a2e7f8

safe_add_sub_harness.s
5f72f5d3b122c6074ff43c23c30a729945bf59fba92c46721d586a0f80331ce9

rv32i_virt.ld
4141dceea344361eb21d02baac48574e803f6c55288d105da896bdac39a6513b

backend.py
4bfa17476a76c4c374698ef47e6d55a5006765109190a7f029491bfcb301ea65

pipeline.py
ec2fd84d32560b2f33fb770f166c3613fd8f9a9de9a8e8ae36366c4d1ed49640

verification.py
13d3586aedc847bde223c7de9f44692b5f8f50e8177e700e46a4e637254a9fea
```

The evidence also records the exact source revision, assembler/linker/QEMU invocations, tool versions, harness object hash, linked ELF hash, and linker-script binding.

## Validation binding

The current completed validation binding is:

```text
validation kind: emulator
emulator:        qemu-system-riscv32
machine:         virt
ISA:             RV32I
```

The planned physical validation binding remains separate:

```text
validation kind: hardware
CPU core:        Hazard3 RISC-V
SoC:             RP2350
board:           Raspberry Pi Pico 2
```

Pico 2 is validation hardware, not the architectural target. Physical Hazard3/RP2350 execution is not yet part of the completed evidence set.

## Remaining deferred items

The hostile-review repair pass does not claim that every future-backend problem has been solved. In particular:

```text
POC-1C.B entry requirement
    reserve and initialize a stack
    install a minimal trap/failure path
    then begin forced-spill / branch / call stress

Future literal support
    make immediate/constant legalization explicit
    do not silently move that semantic responsibility into assembler pseudo-ops

Optional defense-in-depth
    add linked-image disassembly / ISA audit evidence
```

## Result

POC-1C.A demonstrates a working **C-free executable-generation path** for the declared RV32I subset through native target assembly, conventional assembler/linker tooling, and exhaustive emulator-side accepted-contract observation over the declared domain.

The deterministic verification path for this POC is now target-neutral rather than host-C-dependent.

The result does **not** claim a formally verified native compiler, a formally verified executable, or structural identity between SpecIR and target assembly. It is a working implementation baseline with explicit evidence strength, negative-control sensitivity, source/artifact bindings, and trusted-computing-base boundaries.
