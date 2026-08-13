# Design Principles

## P1 — Specification First

The architecture starts from required behavior and constraints rather than a chosen programming language.

## P2 — Preserve Semantics

Important engineering meaning must not be flattened into comments or lost before verification. Examples include units, ranges, timing, safety state, resource constraints, and ownership where relevant.

## P3 — AI Proposes; Verifier Decides

Probabilistic reasoning is useful for synthesis. Acceptance must depend on deterministic mechanisms.

## P4 — Avoid Textual Round Trips

Do not force structured semantics through a human-oriented programming language unless that representation provides a concrete engineering advantage.

## P5 — Reuse Mature Backends

LLVM, MLIR, existing linkers, ABI implementations, and verified compiler research are assets, not competitors.

## P6 — Explicit Ambiguity

Unresolved specification ambiguity should become a visible state or question, not a silently invented implementation choice.

## P7 — Traceability by Construction

Requirement, specification, SpecIR, verification evidence, generated artifacts, and runtime diagnostics should remain connected.

## P8 — Inspectable but Not Human-Authored by Default

SpecIR should be reviewable and serializable. Its design should not optimize for manual coding convenience.

## P9 — Domain-Aware Semantics

General-purpose semantics are necessary but may not be sufficient. Embedded/control systems may require timing, units, hardware interfaces, safety behavior, and bounded resources as first-class concepts.

## P10 — Incremental Adoption

Early Spec2Exec implementations may lower to C before moving directly to LLVM/MLIR. A temporary implementation language is acceptable if it is not mistaken for the architectural source of truth.
