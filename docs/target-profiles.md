# Target, Execution, Platform, and Validation Profiles

## Purpose

SpecIR remains machine-independent. Spec2Exec is intended to be implementable across major CPU ISA families and major operating-system/execution environments without changing machine-independent SpecIR semantics.

The architecture separates the executable target from the hardware used to validate it.

```text
Verified SpecIR
      │
      ├── ISA Profile
      │      architecture / ISA
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
             memory map
             startup / vector-table policy
             linker layout
             firmware packaging / signing where applicable
```

A concrete architectural target is the compatible composition:

```text
Target Configuration = ISA Profile + Execution Profile + optional Platform Profile
```

A **Validation Binding** records the concrete CPU core, SoC, board, emulator, or host used to validate that target configuration. Validation hardware is evidence infrastructure, not automatically part of the target semantics.

```text
Target Configuration
      ≠
Validation Binding
```

A CPU core implementation is also not identical to an ISA. For example, Hazard3 is a concrete RISC-V core used to validate an RV32I subset, while Cortex-M33 is a concrete Arm core used to validate an Armv8-M Mainline target profile.

## Architecture coverage goal

Initial architecture families are:

```text
CPU / ISA families
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

Android and generic RTOS coverage are intentionally outside the current implementation roadmap. A specific additional environment may be introduced later only through an explicit target decision.

The goal is not to implement the Cartesian product of every ISA and every OS. Each supported combination must have a valid ISA, ABI, object/executable model, toolchain, runtime, and platform definition.

## Example target configurations

```text
x86_64 + Linux + SysV AMD64 + ELF64
x86_64 + Windows + Microsoft x64 + COFF/PE32+
AArch64 + Linux + AAPCS64 + ELF64
AArch64 + Windows + Windows ARM64 ABI + COFF/PE32+
AArch64 + macOS + Darwin arm64 + Mach-O
RV64 + Linux + selected RISC-V ABI + ELF64
RV32I + bare metal + selected embedded ABI + ELF32
Armv8-M Mainline + bare metal + AAPCS/EABI + ELF32
```

Platform restrictions such as code signing, entitlements, secure boot, firmware headers, or vendor image packaging remain explicit downstream platform concerns; they are not silently treated as properties proven by SpecIR verification.

## POC-1C — RV32I bare-metal target

POC-1C is architecturally defined by its ISA and execution environment, not by Pico 2.

```json
{
  "isa_profile": {
    "architecture": "riscv",
    "isa": "rv32i",
    "extensions": []
  },
  "execution_profile": {
    "environment": "bare-metal",
    "abi": "ilp32-integer-subset",
    "assembly_dialect": "gnu-riscv",
    "object_model": "elf32-riscv"
  }
}
```

Initial validation binding:

```json
{
  "cpu_core": "hazard3",
  "soc": "rp2350",
  "board": "raspberry-pi-pico-2",
  "processor_mode": "hazard3-riscv"
}
```

The physical Hazard3 core may implement capabilities beyond the selected RV32I subset. Those capabilities are outside POC-1C semantics unless explicitly enabled by a later target decision.

## POC-1D — Armv8-M Mainline bare-metal target

POC-1D is the second embedded ISA target and reuses the same physical validation platform only to reduce unrelated hardware variation.

```json
{
  "isa_profile": {
    "architecture": "arm",
    "isa": "armv8-m.main",
    "endianness": "little"
  },
  "execution_profile": {
    "environment": "bare-metal",
    "abi": "aapcs-integer-subset",
    "floating_point_profile": "excluded-from-poc",
    "assembly_dialect": "gnu-arm",
    "object_model": "elf32-arm"
  }
}
```

Initial validation binding:

```json
{
  "cpu_core": "cortex-m33",
  "soc": "rp2350",
  "board": "raspberry-pi-pico-2",
  "processor_mode": "cortex-m33"
}
```

Floating-point, TrustZone/security-state behavior, DSP-specific operations, and other Cortex-M33/RP2350 features remain outside the initial POC-1D semantic scope unless explicitly enabled.

## Why Pico 2 is useful but not architectural

RP2350/Pico 2 is useful because one physical platform exposes both validation cores:

```text
                  Target architecture coverage

        RV32I / bare metal      Armv8-M / bare metal
                │                       │
                ▼                       ▼
             Hazard3               Cortex-M33
                │                       │
                └──────────┬────────────┘
                           ▼
                    RP2350 / Pico 2
                  validation platform
```

This allows cross-ISA hardware validation while holding the SoC/board largely constant. Replacing Pico 2 with another compatible validation platform must not require changing machine-independent SpecIR or redefining the architectural target.

## POC-1E — Hosted target expansion

POC-1E validates composition of ISA and hosted Execution Profiles.

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

This structure keeps reusable ISA code-generation concerns separate from OS/ABI/object-format concerns wherever technically meaningful.

## Architectural rule

```text
SpecIR semantics
      !=
ISA Profile
      !=
Execution Profile
      !=
Platform Profile
      !=
Validation Binding
```

Changing ISA, OS, ABI, object format, board, CPU core, emulator, or validation hardware must not silently change the accepted machine-independent semantics of the same verified SpecIR.
