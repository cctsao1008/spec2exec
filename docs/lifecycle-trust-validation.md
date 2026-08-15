# Bounded Lifecycle Trust Graph Validation

Issue: #62  
Architecture: RFC 0012 — Accepted / Lifecycle Trust Baseline

## Validated implementation revision

```text
797c0e4497e6fb9355236f659b96bf4e7870ecdc
Complete bounded lifecycle Trust Graph fixtures and CI wiring (#62)
```

GitHub Actions validation:

```text
workflow       Trust Research and Workflow POCs
run            31907601851
job            95067745186
conclusion     success
runner         Ubuntu 24.04.4 / ubuntu-24.04 image 20260810.271.1
Python         3.12.13
```

The workflow checked out the exact validated revision above.

## Bounded subject

```text
property       PAYMENT-RETRY-SAFETY
artifact       PAY-CANDIDATE-ACCEPTED
artifact sha   95018cb2c86bb1bea9cffb89e12ee31c711a26de159a1dcdacee21ce8b2b4c72
```

The same artifact SHA-256 is bound in all three lifecycle scenarios. Only the external API contract/context and lifecycle evidence differ.

## Unit-test result

```text
lifecycle-trust tests    29 / 29 PASS
```

The suite includes the 16 mandatory fail-closed controls from #62 plus additional checks for source-class omission, authority scope, policy lineage, affected-evidence reuse, invalid RFC 0011 grant kinds, RFC 0006 non-ranking, and property-scoped result semantics.

The existing trust-research regressions also remained green:

```text
A0 / C0 scorer tests                  4 / 4 PASS
semantic-review / CODEOWNERS tests    9 / 9 PASS
existing-compiler tests               2 / 2 PASS
```

## Three validation scenarios

### P1 — v7 baseline

```text
scenario        payment-retry-v7-baseline
expected        CURRENT
actual          CURRENT
blockers        0
input sha256    bfbd82834b80db8f7b8449c0d050445c2550458bb9cff4f6b1d9fc4a829e2cec
result sha256   7174f557457fdbde65102952ee542913fc8ee59d09157e3d48868e830aa3fda4
```

### P2 — v7 → v8, same client artifact

```text
scenario        payment-retry-v8-stale
expected        BLOCKED
actual          BLOCKED
blockers        2
input sha256    0c31e59fe192e305723e5bd62b7393166fd72960fd3218a5530a04ddf0a7bf83
result sha256   ef92682f4383258ed52c2f075c2855cc1e23614c7e5da907e456b5806c621359
```

The result records:

```text
API-IDEMPOTENCY-01
    AssumptionLifecycle.BASIS_STALE

IE-API-V7-V8 → CLAIM-PAYMENT-RETRY-SAFETY
    ImpactDisposition.REVALIDATION_REQUIRED

CurrentTrustProjection
    BLOCKED
```

Historical evidence remains recorded. The unchanged artifact hash does not keep the current property projection CURRENT.

### P3 — bounded v8 revalidation

```text
scenario        payment-retry-v8-revalidated
expected        CURRENT
actual          CURRENT
blockers        0
input sha256    92391be0303b17d42e7ebf91c6110692071b298bf54d36a544146a67db992fb4
result sha256   fa3054146d90fa12738e88bb5a377de858d299ea78d0ea2ca5b5e4ebb931671e
revalidation    RV-API-IDEMPOTENCY-V8
```

The revalidation uses the policy-accepted RFC 0006 evidence tuple:

```text
CHECKED / contract-equivalence-check
```

It restores the affected assumption relationship for the v8 EvaluationContext. It does not create semantic authority or upgrade unrelated evidence classes.

## Selective evidence reuse

The bounded experiment retains these historical evidence records across the contract-change scenarios when their represented dependency basis is unchanged:

```text
EV-CLIENT-ARTIFACT-001
EV-SEMANTIC-REVIEW-001
```

Separate negative controls demonstrate that a knowledge-only defect in the TCB/tool dependency makes affected evidence non-reusable while unrelated bounded evidence may remain reusable.

## Deterministic contracts

```text
prototypes/lifecycle_trust/evaluate.py
    sha256 d0222847c5419e170aff03edce6c416779ffcfbf93e2a41261c1ea068ef174fa

spec/schemas/lifecycle-trust-input-v0.1.schema.json
    sha256 e4b2b090cd079ace668763a71239c1551edbf4805379c89043a87d7afb9ef22a

spec/schemas/lifecycle-trust-result-v0.1.schema.json
    sha256 8c44785fb298e980362811502ae925ca58fc34c00687b6b717ad359d660a6828
```

These schemas are bounded #62 experiment contracts. They do not freeze a universal RFC 0012 storage schema.

## CI artifact

```text
artifact name     trust-research-evidence
artifact id       9252771947
size              12615 bytes
zip sha256        6c0aacc8511d4bf644801ad4cf64d40b7b2b7b0619df689d88550c4f24af8068
```

The artifact contains the lifecycle validation summary plus JSON/Markdown results for all three lifecycle scenarios, along with the existing payment-retry and existing-compiler evidence outputs.

## Claim boundary

This validation supports only the bounded statement that the Accepted RFC 0012 lifecycle rules can be implemented deterministically for this payment-retry/idempotency experiment such that the tested negative conditions fail closed, an external dependency change can stale current trust without changing artifact bytes, and a policy-accepted revalidation can restore a fresh property/context projection with selective reuse.

It does **not** claim:

- formal proof of RFC 0012;
- universal dependency completeness;
- production payment safety;
- cryptographic organizational authority;
- certification;
- a generic Trust Graph platform;
- an evidence-strength ordering;
- that `CURRENT` is an artifact-wide trust label.
