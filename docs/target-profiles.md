# Target and Platform Profiles

## Purpose

SpecIR remains machine-independent. Target-specific information is selected after SpecIR verification and must not be embedded into SpecIR merely to simplify code generation.

The architecture distinguishes two configuration layers:

```text
Verified SpecIR
      │
      ├── Target Profile
      │      CPU architecture / ISA
      │      enabled ISA extensions
      │      ABI / calling-convention subset
      │      assembly dialect
      │      object model
      │
      └── Platform Profile (optional)
             SoC / board identity
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

### POC-1C — RV32I

```json
{
  "architecture": "riscv",
  "isa": "rv32i",
  "extensions": [],
  "abi": "ilp32-integer-subset",
  "assembly_dialect": "gnu-riscv",
  "object_model": "elf32-riscv"
}
```

POC-1C keeps M/C/A/F/D extensions disabled.

### Later ARM target — Cortex-M3

```json
{
  "architecture": "arm",
  "isa": "armv7-m",
  "core": "cortex-m3",
  "endianness": "little",
  "abi": "aapcs-integer-subset",
  "fpu": "none",
  "assembly_dialect": "gnu-arm",
  "object_model": "elf32-arm"
}
```

### Later ARM target — Cortex-M4

```json
{
  "architecture": "arm",
  "isa": "armv7e-m",
  "core": "cortex-m4",
  "endianness": "little",
  "abi": "aapcs-integer-subset",
  "fpu": "none-or-explicit-profile",
  "assembly_dialect": "gnu-arm",
  "object_model": "elf32-arm"
}
```

A Cortex-M4 profile with floating-point support must explicitly declare the selected FPU and floating-point ABI rather than treating all Cortex-M4 targets as identical.

## Platform Profile

A Platform Profile is optional and captures SoC/board details that are not intrinsic to the CPU ISA.

Conceptual fields may include:

```text
soc
board
flash_origin / flash_size
ram_origin / ram_size
linker_script or linker-layout identity
startup / vector-table policy
firmware image format
```

For example, STM32F103 and another Cortex-M3 SoC may share the same ARMv7-M Target Profile while using different Platform Profiles for memory layout and startup conventions.

## Architectural rule

```text
SpecIR semantics
      ≠
Target Profile
      ≠
Platform Profile
```

Changing the target or platform profile must not silently change the accepted machine-independent semantics of the same verified SpecIR.

This separation is intended to make cross-target experiments meaningful: the same verified SpecIR can later be generated for RV32I and Cortex-M3/M4 while target-specific semantics remain below the Target Code Generation boundary.
