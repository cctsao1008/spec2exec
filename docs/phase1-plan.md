# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **Next architecture experiment:** POC-1C — First Native Target Backend
- **Next semantic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Adversarial Semantic Resolution

## Objective

Phase 1 tests the deterministic lower half without connecting AI to executable generation.

Following RFC 0009, the primary architecture is now:

```text
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

C and LLVM are optional reference/comparison paths rather than mandatory architecture stages.

## POC-1A — Bounded Integer Semantics

POC-1A uses `i32/u32`, straight-line `+ - *`, ranges, pre/postconditions, traceability, and `overflow_behavior = forbidden`.

The hardened implementation distinguishes:

```text
P2.no_signed_overflow_ub
P2.no_unsigned_wraparound
```

P3-A uses a model-scoped 32-bit bit-vector claim:

```text
P3A.restricted_emitted_expression_equivalence = SOLVER_PROVEN
semantic_model = fixed-width-bitvector-v1
```

Its recorded obligations are:

```text
Q0 domain_non_vacuous       SAT
Q1 no_overflow_or_wrap      UNSAT
Q2 encoder_cross_check      UNSAT
Q3 result_equivalence       UNSAT
Q4 harness_sensitivity      SAT
```

P2 interval analysis and P3-A bit-vector safety cross-validate each other. For `safe_add`, P4 executes all 10,201 accepted input pairs and records `TESTED_EXHAUSTIVE`.

## POC-1B — C Semantic and Optimization Preservation

POC-1B adds an independent C-aware reference path using CBMC.

```text
function: safe_add_sub
body:     (a + b) - b
a,b:      i32 [-100,100]
overflow: forbidden
contract: result == a
```

The first successful CI run recorded:

```text
P3-A BitVec model             SOLVER_PROVEN
P3-B generated-C contract     MODEL_CHECKED
Clang -O0 add/sub count       2
Clang -O2 add/sub count       0
P4 exhaustive cases           40,401
POC-1B result                 PASS
```

This remains valid reference-path evidence. It does not make generated C a mandatory final architecture stage. See RFC 0008 and RFC 0009.

## POC-1C — First Native Target Backend

POC-1C should prove that the architecture can bypass a high-level-language compiler and generate target assembly directly from verified SpecIR.

Minimal objective:

```text
Verified SpecIR
      ↓
Target Code Generator
      ↓
Target Assembly
      ↓
Existing Assembler
      ↓
Object
      ↓
Linker
      ↓
Executable / Firmware Artifact
```

POC-1C should remain intentionally small. The first backend should reuse the current bounded-arithmetic semantic core and should not introduce state, timing, memory aliasing, or hardware-register semantics at the same time.

Required evidence should distinguish:

```text
SpecIR semantic verification
target-code-generation preservation evidence
assembler/object artifact identity
linker/image construction evidence
runtime or emulator behavior when practical
```

The target ISA/profile remains an explicit selection decision rather than an assumption baked into SpecIR.

## A0 — Semantic Resolution

A0 remains independent from executable generation. The benchmark/scoring harness exists; model baselines have not yet been run.

## POC-2 — State Machine

POC-2 remains the next semantic-complexity experiment. It should introduce persistent finite-state behavior and measure transition correctness, invariant burden, solver scaling, evidence coverage, and SpecIR maintenance cost without simultaneously adding timing or hardware semantics.

POC-1C and POC-2 answer different questions: POC-1C validates the native target architecture; POC-2 validates behavioral-state semantics.

## POC-3 — Thermal Motor Protection

POC-3 remains the first domain-significant embedded/control experiment, adding physical quantities, timing, fault/recovery behavior, provenance, and unresolved-requirement handling.

## Falsification orientation

The project should continue measuring engineering effort, defect detection, traceability, verification coverage, change propagation, and maintenance burden. A technically working pipeline is not sufficient evidence of value if its specification/verifier/backend complexity outweighs the benefits.
