# RFC 0001 — Spec2Exec Architecture

- **Status:** Draft
- **Scope:** Foundational architecture

## Summary

Spec2Exec is a specification-centric software development architecture and research hypothesis. It investigates whether specifications can become the primary engineering artifact between human intent and executable software without requiring manually authored general-purpose source code as the mandatory interface.

The primary path is:

```text
Human Intent
    ↓
Draft Specification
    ↓
Semantic Resolution / Synthesis
    ↓
Resolved Specification
    ↓
Human / Domain Specification Acceptance
    ↓
Accepted Specification
    ↓
Semantic Synthesis
    ↓
Candidate SpecIR
    ↓
Deterministic Verification
    ↓
Lowering
    ↓
Compiler Backend
    ↓
Executable
```

## Motivation

AI coding tools usually insert AI before a conventional programming language:

```text
Intent → AI → C/Rust/Python → Compiler → Executable
```

This leaves programming-language source as the primary formal interface and often loses higher-level engineering semantics such as units, timing, assumptions, safety constraints, failure behavior, provenance, and requirement identity.

Spec2Exec investigates whether an accepted specification plus a machine-oriented formal intermediate representation can serve as the primary architectural contract instead.

## Trust model

Spec2Exec separates three distinct correctness questions:

1. **Intent fidelity** — does the accepted specification represent what the human/domain authority actually intends?
2. **Specification / SpecIR correctness** — is the formal representation internally consistent and compliant with declared contracts?
3. **Implementation conformance** — does the generated executable preserve the verified SpecIR semantics through lowering and compilation?

These questions have different authorities. Deterministic verification cannot prove that an incorrect specification matches human intent.

## Decision

The architecture shall:

1. distinguish Intent, Draft Specification, Accepted Specification, SpecIR, and Executable;
2. make unresolved ambiguity and assumptions explicit rather than silently inventing requirements;
3. include a human/domain specification acceptance gate where intent fidelity matters;
4. treat AI semantic synthesis as untrusted candidate generation;
5. place deterministic verification before lowering;
6. distinguish proven, checked, tested, estimated, and advisory claims;
7. reuse existing compiler backends;
8. retain requirement-to-runtime traceability and provenance;
9. permit C or another language as an early lowering target without treating generated source as the source of truth.

## Non-claim

Spec2Exec does not claim to solve the general intent problem or prove specification completeness. Its goal is to make unresolved semantics, assumptions, authority, and verification evidence explicit and auditable.

## Open questions

- What is the minimum semantic core of SpecIR?
- Which properties must be deterministic versus advisory?
- How should unresolved ambiguity, assumptions, and provenance be represented?
- What constitutes sufficient specification acceptance for a target domain?
- What is the debug model when no primary human-authored source exists?
- How can lowering preserve traceability and verified properties?
- What is the smallest meaningful proof of concept beyond pipeline plumbing?
