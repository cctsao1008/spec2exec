# Physical Decision Contract / Trust Continuity Research Track

**Status:** Research hypothesis / externalization probe  
**Issue:** #70 — Trust Continuity / Physical Decision Contract  
**Normative status:** Not an RFC; not accepted architecture  
**Priority:** P2 research exploration  
**Relationship to #69:** Separate; does not modify the Comparative Assurance protocol

## Purpose

This research track asks whether Spec2Exec's authority, evidence, identity, assumption, validity, and lifecycle concepts can remain explicitly bound as execution crosses from accepted software semantics into context-dependent physical action.

The track deliberately does **not** assume that Physical Decision Contract (PDC) is novel, necessary, or superior to established Runtime Assurance (RTA), Simplex, safety-filter, Control Barrier Function (CBF), assume-guarantee, contract-based CPS, runtime-verification, assurance-case, authorization, or provenance approaches.

The current question is narrower:

> **After accounting for established approaches, does a useful cross-boundary Trust Continuity problem remain?**

## Positioning hierarchy

```text
Spec2Exec core
    = current validated research program

Physical Decision Contract (PDC)
    = physical-runtime externalization probe

Trust Continuity
    = higher-order research hypothesis
```

This hierarchy is intentionally one-way at this stage. PDC may reference accepted Spec2Exec RFCs and validated baselines, but PDC does not redefine them.

## Higher-order hypothesis

> **The possible general contribution is not execution admission itself, but trust continuity across heterogeneous consequential-execution boundaries.**

The working question is whether the following remain explicitly bound rather than silently recreated at each boundary:

```text
Authority
Evidence
Assumptions
Identity
Validity
```

Continuity does not mean that trust remains permanently valid. A claim may become stale, invalid, defeated, or require re-evaluation while its historical acceptance remains true.

## Candidate non-collapse invariants

```text
Proposal ≠ Authority
Authority ≠ Admission
Feasibility ≠ Modification Authority
Veto Authority ≠ Fallback Authority
Historical Validity ≠ Current Validity
Evidence Producer ≠ Decision Authority
Deterministic ≠ Correct
Plausibility ≠ Permission
Execution Capability ≠ Execution Permission
Represented Dependencies ≠ Complete Dependencies
```

These are research propositions, not accepted Spec2Exec invariants.

## Candidate residual claims

The current non-overlap work is organized around four candidate claims:

### TC1 — Semantic-to-runtime capability binding

Can a runtime proposal class be explicitly traced to the semantic basis that authorized the exact executable/runtime role to propose that class of behavior?

### TC2 — Artifact/runtime/actuation identity continuity

Can the chain remain bound across:

```text
accepted semantics
→ exact executable artifact
→ runtime instance
→ proposal
→ admission decision
→ consequential action
```

without relying on an unexamined identity assumption at a boundary?

### TC3 — Authority-preserving intervention

A mechanism may show that proposed action `u` is unsafe and that action `u'` is safe or feasible. That does not by itself establish authority to select `u'`.

The research therefore distinguishes:

```text
REJECT + COUNTER-PROPOSAL
```

from:

```text
AUTHORIZED TRANSFORMATION
```

and separately distinguishes veto authority from fallback-selection authority.

### TC4 — Cross-boundary assumption invalidation

Can a design-time assumption remain explicitly connected to the semantic decisions, artifact assurance claims, runtime dependencies, and admission decisions that depend on it, such that invalidation propagates without rewriting historical truth?

## Completeness pressure

C0 established the structural lesson:

> An authority gate cannot reject an obligation that was never discovered.

The runtime analogue under investigation is:

> **A runtime admission mechanism cannot invalidate a load-bearing dependency that was never represented.**

This is an analogy only. It does not expand or redefine C0.

## Strong overlap already assumed

This research begins from the presumption that established work already covers substantial parts of the problem:

- Runtime Assurance / Simplex;
- safety filters and CBFs;
- assume-guarantee and contract-based CPS design;
- runtime verification;
- assurance cases and compositional assurance;
- delegated authorization / capability-based governance;
- provenance and audit mechanisms.

PDC must not claim novelty merely for:

```text
putting a gate before actuation
checking runtime state or constraints
assume-guarantee contracts
safe-set filtering
backup-controller switching
recording provenance
runtime authorization alone
```

## Falsification pressure

The hypothesis is weakened if:

1. existing RTA + contract + safety-filter + authorization/provenance mechanisms already provide equivalent semantics;
2. Trust Continuity improves auditability but not consequential assurance;
3. dependency completeness cannot be bounded usefully;
4. identity/evidence linkage imposes prohibitive runtime or engineering cost;
5. modification/fallback authority provides no practical distinction beyond existing delegation;
6. the proposal adds vocabulary rather than engineering capability.

The comparison target is therefore conceptually:

```text
PDC / Trust Continuity
vs
RTA + assume-guarantee contracts + safety filters + provenance + delegated authorization
```

## Current repository scope

This track currently contains research documentation only:

```text
research/physical-decision-contract/
├── README.md
├── research-positioning.md
└── non-overlap-matrix.md
```

Do not add yet:

```text
schema implementation
prototype code
new evidence classes
CI targets
SpecIR changes
RFC changes
PDC-specific backend work
```

## Gates before implementation

### Gate 1 — Literature / non-overlap

Determine whether TC1–TC4 contain a non-trivial residual claim after comparison with established approaches.

### Gate 2 — Minimal semantic model

Define at least:

```text
admission
modification authority
fallback authority
identity continuity
dependency invalidation
UNKNOWN semantics
```

without circular authority or hidden defaults.

Only if both gates survive should this track consider a schema or physical prototype.

## Relationship to accepted Spec2Exec baselines

Relevant accepted baselines may be referenced as inputs:

- RFC 0010 — Trust-Chain Architecture;
- RFC 0011 — Semantic Authority, Delegation, and Default Policy;
- RFC 0006 — Semantic Preservation and Evidence Model;
- RFC 0012 — Lifecycle-Aware Trust Graph.

This research track does not modify their normative meaning.

## Current claim boundary

A defensible statement at this stage is:

> **Spec2Exec currently studies trust in the transition from authorized semantics to executable behavior. PDC is a proposed externalization probe asking whether authority, evidence, assumptions, identity, and validity can remain explicitly bound as execution crosses from software realization into context-dependent physical action.**
