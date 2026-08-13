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

`Lowering` remains a transformation term, not a required top-level component. Backend-internal IRs may be introduced when concrete complexity justifies them.

See `rfcs/0009-native-target-code-generation.md` for the architecture decision.

## Status

```text
POC-0   COMPLETE
POC-1A  COMPLETE
POC-1B  COMPLETE
POC-2   NEXT
POC-3   PLANNED
A0      PARALLEL
```

POC-1A and POC-1B remain valid reference-path experiments using generated C. Their evidence is scoped to those experiments and does not make C a required final architecture stage.

## License

License selection remains intentionally pending.
