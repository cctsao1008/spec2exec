# C0 v1 Prediction and Result Format

## Prediction input

A system under test emits one JSONL row per benchmark case:

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

Requirements:

- every benchmark case appears exactly once;
- unknown case IDs fail closed;
- every obligation ID is a non-empty string;
- duplicate predicted obligation IDs fail closed;
- v1 uses canonical case-local IDs rather than fuzzy natural-language matching.

## Scorer result

The scorer emits a versioned JSON object containing at least:

```json
{
  "benchmark_version": "c0/v1",
  "cases": 6,
  "gold_obligations": 33,
  "predicted_obligations": 0,
  "obligation_recall": 0.0,
  "unsafe_omission_rate": 1.0,
  "spurious_obligation_rate": 0.0,
  "high_impact_recall": 0.0,
  "by_domain": {},
  "cases_detail": {}
}
```

The values above illustrate field shape only; they are not a model baseline.

A future measured model/agent run should additionally bind the exact model/system identifier, harness/prompt revision, sampling settings, source revision, and raw predictions, following the same reproducibility discipline as A0.
