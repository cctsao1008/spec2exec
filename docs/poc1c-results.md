# POC-1C.A — RV32I Native Pipeline Validation Results

- **Status:** Emulator baseline PASS
- **Target configuration:** RV32I + bare metal
- **Physical hardware validation:** pending
- **Successful commit:** `6355fdbae7f61496f892f5899bc8228895f0d02a`
- **GitHub Actions run:** `31726666312`

## What was validated

POC-1C.A exercises the native Spec2Exec path without generated C, LLVM IR, or another high-level-language compiler stage:

```text
Accepted Specification
        ↓
Machine-independent SpecIR
        ↓
Deterministic P1/P2 checks
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
40,401-case exhaustive runtime comparison
```

The native runtime harness is assembly-only.

## Test subject

```text
safe_add_sub(a, b) = (a + b) - b

a,b ∈ [-100,100]
overflow_behavior = forbidden
contract: result == a
```

The generated target code for the successful run is structurally equivalent to:

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

This is backend decision evidence, not a mandatory MachineIR.

## Fail-closed tests

The successful CI run executes five unit tests:

```text
code generation / bookkeeping                  PASS
unsupported mul operation                      PASS (rejected)
ninth integer argument                         PASS (rejected)
legacy machine-specific function.target field  PASS (rejected)
temporary-register pool exhaustion             PASS (rejected)
```

The expected failure policy remains:

```text
unsupported operation       → E_TARGET_UNSUPPORTED_OPERATION
unsupported ABI shape       → E_TARGET_ABI
register exhaustion         → E_TARGET_OUT_OF_REGISTERS
machine detail in SpecIR    → E_SPECIR_TARGET_LEAK
```

No silent spill, live-register reuse, or unsupported-operation emulation is permitted in POC-1C.A.

## Evidence boundaries

The result deliberately does not collapse the native pipeline into one PASS:

```text
P1/P2  specification / SpecIR obligations       CHECKED
P3     SpecIR → RV32I assembly                  TESTED
P4-A   RV32I assembly → ELF32 object            TRUSTED
P4-L   object → linked RV32I ELF                TRUSTED
P4-R   linked ELF → runtime observation         TESTED_EXHAUSTIVE
```

`P3` is not a formal equivalence proof. Runtime agreement cross-validates the generated assembly but does not discharge the P3 semantic-preservation obligation.

## Toolchain evidence

Successful CI environment:

```text
GitHub runner OS       Ubuntu 24.04.4
GNU assembler          2.42 (2.42-1ubuntu1+6)
GNU linker             2.42 (2.42-1ubuntu1+6)
QEMU                    8.2.2 (Debian 1:8.2.2+ds-0ubuntu1.18)
```

Assembler invocation uses:

```text
-march=rv32i
-mabi=ilp32
```

The linker uses the `elf32lriscv` emulation and the POC-specific linker script.

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
dfbab5229e1519a575037209067d38353a046057719a083febc0adfd4e9e7171

backend-state.json
10cc1a8d81019dfb565ffd272ce63d688b7c7c47eb18866e09e8ca8c1e9762ef

evidence.json
7cac08f1222d461ba1279ad6f1a65a1db95383b35441c2fc87d566bd59444926
```

Source bindings:

```text
safe_add_sub.specir.json
d45f6b02bf484fdd69de4c62473405487ab8e93b6f9f9f7beb64ec92dd5cabeb

specification.json
faedcfe74e01547fde7bca2ea46251f826579e5a55099b895b64b4ad80a2e7f8
```

## Validation binding

The current completed validation binding is:

```text
emulator: qemu-system-riscv32
machine:  virt
ISA:      RV32I
```

The planned physical validation binding is separate:

```text
CPU core: Hazard3 RISC-V
SoC:      RP2350
board:    Raspberry Pi Pico 2
```

Pico 2 is validation hardware, not the architectural target. Physical Hazard3/RP2350 execution is not yet part of the completed evidence set.

## Result

POC-1C.A demonstrates a working C-free native executable-generation path for the declared RV32I subset through assembly, object generation, linking, and exhaustive emulator execution.

It does **not** claim a formally verified native compiler or verified executable. The result is an implementation baseline with explicit evidence strength and trusted-computing-base boundaries.
