# RFC 0007 — Experimental Bounded Integer Semantics

- **Status:** Draft / Experimental
- **Scope:** POC-1A semantic core and P3-A evidence

## Purpose

POC-1A is the first Spec2Exec experiment with nontrivial semantic contracts. Its goal is a deliberately small integer subset that supports deterministic checking, model-scoped translation validation, and exhaustive executable testing.

## Semantic core

The initial types are:

```text
i32
u32
```

The body is straight-line and side-effect free. The arithmetic subset is:

```text
+  -  *
```

Division, remainder, floating point, pointers, arrays, structures, loops, recursion, mutable local state, implicit casts, concurrency, timing, and hardware semantics remain outside POC-1A.

## Overflow policy

POC-1A uses:

```text
overflow_behavior = forbidden
```

For every accepted input, each arithmetic intermediate must remain within the declared fixed-width type.

The evidence distinguishes the reason:

```text
i32 overflow       P2.no_signed_overflow_ub
u32 wrap/underflow P2.no_unsigned_wraparound
```

Both are blocking under the current `forbidden` policy. Future profiles may define other runtime arithmetic policies.

## Contract domain

Semantic claims apply only to accepted inputs satisfying the declared preconditions. Runtime handling of precondition violations is not defined by POC-1A.

Behavior outside that domain must not be represented as verified evidence.

## Specification ↔ SpecIR projection

The accepted specification and SpecIR are distinct artifacts. Machine-comparable semantics must remain linked by trace identifiers and deterministic checks.

The verifier rejects orphan constraints, missing accepted clauses, range drift, type drift, and behavior-expression drift.

## P2 safety check

P2 uses deterministic interval analysis to check all arithmetic intermediates and output-range containment.

This analysis is not treated as the sole proof mechanism. P3-A independently checks the same arithmetic-safety condition with a bit-vector model. The two results cross-validate each other; disagreement rejects the preservation claim.

## P3-A — model-scoped translation validation

The initial POC used mathematical integers and described the result too broadly as `PROVEN`. The hardened experiment replaces that wording and model.

P3-A uses 32-bit bit-vectors and records:

```text
claim: P3A.restricted_emitted_expression_equivalence
status: SOLVER_PROVEN
semantic_model: fixed-width-bitvector-v1
scope.target: restricted emitted-expression model
```

`SOLVER_PROVEN` means the declared solver obligations succeeded under the named model, scope, assumptions, and trusted components. It is not a claim of complete C source semantics or compiler correctness.

The proof obligations are deliberately separate:

```text
Q0 domain non-vacuous           expected SAT
Q1 no overflow or wrap          expected UNSAT
Q2 safety encodings agree       expected UNSAT
Q3 result mismatch              expected UNSAT
Q4 known mutation detectable    expected SAT
```

Q3 runs in a fresh solver context without assuming Q1 safety predicates. This prevents a contradictory safety condition from making result equivalence vacuously true.

Each arithmetic node receives its own safety obligation. Signed inputs use signed bit-vector range comparisons; unsigned inputs use unsigned comparisons.

## Literal typing and host-C model

C literal typing is part of lowering semantics. A fixed-width SpecIR model must not be silently changed by a wider C literal type.

The experimental lowering uses:

```text
i32 minimum value → INT32_MIN
i32 other values  → int-compatible literal form
u32 values        → UINT32_C(value)
```

The host-C artifact also checks the prototype's expected `int32_t`/`uint32_t` widths and aliases where supported by the compiler.

These restrictions are intentionally narrow. A future general C lowering contract must model C type conversions explicitly rather than relying on host assumptions.

## Artifact binding

Evidence is bound to exact artifacts with SHA-256 identifiers for the SpecIR and generated C source. A build step rejects a generated C source whose hash differs from the source validated by P3-A.

## Traceability versus structure

Spec2Exec does not require one-to-one AST or instruction identity. Optimization may fold, merge, eliminate, or reorder internal nodes.

Traceability is therefore allowed to be many-to-many and is anchored in accepted requirements/contracts, SpecIR semantics, evidence claims, and artifact identities.

POC-1B tests this decision directly. See RFC 0008.

## P4 evidence

For sufficiently small domains, the compiled binary is invoked for every accepted input combination and compared with the SpecIR evaluator.

```text
status: TESTED_EXHAUSTIVE
```

POC-1A refuses domains above the configured exhaustive limit. A future sampled mode must use an explicitly weaker evidence label rather than silently degrading `TESTED_EXHAUSTIVE`.

## Nonclaims

POC-1A does not prove human intent fidelity, general specification completeness, complete C semantics, compiler correctness, machine-code equivalence, or behavior outside accepted preconditions.

## Design guardrail

A new semantic operation should not enter SpecIR unless its verification behavior, lowering behavior, evidence implications, and failure semantics are defined together.
