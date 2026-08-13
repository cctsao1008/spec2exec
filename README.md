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

Native target code generation is the primary path. C and LLVM remain optional reference/comparison paths.

SpecIR remains machine-independent. Concrete executable targets are composed from ISA, Execution, and optional Platform Profiles so support can expand across CPU architectures, operating systems, and bare-metal/RTOS environments without changing SpecIR semantics.

## Target coverage goal

Spec2Exec is intended to be implementable across major CPU ISA families and major execution environments rather than being tied to one development board, one ISA, or one operating system.

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
    Android
    bare metal
    selected RTOS profiles
```

Not every ISA/OS pair is valid or useful. Each supported target configuration must explicitly identify its ISA, ABI, object/executable model, runtime environment, and platform assumptions.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  NEXT-ARCH    Pico 2 Hazard3 / RV32I native validation
POC-1C.B  FOLLOW-UP    Hazard3 backend stress
POC-1D    PLANNED      Pico 2 Cortex-M33 / Armv8-M cross-target validation
POC-1E    PLANNED      hosted ISA / OS expansion
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1C uses the Hazard3 RISC-V cores in RP2350 on Raspberry Pi Pico 2 while deliberately constraining generated semantics to the RV32I base-integer subset.

POC-1D uses the same Raspberry Pi Pico 2 / RP2350 platform switched to its Arm Cortex-M33 cores. The initial Arm ISA profile is Armv8-M Mainline / Cortex-M33.

POC-1E begins hosted portability with reusable ISA and Execution Profiles rather than treating one OS as intrinsic to one CPU architecture. Initial configurations are planned around x86_64/Linux, x86_64/Windows, AArch64/Linux, and AArch64/macOS, followed by additional valid combinations such as AArch64/Windows, AArch64/Android, and RV64/Linux.

The intended long-term model is:

```text
                        same Verified SpecIR
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
              RISC-V           Arm           x86_64
            RV32 / RV64   M-profile/AArch64     │
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                      Execution Profiles
                 Linux / Windows / macOS
                 Android / bare metal / RTOS
                                │
                                ▼
                     Platform / Toolchain
                                │
                                ▼
                   Executable / Firmware
```

See `docs/target-profiles.md`, `docs/phase1-plan.md`, and `rfcs/0009-native-target-code-generation.md`.

## License

License selection remains intentionally pending.
