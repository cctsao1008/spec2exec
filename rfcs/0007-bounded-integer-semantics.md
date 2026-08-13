# RFC 0007 — Experimental Bounded Integer Semantics

- **Status:** Draft / Experimental
- **Scope:** POC-1A semantic core

## Purpose

POC-1A is the first Spec2Exec experiment with nontrivial semantic contracts. Its goal is not language completeness. Its goal is a deliberately small integer subset that can support deterministic checking, translation validation, and exhaustive executable testing.

## Decisions

### Fixed-width integer types

The initial type set is:

```text
i32
u32
```

There is no abstract `int`, implicit widening, implicit signedness conversion, floating point, pointer, array, structure, or arbitrary-precision integer in POC-1A.

### Arithmetic subset

The body is straight-line and side-effect free. The initial arithmetic operators are:

```text
+  -  *
```

Comparisons and boolean operators are permitted in contracts. Division and remainder are deferred because divisor validity and signed rounding/remainder semantics deserve a separate experiment.

### Overflow semantics

POC-1A uses:

```text
overflow_behavior = forbidden
```

This is a specification/verification rule, not a request for C undefined behavior.

For every accepted input satisfying the declared preconditions, the verifier must establish that each arithmetic intermediate stays within the fixed-width machine type. If it cannot establish this, the SpecIR is rejected before lowering.

Future profiles may define other arithmetic behavior such as wrap, checked trap, fixed-point, or saturation. POC-1A does not freeze a universal overflow policy for all future SpecIR.

### Preconditions and behavior outside the contract domain

POC-1A uses **contract semantics**. Semantic claims apply to inputs satisfying accepted preconditions. Runtime enforcement of violated preconditions is deferred.

Behavior outside the accepted precondition domain is therefore outside POC-1A's semantic claim. It must not be described as proven or tested by the POC-1A evidence record.

### No intentional undefined behavior

The generated C path must not rely on signed overflow, invalid shifts, division by zero, uninitialized data, invalid pointer behavior, or other intentional C undefined behavior for any input inside the accepted contract domain.

### Representation

POC-1A may use a single expression tree. Long-term SpecIR is not required to remain tree-only. Immutable SSA-like intermediate values may be introduced when they improve graph representation, verification, lowering, or traceability.

Mutable assignment is not part of the POC-1A semantic core.

## Specification ↔ SpecIR projection

Specification and SpecIR are distinct artifacts with distinct roles:

- the accepted specification records authoritative engineering constraints and acceptance;
- SpecIR records the machine-oriented formal projection used for verification and lowering.

The verifier must reject:

```text
SpecIR constraint with no authoritative trace      → orphan constraint
accepted specification clause missing from SpecIR → missing projection
numerically different projected range             → drift
behavior expression different from accepted spec  → drift
```

POC-1A uses canonical projections for input ranges and the output relation so drift is deterministically detectable.

## P3 translation-validation granularity

POC-1A does **not** require AST-node identity between SpecIR and generated C.

The semantic obligation is boundary-oriented:

> Under accepted preconditions, does the generated C function produce the same observable return value as the SpecIR function?

For POC-1A, the validator extracts the exact emitted C return expression, independently parses that textual expression, translates both SpecIR and emitted-C models to SMT, and asks whether a valid input exists for which their results differ.

If the negated equivalence query is UNSAT, the evidence may record a narrow claim such as:

```text
subject: safe_add function output
property: SpecIR ↔ emitted C expression equivalence
status: PROVEN
scope: accepted input domain, POC-1A expression subset
```

This is not a proof of the C compiler or of arbitrary C.

## Traceability versus structural identity

Traceability and semantic equivalence are separate concerns.

Compiler/lowering optimizations may fold, merge, eliminate, or reorder nodes. Spec2Exec therefore must not require one-to-one AST-node correspondence as a condition of semantic preservation.

Traceability metadata may be many-to-many:

```text
requirement clause
   ↕
SpecIR node(s)
   ↕
lowered region / evidence claim
```

Optimization is acceptable when boundary semantics are preserved and provenance remains explainable at the supported granularity.

## P4 evidence

For sufficiently small declared domains, POC-1A invokes the compiled binary for every input combination and compares the result with the SpecIR evaluator.

Evidence is recorded as:

```text
TESTED_EXHAUSTIVE
```

For larger domains, later experiments may use boundary/property-based sampling and must use a weaker evidence label.

## Design guardrails

POC-1A explicitly avoids:

- syntax sugar;
- implicit casts;
- mutable local state;
- modules/imports/generics;
- loops/recursion;
- pointers/memory aliasing;
- floating point;
- hardware semantics;
- timing/concurrency semantics.

New semantic operations should not be accepted unless verification behavior, lowering behavior, and evidence implications are defined together.

## Falsification relevance

POC-1A begins measuring whether semantic contracts and preservation evidence provide useful engineering guarantees without simply recreating a human-authored programming language. Later POCs must compare engineering effort, traceability coverage, verification coverage, change propagation, and maintenance burden rather than relying on source-line counts alone.
