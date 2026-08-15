# A0F v1 Blinded Field-Level Semantic Resolution Prompt

## Contamination rule

For a measured A0F baseline, provide the system under test with **only**:

1. this evaluation prompt; and
2. `evaluation-input-v1.jsonl`.

Do **not** provide the full Spec2Exec repository, `benchmark.jsonl`, scorer source,
README discussion containing gold states, prior model outputs, or any file exposing
the expected field labels.

A run performed after the evaluated context has seen the gold field states is
contaminated and must not be reported as a measured A0F baseline.

## Task

Each input case provides:

- a requirement;
- a fixed list of semantic field identifiers.

For every supplied field identifier, classify whether the requirement itself gives
enough authoritative information for that field.

Use exactly one state:

- `RESOLVED`: the supplied requirement explicitly determines the field.
- `UNRESOLVED`: the field is relevant, but required executable semantics are
  missing or ambiguous.
- `CONFLICT`: supplied authoritative statements disagree about that field and no
  supplied precedence rule resolves the disagreement.
- `NOT_APPLICABLE`: the field is explicitly outside the semantics/scope of this
  case, or the requirement makes the concept inapplicable.

Do not use common practice, engineering intuition, safety convention, external
documentation, or a plausible default as a substitute for missing information.

A named external policy or configuration is not enough to resolve fields whose
contents are not supplied, unless the requirement itself states the relevant rule.

If a supplied precedence rule resolves an apparent conflict, classify the governed
field according to the resulting supplied semantics rather than as `CONFLICT`.

## Output

Return JSONL only, preserving every case ID exactly once.

Each row must have exactly this shape:

```json
{"id":"A0F-001","field_states":{"retry_count":"RESOLVED","backoff_policy":"UNRESOLVED"}}
```

Rules:

- `field_states` must contain every field identifier supplied for that case,
  exactly once.
- Do not add field identifiers that were not supplied.
- State values must be exactly `RESOLVED`, `UNRESOLVED`, `CONFLICT`, or
  `NOT_APPLICABLE`.
- Do not add commentary outside the JSONL rows.
