# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C experiment
- **Next deterministic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Adversarial Semantic Resolution

## Objective

Phase 1 tests the deterministic lower half without connecting AI to executable generation.

```text
Accepted Specification
      ↓
SpecIR
      ↓
Deterministic Verification
      ↓
Preservation Evidence
      ↓
Lowering / Compiler
      ↓
Executable
```

## POC-1A — Bounded Integer Semantics

POC-1A uses `i32/u32`, straight-line `+ - *`, ranges, pre/postconditions, traceability, and `overflow_behavior = forbidden`.

The hardened implementation distinguishes:

```text
P2.no_signed_overflow_ub
P2.no_unsigned_wraparound
```

P3-A now uses a model-scoped 32-bit bit-vector claim instead of the earlier bare `PROVEN` wording:

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

P2 interval analysis and P3-A bit-vector safety cross-validate each other. Generated C uses type-aware integer literals and exact SpecIR/C hashes bind evidence to the compiled source.

For `safe_add`, P4 still executes all 10,201 accepted input pairs and records `TESTED_EXHAUSTIVE`.

## POC-1B — C Semantic and Optimization Preservation

POC-1B adds an independent C-aware path using CBMC.

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

The optimization observation has no semantic proof status by itself. It demonstrates that the original add/sub structure disappeared while contract-level evidence and exhaustive behavior checks remained available.

This supports only a narrow result: for the current straight-line bounded-integer example, traceability does not require one-to-one node identity.

POC-1B does not claim compiler correctness, machine-code equivalence, target ABI correctness, or hardware semantics. See RFC 0008.

## A0 — Semantic Resolution

A0 remains independent from executable generation. The benchmark/scoring harness exists; model baselines have not yet been run.

## POC-2 — State Machine

POC-2 should introduce persistent finite-state behavior and measure transition correctness, invariant burden, solver scaling, evidence coverage, and SpecIR maintenance cost without simultaneously adding timing or hardware semantics.

## POC-3 — Thermal Motor Protection

POC-3 remains the first domain-significant embedded/control experiment, adding physical quantities, timing, fault/recovery behavior, provenance, and unresolved-requirement handling.

## Falsification orientation

The project should continue measuring engineering effort, defect detection, traceability, verification coverage, change propagation, and maintenance burden. A technically working pipeline is not sufficient evidence of value if its specification/verifier complexity outweighs the benefits.
