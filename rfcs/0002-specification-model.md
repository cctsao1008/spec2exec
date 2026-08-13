# RFC 0002 — Specification Model

- **Status:** Draft

## Goal

Define what qualifies as a Spec2Exec specification and how incomplete human intent becomes an executable-ready contract without hiding ambiguity or assumptions.

## Proposed layers

```text
Intent
  ↓
Draft Specification
  ↓
Semantic Resolution
  ↓
Resolved Specification
  ↓
Human / Domain Acceptance
  ↓
Accepted Specification
  ↓
Formalized Specification / SpecIR
```

## Required properties

A specification should be able to express, when relevant:

- observable behavior;
- inputs and outputs;
- data types and domains;
- invariants;
- error and failure behavior;
- environmental assumptions;
- timing and resource constraints;
- hardware/software interfaces;
- acceptance criteria;
- provenance and requirement identity;
- unresolved semantics;
- authority / approval status.

## Semantic status

Specification elements should be able to carry an explicit status such as:

- `declared` — supplied directly by an authoritative requirement;
- `derived` — mechanically or logically derived from other accepted facts;
- `assumed` — required for progress but not yet established;
- `unresolved` — missing or ambiguous semantics that require resolution;
- `accepted` — reviewed and accepted by the relevant human/domain authority;
- `verified` — checked by a named deterministic verification mechanism.

The exact vocabulary may change, but Spec2Exec must not collapse these categories into a single notion of "correct".

## Ambiguity rule

A synthesis engine must not invent a safety-critical or externally observable requirement merely to make compilation possible. Missing required semantics must become an explicit unresolved item.

## Specification acceptance gate

Deterministic verification can establish consistency with formal rules, but cannot establish that a specification faithfully represents human intent. Where intent fidelity matters, progression to an executable-release path requires an explicit specification acceptance step by a human or domain authority.

Acceptance does not mean that the specification is mathematically complete. It means that the responsible authority has reviewed the resolved behavior, assumptions, and unresolved items allowed for that release class.

## Release blocking rule

A target or domain may declare classes of unresolved items as blocking. For example:

```text
required unresolved safety item > 0
    → production lowering rejected
```

Prototype and exploratory modes may use different policies, but the mode and remaining uncertainty must be explicit.

## Provenance

Every accepted or derived semantic element should be traceable toward its origin where practical:

```text
SpecIR node
  ↑
Specification clause
  ↑
Requirement / decision / assumption
  ↑
Authority and acceptance evidence
```

## Non-claim

Spec2Exec does not claim that specification completeness can be automatically proven in the general case. The architecture instead makes incompleteness, assumptions, and authority visible and machine-trackable.
