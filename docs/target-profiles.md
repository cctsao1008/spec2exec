# Target, Execution, and Platform Profiles

## Purpose

SpecIR remains machine-independent. Spec2Exec is intended to be implementable across major CPU ISA families and major operating-system/execution environments without changing machine-independent SpecIR semantics.

The architecture therefore does not define one fixed target matrix. It defines composable target dimensions:

```text
Verified SpecIR
      │
      ├── ISA Profile
      │      architecture / ISA
      │      core/profile where relevant
      │      enabled extensions/features
      │      endianness
      │
      ├── Execution Profile
      │      ABI / calling convention
      │      operating system or bare-metal environment
      │      assembly dialect
      │      object model
      │      executable / loader conventions
      │
      └── Platform Profile (optional)
             SoC / board / machine identity
             processor mode
             memory map
             startup / vector-table policy
             linker layout
             firmware packaging / signing where applicable
```

A concrete target configuration is the compatible composition of these profiles:

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
```

Not every ISA/OS combination is meaningful or available. Spec2Exec must support valid combinations without encoding one operating system, ABI, object format, or board into SpecIR.

## Architecture coverage goal

The long-term target architecture goal is implementation coverage across major contemporary CPU ISA families and execution environments, rather than a closed list of POC targets.

Initial coverage families include:

```text
CPU / ISA families
    x86_64
    AArch64 / Arm64
    RISC-V (RV32 and RV64 profiles)
    Arm M-profile (including Armv8-M / Cortex-M33)

Hosted operating-system environments
    Linux
    Windows
    macOS
    Android

Embedded execution environments
    bare metal
    RTOS profiles where justified (for example FreeRTOS / Zephyr)
```

Additional ISA or OS profiles may be added without changing the primary architecture.

The goal is not to implement the Cartesian product of every ISA and every OS. The goal is that each supported combination is expressed explicitly through compatible ISA, Execution, and Platform Profiles.

## Example target configurations

The following examples are illustrative architecture configurations, not a frozen support list:

```text
x86_64 + Linux + SysV AMD64 + ELF64
x86_64 + Windows + Microsoft x64 + COFF/PE32+
AArch64 + Linux + AAPCS64 + ELF64
AArch64 + Windows + Windows ARM64 ABI + COFF/PE32+
AArch64 + macOS + Darwin arm64 + Mach-O
AArch64 + Android + Android/AArch64 ABI + ELF
RV64 + Linux + selected RISC-V ABI + ELF64
RV32 + bare metal + selected embedded ABI + ELF32
Armv8-M + bare metal + AAPCS/EABI + ELF32
Armv8-M + RTOS + declared RTOS/platform conventions
```

Platform restrictions such as code signing, entitlements, secure boot, firmware headers, or vendor image packaging remain explicit downstream platform concerns; they are not silently treated as properties proven by SpecIR verification.

## POC-1C — Raspberry Pi Pico 2 Hazard3 / RV32I subset

POC-1C uses the Hazard3 RISC-V cores in RP2350 as the first hardware-validation target while intentionally constraining Spec2Exec code generation to the RV32I base-integer subset.

```json
{
  "isa_profile": {
    "architecture": "riscv",
    "isa": "rv32i",
    "core": "hazard3",
    "extensions": []
  },
  "execution_profile": {
    "environment": "bare-metal",
    "abi": "ilp32-integer-subset",
    "assembly_dialect": "gnu-riscv",
    "object_model": "elf32-riscv"
  },
  "platform_profile": {
    "soc": "rp2350",
    "board": "raspberry-pi-pico-2",
    "processor_mode": "hazard3-riscv"
  }
}
```

The physical Hazard3 core may implement capabilities beyond this profile. Extra capabilities are outside the accepted POC-1C semantics unless explicitly enabled.

## POC-1D — Raspberry Pi Pico 2 Cortex-M33 / Armv8-M Mainline

POC-1D uses the same RP2350/Pico 2 platform in Arm mode.

```json
{
  "isa_profile": {
    "architecture": "arm",
    "isa": "armv8-m.main",
    "core": "cortex-m33",
    "endianness": "little"
  },
  "execution_profile": {
    "environment": "bare-metal",
    "abi": "aapcs-integer-subset",
    "floating_point_profile": "excluded-from-poc",
    "assembly_dialect": "gnu-arm",
    "object_model": "elf32-arm"
  },
  "platform_profile": {
    "soc": "rp2350",
    "board": "raspberry-pi-pico-2",
    "processor_mode": "cortex-m33"
  }
}
```

Floating-point, TrustZone/security-state behavior, DSP-specific operations, and other Cortex-M33/RP2350 features remain outside the initial POC-1D semantic scope unless explicitly enabled.

## POC-1E — Hosted target expansion

POC-1E begins the hosted target track. It should not be defined as "x86_64 equals desktop OS". Instead, it validates composition of ISA and Execution Profiles.

First hosted configurations should cover at least:

```text
x86_64 + Linux
x86_64 + Windows
AArch64 + Linux
AArch64 + macOS
```

Then extend the same model to additional valid combinations such as Windows on AArch64, Android on AArch64, and RV64 Linux.

This structure keeps reusable ISA code-generation concerns separate from OS/ABI/object-format concerns wherever the implementation permits.

## Cross-target model

```text
                              same Verified SpecIR
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
                 RISC-V             Arm             x86_64
               RV32 / RV64      M-profile/AArch64      │
                    │                 │                 │
                    └────────────┬────┴────────────┬────┘
                                 ▼                 ▼
                        Execution Profiles    Platform Profiles
                         Linux / Windows      Pico 2 / SoC / board
                         macOS / Android      bare-metal / RTOS
                         bare metal
                                 │
                                 ▼
                    Object / Link / Executable
```

The architecture claim is portability of accepted machine-independent semantics across compatible target configurations, not identical assembly or identical runtime mechanisms.

## Architectural rule

```text
SpecIR semantics
      !=
ISA Profile
      !=
Execution Profile
      !=
Platform Profile
```

Changing ISA, OS, ABI, object format, board, or runtime environment must not silently change the accepted machine-independent semantics of the same verified SpecIR.
