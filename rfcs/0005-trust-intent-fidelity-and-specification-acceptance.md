# RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance

- **Status:** Draft
- **Scope:** Trust model and the boundary between human intent and machine-verifiable artifacts

## Problem

Formal verification can establish that an artifact satisfies a formal specification, but it cannot generally establish that the formal specification represents what a human actually intended.

This distinction is fundamental to Spec2Exec.

A pipeline may be internally perfect and still produce the wrong behavior if the accepted specification is wrong:

```text
Human intent: shut down motor above 90 degC
        ↓
Incorrect specification: shut down above 120 degC
        ↓
Formally consistent SpecIR
        ↓
Correct lowering
        ↓
Correct executable for the wrong requirement
```

Downstream verification does not repair the intent/specification mismatch.

## Decision

Spec2Exec shall explicitly separate:

```text
Intent fidelity
Specification correctness
Implementation conformance
```

No single PASS state may imply all three unless separate evidence exists for each applicable layer.

## Architecture

```text
Human Intent
     ↓
Draft Specification
     ↓
AI-assisted Semantic Resolution
     │
     ├── ambiguity / missing semantics ─────┐
     │                                     │
     ▼                                     │
Resolved Specification                    │
     │                                     │
     ▼                                     │
Human / Domain Specification Gate ◄────────┘
     │
     ▼
Accepted Specification
     ↓
Semantic Synthesis (untrusted)
     ↓
Candidate SpecIR
     ↓
──── deterministic trust boundary ────
     ↓
Verification
     ↓
Lowering / Compiler Backend
     ↓
Executable
```

## Human / domain specification gate

The specification gate exists to establish accountable acceptance of externally observable and domain-significant behavior before it is treated as the source of truth.

The gate may vary by domain:

- an individual developer for an exploratory example;
- a system engineer for an embedded product;
- a safety authority for a safety-critical subsystem;
- a formal review workflow for regulated software.

Spec2Exec does not prescribe one universal governance process, but the authority and acceptance state must be representable.

## Ambiguity handling

The system must prefer explicit uncertainty over invented certainty.

Examples of semantic states include:

```text
KNOWN
ASSUMED
DERIVED
UNRESOLVED
ACCEPTED
VERIFIED
```

If a required value is absent, the synthesis system should emit a structured unresolved item instead of selecting a plausible value without provenance.

Example:

```text
thermal_shutdown_threshold:
    status: unresolved
    reason: no authoritative threshold supplied
    blocks: production_release
```

## Provenance

Important semantics should retain provenance such as:

```text
requirement_id
source
revision
authority
acceptance_state
derivation
verification_evidence
```

The objective is not administrative overhead. The objective is to prevent an AI-derived assumption from becoming indistinguishable from an authoritative requirement.

## Trust principle

**Semantic synthesis is untrusted.**

AI, search, heuristics, solvers, planners, and other synthesis mechanisms may propose candidate semantics. Their output only gains specific evidence status after the appropriate acceptance or deterministic checks.

## Non-goals

Spec2Exec does not claim to:

- read a person's mind;
- automatically prove that a specification is complete in the general case;
- eliminate human responsibility for domain decisions;
- treat verifier success as proof of intent fidelity;
- eliminate all assumptions or uncertainty.

## Research objective

The research question is narrower and more testable:

> Can uncertainty, assumptions, provenance, human authority, deterministic verification, and implementation conformance be represented explicitly enough that unverified semantics do not silently become executable truth?

## Consequence for proof of concept

The first implementation should not begin with AI generation. It should first prove the deterministic lower half of the architecture:

```text
Manually constructed minimal SpecIR
        ↓
Parser / loader
        ↓
Deterministic verifier
        ↓
Lowering
        ↓
C or LLVM IR
        ↓
Existing compiler backend
        ↓
Executable
```

AI semantic synthesis should be introduced only after this path is independently testable.
