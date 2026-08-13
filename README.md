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

SpecIR remains machine-independent. A concrete executable target is composed from an **ISA Profile**, an **Execution Profile**, and an optional **Platform Profile**. A specific CPU core or development board may be used as validation hardware, but it is not the architectural target unless the generated semantics explicitly depend on that core or platform.

## Target coverage goal

Spec2Exec is intended to be implementable across major CPU ISA families and major execution environments without changing machine-independent SpecIR semantics.

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

Not every ISA/OS pair is valid or useful. Each supported target configuration must explicitly identify its ISA, ABI, object/executable model, runtime environment, and platform assumptions.

## Validation platforms

Validation hardware is deliberately separate from architecture coverage.

The initial embedded validation platform is Raspberry Pi Pico 2 / RP2350 because the same SoC can execute with either of two CPU-core families:

```text
RP2350 / Pico 2
├── Hazard3 RISC-V cores
│   └── validate the RV32I bare-metal target path
└── Arm Cortex-M33 cores
    └── validate the Armv8-M Mainline bare-metal target path
```

Pico 2 is therefore a **validation platform**, not a Spec2Exec architecture target.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  NEXT-ARCH    RV32I bare-metal native validation
POC-1C.B  FOLLOW-UP    RV32 backend stress
POC-1D    PLANNED      Armv8-M Mainline bare-metal cross-target validation
POC-1E    PLANNED      hosted ISA / OS expansion
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1C validates the RV32I bare-metal path using the Hazard3 cores in RP2350/Pico 2. POC-1D validates the Armv8-M Mainline bare-metal path using the Cortex-M33 cores in the same RP2350/Pico 2 platform.

POC-1E begins hosted portability with reusable ISA and Execution Profiles. Initial configurations are planned around x86_64/Linux, x86_64/Windows, AArch64/Linux, and AArch64/macOS, followed by AArch64/Windows and RV64/Linux when practical.

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
                         bare metal
                                 │
                                 ▼
                    optional Platform Profile
                                 │
                                 ▼
                      Executable / Firmware
```

See `docs/target-profiles.md`, `docs/phase1-plan.md`, and `rfcs/0009-native-target-code-generation.md`.

## License

License selection remains intentionally pending.
