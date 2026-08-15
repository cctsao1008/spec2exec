# Payment Retry — Lifecycle Trust Experiment (#62)

This directory is the first bounded executable/validation experiment for
**RFC 0012 — Accepted / Lifecycle Trust Baseline**.

It extends the existing payment-retry semantic-authority example without
changing the earlier `unsafe-candidate.json` / `accepted-candidate.json`
workflow POC.

## Research question

Can Spec2Exec distinguish:

```text
historical evidence / historical acceptance
        !=
current property-scoped trust validity
```

when an external dependency changes while the bound client artifact remains
byte-identical?

The bounded property is:

```text
PAYMENT-RETRY-SAFETY
```

The experiment deliberately distinguishes:

```text
client semantic obligation
    idempotency_requirement = true

provider/environment assumption
    the bound payment API preserves idempotency for the selected
    endpoint, operation, key scope, and contract revision
```

The second proposition is not silently converted into accepted client
semantics.

## Three checked fixtures

### 1. `baseline-v7.json`

```text
Payment API contract v7
        ↓
API-IDEMPOTENCY-01 basis is current
        ↓
policy-adequate dependency completeness
        ↓
CurrentTrustProjection = CURRENT
```

### 2. `contract-v8-stale.json`

Only the external contract/context changes:

```text
Payment API v7 → v8

client artifact SHA-256:
95018cb2c86bb1bea9cffb89e12ee31c711a26de159a1dcdacee21ce8b2b4c72
        remains unchanged
```

The old provider-assumption basis is no longer current:

```text
API-IDEMPOTENCY-01
    → AssumptionLifecycle.BASIS_STALE

PAYMENT-RETRY-SAFETY
    → ImpactDisposition.REVALIDATION_REQUIRED

CurrentTrustProjection
    → BLOCKED
```

Historical evidence remains historical evidence. Byte identity does not keep
the property CURRENT.

### 3. `contract-v8-revalidated.json`

A bounded revalidation claim supplies a policy-accepted RFC 0006 evidence
record for the v8 context:

```text
LifecycleRevalidationClaim
    CHECKED / contract-equivalence-check
        ↓
API-IDEMPOTENCY-01 basis current for v8
        ↓
fresh CurrentTrustProjection
        ↓
CURRENT
```

The lifecycle record does not manufacture semantic authority and does not
upgrade unrelated evidence classes.

## Bounded logical records

The fixture uses only the RFC 0012 records needed for this experiment:

```text
TrustClaim
EvaluationContext
AssumptionRecord
DependencyEdge
DependencyCompletenessClaim
DefeaterRecord
InvalidationEvent
ImpactEvaluation / input impact assertion
ProjectionPolicy
LifecycleRevalidationClaim
RecordSupersession
CurrentTrustProjection
```

`ReAssuranceRecord` is not materialized as a separate input record in this
first slice because the final projection can be reconstructed directly from
the narrow revalidation plus unchanged/reusable evidence.

The exact POC contracts are documented by:

```text
spec/schemas/lifecycle-trust-input-v0.1.schema.json
spec/schemas/lifecycle-trust-result-v0.1.schema.json
prototypes/lifecycle_trust/evaluate.py::validate_document
```

These schemas are experiment contracts. They are **not** a claim that RFC 0012
has frozen a universal storage schema.

## Authority boundary

`authority_records` are treated as **imported RFC 0011 results**.

The lifecycle evaluator checks that a referenced record is already:

```text
AuthorityValidity.AUTHORIZED
```

and that it uses an RFC 0011 grant kind and contains the bounded scopes needed
by this experiment.

The evaluator does **not** derive authority from:

```text
plausibility
record presence
ProjectionPolicy
LifecycleRevalidationClaim
ReAssurance
CODEOWNERS
```

The Trust Graph therefore remains a consumer of semantic authority, not a
parallel authority system.

## Evidence boundary

RFC 0006 status labels remain exact typed labels.

The experiment uses exact `(status, method)` profiles. It does not define a
ranking such as:

```text
HUMAN-DECLARED < CHECKED < TESTED < PROVEN
```

and it never upgrades one class into another because a lifecycle blocker was
resolved.

## Dependency completeness

The v1 ProjectionPolicy requires coverage of:

```text
ASSUMES
SEMANTIC_DEPENDS_ON
EVIDENCE_DEPENDS_ON
TCB_DEPENDS_ON
```

and the source-record classes:

```text
AssumptionRecord
AcceptedSemantics
EvidenceRecord
TCBRecord
```

The POC also carries explicit `established_material_relations`.

This lets the evaluator reject:

```text
known material relation
        ↓
edge silently omitted
```

and:

```text
known material ASSUMES dependency
        ↓
ProjectionPolicy simply declines to require ASSUMES
```

without claiming that the POC can discover every real-world payment
dependency.

## ProjectionPolicy semantics

For this experiment:

```text
no applicable policy
    → BLOCKED

multiple applicable policies with no deterministic precedence
    → BLOCKED

missing/invalid imported RFC 0011 adoption authority
    → BLOCKED

policy revision with undeclared lineage
    → BLOCKED

permissive applicability/coverage/precedence change without bounded
RFC 0011 authority + rationale
    → BLOCKED

cached projection bound to a non-governing policy revision
    → BLOCKED
```

The precedence number is only the bounded POC representation of RFC 0012's
deterministic policy-selection relation. It is not a trust score.

## Negative controls

`tests/lifecycle_trust/test_lifecycle_trust.py` includes the issue #62
fail-closed controls:

```text
missing ProjectionPolicy
ambiguous ProjectionPolicy selection
missing/invalid adoption authority
unscoped adoption authority
silent material dependency-kind omission
silent material source-class omission
permissive applicability broadening without authority
stale cached policy projection
missing DependencyCompletenessClaim
policy-inadequate completeness coverage
missing established ASSUMES edge
NO_MATERIAL_EFFECT without policy-required basis
ACCEPTED_RESIDUAL without authority
DEPENDENCY_COMPLETENESS residual without explicit permission
EvaluationContext mismatch
knowledge-only TCB defect with unchanged revision
RecordSupersession with cached old basis
evidentiary self-support cycle
```

It also checks that affected evidence becomes non-reusable while independent
bounded evidence can remain selectively reusable.

## Run locally

```bash
python -m unittest discover \
  -s tests/lifecycle_trust \
  -p 'test_*.py' \
  -v

python prototypes/lifecycle_trust/validate.py \
  --build-dir build/lifecycle-trust \
  --summary build/lifecycle-trust/validation-summary.json
```

The validation runner emits deterministic JSON/Markdown projection records and
a summary containing:

```text
source revision
Python runtime version
discovered unit-test count
input SHA-256
result SHA-256
evaluator SHA-256
artifact byte-identity check
scenario decisions
```

## Scope limit

This experiment does not implement:

- a graph database;
- general dependency inference;
- production payment assurance;
- certification;
- runtime Simplex/fallback control;
- cross-component retry amplification;
- enterprise identity/quorum governance;
- a scalar confidence score;
- a universal proof of dependency completeness.

A successful experiment only supports the bounded claim that RFC 0012's
lifecycle rules can be made deterministic and fail-closed for this payment
retry/idempotency subject.
