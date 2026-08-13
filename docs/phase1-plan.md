# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **Phase 0 architecture definition:** complete for the initial prototype baseline
- **POC-0:** complete
- **Current deterministic experiment:** POC-1A — Bounded Integer Semantics
- **Parallel research track:** A0 — Adversarial Semantic Resolution Benchmark

## Objective

Phase 1 tests the lower half of the Spec2Exec architecture without connecting AI to executable generation.

```text
Accepted Specification
      ↓
Candidate SpecIR
      ↓
Deterministic Verification
      ↓
Semantic-Preservation Evidence
      ↓
Lowering
      ↓
Existing Compiler Backend
      ↓
Executable
```

AI semantic resolution is studied independently in A0 so the upper-half risk can be measured without contaminating the deterministic implementation experiments.

## POC-0 — Hello World

**Status: Complete**

POC-0 established repository plumbing, accepted-specification linkage, a tiny SpecIR representation, deterministic verification, C lowering, executable generation, runtime checks, negative tests, and CI reproduction.

It did not establish nontrivial arithmetic semantics or lowering equivalence.

## POC-1A — Bounded Integer Semantics

### Goal

Introduce the first nontrivial SpecIR contracts while keeping the semantic surface deliberately small.

The experimental core is:

```text
i32 / u32
+ - *
comparisons / booleans in contracts
input/output ranges
preconditions
postconditions
overflow_behavior = forbidden
straight-line, side-effect-free body
traceability
```

Explicitly deferred:

```text
float
/ and %
loops / recursion
pointers / memory aliasing
arrays / structs
mutable local state
implicit casts
concurrency
timing
hardware I/O
```

### Contract-domain rule

POC-1A semantic claims apply only to inputs satisfying the accepted preconditions. Runtime enforcement of violated preconditions is a later experiment.

Behavior outside the accepted contract domain is not claimed to be verified by POC-1A.

### P1 — Accepted Specification → SpecIR

POC-1A must reject:

- an untraceable numeric constraint;
- an accepted specification clause missing from SpecIR;
- a projected range that differs from the accepted specification;
- a behavior expression that differs from the accepted specification.

Specification and SpecIR therefore remain different artifacts, but drift between their machine-comparable semantics is a deterministic verification failure.

### P2 — SpecIR checks

POC-1A checks:

- fixed-width integer types;
- range validity within the declared machine type;
- canonical precondition projection;
- canonical output/postcondition projection;
- static exclusion of arithmetic overflow over the accepted input domain;
- output-range containment;
- traceability coverage.

### P3 — Translation validation

POC-1A uses boundary-level semantic equivalence rather than AST-node identity.

```text
SpecIR function semantics
          ↓
   emitted C function
```

The validator extracts the exact emitted C return expression, parses it independently, translates the SpecIR and emitted-C expressions to SMT, and asks whether any accepted input makes their outputs differ.

An UNSAT result supports a narrow `PROVEN` claim for function-output equivalence within the supported POC-1A expression subset and assumptions.

It does not prove the C compiler.

### P4 — Executable behavior

For the initial small input domain, the compiled shared-library function is invoked for every accepted input combination and compared with the SpecIR evaluator.

Evidence is recorded as:

```text
TESTED_EXHAUSTIVE
```

Later larger domains may require weaker sampled evidence and must be labeled accordingly.

### P3 granularity decision

Traceability must not require one-to-one AST/node identity. Optimizations may fold or eliminate intermediate nodes. Semantic preservation is judged at a declared contract boundary such as function input/output or, in later POCs, a state-transition boundary.

Provenance may therefore be many-to-many and is distinct from structural identity.

See RFC 0007.

## A0 — Adversarial Semantic Resolution Benchmark

### Goal

Measure whether an AI semantic-resolution system can expose missing, ambiguous, and conflicting requirements instead of inventing plausible executable values.

A0 is intentionally disconnected from the executable pipeline.

Initial decisions:

```text
RESOLVED
UNRESOLVED
CONFLICT
```

Initial metrics include:

- unsafe resolution rate;
- unresolved recall;
- conflict recall;
- resolved-case accuracy;
- overall decision accuracy.

No favorable threshold is selected in advance. Initial runs establish baselines and an error taxonomy.

## POC-1B — Preservation Stress Tests

After the initial POC-1A path is stable, add deliberately transformed expressions to test whether translation validation survives legal algebraic rewrites without requiring node-for-node correspondence.

The objective is to test the distinction between traceability provenance and semantic equivalence before POC-2 introduces state.

## POC-2 — State Machine

Purpose: introduce persistent behavioral state and test whether preservation evidence still scales.

Planned measurements include:

- state/transition semantics;
- invalid-transition rejection;
- state invariants;
- translation-validation solver time versus state-space size;
- amount of human-supplied invariant information required;
- SpecIR maintenance burden and architecture drift indicators.

## POC-3 — Thermal Motor Protection

Purpose: first domain-significant embedded/control example.

Candidate capabilities:

- physical quantity semantics;
- thresholds and timing;
- safe output values;
- fault states;
- recovery behavior;
- unresolved requirement handling;
- provenance and specification acceptance.

POC-3 should also provide a controlled comparison against a source-centric implementation with explicit contracts/tests to test whether Spec2Exec provides enough additional traceability, verification coverage, or change-propagation value to justify its extra machinery.

## Falsification orientation

The project should treat these as warning classes rather than move the goalposts indefinitely:

1. specification/semantic-resolution burden does not decrease enough to justify the architecture;
2. semantic-preservation evidence becomes disproportionately expensive as state/control complexity increases;
3. SpecIR drifts into a mandatory human-authored programming language;
4. verified/checked evidence coverage declines while `TRUSTED`, `ASSUMED`, and `UNRESOLVED` dominate real examples;
5. source-centric workflows with existing contract/formal tools match or exceed Spec2Exec on relevant engineering outcomes.

Metrics should emphasize engineering effort, defect detection, traceability coverage, verification coverage, change propagation, retargeting, and maintenance burden rather than raw line counts alone.
