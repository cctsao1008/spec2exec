# RFC 0012 — Lifecycle-Aware Trust Graph

- **Status:** Draft / Proposed
- **Issue:** #61
- **Scope:** first-class assumptions, defeaters/residual doubt, dependency edges, deterministic trust invalidation, and re-assurance across revision-bound claims and artifacts

## Summary

Spec2Exec already models a trust chain from candidate semantics to accepted semantics, verification, realization, and exact executable artifacts. It also already records assumptions, revisions, traceability, authority state, Trusted Computing Base components, and artifact hashes.

The remaining lifecycle gap is that these records are still mostly interpreted as a sequence of stage-local facts.

This RFC proposes a cross-cutting **Trust Graph** that makes three additional questions first-class:

1. **Assumption validity:** what claims depend on an assumption, and what happens when that assumption no longer has a current basis?
2. **Defeaters / residual doubt:** what concrete reasons could defeat a trust claim, which have been resolved, and which remain explicit limitations?
3. **Trust invalidation / re-assurance:** when a requirement, policy, dependency, tool, assumption, or artifact revision changes, which trust claims become potentially stale or invalid and which evidence may still be reused?

The Trust Graph is **not a new serial compiler stage** and does not replace the current executable semantic path.

The intended architecture is:

```text
                 EXECUTABLE SEMANTIC PATH

Intent / Requirements
        ↓
Semantic Obligation Discovery
        ↓
Resolution / Conflict Exposure
        ↓
Executable Semantic Closure
        ↓
Semantic Authority
        ↓
Accepted Specification
        ↓
Deterministic Verification
        ↓
Target Realization
        ↓
Executable / Firmware / Artifact

                    │
                    │ cross-cutting
                    ▼

                     TRUST GRAPH

Trust Claims ↔ Evidence ↔ Assumptions ↔ Defeaters
     ↕             ↕            ↕            ↕
Authority      Provenance    Dependencies   Residual Doubt
     ↕             ↕            ↕            ↕
Traceability ↔ Artifact Bindings ↔ Validity / Invalidation
                              ↕
                         Re-assurance
```

The central lifecycle rule is:

> **Historical acceptance and evidence remain immutable facts about what was accepted or observed at a revision. Current trust validity is evaluated against the current dependency graph. A change does not rewrite history; it may create a deterministic revalidation, re-acceptance, or re-assurance obligation.**

## Motivation

The current architecture can correctly establish a statement such as:

```text
retry_count = 3
    authority_validity = AUTHORIZED

semantic-review gate
    evidence_status = CHECKED

artifact X
    runtime property = TESTED
```

but that statement may depend on a contextual assumption such as:

```text
payment operation is idempotent
```

If the payment API later changes so that retries are no longer idempotent, none of the following historical facts become false merely because time passed:

- the authority policy really did authorize `retry_count = 3` at its recorded revision;
- the deterministic gate really did accept the bound records;
- the executable really did produce the recorded runtime observations.

What changes is whether those historical facts still justify a **current trust claim** for the selected deployment context.

Likewise, a requirement edit may invalidate only part of a trust chain:

```text
Requirement R7 changed
        ↓
Semantic obligation O3 is affected
        ↓
Acceptance A12 requires re-evaluation
        ↓
P1/P2 claims depending on A12 become potentially stale
        ↓
Executable E9 is still the same bits
        ↓
But E9 can no longer carry the same current trust claim
until the affected chain is re-assured
```

Spec2Exec therefore needs more than revision hashes. It needs explicit dependency and invalidation semantics.

## Relationship to existing RFCs

### RFC 0010 — Trust-Chain Architecture

RFC 0010 remains the top-level trust architecture.

This RFC refines the statement that Trust Architecture and Evidence Architecture span the whole flow by giving lifecycle-bearing trust relationships an explicit graph model.

It does not replace the RFC 0010 runtime flow.

### RFC 0011 — Semantic Authority

RFC 0011 remains the normative owner of:

- semantic obligations;
- AuthorityAnchors / Authority TCB;
- authority policies and delegation;
- executable semantic closure;
- authority completeness;
- immutable AcceptanceRecords;
- current authority validity, including `POTENTIALLY_STALE`;
- `InvalidationEvent` / `RevalidationClaim` concepts for authority state.

This RFC does not redefine `AuthorityValidity` or grant semantics.

Instead, it generalizes dependency/invalidation structure across authority, evidence, assumptions, verification, and artifact bindings.

### RFC 0006 — Evidence Model

RFC 0006 remains the normative owner of evidence classes:

```text
PROVEN
CHECKED
TESTED
TESTED_EXHAUSTIVE
MEASURED
ESTIMATED
HUMAN-DECLARED
HUMAN-ACCEPTED
TRUSTED
ASSUMED
ADVISORY
UNRESOLVED
```

This RFC introduces **no new evidence class**.

Assumption support, defeater resolution, invalidation checks, and re-assurance methods use RFC 0006 evidence records and profiles.

Typed lifecycle/disposition fields defined here are governance/graph state, not evidence strength.

## Trust Graph principles

### 1. The graph is dependency-oriented

A claim can only be invalidated or revalidated meaningfully if its material dependencies are represented.

The architecture therefore prefers explicit typed dependency edges over implicit prose.

### 2. History is immutable; current applicability is computed

Accepted semantics, evidence records, tool observations, and artifacts remain immutable historical records.

A later change produces new lifecycle records rather than mutating old evidence into a different historical statement.

### 3. Invalidation is conservative, not global

A changed dependency does not automatically invalidate every project artifact.

It affects claims reachable through material dependency edges.

However:

> **When a material dependency relationship is known to exist but the effect of a change cannot be determined, the affected claim fails closed as requiring revalidation rather than being silently reused.**

### 4. Reuse requires a basis

Evidence reuse across revisions is not inferred merely because filenames, object IDs, or human descriptions look similar.

Reuse requires either:

- unchanged content-addressed dependencies; or
- a deterministic equivalence/relevance check; or
- an explicit human/domain revalidation where that method is permitted by policy;
- another RFC 0006 evidence-bearing method appropriate to the property.

### 5. Defeaters do not become confidence arithmetic

A claim is not assigned a synthetic numeric trust score merely because several objections were resolved.

Resolved defeaters are explicit claim-relative facts. Open or accepted residual defeaters remain visible limitations.

## Logical record graph

The first architecture model adds the following logical records to the existing claim/evidence/authority model.

```text
TrustClaim
AssumptionRecord
DependencyEdge
DefeaterRecord
InvalidationEvent
ImpactEvaluation
RevalidationClaim / ReAssuranceClaim
```

These are logical records. Exact JSON schemas and storage layout are deferred to a later implementation issue.

## TrustClaim

RFC 0006 already defines evidence-bearing claims. This RFC uses `TrustClaim` as the graph node representing a property claim that may have dependencies and lifecycle state.

A TrustClaim should be able to identify at least:

```text
claim_id
subject / subject revision
property
scope
current evidence references
assumption references
authority / provenance references when applicable
artifact bindings
dependency references
defeater references
source revision
```

The evidence status remains owned by RFC 0006.

A TrustClaim does not mean the whole artifact is trusted. It remains property-scoped.

## AssumptionRecord

An assumption becomes first-class when a material trust claim depends on it.

A logical AssumptionRecord supports at least:

```text
assumption_id
statement
subject / environment context
scope
source / basis
source revision
supporting evidence references
validity conditions / applicability context
dependent claim references
supersession / invalidation relation when applicable
```

### Assumption support is evidence-bearing

Examples:

```text
payment API is idempotent
    evidence_status = HUMAN-DECLARED
```

or:

```text
sensor update period <= 10 ms
    evidence_status = MEASURED
```

or:

```text
assembler preserves target object semantics
    evidence_status = TRUSTED
```

These statuses retain RFC 0006 meaning.

### Assumption lifecycle

This RFC does not introduce a competing evidence scale for assumptions.

An assumption may instead have a typed lifecycle evaluation such as:

```text
CURRENT
POTENTIALLY_STALE
VIOLATED
UNKNOWN
```

These terms describe **current dependency validity**, not evidence strength.

`CURRENT` means the currently selected context still matches the represented basis/conditions.

`POTENTIALLY_STALE` means a dependency revision/context changed and the assumption has not yet been shown reusable.

`VIOLATED` means the current context is known not to satisfy the assumption.

`UNKNOWN` means the system lacks a sufficient basis to classify current validity.

For a material gated claim, `POTENTIALLY_STALE`, `VIOLATED`, or `UNKNOWN` must not be silently projected as current trust.

## DependencyEdge

A Trust Graph is only useful if dependency semantics are explicit enough to support impact analysis.

A logical edge identifies at least:

```text
edge_id
source node / revision
target dependent node / revision
dependency kind
scope / property relation
materiality
method / producer
source revision
```

Initial dependency kinds may include concepts equivalent to:

```text
SEMANTIC_DEPENDS_ON
AUTHORITY_DEPENDS_ON
ASSUMES
EVIDENCE_DEPENDS_ON
DERIVED_FROM
REALIZED_FROM
VALIDATED_AGAINST
TRACE_DEPENDS_ON
```

Exact enum naming is implementation detail until schema review.

### Direction

For invalidation propagation, edges are interpreted as:

```text
source dependency changed
        ↓
target dependent claim may require impact evaluation
```

Example:

```text
API-IDEMPOTENCY assumption
        ↓ ASSUMES
retry-safety claim
        ↓ EVIDENCE_DEPENDS_ON
accepted payment-retry trust claim
        ↓ REALIZED_FROM / artifact binding
payment executable artifact
```

## DefeaterRecord

A **defeater** is a concrete reason that a TrustClaim may fail, may be unsupported, or may not justify the intended conclusion under the declared scope.

Examples already implicit in current Spec2Exec architecture include:

```text
stale authority policy
conflicting applicable grant
missing provenance
unauthenticated authority root
omitted semantic obligation
unsupported environment assumption
incomplete runtime oracle
unknown change impact
```

A DefeaterRecord supports at least:

```text
defeater_id
target claim
statement / challenge
origin / producer
scope
basis / evidence references
disposition
resolution or residual-acceptance references
source revision
```

### Defeater disposition namespace

The initial architecture uses claim-relative concepts equivalent to:

```text
OPEN
RESOLVED
ACCEPTED_RESIDUAL
```

These are not RFC 0006 evidence statuses.

- `OPEN` — the challenge is material and not yet resolved/dispositioned.
- `RESOLVED` — the challenge has been addressed under an explicit method/evidence basis.
- `ACCEPTED_RESIDUAL` — the challenge remains a known limitation/risk and an applicable authority/governance process explicitly accepts that residual condition for the stated scope.

`ACCEPTED_RESIDUAL` does **not** strengthen the evidence status of the underlying claim and does not transform `TESTED` into `PROVEN`, `TRUSTED` into `VERIFIED`, or `ASSUMED` into `CHECKED`.

### Fail-closed use

When a gate requires a claim with no residual-doubt allowance, an `OPEN` material defeater blocks use of that claim.

Whether `ACCEPTED_RESIDUAL` is permitted is policy/property specific and must be explicit. It must not be inferred from impact labels or convenience.

## InvalidationEvent

An InvalidationEvent records that a dependency subject, context, or revision changed in a way that may affect dependent claims.

It should identify at least:

```text
invalidation_event_id
changed subject
prior revision / new revision
change kind
observed time / repository revision
producer
initial affected roots
```

An event does not erase prior records.

Examples:

```text
Requirement revision changed
AuthorityPolicy superseded
AuthorityAnchor protection basis changed
Assumption source/API contract changed
Verifier revision changed
Compiler/tool version changed
Generated artifact changed
Deployment configuration changed
```

## ImpactEvaluation

An ImpactEvaluation deterministically or explicitly evaluates how an InvalidationEvent affects dependent graph nodes.

For each affected dependency edge it records a disposition equivalent to:

```text
NO_MATERIAL_EFFECT
REVALIDATION_REQUIRED
INVALIDATED
UNKNOWN_IMPACT
```

These are graph lifecycle dispositions, not evidence classes.

### NO_MATERIAL_EFFECT

The changed dependency has been shown not to affect the target claim/property under a bound method and revisions.

### REVALIDATION_REQUIRED

The prior claim may still hold, but current reuse is not established for the new dependency/context.

### INVALIDATED

The changed dependency is known to break the claim, assumption, authority applicability, property, or artifact binding.

### UNKNOWN_IMPACT

A material dependency exists but the current system cannot determine whether the change affects the claim.

For a gated current-trust projection:

> **`REVALIDATION_REQUIRED`, `INVALIDATED`, and `UNKNOWN_IMPACT` fail closed for the affected claim until an appropriate revalidation/re-assurance basis exists.**

## Deterministic invalidation propagation

Given an InvalidationEvent and a known dependency graph:

1. Bind the event to an exact changed subject/revision.
2. Enumerate outgoing material dependency edges from the changed node.
3. Produce an ImpactEvaluation for each directly dependent claim/node.
4. For every node whose current-use status is not `NO_MATERIAL_EFFECT`, traverse its dependent edges transitively.
5. Preserve independent/unreachable claims as unchanged.
6. Stop propagation only when a bound method establishes no material effect, or when the graph contains no dependent edge.
7. If the system knows that a material relation exists but lacks sufficient dependency detail to evaluate it, record `UNKNOWN_IMPACT`; do not silently reuse the claim.

Pseudo-flow:

```text
Changed Subject
      ↓
Known Dependency Edges
      ↓
Impact Evaluation
   ┌──┼───────────────┐
   ↓  ↓               ↓
NO_EFFECT   REVALIDATE / INVALID / UNKNOWN
   │                    │
reuse                  propagate
                         ↓
                  dependent claims
                         ↓
                  artifact trust state
```

The propagation result is evidence-bearing insofar as it makes claims about exact dependency and impact relations; its evidence status/method remain RFC 0006 concerns.

## Revalidation and re-assurance

### Revalidation

A RevalidationClaim establishes that a previously represented property/assumption/authority relationship remains applicable under changed revisions or context.

It identifies:

```text
prior claim / record
new dependency revisions
property / scope
method
producer
assumptions
RFC 0006 evidence status
new subject/artifact bindings
```

### Re-assurance

`Re-assurance` is the broader process of restoring a current trust chain after invalidation.

It may require one or more of:

```text
re-extraction
semantic re-resolution
re-acceptance / re-authorization
re-running deterministic verification
re-running translation/preservation checks
rebuilding artifacts
re-testing / re-measuring
new assumption validation
new defeater resolution
```

A ReAssuranceClaim never asserts more than the component evidence supports.

It is legitimate for some existing evidence to be reused and other evidence to be regenerated.

## Selective evidence reuse

A lifecycle-aware architecture should avoid both extremes:

```text
change anything → rerun everything
```

and:

```text
artifact still exists → trust everything
```

Selective reuse is permitted when dependency analysis provides a basis.

Example:

```text
AuthorityPolicy revision changed
        ↓
AcceptanceRecord applicability requires re-evaluation
        ↓
P1 accepted-specification linkage requires refresh
        ↓
Generated assembly bytes happen to be unchanged
        ↓
Assembler version/trust record may still be reusable
        ↓
But the executable's current semantic-authority trust claim
cannot be reused until upstream re-assurance completes
```

An unchanged SHA is strong evidence that the bits did not change. It is not by itself evidence that the **meaning or authority context** for those bits remained current.

## Worked example A — payment retry and idempotency

### Initial state

Requirement:

```text
Retry failed payment requests.
```

Authorized semantics:

```text
retry_count = 3
retry_on_timeout = false
backoff_policy = exponential
```

Material assumption:

```text
ASSUMPTION API-IDEMPOTENCY-01
statement:
  repeating the selected payment operation with the same idempotency key
  does not create an additional charge
source:
  Payment API contract v7
```

Trust dependencies:

```text
API-IDEMPOTENCY-01
        ↓ ASSUMES
PAYMENT-RETRY-SAFETY-CLAIM
        ↓
PAYMENT-RETRY-ACCEPTANCE
        ↓
PAYMENT-ARTIFACT-X
```

### Change

The provider publishes API contract v8 and changes idempotency behavior for the selected endpoint.

Record:

```text
InvalidationEvent:
  changed_subject = Payment API contract
  old_revision = v7
  new_revision = v8
```

The graph must not rewrite the old acceptance or old tests.

Instead:

```text
API-IDEMPOTENCY-01          → POTENTIALLY_STALE / impact evaluation required
PAYMENT-RETRY-SAFETY-CLAIM → REVALIDATION_REQUIRED
PAYMENT-RETRY-ACCEPTANCE   → current trust projection blocked
PAYMENT-ARTIFACT-X         → same bytes may exist,
                             but previous current trust claim is not reusable
```

If a deterministic contract check or authorized domain review establishes that the selected endpoint remains idempotent under v8, a bound RevalidationClaim may restore current use without inventing a new semantic-authority event unnecessarily.

If v8 is known non-idempotent, the assumption is `VIOLATED`, the affected safety claim is invalidated, and semantic re-resolution/re-authorization is required.

## Worked example B — artifact-chain change impact

Initial chain:

```text
Requirement R
    ↓
Accepted Specification S
    ↓ P1/P2
Verified SpecIR I
    ↓ P3
Assembly A
    ↓ P4-A/P4-L
Executable E
    ↓ P4-R
Runtime evidence T
```

Suppose only Requirement R changes.

The dependency graph shows:

```text
R → S → I → A → E → T
```

The event does not assert that every downstream artifact is physically modified.

It asserts that the prior current semantic trust chain requires impact evaluation.

Possible result:

```text
R → S      REVALIDATION_REQUIRED
S → I      REVALIDATION_REQUIRED
I → A      blocked from current reuse until upstream semantics are current
A → E      object/link evidence may remain historically valid for exact old A/E
E → T      old runtime observations remain historical TESTED evidence
```

After re-resolution, suppose S and I are deterministically shown equivalent to their old revisions and regenerated A/E hashes are identical.

Then new equivalence/revalidation evidence can justify selective reuse instead of pretending either that nothing happened or that every tool claim must be recreated from zero.

## Defeater examples in current Spec2Exec

Many current rejection conditions can be projected as defeaters without changing their existing owning semantics.

Examples:

```text
Claim: selected semantics are properly authorized
Possible defeaters:
- applicable authority policy is stale
- another applicable grant conflicts
- authority root is unauthenticated beyond declared TCB
- self-authorization is not permitted

Claim: all material semantic obligations were gated
Possible defeaters:
- C0-style obligation omission
- unsupported closure exclusion
- unknown selected-configuration effect

Claim: executable carries accepted semantics
Possible defeaters:
- P3 preservation only TESTED, not PROVEN
- assembler/linker are TRUSTED TCB components
- runtime evidence exercises QEMU, not physical hardware
```

Some of these are blockers. Some are honest residual limitations already accepted by the current POC scope.

The Trust Graph makes that distinction machine-visible without pretending all residual doubt can or should be eliminated.

## Assurance-argument projection

This RFC does not make Spec2Exec a GSN/SACM authoring tool.

However, the Trust Graph should preserve enough structure that a future adapter can project:

```text
Claim
├── Context
├── Assumptions
├── Supporting subclaims
├── Evidence
├── Defeaters
└── Residual limitations
```

into an external assurance-case representation when useful.

The projection is informative unless a later Accepted RFC defines stronger semantics.

## Non-goals

This RFC does not define:

- a general proof that all real-world requirements are complete;
- a universal scalar trust/confidence score;
- a replacement for GSN, SACM, or assurance-case tools;
- certification acceptance criteria;
- a universal risk/criticality ladder;
- automatic derivation that `CRITICAL` implies a particular evidence class;
- runtime Simplex/fallback-controller architecture;
- continuous runtime assumption monitoring semantics;
- cross-component emergent-semantics composition;
- enterprise identity/governance/quorum policy;
- philosophical proof that an AuthorityAnchor is ultimately legitimate;
- a general dependency-inference system for arbitrary repositories.

## Deferred work

### Risk / criticality profiles

A future workstream may define property-specific assurance profiles such as required methods, authority policies, evidence classes, independence, runtime monitoring, or residual-risk disposition.

It must not reduce RFC 0006 evidence classes to a universal scalar ordering.

### Runtime assurance

Runtime assumption monitoring, operational violation handling, and fail-safe/fallback behavior are natural future extensions, especially for FSM/motor-safety POCs.

They are not required to establish this lifecycle graph architecture.

### System composition / emergent semantics

Cross-component behavior such as retry amplification can create semantic obligations not present in any single component specification.

This is a major future research topic and should receive its own Issue/RFC only after the current single-build trust graph is validated.

### Stronger organizational governance

Authentication, delegation depth, revocation, quorum, organizational role mapping, and accountability remain future semantic-authority work layered on RFC 0011.

## Initial architecture invariants

If this RFC is accepted, the intended invariants are:

1. **Historical acceptance/evidence records are immutable; current validity is computed separately.**
2. **Material assumptions are first-class dependency nodes rather than untraceable prose only.**
3. **A changed material dependency cannot be silently ignored when its impact is unknown.**
4. **Invalidation propagates through known material dependency edges, not globally by default.**
5. **Evidence reuse across revisions requires unchanged bound dependencies or an explicit revalidation/equivalence basis.**
6. **Defeaters are claim-relative challenges, not evidence-strength labels.**
7. **Open material defeaters block gated current use unless an applicable policy explicitly permits residual acceptance.**
8. **Accepted residual doubt remains visible and does not strengthen the underlying evidence class.**
9. **An unchanged artifact hash does not by itself establish unchanged semantic authority, assumptions, or current trust context.**
10. **Re-assurance may selectively reuse valid evidence but must bind all reused and regenerated claims to the new dependency context.**
11. **Trust Graph state spans the executable semantic path; it is not inserted as a misleading serial compiler stage.**
12. **RFC 0006 remains the only normative owner of evidence classes.**

## Minimum implementation experiment after architecture acceptance

This RFC does not authorize implementation by itself.

A later implementation Issue should choose a bounded experiment such as the existing payment-retry POC:

```text
Payment API idempotency assumption revision changes
        ↓
deterministic dependency traversal
        ↓
semantic-review trust claim becomes REVALIDATION_REQUIRED
        ↓
artifact remains byte-identical
        ↓
current merge/deployment trust projection blocks
        ↓
revalidation record restores current use or proves invalidation
```

The experiment should demonstrate selective invalidation and selective evidence reuse without creating a full repository-wide dependency-analysis product.

## Open review questions

Before promotion from Draft:

1. Are the proposed assumption lifecycle concepts sufficient without overlapping RFC 0011 `AuthorityValidity`?
2. Are `OPEN / RESOLVED / ACCEPTED_RESIDUAL` appropriate typed defeater dispositions, or should different names be used?
3. Is `UNKNOWN_IMPACT → fail closed` scoped precisely enough to avoid accidental whole-project invalidation?
4. Are the proposed dependency kinds sufficient for a minimal implementation without over-modeling?
5. Should RevalidationClaim and ReAssuranceClaim remain distinct logical records or use one record with a method/profile distinction?
6. Which current POC limitation should become the first explicit residual defeater in implementation?
7. What is the minimum machine-readable structure needed for later GSN/SACM projection without importing assurance-case semantics prematurely?

## Status / next step

This RFC is intentionally **Draft / Proposed**.

The next step is architecture review of the lifecycle semantics, especially:

- selective invalidation soundness;
- unknown-impact fail-closed behavior;
- assumption lifecycle vs evidence-strength separation;
- residual-doubt semantics;
- compatibility with RFC 0006 and RFC 0011.

No executable trust-graph implementation should be merged solely on the basis of this draft.