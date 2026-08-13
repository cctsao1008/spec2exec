# Contributing to Spec2Exec

Spec2Exec is currently architecture-first. Contributions should preserve the distinction between specification-centric synthesis and ordinary AI code generation.

## Contribution flow

```text
Idea
  ↓
Discussion
  ↓
RFC
  ↓
Accepted architecture / contract
  ↓
Issue
  ↓
Implementation
```

## Before implementation

For architectural changes, define:

- problem statement;
- scope and non-goals;
- semantic contract;
- verification boundary;
- lowering implications;
- traceability impact;
- failure modes;
- alternatives considered.

## Design rule

Do not introduce a human-facing syntax merely because it is convenient to implement. SpecIR is intended to be machine-oriented and human-inspectable, not human-authored by default.

## AI-generated contributions

AI may be used to synthesize proposals, code, tests, and documentation, but acceptance must depend on deterministic review, tests, static analysis, or formal verification appropriate to the artifact.
