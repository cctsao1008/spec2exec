# C0 — Semantic Obligation Discovery / Completeness Benchmark

## Purpose

C0 tests the upstream problem that an authority gate cannot solve by itself:

> Did the system identify the authority-relevant semantic questions that must be resolved before executable synthesis?

RFC 0011 can reject an unauthorized or unresolved `SemanticObligation` once that obligation exists. It cannot reject an obligation that an upstream process silently failed to surface.

C0 therefore evaluates **semantic-obligation discovery**, not authorization and not executable semantic closure.

## Distinction from A0 and executable semantic closure

```text
C0 Obligation Discovery
    requirement → candidate semantic obligations
    question: what must be decided?

A0 Semantic Resolution
    known obligation → RESOLVED / UNRESOLVED / CONFLICT
    question: did the system invent certainty?

RFC 0011 Authority
    resolved value → authority evaluation
    question: who/what authorized it?

Executable Semantic Closure
    known obligations → selected build subset
    question: which obligations affect this build?
```

## Case format

Each JSONL case declares a benchmark-specific gold obligation set:

```json
{
  "id": "C0-001",
  "benchmark_version": "c0/v1",
  "domain": "payment-retry",
  "requirement": "Retry failed payment requests.",
  "gold_obligations": [
    {
      "id": "retry_count",
      "impact": "HIGH",
      "rationale": "The retry budget changes observable payment behavior."
    }
  ]
}
```

The gold set is a **benchmark oracle for the declared case**, not a claim of universal completeness for a real production or regulated system.

## Prediction format

```json
{
  "id": "C0-001",
  "obligations": [
    "retry_count",
    "retryable_failures",
    "idempotency_requirement"
  ]
}
```

IDs are canonical within the benchmark case. The scorer intentionally avoids fuzzy natural-language matching in v1.

## Metrics

- `obligation_recall` — discovered gold obligations / all gold obligations.
- `unsafe_omission_rate` — omitted gold obligations / all gold obligations.
- `spurious_obligation_rate` — predicted non-gold obligations / all predicted obligations.
- `high_impact_recall` — recall over obligations labeled `HIGH` or `CRITICAL`.
- per-domain recall and omission rate.

The primary trust-oriented metric is `unsafe_omission_rate`.

A low omission rate on C0 does **not** prove a real-world specification is complete. It measures performance against the declared benchmark oracle.

## Guardrails

- Do not generate a gold set after seeing a model output merely to make the model look better.
- Do not connect C0 predictions directly to executable SpecIR.
- A discovered obligation still needs A0-style resolution handling and RFC 0011 authority.
- False positives matter because surfacing arbitrary noise can make the workflow unusable; therefore C0 reports a spurious-obligation rate rather than optimizing recall alone.
