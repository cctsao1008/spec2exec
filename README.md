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

Native target code generation is the primary architecture path. C and LLVM are optional reference/comparison paths, not mandatory stages.

`Lowering` remains a transformation term, not a required top-level component. A named TargetIR/MachineIR is optional, while machine-oriented backend bookkeeping must remain explicit and testable.

Target-specific information is selected through a **Target Profile** after SpecIR verification. Optional **Platform Profiles** carry SoC/board memory and image-layout details. Neither is part of machine-independent SpecIR.

The native evidence path keeps SpecIR→assembly, assembly→object, object→linked executable, and runtime observation as separate claims.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  NEXT-ARCH    RV32I native pipeline validation
POC-1C.B  FOLLOW-UP    RV32I backend stress
POC-1D    PLANNED      cross-target Cortex-M3 / ARMv7-M
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1A and POC-1B remain valid C-based reference-path experiments.

POC-1C selects **RISC-V RV32I base integer** as the first native Target Profile, with M/C/A/F/D extensions excluded from the initial experiment.

POC-1C.A initially supports only target operations that are explicitly implemented for that profile. The first whitelist is `add` and `sub`; unsupported operations such as `mul` fail closed. The backend uses a bounded temporary-register pool, fails on register exhaustion, enforces a narrow integer ABI boundary, and emits machine-readable backend bookkeeping evidence.

POC-1C.B later stresses live-value pressure/spilling, a single branch/merge, and a single non-recursive call to determine whether an explicit TargetIR/MachineIR becomes justified.

POC-1D is planned as the first cross-target portability experiment using the same verified SpecIR with a **Cortex-M3 / ARMv7-M** Target Profile. **Cortex-M4 / ARMv7E-M** follows later, with FPU/float-ABI choices declared explicitly when used.

## Key documents

```text
docs/architecture.md
docs/phase1-plan.md
docs/target-profiles.md
rfcs/0001-spec2exec-architecture.md
rfcs/0006-semantic-preservation-and-evidence-model.md
rfcs/0009-native-target-code-generation.md
```

## License

License selection remains intentionally pending.
