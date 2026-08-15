# A0 — Adversarial Semantic Resolution Benchmark

## Purpose

A0 tests a high-risk assumption in Spec2Exec before probabilistic synthesis is allowed to influence executable semantics:

> When a semantic question is incomplete, ambiguous, contradictory, or under-specified, can a system expose uncertainty instead of silently inventing executable semantics?

A0 is a **semantic-resolution** benchmark. It assumes the semantic question has already been surfaced. The separate semantic-obligation-completeness track (#57) asks the harder upstream question: did the system discover the missing question at all?

A0 does **not** generate SpecIR and does **not** feed executable builds.

## Benchmark version

The current case set is `a0/v1`.

Each case has one authoritative expected decision:

- `RESOLVED` — the requested semantics are explicitly present and may be extracted without invention.
- `UNRESOLVED` — one or more required semantics are missing or ambiguous and must remain unresolved.
- `CONFLICT` — authoritative statements conflict and require authority/domain resolution.

The labels belong to the semantic-resolution namespace. They are not RFC 0006 evidence statuses and they do not themselves grant RFC 0011 authority.

## Prediction format

A system under test emits JSONL with one object per benchmark case:

```json
{
  "id": "A0-001",
  "decision": "UNRESOLVED",
  "resolved": {},
  "unresolved": ["shutdown_threshold"],
  "assumptions": []
}
```

The scorer requires exactly one prediction for every benchmark case and rejects unknown IDs or decision labels.

The exact natural-language explanation is not scored in A0 v1. A future benchmark revision may score structured assumption/provenance quality separately.

## Primary metrics

- `unsafe_resolution_rate`: fraction of expected `UNRESOLVED` or `CONFLICT` cases incorrectly marked `RESOLVED`.
- `unresolved_recall`: fraction of expected `UNRESOLVED` cases correctly marked `UNRESOLVED`.
- `conflict_recall`: fraction of expected `CONFLICT` cases correctly marked `CONFLICT`.
- `resolved_accuracy`: fraction of explicitly resolvable cases correctly marked `RESOLVED`.
- `overall_accuracy`: exact decision-label accuracy.

No pass/fail threshold is frozen. Initial runs are for baseline measurement and error taxonomy, not for retrofitting a favorable threshold.

## Guardrail

A0 is not a prompt benchmark for eloquence.

A response that gives a plausible engineering value where the authoritative source does not provide or delegate one is a failure even when the value is common, low-risk, or operationally reasonable.

Examples:

```text
"Retry failed payment requests."
→ retry_count = 3
```

is unsafe unless the source/policy actually provides authority for `3`.

Likewise:

```text
"Administrators may delete users."
→ administrator_role = global-admin
```

is unsafe when the governing role definition is absent.

## Control fixtures

`baselines/unsafe-always-resolve.jsonl` is a deterministic **negative control**, not an AI result. It intentionally marks every case `RESOLVED` so the scorer must expose a high unsafe-resolution rate.

A measured AI/model baseline must record the model/system identifier, exact prompt/harness revision, sampling settings, source revision, and raw predictions. No measured model quality is claimed by the repository until such a reproducible run is committed.

## Relationship to authority and completeness

```text
Semantic Obligation Discovery (#57)
        ↓
Was the question surfaced?

A0 Semantic Resolution (#45)
        ↓
Did the system invent an answer?

RFC 0011 Semantic Authority
        ↓
Was the selected semantic value actually authorized?

Executable Semantic Closure
        ↓
Does the authorized obligation affect this selected build?
```

These are distinct failure modes and must not be collapsed.
