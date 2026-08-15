# A0 v1 Measured Baseline — Claude Opus 5 / High

## Status

This record preserves the first measured external-model baseline for Spec2Exec A0 v1 under the repository's blinded evaluation protocol.

The system under test was presented in a fresh Claude web chat with only:

```text
evaluation-prompt-v1.md
evaluation-input-v1.jsonl
```

The operator did not provide the repository, `benchmark.jsonl`, scorer source, prior outputs, or gold-derived discussion to the evaluation chat.

The UI label shown for the run was:

```text
Model   Opus 5
Effort  High
Mode    Chat
Cowork  not selected
```

Temperature and seed are not exposed by the evaluated web UI and are recorded as not applicable rather than inferred.

## Reproducibility bindings

```text
benchmark version       a0/v1
source revision         badad379f9d796f88ad8ba2c83b112456cc59e2b
harness revision        badad379f9d796f88ad8ba2c83b112456cc59e2b

evaluation prompt
sha256 def0dae9c218cfccd2cb5cf34dd9aa5b007de76a23859c3383403180f28fa574

evaluation input
sha256 ed37856aa47695383dae757006d47346d74b40da29c59c89f240ffa70cad728c

raw predictions
sha256 b8cd668fe292531698328edee728bb5295d663313051098d4c7caa66b248919c

recorded scorer output
sha256 0eb5f6ba4d1a9f74e6b7e5c00a71cfa0fae64cb56da2a0d415af64c2a4bf2c79

operator screenshot
sha256 a5cd299919c04261a3a2167bdf9343c37da56fd6e3ffc50feb87f3761bb20507
```

## Deterministic A0 score

The repository A0 scorer evaluates the three decision labels:

```text
RESOLVED
UNRESOLVED
CONFLICT
```

Measured result:

| Metric | Result |
|---|---:|
| Cases | 24 |
| Overall accuracy | 1.0000 |
| Unsafe resolution rate | 0.0000 (0 / 14 unresolved-or-conflict cases) |
| Unresolved recall | 1.0000 |
| Conflict recall | 1.0000 |
| Resolved accuracy | 1.0000 |

Confusion matrix:

| Gold \\ Predicted | RESOLVED | UNRESOLVED | CONFLICT |
|---|---:|---:|---:|
| RESOLVED | 10 | 0 | 0 |
| UNRESOLVED | 0 | 11 | 0 |
| CONFLICT | 0 | 0 | 3 |

Every domain in A0 v1 scored decision-label accuracy 1.0, and no case whose gold decision was `UNRESOLVED` or `CONFLICT` was incorrectly converted to `RESOLVED`.

## Reproduction

From the repository root:

```bash
python research/a0-semantic-resolution/score.py \
  research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816.predictions.jsonl \
  --output /tmp/claude-opus-5-high-20260816.score.json

diff -u \
  research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816.score.json \
  /tmp/claude-opus-5-high-20260816.score.json
```

The research regression suite also checks that the measured predictions reproduce the committed scorer output.

## Claim boundary

This is a measured result for **24 A0 v1 cases under this exact blinded prompt/input and declared run procedure**.

It does **not** establish:

- general Claude/Opus model quality;
- universal semantic-completeness performance;
- semantic authority;
- executable correctness;
- certification or safety qualification;
- robustness to held-out or adversarial A0 revisions;
- that the model's free-form `unresolved`, `resolved`, or `assumptions` fields exactly match the benchmark's field-level annotations.

The current A0 scorer primarily evaluates the decision namespace. In particular, the perfect score above means all 24 `RESOLVED` / `UNRESOLVED` / `CONFLICT` decisions matched A0 v1 gold labels. It should not be expanded into a claim that every explanatory field was independently scored as correct.

No favorable pass threshold was introduced after observing this result.

The predictions remain disconnected from executable SpecIR generation and do not gain RFC 0011 semantic authority from benchmark performance.
