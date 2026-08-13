# RFC 0006 — Semantic Preservation and Evidence Model

- **Status:** Draft
- **Scope:** Transformation obligations and evidence across the Spec2Exec pipeline

## Problem

Spec2Exec contains several transformations between authoritative engineering intent and executable behavior. A verifier PASS at one layer does not automatically prove semantic preservation across every later transformation.

The architecture must therefore make each transformation obligation and its evidence explicit.

```text
Accepted Specification
        ↓  P1
Candidate SpecIR
        ↓  P2
Verified-for-declared-properties SpecIR
        ↓  P3
Lowered Artifact
        ↓  P4
Executable
```

## Decision

Spec2Exec shall not use a single undifferentiated notion of "correct" or "verified" for the entire pipeline.

Each property claim must identify:

- the subject artifact;
- the property being claimed;
- the evidence class;
- assumptions and dependencies;
- the producer of the evidence;
- traceability back to the relevant requirement or SpecIR node where practical.

## Preservation obligations

### P1 — Accepted Specification → SpecIR

Question:

> Does the candidate SpecIR represent the accepted specification for the properties being mapped?

Possible evidence includes:

- requirement identifiers;
- explicit field-to-node mapping;
- human/domain acceptance;
- deterministic checks for directly comparable observable properties;
- formal equivalence only where a sufficiently formal source specification exists.

P1 is not a general proof of human intent fidelity.

### P2 — SpecIR property verification

Question:

> Which declared SpecIR properties have actually been checked or proven?

Examples include:

- schema validity;
- type consistency;
- range constraints;
- unit consistency;
- state invariants;
- resource bounds;
- timing properties where supported.

A PASS applies only to the named properties under the named assumptions.

### P3 — SpecIR → Lowered Artifact

Question:

> Does lowering preserve the SpecIR semantics relevant to the generated artifact?

Possible strategies include:

- deterministic lowering with regression tests;
- translation validation;
- equivalence checking;
- proof-producing transformations;
- verified lowering passes.

POC implementations may initially classify this step as TESTED or TRUSTED rather than PROVEN, but the status must be explicit.

### P4 — Lowered Artifact → Executable

Question:

> What evidence exists that the external compiler/backend preserves the semantics required by Spec2Exec?

Possible policies include:

- treat a conventional compiler as part of the trusted computing base;
- use a verified compiler where appropriate;
- add post-build validation or differential tests;
- preserve compiler version and build configuration as provenance.

Spec2Exec does not attempt to reimplement mature compiler backends merely to own this obligation.

## Evidence classes

The initial vocabulary is:

```text
PROVEN
CHECKED
TESTED
MEASURED
ESTIMATED
HUMAN-DECLARED
HUMAN-ACCEPTED
TRUSTED
ASSUMED
ADVISORY
UNRESOLVED
```

These labels describe evidence strength or provenance; they are not interchangeable.

## Evidence record

A future normative evidence record should be able to represent at least:

```text
claim_id
subject
property
status
assumptions
producer
source_revision
trace
artifacts
notes
```

Example:

```text
claim_id: EV-P0-004
subject: program.hello
property: observable_stdout_linkage
status: CHECKED
trace: [REQ-HELLO-001]
producer: spec2exec-poc0-verifier
```

## No collapsed PASS

A pipeline result such as:

```text
VERIFIED = true
```

is insufficient unless it is merely a summary with machine-readable underlying claims.

A more accurate report is property-oriented:

```text
document_structure              CHECKED
requirement_trace_linkage       CHECKED
observable_stdout_linkage       CHECKED
lowering_equivalence_proof      UNRESOLVED
C_compiler_correctness          TRUSTED
human_intent_fidelity           HUMAN-ACCEPTED or outside verifier scope
```

## Trusted computing base

Every proof of concept must document its trusted computing base.

For POC-0 the initial TCB includes, at minimum:

- the Python runtime executing the prototype verifier/lowerer;
- the POC-0 implementation itself;
- the host operating system;
- the host C compiler and linker;
- the runtime environment used for execution checks.

The purpose of naming the TCB is not to claim these components are faulty. It is to prevent their correctness from being silently counted as proven by Spec2Exec.

## POC-0 evidence policy

POC-0 intentionally makes only limited claims.

The prototype may CHECK:

- SpecIR v0 structure;
- supported operation kinds;
- operation identifier uniqueness;
- traceability scope;
- process exit status range;
- linkage between the accepted Hello specification and SpecIR stdout/exit behavior.

The prototype does not yet prove:

- human intent fidelity;
- general specification completeness;
- semantic equivalence of lowering;
- C compiler correctness;
- machine-code equivalence.

The lowering and runtime path are engineering experiments, not a verified compiler theorem.

## Research objective

The research question is:

> Can Spec2Exec make semantic-preservation obligations and evidence explicit enough that users can distinguish what is proven, checked, tested, assumed, trusted, or unresolved at every transformation boundary?

## Consequence

RFC 0006 closes the Phase 0 architecture-definition loop for the initial prototype. Further refinement should be driven by evidence from working proof-of-concept implementations rather than architecture documents alone.
