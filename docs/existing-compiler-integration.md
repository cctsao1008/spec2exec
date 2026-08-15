# Existing-Compiler Realization Experiment

## Purpose

Spec2Exec is not intended to become valuable only if it owns every compiler backend.

The native RV32I path remains important because it demonstrates that executable generation does not inherently require a human-oriented programming-language stage. This experiment answers a different question:

> Can the same trust/evidence model remain explicit when target realization is delegated to an existing compiler?

## Path

The experiment deliberately reuses the historical POC-0 C lowering:

```text
Accepted POC Specification
        ↓
SpecIR checks / trace linkage
        ↓
generated C
        ↓
host C compiler
        ↓
host executable
        ↓
runtime observation
```

## Evidence boundaries

The experiment-local claim IDs use RFC 0006 evidence statuses:

| Boundary | Status | Meaning |
|---|---|---|
| `CGEN.specir_to_c` | `TESTED` | The deterministic lowering is exercised and linked to the POC specification/runtime oracle; no formal equivalence proof is claimed. |
| `CC.c_to_executable` | `TRUSTED` | The exact external host C compiler/version/invocation is named as trusted infrastructure. |
| `CRUN.runtime_observation` | `TESTED` | The executable is run and stdout/exit status are checked against the accepted POC behavior. |
| `CRUN.sensitivity` | `TESTED` | A known-bad generated-C mutation is rebuilt and must be detected by the runtime oracle. |

`TRUSTED` is not `VERIFIED`. Runtime agreement does not prove compiler correctness.

## Relationship to native realization

```text
Native RV32I path
    demonstrates language-free target realization

Existing-compiler path
    demonstrates evidence-model composition with conventional toolchains
```

Neither path replaces the other.

The research value is that semantic authority, verification claims, tool trust, artifact hashes, and runtime observations remain separated even when realization strategy changes.
