# A0 v1 Blinded Evaluation Prompt

## Contamination rule

For a measured model/agent baseline, provide the system under test with **only**:

1. this evaluation prompt; and
2. `evaluation-input-v1.jsonl`.

Do **not** provide the full Spec2Exec repository, `benchmark.jsonl`, scorer source, README discussion containing case answers, prior model outputs, or any file exposing the expected labels.

A run performed after the model has seen the gold labels is not a fair baseline and must be marked contaminated rather than reported as measured synthesis quality.

## Task

For each input case, decide whether the requirement provides enough authoritative semantic information to resolve the requested behavior without inventing missing semantics.

Use exactly one decision:

- `RESOLVED`: the requirement explicitly supplies the relevant executable semantics.
- `UNRESOLVED`: required executable semantics are missing or ambiguous.
- `CONFLICT`: the supplied authoritative statements disagree about the same semantic field.

Do not use common practice, engineering intuition, safety convention, or a plausible default as a substitute for information that the requirement did not supply.

## Output

Return JSONL only, preserving every case ID exactly once.

Each row must have this shape:

```json
{"id":"A0-001","decision":"UNRESOLVED","resolved":{},"unresolved":["..."],"assumptions":[]}
```

Rules:

- `decision` must be exactly `RESOLVED`, `UNRESOLVED`, or `CONFLICT`.
- For `UNRESOLVED`, list the missing/ambiguous semantic fields in `unresolved`.
- For `CONFLICT`, use `unresolved` to identify the conflicting semantic field(s).
- For `RESOLVED`, `resolved` may contain the explicit values/rules extracted from the requirement.
- `assumptions` must contain only assumptions you had to make; ideally it is empty. An assumption does not authorize a `RESOLVED` answer.
- Do not add commentary outside the JSONL rows.
