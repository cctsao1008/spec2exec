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
      └── Platform Profile (optional)
             SoC / board identity
             processor mode / architecture selection
             memory map
             Flash / RAM placement
             startup / image conventions
             linker layout
```

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

## Why use the same Pico 2 platform

RP2350 can execute using either its Cortex-M33 pair or its Hazard3 RISC-V pair. This creates a useful portability experiment:

```text
                     same Verified SpecIR
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
        Hazard3 / RV32I       Cortex-M33 / Armv8-M
                 │                     │
                 ▼                     ▼
          RISC-V assembly          Arm assembly
                 │                     │
                 └──────────┬──────────┘
                            ▼
                    same RP2350 / Pico 2
```

The experiment therefore changes the processor architecture while holding the physical development platform largely constant.

## Platform Profile

A Platform Profile is optional and captures SoC/board details that are not intrinsic to the CPU ISA.

Conceptual fields may include:

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

The RP2350/Pico 2 platform profile can be shared by both native target experiments while selecting a different processor mode and Target Profile.

## Architectural rule

```text
SpecIR semantics
      ≠
Target Profile
      ≠
Platform Profile
```

Changing the target or platform profile must not silently change the accepted machine-independent semantics of the same verified SpecIR.

The planned cross-target experiment therefore uses the same verified SpecIR first with the Pico 2 Hazard3/RV32I target and then with the Pico 2 Cortex-M33/Armv8-M Mainline target while keeping target-specific semantics below the Target Code Generation boundary.
