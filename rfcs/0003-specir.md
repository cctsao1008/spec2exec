# RFC 0003 — SpecIR

- **Status:** Draft

## Purpose

SpecIR is the formal contract between semantic synthesis and deterministic verification/lowering.

It is a formal intermediate representation, not a human-authored general-purpose source language. Humans must be able to inspect, review, diff, and debug it, but manual authoring is not the primary design center.

## Design objective

SpecIR should be:

- unambiguous;
- formally structured;
- typed;
- serializable;
- composable;
- versionable;
- target-independent where practical;
- human-inspectable;
- machine-authored by default;
- rich enough to preserve engineering contracts;
- traceable to accepted specification elements and provenance.

## Candidate semantic domains

### Core

- functions / operations;
- state;
- data flow;
- control flow;
- type system;
- interfaces;
- preconditions / postconditions;
- invariants;
- effects where relevant;
- provenance and semantic identity.

### Engineering extensions

- physical units;
- ranges / saturation;
- timing / deadlines;
- concurrency / ownership;
- resource limits;
- safety state / safe values;
- hardware interfaces;
- fault transitions;
- numerical precision constraints.

## Semantic status and provenance

SpecIR elements should be capable of preserving metadata that distinguishes, where relevant:

```text
declared
accepted
derived
assumed
unresolved
verified
```

A machine-checkable property must not be confused with a human-approved requirement, and a human-approved requirement must not be presented as formally proven merely because it was accepted.

## Formal-language boundary

SpecIR necessarily requires formal syntax and semantics sufficient for deterministic processing. This does not make human-facing programming ergonomics its purpose.

The distinction is architectural:

```text
General-purpose source language
    optimized for human → implementation

SpecIR
    optimized for synthesis → verification → lowering
```

Spec2Exec therefore does not require the claim that SpecIR is "not a language" in the broad formal sense. The important constraint is that SpecIR must not become the mandatory manually authored programming interface.

## Anti-goal

SpecIR must not evolve primarily around ergonomic manual syntax. If normal development requires engineers to hand-write large amounts of SpecIR, memorize its grammar, and use it as the main implementation language, the project risks recreating another general-purpose programming language and has failed an important design objective.

## Required work before stabilization

A stable SpecIR definition will require at minimum:

- a concrete schema or grammar;
- type and validity rules;
- execution / behavioral semantics for the minimal core;
- canonical serialization;
- versioning rules;
- traceability identifiers;
- deterministic verification rules;
- lowering rules for the supported proof-of-concept subset.
