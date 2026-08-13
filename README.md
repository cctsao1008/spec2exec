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

Native target code generation is the primary architecture path. C and LLVM are optional reference or comparison paths, not mandatory stages.

`Lowering` remains a transformation term, not a required top-level component. A named TargetIR/MachineIR is optional, while machine-oriented backend bookkeeping must still be explicit and testable. It is promoted to a named representation when register/liveness/control-flow complexity justifies it.

The assembler and linker remain explicit downstream trust/evidence boundaries; a SpecIR-to-assembly semantic-preservation claim does not automatically prove the linked executable.

See `rfcs/0009-native-target-code-generation.md` for the architecture decision and hostile-review hardening.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  NEXT-ARCH    RV32I native pipeline proof
POC-1C.B  FOLLOW-UP    native backend stress
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1A and POC-1B remain valid C-based reference-path experiments.

POC-1C selects **RISC-V RV32I base integer** as the first native target profile, with M/C/A/F/D extensions excluded from the initial experiment. This target choice is not embedded into machine-independent SpecIR.

POC-1C.A will test:

```text
Verified SpecIR
    ↓
RV32I Target Code Generator
    ↓
RV32I Assembly
    ↓
Unmodified Assembler
    ↓
ELF32 Object
    ↓
Unmodified Linker
    ↓
RV32I ELF
    ↓
Emulator / Runtime Evidence
```

The first code generator must use a minimal register-resource model rather than a hard-coded assembly template for one example.

POC-1C.B will later stress multiple live values/spilling, a single branch/merge, and a single non-recursive function call. Those experiments determine when an explicit TargetIR/MachineIR becomes justified.

## Key documents

```text
docs/architecture.md
docs/phase1-plan.md
rfcs/0001-spec2exec-architecture.md
rfcs/0009-native-target-code-generation.md
```

## License

License selection remains intentionally pending.
