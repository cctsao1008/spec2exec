# A0F v1 Result Format

Each prediction file is JSONL with one row per benchmark case.

```json
{
  "id": "A0F-001",
  "field_states": {
    "retryable_failures": "RESOLVED",
    "retry_count": "RESOLVED",
    "backoff_policy": "UNRESOLVED"
  }
}
```

Requirements:

- Every benchmark case ID appears exactly once.
- `field_states` contains exactly the supplied field IDs for the case.
- No missing or extra field IDs are allowed.
- Every value is one of:
  - `RESOLVED`
  - `UNRESOLVED`
  - `CONFLICT`
  - `NOT_APPLICABLE`

The deterministic scorer rejects malformed case IDs, field sets, or labels.

A measured-run report should also preserve:

- model/system identity as displayed by the provider;
- provider/runtime;
- effort/reasoning/sampling controls if exposed;
- prompt/input hashes;
- predictions hash;
- source revision;
- contamination declaration;
- scorer output.

Do not select a favorable pass threshold after observing results. The repository
records raw metrics rather than converting them into an invented universal trust
grade.
