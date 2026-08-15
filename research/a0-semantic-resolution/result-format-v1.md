# A0 v1 Result Format

A measured run consists of:

1. raw JSONL predictions;
2. a machine-readable run manifest;
3. scorer output.

## Prediction row

```json
{
  "id": "A0-017",
  "decision": "UNRESOLVED",
  "resolved": {},
  "unresolved": ["retry_count"],
  "assumptions": []
}
```

Required fields are `id` and `decision`. `decision` is one of `RESOLVED`, `UNRESOLVED`, or `CONFLICT`.

## Run manifest

A model/agent baseline should record at least:

```json
{
  "schema": "spec2exec.a0-run/v1",
  "benchmark_version": "a0/v1",
  "system_id": "...",
  "system_version": "...",
  "harness_revision": "...",
  "prompt_sha256": "...",
  "sampling": {
    "temperature": "...",
    "seed": "..."
  },
  "source_revision": "...",
  "predictions_sha256": "..."
}
```

Use `"not-applicable"` or an explicit explanation when a system does not expose a sampling control. Do not silently omit it.

The repository's deterministic control fixtures are not model baselines and must not be presented as measured AI synthesis quality.
