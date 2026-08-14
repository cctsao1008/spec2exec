# RFC 0011 — Semantic Authority, Delegation, and Default Policy

- **Status:** Draft / Proposed — revision 2 after hostile architecture review
- **Issue:** #53
- **Dependency:** #54 must reconcile evidence vocabulary and RFC lifecycle before this RFC is promoted to Accepted
- **Scope:** semantic obligations, authority trust anchors, delegated defaults, authority validity, applicability, provenance, attribution, revision/invalidation, and fail-closed acceptance before SpecIR synthesis

## Summary

Spec2Exec does not require every implementation choice or every missing detail to be manually approved. It requires every **semantic obligation in the executable semantic closure of a selected build** to have an explicit, revision-bound authority basis.

A **semantic obligation** is an authority-relevant decision or constraint whose alternatives can change the accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build. Semantics-preserving implementation choices such as register allocation or equivalent instruction selection are not authority obligations merely because they change the exact binary.

A reasonable default may be used without an immediate human clarification step **only when an applicable authority policy already grants authority for that decision under a bounded scope**. The fact that a default is common, low-impact, plausible, recommended by an AI system, or described as an industry practice does not itself create authority.

The central rule remains:

> **Capability, plausibility, convention, and low impact do not create semantic authority. Authority originates at declared trust anchors and may be delegated through scoped, revisioned, bounded, and revocable policies.**

The authority chain itself is not infinitely provable. Spec2Exec must explicitly declare where authority derivation stops and trust begins. The declared anchor set is therefore the **Authority TCB**.

This RFC refines RFC 0010 and is intended, once accepted, to supersede the mixed authority-state model in Draft RFC 0005. Evidence-strength vocabulary remains owned by RFC 0006 / issue #54 rather than by this RFC.

## Motivation

Specification-oriented development systems must balance two legitimate goals:

1. expose consequential ambiguity before implementation;
2. avoid blocking productive work on every ordinary missing detail.

A productivity-oriented system may therefore fill gaps using reasonable defaults and record assumptions. Spec2Exec should be able to consume such artifacts without treating every assumption as either automatically trusted or automatically forbidden.

The missing distinction is not whether a value looks reasonable. The missing distinction is whether the value has an **authority basis** for the selected build and semantic scope.

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

Likewise, three individually authorized choices can still compose into forbidden behavior. For example:

```text
retries = 3                  AUTHORIZED
backoff = exponential        AUTHORIZED
retry POST = true            AUTHORIZED

composition:
payment POST + retry
        ↓
possible duplicate charge
```

The authority model must therefore cover both **per-obligation authorization** and **constraints over the executable semantic closure**.

## Architecture boundary

Unresolved or invalid authority state remains before executable SpecIR.

Preferred boundary:

```text
Source Artifacts / Candidate Frontends
        ↓
Extraction / Interpretation
        ↓
Candidate Semantic Obligations
        │
        ├── resolution state
        ├── provenance
        ├── applicability
        ├── authority-relevant classifications
        ├── conflict sets
        ├── dependencies
        └── authority bindings / exercises
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

`UNRESOLVED`, `CONFLICT`, unauthorized, revoked, expired, invalidated, or potentially stale obligations in the executable semantic closure must fail closed before SpecIR synthesis.

This RFC does **not** move those states into executable SpecIR by default.

## Candidate-semantics sources and extraction

Spec2Exec should not compete with tools whose primary purpose is requirement elicitation, specification authoring, planning, or AI coding workflow.

Candidate semantics may originate from:

```text
natural-language requirements
PRDs
requirements-management systems
standards documents
contracts / interface specifications
Spec-Driven Development tools
AI coding-agent workflows
search / retrieval systems
domain-specific frontends
```

A source may contribute:

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

### Extraction is a trust boundary

A source artifact and the semantics extracted from that source are not the same artifact.

The normative conceptual boundary is:

```text
Source Artifact
    hash / revision
        ↓
Extraction / Interpretation
    method / tool / version / transformation
        ↓
Candidate Semantic Obligation
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

Where practical, `source_locator` should be machine-checkable, for example a stable clause identifier, byte/span locator, or another reversible reference into the exact source artifact.

A provenance record stating `clause 4.2` does not by itself establish that clause 4.2 supports the extracted semantic value. The extraction/support claim must carry evidence under the canonical evidence model defined by RFC 0006 / #54.

Lossy normalization, merging, or rewriting must remain traceable to the contributing source spans rather than silently becoming authoritative provenance.

## Semantic obligation

A **semantic obligation** is the authority-gated unit of this RFC.

Working definition:

> A semantic obligation is an authority-relevant decision or constraint whose alternatives can change the accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build.

Examples that are normally semantic obligations:

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

Examples that are normally not semantic obligations when they preserve accepted semantics:

```text
register allocation choice
temporary-register selection
semantics-preserving instruction scheduling
assembler formatting
non-semantic symbol naming
```

A backend transformation may still require preservation evidence, but that is an evidence/realization question rather than a semantic-authority question.

## Typed state model

This RFC does not use one overloaded state field for uncertainty, authority, acceptance, impact, and evidence.

### Resolution state

`resolution_state` answers:

> Is the semantic obligation determinate enough to evaluate for authority and acceptance?

Candidate states are:

```text
RESOLVED
UNRESOLVED
CONFLICT
```

`RESOLVED` means a concrete semantic value, rule, constraint, or derivation is available. It does **not** mean the value is authoritative, accepted, applicable, correct, or verified.

Proposal origin is recorded separately rather than using a `PROPOSED` resolution state.

A derived obligation should identify its derivation procedure and parent obligations rather than being collapsed into a special evidence state.

### Authority validity

`authority_validity` answers:

> Is the obligation currently covered by a valid authority basis for the relevant scope?

Candidate states include:

```text
AUTHORIZED
UNAUTHORIZED
POTENTIALLY_STALE
INVALIDATED
REVOKED
EXPIRED
```

`AUTHORIZED` is a governance/authority state. It is **not an evidence-strength class**.

### Acceptance state

Acceptance is separate from authority validity.

A semantic obligation may be authorized but not yet incorporated into an accepted specification. A historically accepted obligation may later have an authority basis that becomes invalid.

The architecture therefore distinguishes:

```text
NOT_ACCEPTED
ACCEPTED
```

An `AcceptanceRecord` is an immutable historical event. Current validity is evaluated separately.

### Applicability

`applicability` answers whether the semantic obligation belongs to the selected build, target, and configuration.

Candidate states may include:

```text
APPLICABLE
NOT_APPLICABLE
UNKNOWN
```

`UNKNOWN` does not silently exclude an obligation. For fail-closed closure computation, anything not demonstrably outside the executable semantic closure is treated as inside it.

### Attribution assurance

Authority semantics and identity/attribution assurance are separate.

A record may be `AUTHORIZED` while its attribution remains unauthenticated, provided that limitation is explicit and permitted by the applicable policy.

This RFC does not freeze one universal attribution enum. An implementation must represent:

```text
attribution mechanism
producer / claimed identity
assurance level or policy-specific assurance descriptor
supporting evidence
```

The first POC may honestly represent current acceptance as unauthenticated human-declared / VCS-attributed presence. Cryptographic signatures are future work.

### Authority-relevant classifications

Impact, decision class, semantic scope, and applicability can affect which authority policy applies. Therefore they cannot be treated as unrestricted metadata when they widen authority.

Important invariant:

> **Any classification that can widen authority-policy applicability is itself authority-relevant and must have an authorized basis or a deterministic derivation from already authorized data.**

Examples include:

```text
decision_class
impact_class
semantic_scope
applicability category
```

A classification supplied by an untrusted source may conservatively narrow or deny delegation. It must not silently widen delegation.

For example, an untrusted agent may safely classify a decision as `HIGH` when that classification forces stronger authority, but it must not obtain a weaker policy merely by reclassifying a security-sensitive decision as `LOW` or `presentation-only`.

A project may represent authority-relevant classifications as separate `ClassificationRecord` / semantic obligations, or may derive them using an anchor/policy-defined deterministic classifier. In either case, the basis must be recorded and gate-visible.

Impact remains useful as a policy input, but:

```text
LOW impact != automatically authorized
HIGH impact != necessarily human-only
```

## Authority Trust Anchors and Authority TCB

Authority cannot be derived forever. At some boundary a project must declare what it trusts as authoritative.

An **AuthorityAnchor** is a revision-bound trust root whose authority is asserted at the project/governance boundary rather than derived from another Spec2Exec authority source.

Examples may include:

- an explicitly authorized project owner / engineering governance role;
- an approved governing contract or authority record;
- an applicable regulatory or standards authority selected by project governance;
- an approved parent specification designated as a trust root for this build;
- another externally governed root explicitly imported as authoritative.

The existence of a document is not sufficient. The project must explicitly designate the anchor and bind the exact revision or identity represented.

### Authority TCB

The set of declared anchors is the **Authority Trusted Computing Base (Authority TCB)**.

The architecture requires:

1. every authority-binding path terminates at a declared AuthorityAnchor;
2. the authority/delegation graph is acyclic;
3. the anchor set is enumerable and revision-bound;
4. the anchor-set identity/hash is bound into the Accepted Specification or its acceptance record;
5. changing the anchor set creates a validity/re-acceptance obligation.

A project may have multiple anchors. A single semantic obligation may require multiple authority bindings rooted at different anchors, for example a contract plus a safety-governance constraint.

Each **authority path** must terminate at a declared anchor. The architecture does not require the whole project to have exactly one anchor.

The evidence status attached to an anchor assertion belongs to the canonical evidence vocabulary under RFC 0006 / #54. This RFC does not invent a parallel evidence class for anchors.

## Authority source, policy, delegation, and agent

### Authority source

An authority source is an accountable node whose authority is either:

- a declared AuthorityAnchor; or
- derived through a valid, acyclic authority/delegation path that terminates at an anchor.

Possible non-root authority sources include accepted parent specifications, contracts, governance artifacts, policies, or delegated roles.

### Authority policy

An **AuthorityPolicy** defines what authority is granted, to whom, under what scope, and under which constraints.

A policy should identify at least:

```text
policy_id / content hash
source authority or anchor path
source revision
scope / applicability
covered semantic-obligation or decision classes
grant kind
grant bounds
allowed authority agent / agent class
agent version/revision when relevant
self-authorization rule
redelegation rule
constraints
validity interval when applicable
revocation / supersession relation
attribution requirement
```

Unbounded phrases such as:

```text
use industry-standard defaults
use secure defaults
use common web practices
```

are not sufficient by themselves. They must be reduced to a pinned source, bounded value set/range, pinned procedure, explicit constraints, or an explicitly delegated discretionary judgement scope.

### Grant kinds

The architecture distinguishes what is actually delegated:

```text
VALUE
VALUE_SET
CONSTRAINT
PROCEDURE
SOURCE
DISCRETION
```

#### VALUE

Authorizes one exact semantic value or rule.

```text
motor_cutoff = 90°C
```

#### VALUE_SET

Authorizes selection within an enumerated or mechanically bounded set/range.

```text
pagination_size ∈ {20, 50, 100}
```

The value-set definition and constraints are part of the policy revision.

#### CONSTRAINT

Authorizes or asserts an invariant over applicable obligations or their composition.

```text
all retryable external operations must be idempotent
```

Constraints are evaluated over the executable semantic closure rather than only per obligation.

#### PROCEDURE

Authorizes a deterministic decision procedure.

A procedure grant must bind at least:

```text
procedure/tool identity
version/revision
bound inputs or input-source references
constraints
fail-closed fallback
```

A changed procedure/tool version is a validity dependency.

#### SOURCE

Delegates to a specific external source and pinned revision or version-selection rule.

A floating phrase such as `current industry standard` is not sufficient unless the governing policy explicitly authorizes a revision-selection procedure and that procedure is itself bound.

#### DISCRETION

Delegates bounded judgement to an authority agent.

The allowed scope, constraints, attribution requirements, and self-authorization rule must be explicit. `DISCRETION` is not a wildcard grant over arbitrary semantics.

### Authority agent

An **authority agent** is a mechanism permitted to exercise delegated authority under a valid policy.

It may be:

```text
a human role
a deterministic policy engine
a rules engine
a workflow service
an AI system
a future automated system
```

The important distinction remains:

> **An agent receives authority from a valid authority path and policy, not from capability, accuracy, plausibility, or intelligence.**

Agent identity/revision matters when the policy depends on the behavior of that specific agent or procedure.

### Redelegation

Redelegation is fail-closed by default.

A policy must explicitly state whether redelegation is permitted. The first implementation under #53 should use:

```text
redelegation_allowed = false
maximum delegation depth = 1 beyond the anchor/policy relationship
```

More complex delegation chains are deferred. Even when later enabled, the graph must remain acyclic and every path must terminate at a declared anchor.

## Self-authorization and separation of duties

The architecture records `proposer` and `authority_agent` separately.

Default rule:

> **If the same agent originated a candidate and also exercises authority over it, the gate fails closed unless the applicable policy explicitly permits self-authorization for that grant kind and scope.**

This is policy-controlled rather than an absolute prohibition.

For bounded `VALUE_SET` selection or a version-pinned deterministic `PROCEDURE`, the admissible semantics are already bounded by the authority source; permitting the same automation to propose/select the value need not create additional discretion.

For `DISCRETION`, self-authorization is more consequential. If permitted, the policy must explicitly grant it and the resulting acceptance/evidence must expose that proposer and authorizer were the same agent.

No AI system gains self-authorization merely by being accurate or capable.

## Delegated defaults

Spec2Exec does **not** adopt:

```text
LOW impact → AI may choose a default
MEDIUM impact → record assumption
HIGH impact → authority required
```

Instead:

```text
Missing Semantic Obligation
        ↓
Is it in the executable semantic closure?
        │
       YES
        ↓
Is there an applicable valid authority policy?
        │
   ┌────┴────┐
   │         │
  YES        NO
   │         │
   ↓         ↓
Authority exercise /    UNRESOLVED or
policy-authorized       UNAUTHORIZED
selection               ↓
   │                    BLOCK
   ↓
Authority Evaluation
   ↓
Deterministic Gate
```

Workflow ergonomics therefore come from **pre-authorized delegation**, not silent authority creation.

## Conflicts and precedence

`CONFLICT` must preserve the conflicting alternatives and their provenance.

A logical `ConflictSet` should support at least:

```text
conflict_id
semantic obligation / subject
candidate alternatives[]
    value / rule
    source artifact
    source revision
    source locator
    extraction/provenance reference
resolution status
precedence basis when resolved
```

The first #53 implementation may reject every in-closure conflict.

Future automated conflict resolution may use an explicitly authorized precedence relation, jurisdiction rule, or policy. The precedence rule itself must have an authority basis; an untrusted resolver must not invent precedence.

Full jurisdiction and precedence lattices are deferred.

## Executable semantic closure

Authority gating is scoped to a **selected build, target, and configuration**.

It does not globally block on every unresolved statement stored anywhere in a project.

```text
Selected Build Configuration
        ↓
Executable Semantic Closure
        ↓
Authority / Constraint Evaluation
        ↓
Semantic Authority Gate
```

The **executable semantic closure** is the transitive set of semantic obligations and authority constraints that can affect the accepted observable behavior, contract, configuration meaning, or verification obligations of the selected build.

It includes relevant dependencies and applicable constraints.

### Conservative closure rule

Closure computation is itself a trust/evidence boundary.

Normative rule:

> **Anything not demonstrably outside the executable semantic closure is conservatively treated as inside it.**

An under-approximated closure is an authority bypass, because it can exclude unauthorized semantics from gating while still producing an `ACCEPTED` result.

The closure computation therefore needs an explicit method/version and a configuration binding in the acceptance/evidence record.

For the first #53 implementation, multi-configuration closure analysis is not required. The MVI may use one explicitly enumerated POC-1C closure for the selected subject.

## Composition constraints

Per-obligation authorization is necessary but not sufficient.

An AuthorityAnchor or AuthorityPolicy may assert a `CONSTRAINT` grant over the executable semantic closure.

Examples:

```text
all retryable external operations must be idempotent
all actuator limits must remain within approved envelope E
all selected input domains must remain inside verified arithmetic bounds
```

The gate must require:

```text
all applicable semantic obligations have valid authority
AND
all applicable authority constraints over the closure are satisfied
```

Constraint satisfaction is a deterministic claim and must carry evidence through the canonical evidence model. The constraint itself is authoritative because of its authority binding; the fact that the selected closure satisfies it is established by a checking method.

These two facts must not be collapsed.

## Logical record graph

The architecture should prefer a normalized, content-addressed graph over one monolithic mutable record.

Logical record types should include at least:

```text
AuthorityAnchor
AuthorityPolicy
DelegationRecord / AuthorityExercise
SourceArtifact
ExtractionRecord
SemanticObligation
ClassificationRecord
ConflictSet
AuthorityEvaluation
AcceptanceRecord
InvalidationEvent
RevalidationClaim / EquivalenceClaim
```

### SemanticObligation logical fields

A semantic obligation should support at least:

```text
schema_version
namespace / decision_id
subject / semantic_scope
value / rule / alternatives
resolution_state
applicability
decision-class reference
impact-class reference or classification basis
origin / proposer
provenance / extraction references
derivation_method when derived
derived_from[] / dependencies[]
conflict_set reference when applicable
authority_bindings[]
binding_combination
supersedes / superseded_by when applicable
```

`impact_class`, `decision_class`, `semantic_scope`, and applicability must not be free fields if they can widen delegation; they require an authorized or deterministic classification basis.

### Multiple authority bindings

A semantic obligation may require multiple bindings.

The logical model should support:

```text
authority_bindings: [...]
binding_combination:
    all_of
    any_of
    future quorum(k,n)
```

The first implementation may support only `all_of` and one simple `any_of` or even only `all_of`, provided the schema does not hard-code cardinality one.

### Content-addressed references

Authority anchors, policies, source artifacts, extraction records, and accepted specifications should be referenced by stable revision and/or content hash.

This permits a changed dependency to produce a visible validity transition rather than requiring silent in-place mutation of downstream records.

## Authority exercise, evaluation, and gate

The authority gate must not create authority.

The conceptual split is:

```text
Authority Anchor / Policy / Delegation
        ↓
Authority Agent Exercise
        ↓
Authority Evaluation
        ↓
Deterministic Semantic Authority Gate
        ↓
Acceptance Record or structured rejection
```

An `AuthorityExercise` records the action or delegated judgement performed by an authority agent.

An `AuthorityEvaluation` computes whether the recorded exercise is valid under the exact anchor/policy/revision/scope/grant/attribution constraints.

### Gate invariant

> **The Semantic Authority Gate is deterministic and produces no authority. It checks recorded authority/evaluation facts and emits acceptance or explicit reason codes.**

The gate must not mutate an unauthoritative decision into an authoritative one merely because a matching policy was discovered.

### Minimum gate conditions

For every semantic obligation in the executable semantic closure, the gate should require at least:

```text
resolution_state == RESOLVED
applicability == APPLICABLE or conservatively included
all authority-relevant classifications have valid bases
all required authority bindings evaluate valid
all authority paths terminate at declared anchors
authority graph is acyclic
anchor/policy/source/agent/procedure revisions are current
scope and grant kind cover the selected value/rule/procedure
self-authorization complies with policy
required provenance/extraction references are present
required attribution assurance is satisfied
all dependency obligations are gate-valid
no unresolved conflict remains
no POTENTIALLY_STALE / INVALIDATED dependency remains
all applicable CONSTRAINT grants are satisfied over the closure
```

### Structured outcomes

The implementation should not reduce failure to a generic false result.

A future acceptance result should be able to produce structured reason codes such as:

```text
E_AUTH_NO_ANCHOR
E_AUTH_CYCLE
E_AUTH_UNRESOLVED
E_AUTH_CONFLICT
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

Exact code names are implementation details under #53, but structured fail-closed categories are normative in spirit.

## Acceptance is immutable; validity is evaluated

An acceptance event is historical and append-only.

If semantic obligation D was accepted into specification revision S at time T, the project does not rewrite history to say that acceptance never occurred when a policy later changes.

Instead it evaluates whether the historical acceptance is still valid under the current authority dependencies.

### Revision change

Dependency change defaults to a conservative state:

```text
VALID
  ↓ authority/source/policy/agent/procedure/anchor dependency changed
POTENTIALLY_STALE
  ├── REVALIDATED
  ├── REACCEPTED
  └── INVALIDATED
```

`POTENTIALLY_STALE` fails closed for a new build.

### Revalidation

Revalidation requires an explicit `RevalidationClaim` / `EquivalenceClaim` identifying:

```text
old dependency revision
new dependency revision
semantic scope
method
producer
supporting evidence status
result
```

Natural-language revision equivalence will frequently be human-declared rather than formally proven. The evidence status must honestly represent the method and must use the canonical vocabulary owned by RFC 0006 / #54.

A mechanically checkable no-op or hash-preserving transformation may support stronger evidence, but the architecture does not assume equivalence is generally provable.

### Invalidation as evidence-bearing event

Invalidation, revalidation, revocation, and re-acceptance should be represented as explicit events/records rather than mutable flags with no provenance.

This supports shipped artifacts, rollback, branch/fork variants, and later audit: the historical acceptance stays immutable while current validity can differ by evaluation context.

## Attribution and authentication

This RFC separates:

```text
authority semantics
        !=
attribution / identity assurance
        !=
evidence strength
```

An authority policy may require an attribution mechanism or minimum assurance descriptor for an authority exercise.

For example, a POC may allow unauthenticated repository-declared authority, while a future production policy may require workflow-backed or cryptographically attributable approval.

The current POC must not claim authenticated approval merely because `authority_role` is non-empty or because a Git commit contains an author field.

No particular signature or identity system is required by this RFC.

## Governance artifacts and constitutions

Project constitutions, engineering principles, contracts, and governance documents can be genuine authority sources when explicitly designated and revision-bound.

The distinction is:

```text
Governance artifact may be an authority source
        !=
Complete semantic-authority / provenance model
```

A governance artifact often expresses `CONSTRAINT` grants rather than exact `VALUE` grants.

For example:

```text
All external operations MUST be idempotent.
```

is naturally a constraint over the executable semantic closure.

By contrast:

```text
motor cutoff threshold = 90°C
```

is an exact semantic value.

The same authority architecture can represent both, but the grant kind must remain explicit so broad governance principles are not accidentally interpreted as authority to choose arbitrary values.

## Assumptions from external frontends

A frontend may emit:

```text
Assumption:
    OAuth2 is used.
```

An adapter might create:

```text
semantic_obligation_id: AUTH-001
subject: authentication_method
value: OAuth2
resolution_state: RESOLVED
origin:
  proposer: frontend-X
provenance:
  source_kind: frontend-assumption
  source_artifact: ...
  source_hash: ...
  source_locator: ...
authority_validity: UNAUTHORIZED
```

The adapter does not transition it to `AUTHORIZED`.

If a valid authority policy and exercise cover the obligation, a deterministic authority evaluation can establish that the exercise is permitted. The gate then checks that evaluation and may emit an accepted specification record.

If no authority exists, the obligation remains blocked even though the proposal is plausible.

## Relationship to workflow ergonomics

Spec2Exec should not require thirty interactive questions merely because thirty candidate details are missing.

Workflow ergonomics should come from **delegated policy**, not silent authority creation.

A well-designed policy can authorize large classes of ordinary decisions in advance while preserving strict handling for decisions that require stronger authority.

This obtains the productivity benefit of reasonable defaults without weakening the authority invariant.

## Relationship to SDD and AI coding workflows

Spec2Exec treats specification-development and AI coding systems as potential upstream contributors rather than competitors that must be reimplemented.

A useful distinction is:

```text
Specification-development workflow asks:
    Is the specification clear enough to build?

Spec2Exec additionally asks:
    Which semantic obligations are in this build's executable closure?
    Does each carry a valid authority basis?
    Are closure-level authority constraints satisfied?
    What evidence binds those accepted semantics to this exact artifact?
```

This is a boundary distinction, not a claim that upstream specification systems are weak or undisciplined.

## Evidence interaction

This RFC owns semantic-authority concepts. It does **not** own the canonical evidence-strength vocabulary.

Examples:

```text
resolution_state = RESOLVED          authority semantic state
authority_validity = AUTHORIZED      governance state
acceptance_state = ACCEPTED          acceptance state
```

These are not equivalent to:

```text
CHECKED
TESTED
PROVEN
TRUSTED
HUMAN-DECLARED
ASSUMED
```

which are evidence/claim-strength classifications governed by RFC 0006 / #54.

An authority evaluator may produce a deterministic `CHECKED` claim that a policy covers a scope. That evidence does not make the underlying authority anchor `PROVEN`. Likewise, an anchor may be project-declared while the evaluation of its exact hash/revision binding is mechanically `CHECKED`.

The architecture must preserve these layers rather than collapse them into `AUTHORIZED = verified`.

### Typed namespaces

If the same lexical token appears in multiple models, the owning field/type must be explicit.

For example, A0 currently uses:

```text
resolution_state = UNRESOLVED
```

RFC 0006 historically also uses `UNRESOLVED` in an evidence vocabulary. #54 must decide the canonical evidence vocabulary and lifecycle semantics. RFC 0011 does not force A0 to rename its semantic-resolution states solely because a different typed namespace used the same word.

## Relationship to existing RFCs

### RFC 0010

RFC 0011 refines RFC 0010's project-level semantic-authority invariant:

> No unresolved or unauthorized semantic assumption may silently cross the authority boundary and become executable behavior.

RFC 0011 makes the authority roots, delegation, applicability, and fail-closed gate more explicit.

### RFC 0005

Draft RFC 0005 currently contains a mixed state model that combines knowledge, assumptions, derivation, acceptance, and verification on one axis.

Once RFC 0011 is accepted, its typed semantic-authority model is intended to supersede that mixed authority-state taxonomy. #54 is responsible for reconciling lifecycle/dependency wording and the remaining realization conflicts in RFC 0005.

### RFC 0006

RFC 0006 / #54 remains the normative owner of evidence classes and extension rules.

RFC 0011 must not independently introduce evidence classes for trust anchors, attribution, or policy evaluation.

### RFC 0009

RFC 0009 remains the normative native target-realization architecture. Semantic-authority state is resolved before SpecIR; target backends preserve accepted semantics and carry their own evidence boundaries.

## Proposed invariants

If accepted, RFC 0011 should refine the project-level invariants with the following:

1. **A semantic obligation may become executable only when it is resolved, applicable to the selected build, and authorized under valid authority bindings, and all semantic obligations it depends on are likewise gate-valid.**
2. **Authority-relevant classification cannot widen delegation without an authorized or deterministic basis. Untrusted classification may conservatively narrow authority but not expand it.**
3. **Every authority-binding path terminates at a declared, revision-bound AuthorityAnchor. The authority graph is acyclic, and the anchor set is an enumerable Authority TCB bound to acceptance.**
4. **Reasonable defaults require an applicable bounded authority policy; convention alone is not authority.**
5. **Delegated authority identifies an accountable authority path, scope, revision, grant kind, authority agent, relevant agent/procedure/source revision, and revocation/invalidation behavior.**
6. **An authority agent receives authority from delegation, not capability. Self-authorization is fail-closed by default and is permitted only when the applicable policy explicitly grants it for the relevant bounded scope.**
7. **The Semantic Authority Gate is deterministic and produces no authority. It checks recorded authority facts and emits structured acceptance or rejection.**
8. **Per-obligation authorization is not sufficient when anchor/policy constraints apply. Applicable authority constraints must be satisfied over the executable semantic closure.**
9. **Executable semantic closure is build/configuration-specific and conservative: anything not demonstrably outside the closure is treated as inside it.**
10. **Unresolved, conflicting, unauthorized, potentially stale, invalidated, revoked, or expired semantic obligations inside the executable closure fail closed before SpecIR synthesis.**
11. **Acceptance is an immutable event; current validity is evaluated separately against explicit authority dependencies and anchor-set revision.**
12. **`AUTHORIZED` is a governance state, not an evidence class. Attribution assurance and evidence strength remain separately represented.**
13. **Candidate-semantics sources and extraction are not trusted authority by default; extraction/provenance transformations are evidence-bearing boundaries.**
14. **Accepted semantics remain traceable to the exact authority anchors, policies, source revisions, classification bases, and acceptance records on which they depend.**
15. **Authority changes create explicit downstream stale, invalidation, revalidation, re-acceptance, rebuild, or evidence obligations rather than silently preserving acceptance.**

## Minimum viable implementation under #53

The first implementation should test the architecture without becoming an enterprise requirements-management system.

It should remain tied to the real POC-1C subject where possible.

Candidate authority subjects include existing behavior-determining clauses such as:

```text
overflow_behavior = forbidden
accepted input domain a,b ∈ [-100,100]
```

A minimum implementation may include:

```text
1 AuthorityAnchor
1 anchor-set revision/hash
1 AuthorityPolicy
1 direct human-declared VALUE authorization
1 delegated VALUE_SET default/selection
1 deterministic authority evaluator
1 deterministic gate
1 explicitly enumerated executable semantic closure
1 simple CONSTRAINT over the closure
```

Minimum positive cases:

1. direct human-declared authorization accepted under the declared anchor;
2. delegated default/selection accepted inside an authorized bounded value set;
3. applicable closure constraint satisfied.

Minimum negative cases should include at least:

```text
no policy / no authority
value outside grant
stale policy or anchor
UNRESOLVED obligation
CONFLICT in closure
scope mismatch
missing required provenance
self-authorization not permitted by policy
redelegation not permitted
cyclic authority path
classification attempts to widen authority without basis
POTENTIALLY_STALE dependency
closure constraint violation
```

The exact test count and file layout are implementation decisions, but these failure modes should be mechanically exercised before #53 closes.

## Deferred from the first implementation

The first implementation explicitly defers:

- cryptographic signatures / strong identity binding;
- quorum / dual approval;
- redelegation and delegation depth greater than the minimal supported model;
- jurisdiction, customer, product-variant, and deployment-specific precedence;
- external standards ingestion and edition-tracking automation;
- rich SDD / AI extraction adapters;
- runtime/post-deployment revocation enforcement;
- enterprise authority-policy lifecycle management;
- full conflict-precedence lattice;
- multi-configuration executable-closure computation;
- general semantic-equivalence proof for natural-language source revisions.

These are reserved by the logical model where practical but are not required to validate the first authority gate.

## Non-goals

This RFC does not:

- prohibit reasonable defaults;
- require human approval for every semantic obligation;
- equate low impact with automatic authority;
- equate AI capability with authority;
- equate authority validity with evidence strength;
- require one specification frontend;
- require one impact taxonomy;
- require one authentication or signature technology;
- move unresolved authority state into executable SpecIR;
- replace requirements-management, SDD, governance, certification, or assurance-case systems;
- claim certification or regulatory qualification;
- claim that authority can be proved without declared trust anchors.

## Implementation sequence

Issue #53 should proceed only after this RFC receives closure review and #54 establishes compatible evidence/lifecycle semantics.

```text
RFC 0011 v2 closure review
        ↓
#54 evidence / lifecycle reconciliation
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

The first executable implementation should stay deliberately small. It should prove the authority boundary, trust-anchor termination, conservative closure, bounded delegation, and fail-closed behavior before adding broad frontend integration or sophisticated authentication.
