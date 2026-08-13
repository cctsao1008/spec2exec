# RFC 0001 — Spec2Exec Architecture

- **Status:** Draft
- **Scope:** Foundational architecture

## Summary

Define Spec2Exec as a specification-centric software development architecture whose primary path is:

```text
Intent → Specification → Semantic Synthesis → SpecIR → Verification → Lowering → Executable
```

## Motivation

AI coding tools usually insert AI before a conventional programming language:

```text
Intent → AI → C/Rust/Python → Compiler → Executable
```

This leaves the programming language as the primary formal interface and commonly discards higher-level engineering semantics. Spec2Exec investigates whether a formal specification and machine-oriented intermediate representation can replace manually authored source as the main architectural contract.

## Decision

The architecture shall:

1. distinguish Intent, Specification, SpecIR, and Executable;
2. place a deterministic verification boundary before lowering;
3. reuse existing compiler backends;
4. retain requirement-to-runtime traceability;
5. permit C or another language as an early lowering target without treating generated source as the source of truth.

## Open questions

- What is the minimum semantic core of SpecIR?
- Which properties must be deterministic versus advisory?
- How should unresolved ambiguity be represented?
- What is the debug model when no primary human-authored source exists?
- What is the smallest meaningful proof of concept?
