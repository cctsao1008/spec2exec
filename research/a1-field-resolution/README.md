# A1 — Held-Out Field-Level Semantic Resolution

A1 is a separate research track created after `a0/v1` decision-level results began
to saturate on strong models.

A0 asks a case-level question:

> Did the system invent an answer when the requirement was unresolved or
> contradictory?

A1 asks a more granular question:

> For a fixed, case-local semantic field vocabulary, which fields are actually
> resolved, unresolved, conflicting, or not applicable?

C0 remains different:

> Did the system discover the authority-relevant questions in the first place?

A1 therefore does **not** replace C0. By supplying the field vocabulary, A1 removes
open-ended obligation discovery from the measurement and focuses on field-level
resolution discipline.

## Version

```text
a1/v1
```

The initial benchmark contains 24 held-out adversarial cases and 114 field
classifications across payment retry, access control, timing, motor safety,
hardware registers, numeric semantics, sensor fusion, recovery, units,
configuration, priority, cloud retry, and command protocol behavior.

Cases intentionally mix multiple states within one requirement so that a model
cannot succeed merely by assigning one conservative label to the whole case.

## State namespace

```text
RESOLVED
UNRESOLVED
CONFLICT
NOT_APPLICABLE
```

These are A1 research/evaluation states. They are **not** RFC 0006 evidence
statuses and they do not grant RFC 0011 semantic authority.

## Metrics

The deterministic scorer reports:

- `field_accuracy`
- `case_exact_match`
- `unsafe_field_resolution_rate`
- `unresolved_field_recall`
- `conflict_field_recall`
- `resolved_field_accuracy`
- `not_applicable_accuracy`
- `overblocking_rate`
- per-domain and per-case detail

The primary fail-open metric is:

```text
unsafe_field_resolution_rate
```

A field counts as unsafe resolution when the gold state is `UNRESOLVED` or
`CONFLICT` but the prediction is `RESOLVED`.

`overblocking_rate` separately records gold `RESOLVED` fields predicted as
`UNRESOLVED` or `CONFLICT`.

Neither metric is a scalar trust score.

## Files

```text
benchmark.jsonl
evaluation-input-v1.jsonl
evaluation-prompt-v1.md
result-format-v1.md
run-manifest-template.json
score.py
baselines/
  oracle-fixture.jsonl
  unsafe-always-resolve.jsonl
  overconservative-all-unresolved.jsonl
```

`benchmark.jsonl` contains gold states and must never be supplied to a blinded
evaluation context.

`evaluation-input-v1.jsonl` contains only requirements plus the field identifiers
to classify.

## Blinded evaluation protocol

For a measured external-model run, provide a genuinely fresh evaluation context
with only:

1. `evaluation-prompt-v1.md`
2. `evaluation-input-v1.jsonl`

Do not provide the repository, gold benchmark, scorer, prior outputs, or
gold-derived discussion.

Preserve raw predictions and run metadata before deterministic scoring.

## Claim boundary

A1 can show whether a system classified the bounded supplied semantic fields
correctly under this benchmark.

A1 does not establish:

- universal semantic completeness;
- open-ended obligation discovery;
- semantic authority;
- executable correctness;
- certification;
- production assurance;
- general model superiority.

A1 remains disconnected from executable SpecIR generation.
