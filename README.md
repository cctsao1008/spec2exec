# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec explores specification as the primary human-facing artifact between intent and executable software.

## Project thesis

Spec2Exec is not primarily an AI coding tool and is not defined by any particular synthesis model. Its long-term direction is **trust infrastructure for AI-generated software**: separate proposal from semantic authority, bind accepted semantics to deterministic verification and explicit evidence, and preserve that trust chain into executable behavior.

> **AI proposes. Humans authorize semantics. Deterministic systems verify. Evidence justifies trust. Portable backends execute.**

The normative architecture is more general than human-only approval: semantic authority may also come from accepted parent specifications, standards, certified domain models, system contracts, safety authorities, or other explicit governance sources. AI and other synthesis systems are replaceable proposal engines; they do not gain semantic authority merely by producing plausible or high-quality output.

The project value framework is a trust chain:

```text
#1 Trust Architecture
        ↓
#2 Specification / Semantic Authority Model
        ↓
#3 Evidence Architecture
        ↓
#4 Deterministic Verification
        ↓
#5 Portable Executable Realization
   + Preservation Evidence
        ↓
#6 AI Synthesis Quality
```

The core is #1–#4. Portable realization extends accepted semantics to real machines. AI synthesis quality improves productivity and proposal quality, but remains outside the trusted semantic core by default.

See `rfcs/0010-trust-chain-architecture.md` for the project-level trust thesis and long-term invariants.

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

The planned embedded hardware validation platform is Raspberry Pi Pico 2 / RP2350 because the same SoC can execute with either of two CPU-core families:

```text
RP2350 / Pico 2
├── Hazard3 RISC-V cores
│   └── planned hardware validation of the RV32I bare-metal target path
└── Arm Cortex-M33 cores
    └── planned hardware validation of the Armv8-M Mainline bare-metal target path
```

Pico 2 is therefore a **validation platform**, not a Spec2Exec architecture target.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  EMULATOR-PASS  RV32I bare-metal native pipeline
          HW-PENDING     Hazard3 / RP2350 / Pico 2 physical validation
POC-1C.B  NEXT-ARCH      RV32 backend stress
POC-1D    PLANNED        Armv8-M Mainline bare-metal cross-target validation
POC-1E    PLANNED        hosted ISA / OS expansion
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1C.A now has a working C-free native path in CI:

```text
machine-independent SpecIR
    ↓
RV32I code generation
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

The successful baseline records `P3` as `TESTED`, assembler/linker boundaries as `TRUSTED`, and runtime behavior as `TESTED_EXHAUSTIVE`; it does not claim a formally verified native compiler. See `docs/poc1c-results.md`.

POC-1D will validate the Armv8-M Mainline bare-metal path using Cortex-M33 as the initial hardware core. POC-1E begins hosted portability with reusable ISA and Execution Profiles. Initial hosted configurations are planned around x86_64/Linux, x86_64/Windows, AArch64/Linux, and AArch64/macOS, followed by AArch64/Windows and RV64/Linux when practical.

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

See `rfcs/0010-trust-chain-architecture.md`, `rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md`, `rfcs/0006-semantic-preservation-and-evidence-model.md`, `rfcs/0009-native-target-code-generation.md`, `docs/target-profiles.md`, `docs/phase1-plan.md`, and `docs/poc1c-results.md`.

## License

License selection remains intentionally pending.
