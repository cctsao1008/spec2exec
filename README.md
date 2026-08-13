# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec explores specification as the primary human-facing artifact between intent and executable software.

## Primary architecture

```text
Human Intent
    ↓
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

Native target code generation is the primary path. C and LLVM remain optional reference/comparison paths. Target-specific information is selected after SpecIR verification through Target Profiles; bare-metal board/SoC and hosted OS details belong to Platform Profiles.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  NEXT-ARCH    Pico 2 Hazard3 / RV32I native validation
POC-1C.B  FOLLOW-UP    Hazard3 backend stress
POC-1D    PLANNED      Pico 2 Cortex-M33 / Armv8-M cross-target validation
POC-1E    PLANNED      x86_64 Linux / Windows / macOS hosted matrix
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1C uses the Hazard3 RISC-V cores in RP2350 on Raspberry Pi Pico 2 while deliberately constraining generated semantics to the RV32I base-integer subset.

POC-1D uses the same Raspberry Pi Pico 2 / RP2350 platform switched to its Arm Cortex-M33 cores. The initial Arm Target Profile is Armv8-M Mainline / Cortex-M33.

POC-1E adds x86_64 as a third ISA family and explicitly treats hosted operating systems as distinct ABI/object environments:

```text
x86_64 / Linux    SysV AMD64 subset      ELF64
x86_64 / Windows  Microsoft x64 subset   COFF + PE32+
x86_64 / macOS    Darwin x86_64 subset   Mach-O
```

The resulting representative validation matrix is:

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

This is representative architectural coverage rather than a claim of complete ISA or operating-system coverage. A later AArch64/arm64 hosted profile can be added separately without changing machine-independent SpecIR.

See `docs/target-profiles.md`, `docs/phase1-plan.md`, and `rfcs/0009-native-target-code-generation.md`.

## License

License selection remains intentionally pending.
