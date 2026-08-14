# RFC 0011 — Semantic Authority, Delegation, and Default Policy

- **Status:** Draft / Proposed
- **Issue:** #53
- **Scope:** Semantic-authority records, delegated defaults, authority validity, impact classification, provenance, and fail-closed acceptance before SpecIR synthesis

## Summary

Spec2Exec does not require every missing semantic detail to be answered interactively by a human. It requires every executable semantic decision to have an explicit authority basis.

A default may therefore be used without an immediate clarification step **only when an applicable authority policy has already delegated that class of decision**. The fact that a default is common, low-risk, plausible, or recommended by an AI system does not itself create authority.

The central rule is:

> **Capability, plausibility, convention, and low impact do not create semantic authority. Authority originates from an accountable source and may be explicitly delegated through a scoped, revisioned, and revocable policy.**

This RFC refines RFC 0010 and the implementation direction in issue #53.

## Motivation

Specification-oriented development systems often need to balance two legitimate goals:

1. expose consequential ambiguity before implementation;
2. avoid blocking productive work on every ordinary missing detail.

A productivity-oriented system may therefore fill gaps using reasonable defaults and record assumptions. Spec2Exec must be able to consume such artifacts without treating every assumption as either automatically trusted or automatically forbidden.

The missing distinction is **authority**.

For example:

```text
Candidate requirement:
    retry failed requests

Possible defaults:
    retries = 3
    backoff = exponential
    retry POST = false
```

All three choices may be reasonable. None is authoritative merely because it is reasonable.

The architecture therefore needs a mechanism that permits defaults when they are already authorized by policy while failing closed when no such authority exists.

## Design goals

This RFC defines an authority model that:

- keeps semantic uncertainty and authority state before executable SpecIR;
- allows candidate-semantics frontends to remain replaceable;
- permits policy-authorized defaults without requiring a human prompt for every detail;
- separates **semantic resolution**, **authority validity**, and **impact/consequence** into independent dimensions;
- records provenance and revision context for every accepted decision;
- supports delegated authority without treating AI capability as authority;
- invalidates accepted decisions when their authority basis becomes stale, revoked, expired, or superseded;
- fails closed before SpecIR synthesis when executable semantics are unresolved, conflicting, unauthorized, or stale.

## Candidate-semantics frontends

Spec2Exec should not compete with tools whose primary purpose is requirement elicitation, specification authoring, planning, or AI coding workflow.

Candidate semantics may originate from many frontends, including:

```text
Natural-language requirements
PRDs
requirements-management systems
standards documents
contracts / interface specifications
Spec-Driven Development tools
AI coding-agent workflows
search / retrieval systems
domain-specific frontends
```

A frontend may contribute:

```text
requirements
clarifications
assumptions
reasonable defaults
conflict findings
source citations
candidate interpretations
```

These remain **candidate semantics** until authority resolution is complete.

A frontend adapter should preserve where each candidate decision came from rather than flattening the result into an apparently authoritative specification.

Representative flow:

```text
             Candidate-Semantics Frontends
                        │
        ┌───────────────┼────────────────┐
        │               │                │
   SDD / Spec tools    PRD / RM       Standards
        │               │                │
   AI assistants     Contracts       Domain sources
        │               │                │
        └───────────────┼────────────────┘
                        ↓
               Candidate Semantics
                        ↓
              Authority Resolution
                        ↓
             Accepted Specification
                        ↓
                SpecIR Synthesis
```

No particular frontend is part of the trusted semantic core by default.

## Three independent dimensions

A core requirement of this RFC is that the system **must not collapse semantic state, authority, and impact into one field**.

### 1. Semantic-resolution state

This answers:

> Do we know what semantic decision is being proposed?

Candidate states include:

```text
PROPOSED
RESOLVED
UNRESOLVED
CONFLICT
```

`RESOLVED` means that a concrete semantic decision is available. It does **not** mean that the decision is authorized.

### 2. Authority-validity state

This answers:

> Is this semantic decision currently authorized for this scope?

Candidate states include:

```text
AUTHORIZED
UNAUTHORIZED
STALE
REVOKED
EXPIRED
```

A decision may be perfectly clear and still be `UNAUTHORIZED`.

A previously authorized decision may later become `STALE`, `REVOKED`, or `EXPIRED`.

### 3. Impact / consequence classification

This answers:

> What is the consequence if this decision is wrong?

A project may use a scale such as:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

The exact impact taxonomy is policy-dependent and is not itself an authority model.

The critical invariant is:

> **Impact classification may influence which authority policy applies, but impact classification does not create authority.**

Therefore:

```text
LOW impact != automatically authorized
HIGH impact != necessarily human-only
```

A low-impact decision still needs an authority basis. A high-impact decision may be authorized through a sufficiently strong pre-approved policy, standard, contract, or accountable workflow.

## Authority model

### Authority root / source

An **authority source** is an accountable origin from which semantic authority can be derived.

Examples may include:

- an authorized human or engineering role;
- an approved parent specification;
- a governing contract;
- an applicable standard or regulatory requirement;
- a certified or approved domain model;
- a project constitution or governance artifact explicitly designated as authoritative;
- another accepted authority policy.

The existence of a document is not sufficient. Its authority status, scope, and revision must be represented.

### Authority policy

An **authority policy** defines which classes of semantic decisions an authority source delegates, under what scope and constraints.

A policy should identify at least:

```text
policy_id
source_authority
source_revision
scope
decision_class
allowed_resolution_method
constraints
valid_from / valid_until when applicable
revocation / supersession relation
```

### Authority agent

An **authority agent** is a mechanism permitted to exercise delegated authority under an authority policy.

It may be:

```text
a human role
a deterministic policy engine
a rules engine
a workflow service
an AI system
a future automated system
```

The important distinction is:

> **An agent does not become authoritative because it is intelligent or accurate. It is authoritative only for decisions that an accountable authority source has delegated to it under a valid policy.**

An AI system may therefore act as a delegated authority agent in a future configuration, but its model capability is not the authority root.

## Default policy

Spec2Exec does **not** adopt the rule:

```text
LOW impact → AI may choose a default
MEDIUM impact → record assumption
HIGH impact → authority required
```

That rule incorrectly treats consequence classification as an authority grant.

Instead:

```text
Missing Semantic Decision
        ↓
Is there an applicable valid authority policy?
        │
   ┌────┴────┐
   │         │
  YES        NO
   │         │
   ↓         ↓
Policy-authorized    UNRESOLVED /
resolution/default   UNAUTHORIZED
   │
   ↓
Record policy,
revision, scope,
agent, and decision
```

Impact may be used by the authority policy to determine which decisions it delegates.

For example, an approved project policy might authorize a default engine to choose:

```text
ordinary UI pagination size
non-safety display formatting
logging presentation defaults
non-semantic naming conventions
```

while explicitly forbidding delegated defaults for:

```text
access-control decisions
money movement
actuator safety limits
medical alert thresholds
safety interlocks
retention rules governed by regulation
```

The important property is not that the first set is "low risk". The important property is that an accountable policy explicitly delegates those decisions.

## Assumptions from external frontends

A candidate frontend may emit an assumption such as:

```text
Assumption:
    OAuth2 is used.
```

Spec2Exec should not automatically interpret this as either accepted or invalid.

A frontend adapter may map it into a semantic obligation such as:

```text
semantic_decision_id: AUTH-001
candidate_value: OAuth2
provenance:
  source_kind: frontend-assumption
  source_artifact: ...
  source_revision: ...
semantic_resolution: RESOLVED
authority_validity: UNAUTHORIZED
impact: HIGH
```

If an applicable authority policy already authorizes that authentication decision for the relevant scope, the gate may transition the decision to `AUTHORIZED` and record the policy linkage.

If no authority exists, the decision remains blocked even though the proposal is reasonable.

## Governance artifacts and constitutions

Project constitutions, engineering principles, and governance documents can be genuine authority sources when the project explicitly designates them as such.

Spec2Exec should therefore avoid the simplistic claim that governance is "not semantic authority."

The distinction is instead:

```text
Governance artifact may be an authority source
        !=
Complete semantic-authority model
```

A generalized Spec2Exec authority model additionally requires machine-representable provenance such as:

```text
which authority source
which revision
which semantic scope
which delegation policy
which decision depended on it
whether it remains valid
which accepted specification revision incorporated it
which downstream artifacts depend on that acceptance
```

This permits existing governance systems to participate as authority sources rather than forcing Spec2Exec to replace them.

## Normative semantic-decision record

The exact schema is implementation work under issue #53, but the architecture should support at least the following logical fields:

```text
SemanticDecision
├── decision_id
├── subject / semantic_scope
├── candidate_value or alternatives
├── semantic_resolution
├── authority_validity
├── impact_class
├── provenance
│   ├── source_artifact
│   ├── source_revision
│   └── source_location / clause
├── authority_binding
│   ├── authority_source
│   ├── authority_source_revision
│   ├── authority_policy
│   ├── policy_revision
│   ├── authority_agent
│   └── delegation_scope
├── assumptions
├── dependencies / parent decisions
├── accepted_revision_context
└── invalidation state / reason
```

Not every field must be embedded in the Accepted Specification itself. The implementation may use linked authority/provenance records as long as downstream acceptance is mechanically bound to the exact records and revisions on which it depends.

## Authority gate

For every semantic decision required by executable behavior, the gate should enforce at least:

```text
semantic_resolution == RESOLVED
AND
authority_validity == AUTHORIZED
AND
authority source / policy revision is current
AND
scope covers the semantic decision
AND
required provenance is present
```

Otherwise the result must fail closed before executable SpecIR synthesis.

Examples of blocking conditions:

```text
UNRESOLVED
CONFLICT
UNAUTHORIZED
STALE
REVOKED
EXPIRED
scope mismatch
missing authority provenance
superseded authority revision
```

The preferred placement remains:

```text
Draft / Candidate Specification
        │
        ├── semantic decisions
        ├── assumptions
        ├── conflicts
        ├── authority records
        ├── impact classifications
        └── provenance
        ↓
Semantic Authority Gate
        ↓
Accepted Specification
        ↓
Semantic Synthesis
        ↓
Executable SpecIR
```

`UNRESOLVED`, `CONFLICT`, and authority-validity state do not belong in executable SpecIR by default. They should prevent the relevant executable semantics from reaching SpecIR.

## Revision, revocation, and invalidation

Authority is revision-sensitive.

If an accepted decision depends on:

```text
authority source A revision 7
policy P revision 3
parent requirement R revision 12
```

then a change, revocation, expiry, or supersession affecting those dependencies must invalidate the dependent acceptance unless the new revision is proven semantically equivalent for the relevant scope.

A future implementation should maintain an authority dependency graph such as:

```text
Authority Source Revision
        ↓
Authority Policy Revision
        ↓
Semantic Decision
        ↓
Accepted Specification Revision
        ↓
SpecIR / Evidence / Executable Artifacts
```

Invalidation should propagate downstream as an evidence or rebuild obligation rather than silently preserving stale acceptance.

## Authenticated acceptance

This RFC separates **authority semantics** from **authentication technology**.

A record may say who is declared to have accepted a decision without cryptographically proving that identity or action.

Until authenticated acceptance is implemented, evidence should use a status such as:

```text
HUMAN-DECLARED
```

or another explicitly unauthenticated class rather than implying signed or authenticated approval.

Possible future mechanisms include signed VCS provenance, workflow attestations, identity-backed approvals, or other attributable mechanisms. No single mechanism is mandated by this RFC.

## Relationship to impact and workflow ergonomics

Spec2Exec should not require thirty interactive questions merely because thirty candidate details are missing.

Workflow ergonomics should instead come from **delegated policy**, not silent authority creation.

A well-designed policy can authorize large classes of low-consequence or conventional decisions in advance, while preserving strict handling for decisions whose semantics require stronger authority.

This gives the productivity benefit of reasonable defaults without weakening the trust invariant.

## Relationship to SDD and AI coding workflows

Spec2Exec should treat specification-development and AI coding systems as potential upstream contributors, not as competitors that must be reimplemented.

A useful distinction is:

```text
Specification-development workflow asks:
    Is the specification clear enough to build?

Spec2Exec additionally asks:
    Is each executable semantic decision authorized?

And:
    What exact evidence justifies trusting this exact artifact
    to carry those accepted semantics?
```

This is a boundary distinction, not a claim that upstream specification systems are weak or undisciplined.

## Evidence obligations

An accepted semantic decision should eventually support evidence that identifies at least:

```text
claim
semantic decision subject
authority source
source revision
authority policy and revision, when delegated
authority agent, when used
scope
provenance
assumptions
acceptance revision
status / validity
```

Downstream evidence should bind the Accepted Specification revision or hash that incorporates these decisions.

## Non-goals

This RFC does not:

- prohibit reasonable defaults;
- require human approval for every semantic detail;
- equate low impact with automatic authority;
- equate AI capability with authority;
- require one specification frontend;
- require one risk-classification taxonomy;
- require one authentication or signature technology;
- move unresolved authority state into executable SpecIR;
- replace requirements-management, SDD, governance, certification, or assurance-case systems;
- claim certification or regulatory qualification.

## Proposed invariants

If this RFC is accepted, the following should refine the project-level invariants in RFC 0010:

1. **A semantic decision may become executable only when it is both resolved and authorized.**
2. **Impact classification and authority validity are independent dimensions.**
3. **Reasonable defaults require an applicable authority policy; convention alone is not authority.**
4. **Delegated authority must identify an accountable source, scope, revision, and revocation/invalidation behavior.**
5. **An authority agent receives authority from delegation, not from capability.**
6. **Candidate-semantics frontends remain replaceable and are not authority sources by default.**
7. **Stale, revoked, expired, conflicting, unresolved, or unauthorized semantics fail closed before SpecIR synthesis.**
8. **Governance artifacts may be authority sources when explicitly designated and revision-bound.**
9. **Accepted semantics must remain traceable to the authority records and revisions on which they depend.**
10. **Authority changes must create explicit downstream invalidation or re-acceptance obligations.**

## Implementation sequence

Issue #53 should proceed in this order:

```text
RFC review / acceptance
        ↓
Authority-record schema
        ↓
Minimal accepted-spec authority binding
        ↓
Fail-closed authority gate
        ↓
Negative regression tests
        ↓
Revision / stale-authority tests
        ↓
Delegated-default policy tests
        ↓
Evidence integration
        ↓
CI / closure
```

The first executable implementation should stay deliberately small. It should prove the boundary and fail-closed behavior before adding broad frontend integration or sophisticated authentication.
