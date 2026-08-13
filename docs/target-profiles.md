# Target and Platform Profiles

## Purpose

SpecIR remains machine-independent. Target-specific information is selected after SpecIR verification and must not be embedded into SpecIR merely to simplify code generation.

The architecture distinguishes two configuration layers:

```text
Verified SpecIR
      │
      ├── Target Profile
      │      CPU architecture / ISA
      │      core/profile where relevant
      │      enabled ISA subset/extensions
      │      ABI / calling-convention subset
      │      assembly dialect
      │      object model
      │
      └── Platform Profile
             bare-metal SoC / board, or hosted OS environment
             processor mode / architecture selection
             memory / image / loader conventions
             linker layout or executable format
```

A single ISA may therefore have multiple Target Profiles when the ABI or object model differs across execution environments.

## Target Profile

A Target Profile selects the machine semantics required by Target Code Generation.

Conceptual fields include:

```text
architecture
isa
core/profile where useful
endianness
enabled_extensions
abi
floating_point_profile when applicable
assembly_dialect
object_model
```

The exact serialization is intentionally not frozen yet.

## POC-1C — Raspberry Pi Pico 2 Hazard3 / RV32I subset

POC-1C uses the Hazard3 RISC-V cores in RP2350 as the first hardware-validation target while intentionally constraining Spec2Exec code generation to the RV32I base-integer subset.

```json
{
  "architecture": "riscv",
  "isa": "rv32i",
  "core": "hazard3",
  "extensions": [],
  "abi": "ilp32-integer-subset",
  "assembly_dialect": "gnu-riscv",
  "object_model": "elf32-riscv"
}
```

The physical Hazard3 core may implement capabilities beyond this profile. POC-1C deliberately keeps M/C/A/F/D and other optional/custom extensions outside the accepted target semantics unless a later architecture decision explicitly enables them.

Associated validation platform:

```json
{
  "soc": "rp2350",
  "board": "raspberry-pi-pico-2",
  "processor_mode": "hazard3-riscv"
}
```

## POC-1D — Raspberry Pi Pico 2 Cortex-M33 / Armv8-M Mainline

POC-1D uses the same RP2350/Pico 2 platform in Arm mode, allowing cross-target validation without changing the board or SoC.

```json
{
  "architecture": "arm",
  "isa": "armv8-m.main",
  "core": "cortex-m33",
  "endianness": "little",
  "abi": "aapcs-integer-subset",
  "floating_point_profile": "excluded-from-poc",
  "assembly_dialect": "gnu-arm",
  "object_model": "elf32-arm"
}
```

Associated validation platform:

```json
{
  "soc": "rp2350",
  "board": "raspberry-pi-pico-2",
  "processor_mode": "cortex-m33"
}
```

Floating-point, TrustZone/security-state behavior, DSP-specific operations, and other Cortex-M33/RP2350 architectural features are outside the initial POC-1D semantic scope unless explicitly added later.

## POC-1E — x86_64 hosted platform matrix

POC-1E extends the same machine-independent SpecIR to the x86_64 ISA and deliberately treats the operating-system ABI/object environment as part of the target boundary rather than assuming that `x86_64` alone uniquely identifies executable semantics.

The first hosted matrix is:

```text
x86_64 + Linux
x86_64 + Windows
x86_64 + macOS
```

These are separate Target Profiles sharing the same ISA.

### x86_64 / Linux

```json
{
  "architecture": "x86",
  "isa": "x86_64",
  "abi": "sysv-amd64-integer-subset",
  "assembly_dialect": "gnu-x86-64",
  "object_model": "elf64-x86-64"
}
```

Associated hosted Platform Profile:

```json
{
  "execution_environment": "hosted",
  "os": "linux",
  "architecture": "x86_64"
}
```

### x86_64 / Windows

```json
{
  "architecture": "x86",
  "isa": "x86_64",
  "abi": "microsoft-x64-integer-subset",
  "assembly_dialect": "toolchain-selected-x86-64",
  "object_model": "coff-x86-64",
  "executable_model": "pe32+"
}
```

Associated hosted Platform Profile:

```json
{
  "execution_environment": "hosted",
  "os": "windows",
  "architecture": "x86_64"
}
```

### x86_64 / macOS

```json
{
  "architecture": "x86",
  "isa": "x86_64",
  "abi": "darwin-x86_64-integer-subset",
  "assembly_dialect": "darwin-x86-64",
  "object_model": "mach-o-x86-64"
}
```

Associated hosted Platform Profile:

```json
{
  "execution_environment": "hosted",
  "os": "macos",
  "architecture": "x86_64"
}
```

The macOS profile is intentionally named separately rather than being collapsed into the Linux SysV profile: calling convention, symbol naming, object format, linker behavior, and executable conventions are target-environment concerns and must remain explicit.

POC-1E should begin with the same narrow arithmetic subset used by the earlier native experiments. The goal is not to build a complete x86 compiler backend; it is to test whether the same SpecIR semantics survive a third ISA family and multiple hosted ABI/object environments.

A later AArch64/arm64 hosted profile may be added independently. It is not required to begin POC-1E and must not be silently conflated with x86_64 macOS.

## Cross-target validation model

The planned architecture matrix is:

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

This provides representative architectural coverage rather than claiming complete ISA or operating-system coverage.

## Platform Profile

A Platform Profile captures execution-environment details that are not intrinsic to the ISA itself.

For bare-metal systems, conceptual fields may include:

```text
soc
board
processor_mode
flash_origin / flash_size
ram_origin / ram_size
linker_script or linker-layout identity
startup / vector-table policy
firmware image format
```

For hosted systems, conceptual fields may include:

```text
execution_environment
os
architecture
loader / executable environment
runtime assumptions
```

The RP2350/Pico 2 platform profile can be shared by both embedded native target experiments while selecting a different processor mode and Target Profile. Hosted x86_64 experiments instead select Linux, Windows, or macOS Platform Profiles with matching ABI/object Target Profiles.

## Architectural rule

```text
SpecIR semantics
      !=
Target Profile
      !=
Platform Profile
```

Changing the target or platform profile must not silently change the accepted machine-independent semantics of the same verified SpecIR.
