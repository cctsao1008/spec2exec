# RFC 0012 — Lifecycle-Aware Trust Graph

- **Status:** Draft / Proposed — Revision 2
- **Issue:** #61
- **Scope:** first-class assumptions, dependency completeness, defeaters/residual doubt, typed dependency edges, deterministic trust invalidation, context-bound current-trust projection, and re-assurance across revision-bound claims and artifacts

## Summary

Spec2Exec already models a trust chain from candidate semantics to accepted semantics, verification, realization, and exact executable artifacts. It also already records assumptions, revisions, traceability, semantic-authority state, Trusted Computing Base components, and artifact hashes.

The lifecycle gap is not another realization stage. It is that material trust dependencies can change, become unsupported, be newly discovered as defective, or remain historically true while no longer justifying current use.

This RFC proposes a cross-cutting **Trust Graph** that makes four questions first-class:

1. **Dependency completeness:** what does a gated property claim materially depend on, and what basis supports the claim that material dependencies were not silently omitted?
2. **Assumption lifecycle:** what claims depend on an assumption, under which bound context, and what happens when its support/basis/context changes?
3. **Defeaters / residual doubt:** what concrete reasons could defeat a trust claim, which have been resolved, and which remain explicit limitations under an authorized residual-disposition decision?
4. **Trust invalidation / re-assurance:** when a requirement, authority basis, assumption, TCB component, tool, context, dependency, or artifact changes — or when new adverse knowledge is discovered — which property claims remain current, which require revalidation, and which historical evidence may still be reused?

The Trust Graph is **not a new serial compiler stage** and does not replace the current executable semantic path.

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

> **Historical acceptance, evidence, and observations remain immutable records of what was accepted, relied upon, or observed at a revision and context. Current trust validity is computed against a bound evaluation context and an explicit dependency/completeness basis. A later change or discovery does not rewrite history; it may create a deterministic revalidation, re-acceptance, correction/supersession, or re-assurance obligation.**

## Review history

Revision 1 received an external hostile architecture review with verdict:

```text
PASS WITH MAJOR FINDINGS
RFC 0012 REQUIRES MAJOR REVISION BEFORE ACCEPTANCE
```

The two blocking findings were:

```text
B-01  No dependency-graph completeness obligation;
      absence of an edge could be treated as independence.

B-02  Residual acceptance / revalidation could create a second
      authority path outside RFC 0011.
```

Revision 2 hardens those areas and also addresses the review's high-severity findings around:

```text
reuse-permitting lifecycle conclusions
property/context-scoped impact evaluation
cycle / SCC semantics
knowledge-change invalidation
residual-disposition lifecycle binding
evaluation-context binding
typed state namespaces
historical observation vs standing reliance
```

Revision 2 remains Draft until a closure review confirms that these changes close the findings without introducing a new trust bypass.

## Motivation

The current architecture can correctly establish statements such as:

```text
retry_count = 3
    AuthorityValidity.AUTHORIZED

semantic-review gate
    EvidenceStatus.CHECKED

artifact X / runtime property P
    EvidenceStatus.TESTED
```

but those statements may depend on contextual assumptions such as:

```text
payment provider preserves idempotency for the selected endpoint,
key scope, and operation semantics
```

If the provider contract later changes, none of the following historical facts become false merely because time passed:

- the authority policy really did authorize `retry_count = 3` at its recorded revision;
- the deterministic authority/review gate really did accept the bound records;
- the executable really did produce the recorded runtime observations.

What changes is whether those historical facts still justify a **current property-scoped trust projection** for the selected deployment context.

Likewise, a requirement edit may invalidate only part of a trust chain:

```text
Requirement R7 changed
        ↓
Semantic obligation O3 is affected
        ↓
Acceptance A12 requires re-evaluation
        ↓
P1/P2 claims depending on A12 require impact evaluation
        ↓
Executable E9 is still the same bits
        ↓
Some exact historical observations remain true,
but affected current trust projections cannot be reused
until the impacted chain is re-assured
```

Spec2Exec therefore needs more than revision hashes and a set of recorded edges. It needs explicit dependency semantics, a basis for dependency completeness, conservative impact propagation, and typed current-validity decisions.

## Relationship to existing RFCs

### RFC 0010 — Trust-Chain Architecture

RFC 0010 remains the top-level trust architecture.

This RFC refines the statement that Trust Architecture and Evidence Architecture span the whole flow by giving lifecycle-bearing trust relationships an explicit graph model.

It does not replace the RFC 0010 executable/runtime flow.

### RFC 0011 — Semantic Authority

RFC 0011 remains the normative owner of:

- semantic obligations;
- AuthorityAnchors / Authority TCB;
- authority policies and delegation;
- executable semantic closure;
- semantic completeness;
- authority completeness;
- authority-validity state;
- immutable AcceptanceRecords;
- authority-specific invalidation/revalidation mechanics;
- the rule that authority originates only from valid anchor/policy/delegation paths.

This RFC does **not** redefine `AuthorityValidity`, grant semantics, or authority-agent rules.

Authority-specific revalidation continues to use RFC 0011 semantics. RFC 0012 may reference those authority records as nodes/dependencies, but it cannot create a parallel authority system.

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

This RFC introduces **no new evidence class** and no scalar ordering over those classes.

Assumption support, dependency-completeness claims, impact/reuse conclusions, defeater resolution, and revalidation methods use RFC 0006 evidence records and property-specific evidence profiles where applicable.

RFC 0006's typed-namespace rule applies explicitly: lifecycle/disposition tokens defined here are always interpreted under their owning type and must not be stored or rendered as an unqualified generic `status` when that would be ambiguous.

## Trust Graph principles

### 1. The graph is dependency-oriented, but edge presence is not presumed complete

A claim can only be invalidated or revalidated meaningfully if its material dependencies are represented.

Explicit typed dependency edges are preferred over implicit prose.

However:

> **The absence of a represented dependency edge is not evidence that no material dependency exists.**

Selective invalidation is sound only relative to a property-scoped dependency-completeness basis.

### 2. History is immutable; corrections and current use are append-only/computed

Historical records are not silently rewritten.

The architecture distinguishes:

```text
Historical observation
    what was actually observed at a bound revision/context

Historical acceptance / exercise
    what was accepted/authorized under a bound authority context

Standing reliance
    what was relied upon as TRUSTED / ASSUMED / otherwise external

Correction / supersession
    append-only record that a prior record was wrong, incomplete,
    superseded, or should no longer be used as a current basis

Current-use validity
    computed result for an exact property and evaluation context
```

A later defect discovery can defeat current reliance without erasing the historical fact that the component was previously relied upon.

### 3. Invalidation is conservative, property-scoped, and not global by default

A changed dependency does not automatically invalidate every artifact or every claim about an artifact.

It affects property claims reachable through material dependency relationships for the bound context.

If a material relation is represented but its effect is unknown, the impact is fail-closed.

If a material relation may exist but dependency completeness is not established, current reuse is also fail-closed through an open completeness defeater.

### 4. Reuse requires a basis

Evidence or claims are not reused across revisions merely because filenames, object IDs, tool names, or human descriptions look similar.

Reuse requires a recorded basis appropriate to the property, such as:

- unchanged content-addressed dependencies under a completeness basis that covers the relevant relation;
- deterministic equivalence/relevance checking;
- an RFC 0011 authority revalidation/re-acceptance when authority applicability changed;
- a human/domain revalidation when the applicable authority/evidence policy explicitly permits that method;
- another RFC 0006 evidence-bearing method appropriate to the exact property.

An unchanged SHA establishes byte identity for the bound artifact. It does not by itself establish unchanged semantics, authority, assumptions, deployment context, or trust validity.

### 5. Reuse-permitting lifecycle conclusions cost a basis

Lifecycle conclusions that permit reuse, stop invalidation propagation, or remove a blocker must carry an explicit basis.

Examples include:

```text
AssumptionLifecycle.BASIS_CURRENT
DefeaterDisposition.RESOLVED
ImpactDisposition.NO_MATERIAL_EFFECT
```

The basis records the method, producer, bound subject/revisions/context, and RFC 0006 evidence claim appropriate to the property. If an applicable policy defines an evidence profile, the basis must satisfy that profile.

Restrictive conclusions such as `OPEN`, `UNKNOWN_IMPACT`, `REVALIDATION_REQUIRED`, or `VIOLATED` do not require a minimum evidence strength merely to fail closed; their factual assertion remains traceable to its source/basis.

### 6. Defeaters do not become confidence arithmetic

A claim is not assigned a synthetic numeric trust score merely because several objections were resolved.

Resolved defeaters are explicit claim-relative facts. Accepted residual defeaters remain visible limitations.

Neither resolution count nor residual acceptance upgrades an RFC 0006 evidence class.

### 7. The Trust Graph creates no semantic authority

> **No Trust Graph lifecycle transition creates semantic authority.**

Any lifecycle decision that would permit gated current use of semantics that RFC 0011 would otherwise block must be authorized through RFC 0011's existing AuthorityAnchor / AuthorityPolicy / grant / agent / attribution / revision model.

This includes, where authority-relevant:

- accepting residual doubt;
- resolving a defeater whose resolution changes authority-relevant use;
- revalidating an authority relationship;
- selecting a context/configuration that changes applicability or gating;
- waiving or narrowing a blocking condition.

A Trust Graph evaluator may check these records. It does not manufacture authority.

## Logical record graph

The architecture uses the following logical records in addition to existing RFC 0006 / RFC 0011 records:

```text
TrustClaim
EvaluationContext
AssumptionRecord
DependencyEdge
DependencyCompletenessClaim
DefeaterRecord
InvalidationEvent
ImpactEvaluation
LifecycleRevalidationClaim
ReAssuranceRecord
RecordSupersession
CurrentTrustProjection
```

These are logical records. Exact JSON schemas and storage layout are deferred to a later implementation issue.

## Typed state namespaces

RFC 0012 defines three typed lifecycle namespaces.

### AssumptionLifecycle

```text
AssumptionLifecycle.BASIS_CURRENT
AssumptionLifecycle.BASIS_STALE
AssumptionLifecycle.VIOLATED
AssumptionLifecycle.UNKNOWN
```

These describe current use of an assumption basis in a bound context, not evidence strength and not RFC 0011 authority validity.

### DefeaterDisposition

```text
DefeaterDisposition.OPEN
DefeaterDisposition.RESOLVED
DefeaterDisposition.ACCEPTED_RESIDUAL
```

These are claim-relative challenge dispositions, not `SemanticResolutionState` and not evidence statuses.

### ImpactDisposition

```text
ImpactDisposition.NO_MATERIAL_EFFECT
ImpactDisposition.REVALIDATION_REQUIRED
ImpactDisposition.INVALIDATED
ImpactDisposition.UNKNOWN_IMPACT
```

These describe the evaluated impact of an event on an exact dependent property claim in a bound context. They are not `AuthorityValidity` states.

Implementations, schemas, documentation, and UI projections must preserve the owning type. Bare lexical tokens such as `RESOLVED`, `INVALIDATED`, or `UNKNOWN` must not be used where the namespace would be ambiguous.

## EvaluationContext

Every current-trust projection and lifecycle evaluation is scoped to an exact evaluation context.

A logical EvaluationContext identifies, as applicable:

```text
context_id / content hash
selected build
selected target / ISA / platform profile
selected configuration / feature set
selected deployment environment
external service/API revision or endpoint selection
relevant hardware revision
other applicability-determining context
source revision
```

The context is content-addressed or otherwise revision-bound.

> **A current-trust result is valid only for the EvaluationContext against which it was computed. Use in a materially different or unbound context is not reuse; it requires impact evaluation and defaults to `ImpactDisposition.UNKNOWN_IMPACT` until an appropriate basis exists.**

When context selection can change which semantic obligations, authority policies, constraints, or exclusions apply, the selection is authority-relevant under RFC 0011.

## TrustClaim

RFC 0006 already defines property-oriented evidence-bearing claims. RFC 0012 uses `TrustClaim` as a lifecycle graph node representing one such property claim.

A TrustClaim should identify at least:

```text
claim_id
subject / subject revision
property
scope
EvaluationContext reference
current evidence references
assumption references
authority / provenance references when applicable
TCB references
artifact bindings
dependency references
dependency-completeness claim reference
defeater references
source revision
```

A TrustClaim does not mean the whole artifact is trusted. It remains property-scoped.

Artifact-level labels are projections over property claims and must not hide which property is current, stale, invalidated, assumed, tested, or otherwise limited.

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
validity / applicability conditions
EvaluationContext binding
dependent claim references
supersession / invalidation relation when applicable
```

### Assumption support is evidence-bearing

Examples:

```text
payment provider preserves idempotency for endpoint E / operation O
    EvidenceStatus.HUMAN-DECLARED
```

```text
sensor update period <= 10 ms
    EvidenceStatus.MEASURED
```

```text
assembler preserves target object semantics for the relied-upon use
    EvidenceStatus.TRUSTED
```

These statuses retain RFC 0006 meaning.

### Assumption lifecycle

`AssumptionLifecycle` does not claim that the assumption is proven true.

`AssumptionLifecycle.BASIS_CURRENT` means the represented support/basis and applicability conditions are still current for the bound EvaluationContext. The supporting RFC 0006 status may still honestly be `ASSUMED`, `HUMAN-DECLARED`, `TRUSTED`, `MEASURED`, or another appropriate class.

`AssumptionLifecycle.BASIS_STALE` means the assumption's support/basis/context changed and current reuse has not been established.

`AssumptionLifecycle.VIOLATED` means the current context is known not to satisfy the assumption, whether by deterministic contradiction, contract incompatibility, measurement/runtime observation, or another traceable basis appropriate to the statement.

`AssumptionLifecycle.UNKNOWN` means the system lacks a sufficient basis to classify current applicability/support for the bound context.

For a material gated claim, `BASIS_STALE`, `VIOLATED`, or `UNKNOWN` blocks current reuse of any dependent claim until the relevant lifecycle/authority requirements are satisfied.

## DependencyEdge

A logical DependencyEdge identifies a potential material dependency relationship.

It supports at least:

```text
edge_id
source node / revision
target dependent node / revision
dependency kind
scope / property relation
applicable EvaluationContext constraints
method / producer
source revision
```

Material impact is **not** a universal boolean property of an edge. It is evaluated relative to the dependent property and context by `ImpactEvaluation`.

Initial dependency kinds may include concepts equivalent to:

```text
SEMANTIC_DEPENDS_ON
AUTHORITY_DEPENDS_ON
ASSUMES
EVIDENCE_DEPENDS_ON
TCB_DEPENDS_ON
DERIVED_FROM
REALIZED_FROM
VALIDATED_AGAINST
TRACE_DEPENDS_ON
```

Exact enum naming is deferred to schema review.

### Direction

For invalidation propagation:

```text
source dependency changes / is defeated
        ↓
target dependent property claim requires impact evaluation
```

`DERIVED_FROM` and `TRACE_DEPENDS_ON` may be provenance-oriented. A later schema must state whether each concrete edge instance participates in invalidation; provenance presence alone must not silently imply either materiality or independence.

### Mechanically derivable edges

Where existing RFC records already make a dependency explicit, the Trust Graph should derive the corresponding edge rather than rely on manual duplication.

Examples:

```text
RFC 0006 trusted_computing_base entry
        → TCB_DEPENDS_ON

TrustClaim assumption reference
        → ASSUMES

artifact/source hash binding
        → REALIZED_FROM / TRACE_DEPENDS_ON as appropriate

RFC 0011 authority dependency
        → AUTHORITY_DEPENDS_ON
```

Mechanically derived edges contribute to dependency completeness but do not prove that no other material edge exists.

## Dependency completeness

Dependency completeness is the lifecycle analogue of RFC 0011's Semantic Completeness and Authority Completeness.

The invariant is:

> **No material dependency of a gated property claim may be silently absent from the Trust Graph.**

This does not claim that arbitrary real-world dependency discovery can be proven complete in general.

Instead, every gated current-trust projection requires an explicit, property-scoped **DependencyCompletenessClaim** that states the basis under which selective invalidation is considered safe for that claim and context.

A logical DependencyCompletenessClaim supports at least:

```text
completeness_claim_id
target TrustClaim / property
EvaluationContext
covered dependency kinds
covered source/record classes
discovery / enumeration method
producer / tool / version
known exclusions + basis
known unresolved areas
RFC 0006 evidence reference / evidence profile
source revision
```

The completeness claim may honestly be weak. For example:

```text
assumption-edge completeness
    EvidenceStatus.HUMAN-DECLARED

content-addressed artifact-edge completeness
    EvidenceStatus.CHECKED
```

The architecture prefers a visible weak completeness basis over an invisible assumption of completeness.

### Completeness defeater

If a gated claim lacks a required dependency-completeness basis, the graph opens a normal DefeaterRecord such as:

```text
kind: DEPENDENCY_COMPLETENESS
statement: material dependency completeness is not established
DefeaterDisposition.OPEN
```

No special evidence class or confidence score is introduced.

### Three distinct absence/unknown cases

The architecture distinguishes:

```text
1. No material dependency exists for property P in context C
   → supported by a completeness/independence basis

2. Dependency existence is not established
   → open dependency-completeness defeater; current reuse blocked

3. A dependency exists, but the effect of a change is unknown
   → ImpactDisposition.UNKNOWN_IMPACT
```

Absence of an edge without case (1)'s basis is case (2), not independence.

## DefeaterRecord

A **defeater** is a concrete reason that a TrustClaim may fail, may be unsupported, or may not justify the intended current-use conclusion under the declared scope/context.

Examples include:

```text
stale authority policy
conflicting applicable grant
missing provenance
unauthenticated authority root
omitted semantic obligation
unknown dependency completeness
unsupported environment assumption
incomplete runtime oracle
evidentiary self-support cycle
unknown change impact
later-discovered TCB/tool defect
```

A DefeaterRecord supports at least:

```text
defeater_id / kind
target TrustClaim / property
statement / challenge
origin / producer
scope
EvaluationContext
basis / evidence references
DefeaterDisposition
resolution references
residual-acceptance authority binding when applicable
applicability / validity conditions
review trigger / expiry when applicable
source revision
```

### DefeaterDisposition.OPEN

The challenge is material and has not been resolved or validly dispositioned for current use.

A material `OPEN` defeater blocks any gated current-trust projection that depends on the affected claim.

### DefeaterDisposition.RESOLVED

The challenge has been addressed under an explicit method/evidence basis bound to the target property, subject, revisions, and context.

Resolution does not strengthen the underlying claim beyond the evidence actually produced.

### DefeaterDisposition.ACCEPTED_RESIDUAL

The challenge remains a known limitation, but a valid RFC 0011 authority path explicitly permits current use under that residual condition for a bounded property/scope/context.

`ACCEPTED_RESIDUAL` is **not evidence** and does not make the challenged property true.

It does not transform:

```text
TESTED  → PROVEN
TRUSTED → VERIFIED
ASSUMED → CHECKED
```

### Residual-acceptance authority binding

Any `ACCEPTED_RESIDUAL` that permits a use otherwise blocked must bind at least:

```text
AuthorityAnchor / authority path
AuthorityPolicy + revision
applicable RFC 0011 grant kind and bounds
authority agent / attribution
property / scope
subject / artifact revision
EvaluationContext
rationale
applicability conditions
validity interval and/or mandatory review trigger
source revision
```

The RFC 0011 grant must actually cover the residual-disposition decision; RFC 0012 introduces no new grant kind. A bounded `DISCRETION` grant may be appropriate when human judgement is intentionally delegated, but it remains subject to RFC 0011 rules.

`ACCEPTED_RESIDUAL` cannot be used to bypass a semantic obligation that remains unresolved/unauthorized, an unresolved authority conflict, a revoked/invalid authority path, or a non-waivable constraint whose policy does not authorize such residual disposition.

If any bound scope/context/authority/basis changes, the residual disposition becomes non-current and the defeater returns to `OPEN` until re-evaluated under the new context.

## InvalidationEvent

An InvalidationEvent records a change or newly discovered adverse fact that may affect dependent claims.

It supports at least:

```text
invalidation_event_id
changed / challenged subject
prior revision / new revision when applicable
change kind
knowledge/evidence basis
observed time / repository revision
producer
initial affected roots
```

An event does not erase prior records.

Initial change-kind concepts include:

```text
REVISION_CHANGE
CONTEXT_CHANGE
AUTHORITY_BASIS_CHANGE
TCB_BASIS_CHANGE
KNOWLEDGE_CHANGE
DEFEATER_DISCOVERED
RECORD_CORRECTION
```

For `KNOWLEDGE_CHANGE` or `DEFEATER_DISCOVERED`, `prior_revision == new_revision` is valid. The subject bits or tool version may be unchanged while the basis for relying on them changes.

Examples:

```text
Requirement revision changed
AuthorityPolicy superseded
AuthorityAnchor protection basis changed
Assumption source/API contract changed
Verifier revision changed
Compiler/tool version changed
Compiler/tool defect discovered in unchanged version
Generated artifact changed
Deployment configuration changed
Prior provenance record discovered incorrect
```

### TCB/tool defect discovery

RFC 0006 evidence records already name `trusted_computing_base` components.

A newly discovered relevant defect in a TCB component opens an invalidation/defeater event for claims whose current use relies on that component. `TCB_DEPENDS_ON` edges should be mechanically derived from the RFC 0006 TCB references where possible.

Historical facts such as "the tests ran" remain historical facts; the standing reliance on the defective TCB component becomes non-current until an appropriate impact/revalidation basis exists.

## RecordSupersession

A RecordSupersession is append-only metadata for a historical record discovered to be wrong, incomplete, misleading, or superseded.

It identifies:

```text
prior record
reason
correction / replacement record when available
producer / basis
source revision
```

The prior record remains addressable as history, but current projections follow the supersession relation and must not silently use a known-corrected basis.

## ImpactEvaluation

An ImpactEvaluation evaluates how an InvalidationEvent affects one exact dependent property claim.

It is keyed by at least:

```text
invalidation event
dependency edge
target TrustClaim
property
EvaluationContext
```

and records an `ImpactDisposition` plus its method/basis.

### ImpactDisposition.NO_MATERIAL_EFFECT

The changed/challenged dependency has been shown not to affect the target property for the bound context under an explicit basis.

Because this conclusion permits reuse and stops propagation along that property relation, it must carry an RFC 0006 evidence-bearing basis appropriate to the property and any applicable evidence profile.

### ImpactDisposition.REVALIDATION_REQUIRED

The prior property may still hold, but current reuse is not established for the changed dependency/context.

### ImpactDisposition.INVALIDATED

The changed/challenged dependency is known to break the target property, assumption, authority applicability, or artifact binding for the bound context.

### ImpactDisposition.UNKNOWN_IMPACT

A represented material dependency exists, but the effect of the change/challenge on the target property cannot currently be determined.

For a gated current-trust projection:

> **`REVALIDATION_REQUIRED`, `INVALIDATED`, and `UNKNOWN_IMPACT` fail closed for the affected property claim until an appropriate revalidation/re-assurance basis exists.**

## Deterministic invalidation propagation

Given an InvalidationEvent, a bound EvaluationContext, and the represented dependency graph:

1. Bind the event to an exact changed/challenged subject and basis.
2. Identify directly dependent property claims through applicable dependency edges.
3. For each `(event, edge, target claim, property, context)` tuple, produce an ImpactEvaluation.
4. `ImpactDisposition.NO_MATERIAL_EFFECT` may stop propagation for that property relation only when its required basis is present.
5. For `REVALIDATION_REQUIRED`, `INVALIDATED`, or `UNKNOWN_IMPACT`, propagate to dependent property claims transitively.
6. A node with no represented outgoing dependency may terminate propagation only when its applicable DependencyCompletenessClaim covers the relevant dependency classes/property/context.
7. If no such completeness basis exists, open/retain the dependency-completeness defeater; do not infer independence.
8. Independent/unreachable claims whose independence is supported by their completeness basis remain unchanged.
9. Multiple paths to the same property are combined conservatively; one unresolved/invalidating material path is not cancelled by a separate `NO_MATERIAL_EFFECT` path unless a property-specific composition rule establishes that cancellation.
10. The algorithm must terminate under the cycle/SCC rules below.

Pseudo-flow:

```text
Changed / Challenged Subject
            ↓
Represented Dependency Relations
            ↓
Property + Context Impact Evaluation
       ┌────┼────────────────────┐
       ↓    ↓                    ↓
NO_MATERIAL_EFFECT      REVALIDATE / INVALID / UNKNOWN
       │                           │
requires basis                     │
       │                           ▼
 stop this property edge      dependent property claims
                                   │
                                   ▼
                        completeness checked at boundary
```

The propagation result is evidence-bearing when it asserts exact dependency/impact relations. Reuse-permitting conclusions must identify their RFC 0006 evidence basis and any required profile.

## Cycles and graph structure

RFC 0011's **authority graph remains acyclic** under RFC 0011. RFC 0012 does not redefine that rule.

The broader Trust Graph may contain cycles because evidence, observations, assumptions, and validation infrastructure can be mutually related.

Therefore:

> **The invalidation engine must terminate on cyclic graphs and must not interpret "already visited" as evidence of current validity.**

A conforming architecture may use strongly connected component (SCC) decomposition or an equivalent deterministic method.

For an SCC:

- the SCC is evaluated as a unit for propagation;
- a conservative unresolved/invalidating disposition inside the SCC propagates to dependent current-use claims unless a stronger property-specific basis resolves it;
- a cycle containing `EVIDENCE_DEPENDS_ON` / `VALIDATED_AGAINST` relationships that would make a claim materially depend on evidence validated only by the same support cycle creates an `EVIDENTIARY_SELF_SUPPORT` defeater;
- that defeater remains `OPEN` until an out-of-cycle basis or another explicit method resolves the self-support concern.

The first implementation experiment may reject unsupported cycles rather than implement a general fixpoint semantics, provided the rejection is deterministic and fail-closed.

## Gated current-trust projection

A **CurrentTrustProjection** is a machine- or human-consumable statement used by an applicable policy/gate to permit or deny an action such as merge, release, deployment, acceptance, or another explicitly defined trust-dependent action.

It binds at least:

```text
target TrustClaim / property
subject / artifact revision
EvaluationContext
current evidence references
DependencyCompletenessClaim
defeater set + dispositions
impact evaluations
applicable authority references
projection policy / gate
source revision
```

A projection must not collapse property-scoped states into an undifferentiated artifact-wide `TRUSTED` / `INVALIDATED` label.

A gated current-trust projection fails closed when any policy-required property has:

- an open material defeater;
- missing dependency-completeness basis;
- a stale/violated/unknown material assumption;
- `ImpactDisposition.REVALIDATION_REQUIRED`, `INVALIDATED`, or `UNKNOWN_IMPACT`;
- required authority that is not current under RFC 0011;
- another policy-defined unmet evidence/assurance requirement.

Residual acceptance may permit a specifically authorized residual condition only when its RFC 0011 binding is current and the projection policy explicitly permits that residual disposition.

## Revalidation and re-assurance

### LifecycleRevalidationClaim

A `LifecycleRevalidationClaim` is a narrow property-scoped claim that a previously represented non-authority relationship remains applicable/current under changed revisions or context.

It identifies:

```text
prior claim / record
new dependency revisions
property / scope
EvaluationContext
method
producer
assumptions
RFC 0006 evidence claim
applicable evidence profile
new subject/artifact bindings
source revision
```

Authority-specific revalidation remains owned by RFC 0011. When the relationship being restored is authority validity or authority applicability, RFC 0012 references the RFC 0011 revalidation/re-acceptance record rather than substituting a generic lifecycle claim.

### ReAssuranceRecord

A `ReAssuranceRecord` is a composite lifecycle record showing how a broader current trust chain was restored after invalidation.

It may reference one or more of:

```text
re-extraction
semantic re-resolution
RFC 0011 re-acceptance / re-authorization
re-running deterministic verification
re-running translation/preservation checks
rebuilding artifacts
re-testing / re-measuring
new assumption validation
new defeater resolution
new dependency-completeness claim
new context binding
```

A ReAssuranceRecord is not a new evidence class and does not assert more than its component claims/evidence support.

The distinction is intentional:

```text
LifecycleRevalidationClaim
    narrow property/relationship remains current

ReAssuranceRecord
    composition/orchestration record over multiple heterogeneous
    reused and regenerated claims/evidence
```

Merging them would make it harder to determine whether a record is one checkable property claim or a composite current-trust reconstruction.

## Selective evidence reuse

A lifecycle-aware architecture avoids both extremes:

```text
change anything → rerun everything
```

and:

```text
artifact still exists → trust everything
```

Selective reuse is permitted only when dependency/completeness analysis provides a basis.

Example:

```text
AuthorityPolicy revision changed
        ↓
RFC 0011 authority applicability requires re-evaluation
        ↓
P1 accepted-specification linkage may require refresh
        ↓
Generated assembly bytes happen to be unchanged
        ↓
Assembler version/TRUSTED record may remain the same historical reliance
        ↓
But the executable's current semantic-authority property claim
cannot be reused until affected upstream authority/semantic claims are current
```

An unchanged SHA is strong evidence that the bits did not change. It is not by itself evidence that the **meaning, authority context, dependency completeness, assumptions, or deployment context** remained current.

## Worked example A — payment retry and idempotency

### Existing accepted candidate

The current payment-retry example contains accepted semantics equivalent to:

```text
retry_count = 3
retry_on_http_500 = true
retry_on_timeout = false
backoff_policy = exponential
request_timeout_ms = 2000
idempotency_requirement = true
terminal_failure_behavior = surface_failure
```

The client-side semantic obligation:

```text
idempotency_requirement = true
```

is not the same proposition as the provider/environment assumption:

```text
ASSUMPTION API-IDEMPOTENCY-01
statement:
  for endpoint E / operation O, repeating the logical payment request
  with the same correctly scoped idempotency key does not create
  an additional charge
source:
  Payment API contract v7
```

The Trust Graph must preserve that distinction.

Property claim:

```text
CLAIM PAYMENT-RETRY-SAFETY
property:
  retry behavior does not create duplicate charge under declared
  retry/idempotency contract and context
```

Dependencies include at least:

```text
client obligation: idempotency key is used as specified
provider assumption: API-IDEMPOTENCY-01
retry semantics / accepted specification
relevant authority constraint/evidence
```

A DependencyCompletenessClaim for this POC explicitly states which dependency classes were considered. It does **not** claim that all real payment semantics are complete.

Known out-of-scope semantic questions include, unless separately represented:

```text
idempotency-key lifetime / persistence
cross-endpoint key semantics
partial success / ambiguous 500 behavior
system-level retry amplification across other components
```

Those are not silently discharged by this example.

### Provider contract change

The provider publishes API contract v8.

```text
InvalidationEvent
  change_kind = REVISION_CHANGE
  changed_subject = Payment API contract
  old_revision = v7
  new_revision = v8
```

Property-scoped impact:

```text
API-IDEMPOTENCY-01
    → AssumptionLifecycle.BASIS_STALE

PAYMENT-RETRY-SAFETY
    → ImpactDisposition.REVALIDATION_REQUIRED

CurrentTrustProjection(PAYMENT-RETRY-SAFETY, context C)
    → BLOCKED
```

The artifact may remain byte-identical. Historical authority/test records remain historical records. Neither fact restores the current safety property.

If a deterministic contract check or another policy-permitted evidence method establishes the same provider-side idempotency property for v8, a `LifecycleRevalidationClaim` may restore the assumption relationship.

If the provider-side change also affects the basis under which accepted semantics remain authorized, the corresponding RFC 0011 authority revalidation/re-acceptance is mandatory; RFC 0012 revalidation cannot substitute for it.

If v8 is known non-idempotent:

```text
AssumptionLifecycle.VIOLATED
PAYMENT-RETRY-SAFETY → ImpactDisposition.INVALIDATED
```

and semantic re-resolution / RFC 0011 authority handling is required before current use can be restored.

### Missing-edge attack

Suppose the idempotency-key-scope dependency was never represented.

RFC 0012 does **not** allow:

```text
no edge → no dependency → CURRENT
```

Instead, if the DependencyCompletenessClaim does not establish coverage of that relation, the `DEPENDENCY_COMPLETENESS` defeater remains `OPEN` and the gated current-trust projection is blocked.

## Worked example B — artifact-chain change impact at property granularity

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

Suppose Requirement R changes.

Do not assign one lifecycle state to `Executable E` as a whole.

Evaluate exact property claims instead, for example:

```text
Claim P1.spec_linkage(S, I)
    dependency on R/S changed
    → ImpactDisposition.REVALIDATION_REQUIRED

Claim P2.no_overflow(I)
    current-use projection blocked until the accepted-spec basis is current
    → REVALIDATION_REQUIRED or UNKNOWN_IMPACT depending on analysis

Claim P4-A.assembler_boundary(A, object)
    historical object-generation/TRUSTED boundary record for exact old A/object
    remains historical evidence

Claim P4-R.accepted_contract_observation(E)
    old runtime observations remain historical EvidenceStatus.TESTED[_EXHAUSTIVE]
    but current semantic-contract projection is blocked while upstream
    accepted semantics are non-current
```

After re-resolution, suppose S/I are deterministically shown equivalent to their old property-relevant revisions and regenerated A/E hashes are identical.

New equivalence/revalidation evidence can justify selective reuse. The unchanged hashes help establish artifact identity but do not bypass upstream semantic/authority/context re-assurance.

## Worked example C — later-discovered TCB/tool defect

Assume a P4-A/P4-L claim relied on tool version T as:

```text
EvidenceStatus.TRUSTED
trusted_computing_base: tool T
```

Later, a relevant correctness defect is discovered in the same unchanged tool revision.

```text
InvalidationEvent
  change_kind = KNOWLEDGE_CHANGE / DEFEATER_DISCOVERED
  changed_subject = tool T
  prior_revision = T
  new_revision = T
  basis = defect/CVE/correctness finding
```

Mechanically derived `TCB_DEPENDS_ON` edges identify claims that relied on T.

Historical observations remain historical observations. Current reliance on T for affected properties becomes subject to impact evaluation and cannot remain current merely because the version/hash did not change.

## Defeater examples in current Spec2Exec

Many current limitations/rejection conditions can be projected as defeaters without changing their existing owning semantics.

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

Claim: current lifecycle dependency model is sufficient for property P
Possible defeaters:
- dependency-completeness basis missing
- material assumption edge may be omitted
- evidentiary self-support cycle

Claim: executable carries accepted semantics
Possible defeaters:
- P3 preservation only TESTED, not PROVEN
- assembler/linker are TRUSTED TCB components
- runtime evidence exercises QEMU, not physical hardware
```

Some are blockers under current policy. Some may be accepted residual limitations under a bounded RFC 0011 authority path. The Trust Graph makes the distinction visible without pretending all residual doubt can or should be eliminated.

## Assurance-argument projection

This RFC does not make Spec2Exec a GSN/SACM authoring tool.

The Trust Graph may preserve enough structure for a future adapter to project:

```text
Claim
├── Evaluation Context
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

- a general proof that all real-world requirements or dependencies are complete;
- a universal scalar trust/confidence score;
- a replacement for GSN, SACM, or assurance-case tools;
- certification acceptance criteria;
- a universal risk/criticality ladder;
- automatic derivation that `CRITICAL` implies a particular evidence class;
- runtime Simplex/fallback-controller architecture;
- continuous runtime assumption monitoring semantics;
- cross-component emergent-semantics composition;
- enterprise identity/governance/quorum policy beyond RFC 0011 integration;
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

Cross-component behavior such as retry amplification can create semantic obligations/dependencies not present in any single component specification.

This is a major future research topic and should receive its own Issue/RFC only after the bounded single-build Trust Graph experiment is validated.

### Stronger organizational governance

Authentication, delegation depth, revocation, quorum, organizational role mapping, and accountability remain future semantic-authority work layered on RFC 0011.

## Architecture invariants

If this RFC is accepted, the intended invariants are:

1. **Historical records are append-only; current validity is computed separately.** Corrections/supersessions do not silently rewrite prior records.
2. **Material assumptions are first-class dependency nodes rather than untraceable prose only.**
3. **No material dependency of a gated property claim may be silently absent from the Trust Graph.**
4. **Absence of a dependency edge is not evidence of independence.** Independence/current reuse requires a property/context-scoped DependencyCompletenessClaim or another explicit basis.
5. **Known material impact that cannot be determined fails closed.**
6. **Invalidation propagates selectively through property/context-specific dependency relations; it is not global by default.**
7. **Reuse-permitting lifecycle conclusions require an explicit RFC 0006 evidence-bearing basis appropriate to the property and applicable policy.**
8. **Evidence reuse across revisions requires unchanged bound dependencies under a completeness basis or explicit revalidation/equivalence evidence.**
9. **Defeaters are claim-relative challenges, not evidence-strength labels or confidence arithmetic.**
10. **Open material defeaters block gated current use.**
11. **Accepted residual doubt remains visible, does not strengthen the underlying evidence class, and requires an explicit current RFC 0011 authority binding for the bounded property/scope/context.**
12. **The Trust Graph creates no semantic authority.**
13. **Lifecycle/impact state is property-scoped and context-bound.** Artifact-wide labels are projections only.
14. **Every current-trust projection binds the exact EvaluationContext in which it was computed.** Use in a materially different/unbound context fails closed pending impact evaluation.
15. **An unchanged artifact hash does not by itself establish unchanged semantic authority, assumptions, dependency completeness, or current trust context.**
16. **Knowledge changes can invalidate current reliance even when artifact/tool revisions are unchanged.**
17. **The invalidation engine terminates on cycles.** Evidentiary self-support cycles are surfaced as defeaters unless an out-of-cycle basis resolves them.
18. **Re-assurance may selectively reuse valid evidence but must bind reused/regenerated claims to the new dependency and EvaluationContext.**
19. **Trust Graph state spans the executable semantic path; it is not inserted as a misleading serial compiler stage.**
20. **RFC 0006 remains the only normative owner of evidence classes; RFC 0011 remains the normative owner of semantic authority.**

## Minimum implementation experiment after architecture acceptance

This RFC does not authorize implementation by itself.

After closure review, a later implementation Issue should use the payment-retry POC to test the riskiest claims without becoming a generic graph product.

Minimum experiment:

```text
Payment API v7 idempotency assumption
        ↓
ASSUMES edge to PAYMENT-RETRY-SAFETY
        ↓
DependencyCompletenessClaim for that property/context
        ↓
provider contract v7 → v8 InvalidationEvent
        ↓
property/context ImpactEvaluation
        ↓
current trust projection blocks while revalidation required
        ↓
artifact may remain byte-identical
        ↓
LifecycleRevalidationClaim or RFC 0011 re-acceptance as applicable
        ↓
selective current-use restoration
```

Mandatory negative controls should include:

```text
missing completeness basis
missing assumption edge / incomplete discovery declaration
NO_MATERIAL_EFFECT without required basis
ACCEPTED_RESIDUAL without RFC 0011 authority binding
projection consumed under a different EvaluationContext
later-discovered tool defect with unchanged tool revision
deliberate evidence-support cycle
```

A useful falsification criterion is:

> If a practically meaningful property cannot obtain any bounded dependency-completeness basis without either treating all repository/environment facts as dependencies or routinely laundering uncertainty through residual acceptance, the proposed selective Trust Graph architecture is not useful in its current form and should be revised rather than generalized.

## Open closure questions

Before promotion from Draft:

1. Does the DependencyCompletenessClaim + open completeness defeater close the missing-edge bypass without turning every unknown repository fact into global invalidation?
2. Is the authority non-creation rule sufficient to prevent `ACCEPTED_RESIDUAL` / lifecycle revalidation from bypassing RFC 0011?
3. Are reuse-permitting lifecycle conclusions constrained enough without inventing a new scalar evidence hierarchy?
4. Are `(event, edge, target claim, property, EvaluationContext)` impact semantics sufficiently precise for selective invalidation?
5. Are SCC / evidentiary-self-support rules sufficient for termination and honesty without requiring a general fixpoint assurance engine?
6. Is the history / standing reliance / correction / current-validity distinction compatible with RFC 0006 and RFC 0011?
7. Does the payment-retry example now avoid conflating client-side idempotency obligations with provider-side idempotency assumptions?
8. Are `LifecycleRevalidationClaim` and `ReAssuranceRecord` ownership/scope distinctions clear enough relative to RFC 0011 authority revalidation?

## Status / next step

This RFC is intentionally **Draft / Proposed — Revision 2**.

The next step is a closure review against the Revision 1 hostile-review findings, especially:

```text
B-01 dependency completeness
B-02 authority non-creation / residual laundering
H-01 basis for reuse-permitting lifecycle conclusions
H-02 property/context-scoped impact
H-03 cycle/SCC semantics
H-04 knowledge-change invalidation
H-05 residual binding/lifecycle
H-06 evaluation-context binding
M-01 typed namespaces / ownership
```

No executable Trust Graph implementation should be merged solely on the basis of this draft.