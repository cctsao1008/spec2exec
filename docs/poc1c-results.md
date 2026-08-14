# POC-1C.A — RV32I Native Pipeline Validation Results

- **POC-1C.A status:** CLOSED / PASS for the emulator baseline
- **POC-1C.B entry-hardening status:** COMPLETE
- **Target configuration:** RV32I + bare metal
- **Physical hardware validation:** pending
- **Latest tested entry-hardening revision:** `65b346be4478b08a984d20b36cc47b901539371b`
- **GitHub Actions run:** `31765577964`
- **POC-1C tests in that run:** 28 / 28 PASS

## What is validated

POC-1C exercises the native Spec2Exec executable-generation path without generated C, LLVM IR, or another high-level-language compiler stage in the primary path:

```text
Accepted Specification
        ↓
Target-neutral deterministic verification
        ↓
Machine-independent SpecIR
        ↓
RV32I Target Code Generator
        ↓
RV32I assembly
        ↓
GNU assembler (-march=rv32i -mabi=ilp32)
        ↓
Generated ELF32 RISC-V object
        ↓
Trusted bare-metal validation harness
        ↓
GNU linker
        ↓
Validation ELF
        ↓
QEMU rv32 virt
        ↓
40,401-case exhaustive accepted-contract observation
```

The generated Spec2Exec target object remains RV32I-only. The trusted validation harness now uses **Zicsr only to install `mtvec` for an observable diagnostic trap path**; this does not widen the architectural semantics accepted by the Target Code Generator.

## Test subject

```text
safe_add_sub(a, b) = (a + b) - b

a,b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
contract trace: REQ-OPT-001-EQ
```

The accepted contract is now a neutral `function.contract` specification clause. It is checked by P1, represented by a traced SpecIR postcondition, and consumed by P4-R only after target-neutral verification.

The generated target code remains:

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

Runtime validation observes accepted semantics, not instruction-tree identity. A semantically equivalent target program may have a different instruction structure.

## Backend invariants

The direct backend records and enforces:

```text
arguments                    a0..a7
return                       a0
temporary register pool      t0..t6
spill count                  0 for POC-1C.A
callee-saved policy          forbidden without explicit save/restore
preferred_dest policy        root-only
temporary high-water mark    1 for safe_add_sub
```

Until explicit save/restore support exists, generated code fails closed if it touches `s0..s11`, `sp`, `gp`, or `tp`. This protects the runtime harness state carried in callee-saved registers. `preferred_dest` is also explicitly root-only so recursive placement cannot silently overwrite a still-live ABI argument.

## Hostile-review hardening

The implementation-review cycle and closure re-review produced the following landed safeguards:

- QEMU SiFive finisher FAIL encodes process exit code `1`, eliminating the original false-PASS channel;
- negative controls require the exact expected failure status rather than merely any non-zero status;
- runtime sensitivity is now recorded in `evidence.json` as `P4-R.sensitivity`;
- two non-equivalent target-code mutations are assembled, linked, executed, and required to exit `1`;
- an `ebreak` mutation exercises the installed synchronous-trap path and is also required to exit `1`;
- the runtime case counter initializer, increment, expected-count materialization, and final assertion are mechanically bound before exhaustive evidence can be emitted;
- harness matching strips comments, matches normalized instruction lines, and checks the required execution skeleton in order;
- the accepted runtime contract is a verified specification clause rather than a POC-1B-specific side field;
- P1/P2 are target-neutral and do not inject `target: host-c`;
- Target Configuration mechanically selects generated-code assembler flags and linker mode;
- assembly dialect is part of the target-to-toolchain binding key;
- generated-code and harness assembler flags are distinct, preserving RV32I-only generated semantics while allowing Zicsr in trusted trap infrastructure;
- source revision and `working_tree_clean` are recorded;
- `run.py`, the POC-1C workflow, harness, linker script, backend/pipeline/verifier sources, target configuration, tools, invocations, and generated artifacts are evidence-bound;
- real expression-tree register exhaustion is tested through the code generator;
- root-symbol ABI return placement and unsigned-32 backend code-generation coverage are tested.

## Bare-metal runtime infrastructure

POC-1C.B entry hardening now provides the infrastructure required before forced spills:

```text
linker script
    reserves 4096-byte aligned stack region
    exports __stack_top

_start
    initializes sp
    installs mtvec

trap handler
    uses the same SiFive test-finisher failure channel
    exits QEMU with status 1
```

The trap path is dynamically tested with an `ebreak` probe. A bad spill or synchronous fault can therefore become an observable failure instead of an undifferentiated timeout.

## CI coverage

The successful entry-hardening run executes **28 tests** plus the full native pipeline. Coverage includes:

```text
normal code generation / bookkeeping                       PASS
unsupported mul                                             REJECTED
ninth integer argument                                      REJECTED
machine-specific function.target leakage                    REJECTED
raw temporary-pool exhaustion                               REJECTED
real expression-tree register exhaustion                    REJECTED
integer literal outside POC-1C.A                            REJECTED
mixed integer input types                                   REJECTED
non-binary arithmetic operation                             REJECTED
non-expression body                                         REJECTED
root-symbol ABI return placement                            PASS
u32 backend code-generation                                 PASS
callee-saved clobber attempt                                REJECTED
non-root preferred_dest                                     REJECTED
case-counter binding regressions                            PASS
comment-only harness matches                                REJECTED
assembly-dialect/toolchain mismatch                         REJECTED
source/evidence binding regressions                         PASS
neutral contract traceability                               PASS
missing/mismatched contract representation                  REJECTED
non-equivalent native assembly mutations                    EXIT 1
synchronous trap probe                                      EXIT 1
```

CI sets `POC1C_REQUIRE_RUNTIME=1`, so runtime sensitivity tests cannot silently skip because the RV32I/QEMU tools are missing.

## Fail-closed policy

```text
unsupported operation       → E_TARGET_UNSUPPORTED_OPERATION
unsupported literal         → E_TARGET_UNSUPPORTED_LITERAL
unsupported ABI shape       → E_TARGET_ABI
register exhaustion         → E_TARGET_OUT_OF_REGISTERS
callee-saved ABI clobber    → E_BACKEND_ABI_CLOBBER
backend placement violation → E_BACKEND_STATE
machine detail in SpecIR    → E_SPECIR_TARGET_LEAK
target/tool mismatch        → E_TARGET_PROFILE
runtime-domain mismatch     → E_P4_DOMAIN
runtime-oracle mismatch     → E_P4_ORACLE
native runtime failure      → E_RUNTIME
```

## Evidence boundaries

The result deliberately does not collapse the native pipeline into one PASS:

```text
P1/P2             specification / SpecIR obligations       CHECKED
P3                SpecIR → generated RV32I assembly        TESTED
P4-A              generated assembly → generated object    TRUSTED
P4-H              validation harness → harness object      TRUSTED
P4-L              bound objects + linker script → ELF      TRUSTED
P4-R              linked ELF → accepted contract           TESTED_EXHAUSTIVE
P4-R.sensitivity  known-bad controls → failure channel     TESTED
```

`P3` is not a formal equivalence proof. `P4-R` means the linked validation executable satisfied `result == a` for every input pair in the mechanically bound `[-100,100] × [-100,100]` domain. Runtime agreement does not prove compiler correctness or require structural identity between SpecIR and target instructions.

## Toolchain and target binding

Successful CI environment:

```text
GitHub runner OS          Ubuntu 24.04.4
Python                    3.12.3
GNU assembler             2.42 (2.42-1ubuntu1+6)
GNU linker                2.42 (2.42-1ubuntu1+6)
QEMU                       8.2.2 (Debian 1:8.2.2+ds-0ubuntu1.18)
```

Validated bindings:

```text
Architectural target
    ISA Profile           riscv / rv32i / extensions=[]
    Execution Profile     bare-metal / ilp32-integer-subset / elf32-riscv

Generated target object
    assembler flags       -march=rv32i -mabi=ilp32

Trusted validation harness
    assembler flags       -march=rv32i_zicsr -mabi=ilp32
    Zicsr purpose         mtvec installation only

Linker
    flags                 -m elf32lriscv
```

## Runtime-domain and sensitivity binding

```text
a range                   [-100,100]
b range                   [-100,100]
expected cases            40,401
runtime oracle            result == a
runtime oracle kind       accepted-contract-observation
contract trace            REQ-OPT-001-EQ
failure status            1
```

Sensitivity observations from run `31765577964`:

```text
wrong-final-operation     exit 1
wrong-first-operation     exit 1
trap-path-ebreak          exit 1
```

## Successful-run artifact bindings

Key SHA-256 values from tested revision `65b346be4478b08a984d20b36cc47b901539371b`:

```text
target-config.json
9160ba245268499fd22d4537efb586d61eceb9719290670553d6bf4a393d750b

safe_add_sub.s
9e78282830b5e9e87a69b22dc0c358bd07bcff248f04f2709792f45973892a6b

safe_add_sub.o
027486b5efe99dfc21356d26620f9523316db0e32b1a5266396b96f62f799b7d

safe_add_sub.elf
fb029132a30d8030128edf8f373978ee1643a220c448fc02d06fc95ad26fffc8

backend-state.json
62ea82ccd47f5d587866b9f2aac25cc7d934f4963df723e16fbfe702e15b377c

evidence.json
7600bd471e949d961f9c0639f59bb5fd2408677c8197cbc98d0ad28be9921fa9
```

Evidence also binds the accepted specification, SpecIR, harness source/object, linker script, backend, pipeline, `run.py`, target-profile module, verifier, Makefile, POC-1C workflow, exact tool versions/invocations, source revision, and working-tree cleanliness.

## Validation binding

Completed validation binding:

```text
validation kind: emulator
emulator:        qemu-system-riscv32
machine:         virt
architectural target: RV32I + bare metal
```

Planned physical validation remains separate:

```text
validation kind: hardware
CPU core:        Hazard3 RISC-V
SoC:             RP2350
board:           Raspberry Pi Pico 2
```

Pico 2 is validation hardware, not an architectural target. Physical Hazard3/RP2350 execution is not part of the completed evidence set.

## Remaining work

POC-1C.A remains closed. The POC-1C.B entry gate is complete, so B1 may now investigate multiple live values and forced spills.

Non-blocking follow-ups remain:

```text
end-to-end unsigned-32 validation
register-pressure-aware expression ordering
future constant/immediate legalization when literals enter scope
physical Hazard3 / RP2350 validation
optional linked-image disassembly / ISA audit
```

## Result

POC-1C.A demonstrates a working **C-free executable-generation path** for the declared RV32I subset through native target assembly and conventional assembler/linker tooling, with exhaustive emulator-side accepted-contract observation over the declared domain.

The POC-1C.B entry-hardening pass adds explicit ABI guards, verified contract traceability, stronger harness integrity checks, source/evidence bindings, runtime sensitivity evidence, a valid bare-metal stack, and an observable trap path. These additions harden the experimental environment without upgrading P3 to a formal compiler-correctness proof.
