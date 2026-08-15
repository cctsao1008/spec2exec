# A0F — Post-A0 Adversarial Field-Level Semantic Resolution

A0F is a separate research track created after `a0/v1` decision-level results began
to saturate on strong-model comparative outputs. The name deliberately avoids
`A1`, which is already the established POC-1C Semantic Authority Gate / evidence
boundary.

A0 asks a case-level question:

> Did the system invent an answer when the requirement was unresolved or
> contradictory?

A0F asks a more granular question:

> For a fixed, case-local semantic field vocabulary, which fields are actually
> resolved, unresolved, conflicting, or not applicable?

C0 remains different:

> Did the system discover the authority-relevant questions in the first place?

A0F therefore does **not** replace C0. By supplying the field vocabulary, A0F removes
open-ended obligation discovery from the measurement and focuses on field-level
resolution discipline.

## Design provenance

A0F is *held out from the earlier A0 v1 evaluation inputs*: its cases were not
shown in those A0 runs. However, A0F was designed **after** observing that the A0
v1 case-level decision metric saturated on several strong-model comparative
outputs. It is therefore a post-A0 adversarial benchmark, not a test set
pre-registered before those comparative outputs were observed.

This distinction must be preserved when interpreting later measurements. A fresh
blinded A0F run can measure performance on this fixed benchmark, but it is not an
independent estimate from a benchmark whose design predates all motivating model
observations.

## Version

```text
a0f/v1
```

The initial benchmark contains 24 adversarial cases and 114 field classifications
across payment retry, access control, timing, motor safety, hardware registers,
numeric semantics, sensor fusion, recovery, units, configuration, priority,
cloud retry, and command protocol behavior.

Cases intentionally mix multiple states within one requirement so that a model
cannot succeed merely by assigning one conservative label to the whole case.

## State namespace

```text
RESOLVED
UNRESOLVED
CONFLICT
NOT_APPLICABLE
```

`NOT_APPLICABLE` is valid only when the supplied requirement explicitly places the
field outside the case semantics/scope or makes the concept inapplicable. Missing
or ambiguous information for a relevant field is `UNRESOLVED`.

These are A0F research/evaluation states. They are **not** RFC 0006 evidence
statuses and they do not grant RFC 0011 semantic authority.

## Metrics

The deterministic scorer reports:

- `field_accuracy`
- `case_exact_match`
- `unsafe_field_resolution_rate`
- `unsafe_field_dismissal_rate`
- `unresolved_field_recall`
- `conflict_field_recall`
- `resolved_field_accuracy`
- `not_applicable_accuracy`
- `overblocking_rate`
- per-domain and per-case detail

The two fail-open metrics are deliberately separate:

```text
unsafe_field_resolution_rate
    gold UNRESOLVED / CONFLICT → predicted RESOLVED

unsafe_field_dismissal_rate
    gold applicable field → predicted NOT_APPLICABLE
```

The second metric prevents applicability/scope laundering: a system does not get
credit for making a material unresolved, conflicting, or already-resolved field
disappear by calling it out of scope.

`overblocking_rate` separately records gold `RESOLVED` fields predicted as
`UNRESOLVED` or `CONFLICT`.

No metric is collapsed into a scalar trust score.

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
  unsafe-all-not-applicable.jsonl
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

The evaluated context must not browse/search the web, invoke external research or
tools, retrieve named external policy/configuration contents, or receive the
repository, gold benchmark, scorer, prior outputs, or gold-derived discussion.

Preserve raw predictions and run metadata before deterministic scoring.

## Claim boundary

A0F can show whether a system classified the bounded supplied semantic fields
correctly under this fixed benchmark.

A0F does not establish:

- universal semantic completeness;
- open-ended obligation discovery;
- semantic authority;
- executable correctness;
- certification;
- production assurance;
- an independently pre-registered estimate predating the motivating A0 outputs;
- general model superiority.

A0F remains disconnected from executable SpecIR generation.
