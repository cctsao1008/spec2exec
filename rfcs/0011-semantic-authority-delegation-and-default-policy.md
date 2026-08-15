# RFC 0011 — Semantic Authority, Delegation, and Default Policy

- **Status:** Draft / Proposed — closure-reviewed; awaiting #54 reconciliation before acceptance
- **Issue:** #53
- **Dependency:** #54 must reconcile evidence vocabulary and RFC lifecycle before this RFC is promoted to Accepted
- **Scope:** semantic obligations, authority trust anchors, delegated defaults, authority validity, applicability, provenance, attribution, revision/invalidation, completeness, and fail-closed acceptance before SpecIR synthesis

## Summary

Spec2Exec does not require every implementation choice or every missing detail to be manually approved. It requires every **semantic obligation in the executable semantic closure of a selected build** to have an explicit, revision-bound authority basis.

A **semantic obligation** is an authority-relevant decision or constraint whose alternatives can change the accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build. Semantics-preserving implementation choices such as register allocation or equivalent instruction selection are not authority obligations merely because they change the exact binary.

A reasonable default may be used without an immediate human clarification step **only when an applicable authority policy already grants authority for that decision under a bounded scope**. The fact that a default is common, low-impact, plausible, recommended by an AI system, or described as an industry practice does not itself create authority.

The central rule is:

> **Capability, plausibility, convention, and low impact do not create semantic authority. Authority originates at declared trust anchors and may be delegated through scoped, revisioned, bounded, and revocable policies.**

The authority chain itself is not infinitely provable. Spec2Exec explicitly declares where authority derivation stops and trust begins. The declared anchor set and the mechanism that protects/controls anchor declarations are therefore part of the **Authority TCB**.

This RFC refines RFC 0010 and, once Accepted, supersedes the mixed authority-state model in Draft RFC 0005. Evidence-strength vocabulary remains owned by RFC 0006 / issue #54 rather than by this RFC.

## Closure-review disposition

The hostile architecture review of the first draft returned **PASS WITH MAJOR FINDINGS**. Revision 2 introduced AuthorityAnchors, the Authority TCB, typed authority state, bounded grant kinds, policy-controlled self-authorization, conservative executable semantic closure, extraction provenance, immutable acceptance/current validity separation, composition constraints, and a deterministic gate that produces no authority.

The closure review of revision 2 returned:

```text
PASS WITH MINOR FINDINGS
READY FOR #54 RECONCILIATION
```

The closure review identified two remaining completeness risks rather than a new architecture defect:

1. a candidate could be omitted before gating if `obligation-hood` or closure exclusion were treated as untrusted free metadata;
2. an obligation could bind only a favorable authority grant if the evaluator did not discover the complete set of potentially applicable authority grants.

This revision closes those residuals with explicit **semantic completeness** and **authority completeness** invariants.

## Architecture boundary

Unresolved or invalid authority state remains before executable SpecIR.

```text
Source Artifacts / Candidate Frontends
        ↓
Extraction / Interpretation
        ↓
Candidate Semantic Subjects
        │
        ├── obligation-hood determination
        ├── semantic obligations
        ├── resolution state
        ├── provenance
        ├── applicability / closure inclusion-exclusion
        ├── authority-relevant classifications
        ├── conflict sets
        ├── dependencies
        └── authority bindings / exercises
        ↓
Conservative Executable Semantic Closure
        ↓
Complete Authority-Grant Discovery
        ↓
Authority Evaluation
        ↓
Deterministic Semantic Authority Gate
        ↓
Accepted Specification
        ↓
Semantic Synthesis
        ↓
SpecIR
```

`UNRESOLVED`, `CONFLICT`, unauthorized, revoked, expired, invalidated, or potentially stale obligations in the executable semantic closure fail closed before SpecIR synthesis.

This RFC does **not** move those states into executable SpecIR by default.

## Candidate-semantics sources and extraction

Candidate semantics may originate from natural-language requirements, PRDs, requirements-management systems, standards, contracts, SDD tools, AI coding workflows, search/retrieval, or domain-specific frontends.

These remain candidate semantics until authority resolution is complete.

### Extraction is a trust boundary

```text
Source Artifact
    hash / revision
        ↓
Extraction / Interpretation
    method / tool / version / transformation
        ↓
Candidate Semantic Subject
```

The extractor may be a parser, human, AI system, search system, adapter, or other tool. It is not trusted merely because it preserved a source filename or clause number.

An extraction record should preserve at least:

```text
source_artifact
source_hash / revision
source_locator
extractor / producer
extractor version or revision
extraction method
normalization / transformation information
```

Where practical, `source_locator` should be machine-checkable.

A provenance record stating `clause 4.2` does not establish that clause 4.2 supports the extracted value. The extraction/support claim carries evidence under RFC 0006.

Lossy normalization, merging, or rewriting remains traceable to the contributing source spans rather than silently becoming authoritative provenance.

## Semantic obligation

A **semantic obligation** is the authority-gated unit of this RFC:

> An authority-relevant decision or constraint whose alternatives can change the accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build.

Typical semantic obligations include:

```text
motor cutoff threshold
retry policy
access-control rule
overflow behavior
accepted input domain
failure-handling behavior
configuration meaning
contract clause
```

Semantics-preserving choices such as register allocation, temporary-register selection, equivalent instruction scheduling, assembler formatting, and non-semantic naming are not authority obligations merely because they change implementation details.

### Obligation-hood is authority-relevant

Determining that a candidate subject **is not** a semantic obligation can remove it from authority gating. That determination is therefore authority-relevant whenever exclusion could widen what becomes executable without authority.

Normative rule:

> **Obligation-hood and exclusion from the executable semantic closure require an authorized basis or a deterministic derivation from already authorized data. An untrusted source may not silently classify behavior-determining semantics as non-obligatory.**

An unbasis'd exclusion is treated conservatively as in-closure and fails closed with the closure/authority machinery.

## Typed state model

### Resolution state

```text
RESOLVED
UNRESOLVED
CONFLICT
```

`RESOLVED` means a concrete semantic value, rule, constraint, or derivation is available. It does not mean authoritative, accepted, applicable, correct, or verified.

Proposal origin is recorded separately. Derived obligations identify their derivation procedure and parent obligations.

### Authority validity

`authority_validity` is a **computed evaluation state for an exact evaluation context**. It is not an immutable truth stored on the SemanticObligation.

Candidate values are:

```text
AUTHORIZED
UNAUTHORIZED
POTENTIALLY_STALE
INVALIDATED
REVOKED
EXPIRED
```

`AUTHORIZED` is a governance state, not an evidence class.

### Acceptance state

```text
NOT_ACCEPTED
ACCEPTED
```

An `AcceptanceRecord` is an immutable historical event. Current validity is evaluated separately.

### Applicability

```text
APPLICABLE
NOT_APPLICABLE
UNKNOWN
```

`UNKNOWN` never silently excludes an obligation. `NOT_APPLICABLE` requires an authorized or deterministic exclusion basis when exclusion could reduce authority requirements.

### Attribution assurance

Authority semantics and identity/attribution assurance are separate. An implementation represents:

```text
attribution mechanism
producer / claimed identity
assurance descriptor or policy-defined acceptable mechanism
supporting evidence
```

A policy may define acceptable attribution mechanisms or a policy-specific partial order/profile. This RFC does not impose a universal scalar ranking.

The first POC may honestly represent current acceptance as unauthenticated human-declared / VCS-attributed presence. Cryptographic signatures remain future work.

## Authority-relevant classifications

Authority-relevant classifications include at least:

```text
obligation-hood
decision_class
impact_class
semantic_scope
applicability / NOT_APPLICABLE determination
selected build / configuration classification
closure inclusion / exclusion
```

Normative rule:

> **Any classification or scope decision that can widen authority-policy applicability or remove a candidate from authority gating is itself authority-relevant and requires an authorized basis or a deterministic derivation from already authorized data.**

Untrusted classification may conservatively narrow or deny delegation. It must not widen delegation or silently remove a candidate from the gate.

This rule is intentionally asymmetric: conservative escalation is safe; authority-reducing classification is not.

## Authority Trust Anchors and Authority TCB

An **AuthorityAnchor** is a revision-bound trust root whose authority is asserted at the project/governance boundary rather than derived from another Spec2Exec authority source.

The **Authority TCB** includes:

1. the declared AuthorityAnchor records;
2. the exact anchor-set enumeration and revision/hash;
3. the mechanism that controls/protects anchor declaration or modification.

The architecture requires:

1. every authority-binding path terminates at a declared AuthorityAnchor;
2. the authority/delegation graph is acyclic;
3. the anchor set is enumerable and revision-bound;
4. the AcceptanceRecord enumerates the anchors and binds the anchor-set identity/hash;
5. changing the anchor set or its protection/declaration basis creates a validity/re-acceptance obligation.

A project may have multiple anchors, and an obligation may require multiple bindings rooted at different anchors.

The evidence status attached to anchor assertions/protection belongs to RFC 0006. For the first POC, repository write-access governance and human-declared project ownership may be represented honestly as unauthenticated trust inputs rather than stronger authenticated approval.

## Authority policy and grant kinds

An **AuthorityPolicy** defines what authority is granted, to whom, under what scope, and under which constraints.

A policy should identify at least:

```text
policy_id / content hash
source authority / anchor path
source revision
subject/scope/applicability match
covered semantic-obligation or decision classes
grant kind
grant bounds
allowed authority agent / agent class
agent version/revision when relevant
self-authorization rule
redelegation rule
constraint evidence profile when applicable
validity interval when applicable
revocation / supersession relation
attribution requirement
```

Unbounded phrases such as `use industry-standard defaults` are insufficient unless reduced to a pinned source, bounded set/range, pinned procedure, explicit constraints, or explicitly bounded discretionary scope.

Grant kinds are:

```text
VALUE
VALUE_SET
CONSTRAINT
PROCEDURE
SOURCE
DISCRETION
```

### VALUE

Authorizes one exact semantic value or rule.

### VALUE_SET

Authorizes selection within an enumerated or mechanically bounded set/range.

### CONSTRAINT

Authorizes/asserts an invariant over applicable obligations or their composition.

Constraint satisfaction is separate from the authority of the constraint. A policy specifies an **acceptable evidence profile** under RFC 0006, for example allowed evidence statuses, method class, scope, and required subject bindings. The model does not assume a universal scalar `status >= X` ordering.

### PROCEDURE

Authorizes a deterministic decision procedure and binds:

```text
procedure/tool identity
version/revision
bound inputs / input-source references
constraints
fail-closed fallback
```

### SOURCE

Delegates to a specific external source and pinned revision or an explicitly authorized revision-selection procedure.

### DISCRETION

Delegates bounded judgement.

`DISCRETION` must use a closed or mechanically bounded subject/scope expression. Wildcard or open-ended authority such as `scope = *` is not a valid `DISCRETION` grant for the first authority model.

The allowed scope, constraints, attribution requirements, and self-authorization rule must be explicit.

For the first #53 implementation, self-authorizing `DISCRETION` is allowed only when the grant is anchor-direct because redelegation/depth > 1 is already outside the MVI. This is an MVI restriction, not a permanent universal architecture rule.

## Authority agent and self-authorization

An **authority agent** may be a human role, deterministic policy engine, rules engine, workflow service, AI system, or future automation.

> **An agent receives authority from a valid authority path and policy, not from capability, accuracy, plausibility, or intelligence.**

The architecture records `proposer` and `authority_agent` separately.

Default rule:

> **If the same agent originated a candidate and also exercises authority over it, the gate fails closed unless the applicable policy explicitly permits self-authorization for that grant kind and bounded scope.**

For `VALUE_SET` or a version-pinned deterministic `PROCEDURE`, the admissible semantics are already bounded by the authority source. For `DISCRETION`, self-authorization is more consequential and must be explicit and visible in acceptance/evidence.

Redelegation is fail-closed by default. The first implementation uses `redelegation_allowed = false` and maximum depth 1 beyond anchor/policy.

## Conflicts and authority completeness

A semantic `CONFLICT` preserves candidate alternatives and per-candidate provenance.

Separately, the evaluator must discover the complete set of authority grants that could govern an obligation.

### Conservative grant discovery

The gate must not rely only on authority bindings supplied by the obligation itself.

Normative rule:

> **For each in-closure semantic obligation, authority evaluation must conservatively discover the complete set of grants whose declared subject, scope, applicability, and selected-build context can govern that obligation. Every potentially applicable grant is evaluated; grants rejected as inapplicable retain a deterministic or authorized inapplicability basis.**

The evaluation therefore records at least:

```text
authority_bindings_used
authority_grants_evaluated
authority_grants_applicable
authority_grants_rejected_as_inapplicable + basis
```

If applicable grants rooted at different anchors or policies contradict the selected value/rule/procedure and no authorized precedence rule resolves them, the result is an **authority conflict** and fails closed.

Suggested structured failure:

```text
E_AUTH_AUTHORITY_CONFLICT
```

This is distinct from `E_AUTH_CONFLICT`, which represents unresolved candidate-semantic alternatives.

Full jurisdiction and precedence lattices remain deferred; fail-closed conflict preservation is sufficient for the first implementation.

## Executable semantic closure

Authority gating is scoped to a **selected build, target, and configuration**.

The selected configuration itself is authority-relevant when its choice can change which obligations are gated.

The **executable semantic closure** is the transitive set of semantic obligations and authority constraints that can affect accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build.

### Conservative closure rule

> **Anything not demonstrably outside the executable semantic closure is conservatively treated as inside it.**

An under-approximated closure is an authority bypass.

A `ClosureRecord` / AcceptanceRecord therefore identifies:

```text
selected build / target / configuration
closure method + version
included semantic obligations
excluded candidate subjects
basis for each exclusion
applicable authority constraints
transitive dependencies
```

Every exclusion that could reduce authority requirements requires an authorized or deterministic basis. The gate checks both the inclusion set **and the exclusion set**.

For the first #53 implementation, multi-configuration closure analysis is not required. The MVI may use one explicit enumeration.

## Semantic completeness and authority completeness

Two soundness conditions are normative:

### Semantic completeness

> **No authority-relevant semantic obligation may be silently omitted from the executable semantic closure.**

This includes omission by untrusted obligation-hood classification, `NOT_APPLICABLE`, selected-configuration choice, or unbasis'd closure exclusion.

### Authority completeness

> **No applicable authority grant or constraint may be silently omitted from authority evaluation.**

This includes grants not explicitly referenced by the candidate obligation. Authority evaluation derives the potentially applicable set from the declared Authority TCB, policies, subject/scope matching, and selected build context.

These completeness properties are necessary to prevent a plausible, machine-readable ACCEPTED record from being produced by omission.

## Composition constraints

Per-obligation authorization is necessary but not sufficient.

An AuthorityAnchor or AuthorityPolicy may assert a `CONSTRAINT` over the executable semantic closure.

The gate requires:

```text
all applicable semantic obligations have valid authority
AND
all applicable authority constraints are satisfied under their required evidence profiles
```

The authority of a constraint and the evidence that the closure satisfies the constraint are distinct facts.

## Logical record graph

The architecture prefers a normalized, content-addressed graph:

```text
AuthorityAnchor
AuthorityPolicy
DelegationRecord / AuthorityExercise
SourceArtifact
ExtractionRecord
CandidateSubject / SemanticObligation
ClassificationRecord
ConflictSet
ClosureRecord
AuthorityEvaluation
AcceptanceRecord
InvalidationEvent
RevalidationClaim / EquivalenceClaim
```

A SemanticObligation supports multiple authority bindings and an explicit combination rule rather than hard-coding cardinality one.

Content hashes/revisions make dependency changes visible as stale/rebuild/re-acceptance obligations.

## Authority exercise, evaluation, and gate

```text
Authority Anchor / Policy / Delegation
        ↓
Authority Agent Exercise
        ↓
Complete Authority Evaluation
        ↓
Deterministic Semantic Authority Gate
        ↓
Acceptance Record or structured rejection
```

> **The Semantic Authority Gate is deterministic and produces no authority. It checks recorded authority/evaluation facts and emits acceptance or explicit reason codes.**

The gate must not mutate an unauthoritative decision into an authoritative one merely because a matching policy was discovered.

### Minimum gate conditions

For every in-closure obligation, and for every exclusion/applicable authority rule relevant to that closure, the gate requires at least:

```text
resolution_state == RESOLVED
applicability == APPLICABLE or conservatively included
obligation-hood / inclusion / exclusion basis is valid
selected build/configuration basis is valid
all authority-relevant classifications have valid bases
complete authority-grant discovery has been performed
all applicable authority bindings/grants evaluate valid
no contradictory applicable authority grant remains unresolved
all authority paths terminate at declared anchors
authority graph is acyclic
anchor/policy/source/agent/procedure revisions are current
scope and grant kind cover the selected value/rule/procedure
self-authorization complies with policy
required provenance/extraction references are present
required attribution profile is satisfied
all dependency obligations are gate-valid
no unresolved semantic conflict remains
no POTENTIALLY_STALE / INVALIDATED dependency remains
all applicable CONSTRAINT grants satisfy their evidence profiles
```

### Structured outcomes

The implementation should expose structured reason codes, including at least categories equivalent to:

```text
E_AUTH_NO_ANCHOR
E_AUTH_CYCLE
E_AUTH_UNRESOLVED
E_AUTH_CONFLICT
E_AUTH_AUTHORITY_CONFLICT
E_AUTH_NO_POLICY
E_AUTH_SCOPE
E_AUTH_VALUE_OUT_OF_SET
E_AUTH_PROCEDURE_REVISION
E_AUTH_SELF_AUTHORIZATION
E_AUTH_REDELEGATION
E_AUTH_PROVENANCE
E_AUTH_ATTRIBUTION
E_AUTH_POTENTIALLY_STALE
E_AUTH_CONSTRAINT
E_AUTH_CLOSURE
```

Exact names are implementation details; structured fail-closed categories are normative.

## Acceptance is immutable; validity is evaluated

An acceptance event is historical and append-only.

`authority_validity` is computed against an exact evaluation context and dependency set. It is not maintained as an unproven mutable flag on the obligation.

When an authority/source/policy/agent/procedure/anchor dependency changes, an existing acceptance becomes:

```text
POTENTIALLY_STALE
```

for the new evaluation context and fails closed for a new build until an explicit event occurs.

Lifecycle events include:

```text
RevalidationEvent
ReacceptanceEvent
InvalidationEvent
RevocationEvent
```

`REVALIDATED` and `REACCEPTED` are event outcomes/actions, not additional `authority_validity` enum values.

A RevalidationClaim identifies old/new dependency revisions, semantic scope, method, producer, supporting evidence status/profile, and result. Natural-language equivalence will often remain human-declared rather than formally proven.

Historical acceptance remains immutable; current validity may differ by evaluation context, supporting rollback, branch/fork variants, and later audit.

## Attribution and evidence interaction

This RFC separates:

```text
authority semantics
        !=
attribution / identity assurance
        !=
evidence strength
```

RFC 0006 is the normative owner of evidence classes and evidence profiles.

For example:

```text
authority_validity = AUTHORIZED
attribution = unauthenticated repository declaration
evidence_status = HUMAN-DECLARED
```

is coherent and does not imply cryptographic authentication.

A deterministic policy evaluation may be `CHECKED`, while the AuthorityAnchor on which it relies remains a declared/trusted input according to its own evidence.

## Relationship to existing RFCs

- RFC 0010 defines the project-level trust-chain thesis.
- RFC 0005 preserves the intent-fidelity limitation but no longer owns a mixed authority/evidence state taxonomy.
- RFC 0006 owns evidence classes, evidence profiles, preservation boundaries, and RFC lifecycle/dependency rules.
- RFC 0009 owns native target realization.

Once #54 is complete, this RFC may be promoted to Accepted because its evidence and lifecycle dependency is then resolved.

## Proposed invariants

1. **A semantic obligation may become executable only when it is resolved, applicable to the selected build, authorized under valid authority bindings, and all dependencies are gate-valid.**
2. **Obligation-hood, authority-relevant classification, selected configuration, and closure exclusion cannot reduce authority requirements without an authorized or deterministic basis.**
3. **Semantic completeness: no authority-relevant semantic obligation may be silently omitted from the executable semantic closure.**
4. **Authority completeness: no applicable authority grant or constraint may be silently omitted from authority evaluation.**
5. **Every authority-binding path terminates at a declared, revision-bound AuthorityAnchor; the graph is acyclic and the enumerated anchor set plus protection mechanism form the Authority TCB.**
6. **Reasonable defaults require an applicable bounded authority policy; convention alone is not authority.**
7. **Delegated authority identifies an accountable authority path, scope, revision, grant kind, authority agent, relevant revisions, and revocation/invalidation behavior.**
8. **An authority agent receives authority from delegation, not capability. Self-authorization is fail-closed by default and allowed only when explicitly granted for bounded scope.**
9. **The Semantic Authority Gate is deterministic and produces no authority.**
10. **Per-obligation authorization is insufficient when authority constraints apply; applicable constraints must be satisfied over the closure under declared evidence profiles.**
11. **Executable semantic closure is build/configuration-specific and conservative, and exclusion bases are gate-visible.**
12. **Unresolved, conflicting, unauthorized, potentially stale, invalidated, revoked, or expired in-closure obligations fail closed before SpecIR synthesis.**
13. **Acceptance is immutable history; current authority validity is computed against explicit dependencies and evaluation context.**
14. **`AUTHORIZED` is a governance state, not an evidence class. Attribution assurance and evidence strength remain separate.**
15. **Candidate-semantics sources and extraction are not trusted authority by default; extraction/provenance transformations are evidence-bearing boundaries.**
16. **Accepted semantics remain traceable to exact authority anchors, policies, source revisions, classification/exclusion bases, grant-discovery results, and acceptance records.**
17. **Authority changes create explicit downstream stale, invalidation, revalidation, re-acceptance, rebuild, or evidence obligations rather than silently preserving acceptance.**

## Minimum viable implementation under #53

The first implementation remains tied to the real POC-1C subject.

Candidate semantic obligations include:

```text
overflow_behavior = forbidden
accepted input domain a,b ∈ [-100,100]
```

The MVI should include:

```text
1 AuthorityAnchor
1 enumerated anchor set + hash
1 explicit anchor declaration/protection description
1 direct human-declared VALUE authorization
1 delegated VALUE_SET selection
1 deterministic authority evaluator / gate
1 explicitly enumerated ClosureRecord with inclusion + exclusion sets
1 complete applicable-grant discovery pass
1 simple CONSTRAINT over the closure
content-hash binding into accepted-spec/evidence artifacts
```

Minimum negative cases include:

```text
no anchor
authority cycle
no policy / no authority
value outside grant
stale policy or anchor
UNRESOLVED obligation
semantic CONFLICT in closure
scope mismatch
missing provenance
self-authorization not permitted
redelegation not permitted
classification widening without basis
obligation excluded from closure without basis
selected configuration without authority basis
contradicting applicable grant from a second authority source
POTENTIALLY_STALE dependency
closure constraint violation
```

## Deferred from the first implementation

- cryptographic signatures / strong identity binding;
- quorum / dual approval;
- redelegation/depth greater than the MVI;
- jurisdiction/customer/product-variant precedence;
- cross-anchor precedence resolution beyond fail-closed conflict;
- external standards ingestion and edition tracking;
- rich SDD / AI extraction adapters;
- runtime/post-deployment revocation enforcement;
- enterprise authority-policy lifecycle management;
- full precedence lattice;
- multi-configuration executable-closure computation;
- general semantic-equivalence proof for natural-language revisions.

## Non-goals

This RFC does not:

- prohibit reasonable defaults;
- require human approval for every semantic obligation;
- equate low impact with automatic authority;
- equate AI capability with authority;
- equate authority validity with evidence strength;
- require one specification frontend, impact taxonomy, or signature technology;
- move unresolved authority state into executable SpecIR;
- replace requirements-management, governance, certification, or assurance-case systems;
- claim certification or regulatory qualification;
- claim authority can be proved without declared trust anchors.

## Implementation sequence

```text
RFC 0011 closure review                       COMPLETE
        ↓
closure-review residual amendments            COMPLETE
        ↓
#54 evidence / lifecycle reconciliation       REQUIRED BEFORE ACCEPTANCE
        ↓
RFC 0011 acceptance decision
        ↓
Authority + evidence record shape
        ↓
Authority-record schema
        ↓
Minimal accepted-spec authority binding
        ↓
Deterministic authority evaluation + fail-closed gate
        ↓
Negative authority regression tests
        ↓
Revision / POTENTIALLY_STALE tests
        ↓
Delegated-default tests
        ↓
Closure-constraint tests
        ↓
Bind acceptance into downstream evidence
        ↓
CI / #53 closure
```
