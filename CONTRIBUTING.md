# Contributing to Spec2Exec

Spec2Exec is currently architecture-first. Contributions should preserve the distinction between specification-centric synthesis and ordinary AI code generation.

## Contribution flow

```text
Idea / problem / review finding
  ↓
Decide whether traceable engineering work is required
  ↓
Existing Issue?
  ├── yes → work under that Issue
  └── no
       ├── behavior / semantics / architecture / evidence / interface / validation affected
       │      → create Issue first
       └── non-semantic maintenance only
              → direct maintenance commit is acceptable
  ↓
Implementation
  ↓
Regression / evidence
  ↓
CI
  ↓
Commit references Issue when applicable
  ↓
Close Issue only after acceptance criteria pass
  ↓
Unlock dependent Issue / gate
```

## Issue-first engineering rule

Before modifying code, first decide whether the change needs an Issue.

Create or identify an Issue before implementation when the change affects any of the following:

- executable behavior or semantics;
- architecture or architecture boundaries;
- SpecIR, backend, ABI, target, or execution-profile behavior;
- evidence, verification, trust boundaries, or fail-closed behavior;
- interfaces or externally visible contracts;
- CI gates, validation scope, or POC experiments;
- bug fixes or review findings that require technical disposition.

Reuse an existing Issue when the work is already within its declared scope. Do not create one Issue per small edit when several edits are part of the same accepted engineering task.

Create a new Issue when a discovered problem is outside the active Issue's scope, can be independently accepted, affects later roadmap work, or will be deferred rather than repaired immediately.

A separate Issue is normally unnecessary for strictly non-semantic maintenance such as typo fixes, formatting, comment-only changes, small documentation corrections, or mechanical renames that do not alter behavior, evidence claims, interfaces, or validation results.

Do not create Issues retroactively merely to justify a commit. The Issue should state **why the change is needed and what acceptance means**; the commit should state **what implementation changed**.

For gated work, use the project rhythm:

```text
Issue
  ↓
Implementation
  ↓
Regression / Evidence
  ↓
CI
  ↓
Close Issue
  ↓
Unlock dependent Issue
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
