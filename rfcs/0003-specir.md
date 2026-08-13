# RFC 0003 — SpecIR

- **Status:** Draft

## Purpose

SpecIR is the formal contract between semantic synthesis and deterministic verification/lowering.

## Design objective

SpecIR should be:

- unambiguous;
- typed;
- serializable;
- composable;
- target-independent where practical;
- human-inspectable;
- machine-authored by default;
- rich enough to preserve engineering contracts.

## Candidate semantic domains

### Core

- functions / operations;
- state;
- data flow;
- control flow;
- type system;
- interfaces;
- preconditions / postconditions;
- invariants.

### Engineering extensions

- physical units;
- ranges / saturation;
- timing / deadlines;
- concurrency / ownership;
- resource limits;
- safety state / safe values;
- hardware interfaces;
- fault transitions.

## Anti-goal

SpecIR must not evolve primarily around ergonomic manual syntax. If humans begin hand-writing SpecIR as the normal path, the project risks recreating another general-purpose programming language.
