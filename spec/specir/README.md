# SpecIR

This directory contains the evolving normative and experimental definition of **SpecIR**, the formal machine-oriented representation between semantic synthesis and deterministic verification/lowering.

No syntax is frozen yet.

## Current status

RFC 0003 defines the architectural role and design constraints. Phase 1 will introduce a deliberately minimal **experimental** subset for the deterministic Hello World pipeline.

The experimental subset is a test vehicle, not a stable language specification.

## Design boundary

SpecIR must be:

```text
machine-oriented
formally structured
human-inspectable
machine-authored by default
optimized for synthesis → verification → lowering
```

It must not evolve into a mandatory manually authored general-purpose source language.

## Phase 1 rule

The first experimental SpecIR may be manually constructed only as a test fixture so the deterministic lower half can be tested without AI:

```text
Accepted Specification
      ↓
Manually Constructed Candidate SpecIR
      ↓
Verifier
      ↓
Lowering
      ↓
Executable
```

See `docs/phase1-plan.md` and RFC 0005 before introducing AI semantic synthesis.
