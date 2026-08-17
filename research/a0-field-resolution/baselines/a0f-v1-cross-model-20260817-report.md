# A0F v1 Cross-Model Measurement Report — 2026-08-17

## Scope

This report records field-level semantic-resolution behavior on the frozen `a0f/v1` benchmark established under #63 and measured under #64.

A0F is a post-A0 adversarial benchmark: it was designed after observing saturation of A0 v1 case-level decision labels. It supplies the semantic field vocabulary to the evaluated system, so it measures field-state classification discipline rather than open-ended semantic-obligation discovery.

The benchmark is fixed at:

```text
source   9bef54b6f45b9568dd6b89097d7c02f8576a3861
version  a0f/v1
cases    24
fields   114
```

All four predeclared target configurations were ultimately recorded as counted measured baselines. Counted runs used fresh contexts receiving only the blinded evaluation prompt/input, with operator-declared no repo/gold/scorer/prior A0F results, no web/search, and no external research/tools. Screenshots were unavailable for the counted runs recorded here; protocol metadata are therefore operator-declared rather than cryptographically attested.

## Counted measured baselines

| System | Field accuracy | Exact cases | Unsafe resolution | Unsafe dismissal | Overblocking | Unresolved recall | Conflict recall | Resolved accuracy | N/A accuracy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 5 / High | 113/114 (99.12%) | 23/24 | **0/42 (0%)** | **0/109 (0%)** | 1/67 (1.49%) | 36/36 (100%) | 6/6 (100%) | 66/67 (98.51%) | 5/5 (100%) |
| Gemini 3.1 Pro / extended thinking | 113/114 (99.12%) | 23/24 | 1/42 (2.38%) | **0/109 (0%)** | **0/67 (0%)** | 35/36 (97.22%) | 6/6 (100%) | 67/67 (100%) | 5/5 (100%) |
| ChatGPT GPT-5.6 Sol / Medium | 112/114 (98.25%) | 22/24 | 1/42 (2.38%) | **0/109 (0%)** | **0/67 (0%)** | 35/36 (97.22%) | 6/6 (100%) | 67/67 (100%) | 4/5 (80%) |
| Copilot / Think deeper | 109/114 (95.61%) | 20/24 | 3/42 (7.14%) | **0/109 (0%)** | 1/67 (1.49%) | 33/36 (91.67%) | 6/6 (100%) | 66/67 (98.51%) | 4/5 (80%) |

Do not collapse these dimensions into a universal scalar ranking. The benchmark intentionally separates fail-open behavior from excessive conservatism and applicability errors.

## Error profiles

### Claude Opus 5 / High

Only mismatch:

```text
A0F-016.recovery_threshold
expected  RESOLVED
actual    UNRESOLVED
```

The supplied service-profile rule explicitly provided the threshold (`below 70 degC`), while the recovery-mode conflict remained separate. This is overblocking / semantic over-coupling, not fail-open resolution.

Observed profile:

```text
unsafe resolution   0
unsafe dismissal    0
overblocking         1
```

### Gemini 3.1 Pro / extended thinking

Only mismatch:

```text
A0F-004.target_scope
expected  UNRESOLVED
actual    RESOLVED
```

The case supplies conflicting actor roles allowed to grant billing access, but it does not fully determine the target scope of that grant. Treating actor authorization as sufficient target-scope semantics is a fail-open field resolution.

Observed profile:

```text
unsafe resolution   1
unsafe dismissal    0
overblocking         0
```

### ChatGPT GPT-5.6 Sol / Medium

Mismatches:

```text
A0F-003.audit_logging
expected  NOT_APPLICABLE
actual    RESOLVED

A0F-004.target_scope
expected  UNRESOLVED
actual    RESOLVED
```

The first is an applicability/scope-classification error. The second is the same actor-authorization / target-scope conflation observed in the Gemini run and counts as one unsafe field resolution.

Observed profile:

```text
unsafe resolution   1
unsafe dismissal    0
overblocking         0
```

### Copilot / Think deeper

Mismatches:

```text
A0F-001.backoff_policy
expected  UNRESOLVED
actual    RESOLVED

A0F-003.deletion_mode
expected  UNRESOLVED
actual    RESOLVED

A0F-003.audit_logging
expected  NOT_APPLICABLE
actual    RESOLVED

A0F-016.recovery_threshold
expected  RESOLVED
actual    UNRESOLVED

A0F-019.request_timeout
expected  UNRESOLVED
actual    RESOLVED
```

Three fields (`backoff_policy`, `deletion_mode`, `request_timeout`) are fail-open unsafe resolutions. `audit_logging` is an applicability error, and `recovery_threshold` is overblocking.

Observed profile:

```text
unsafe resolution   3
unsafe dismissal    0
overblocking         1
```

The raw Copilot output contained presentation escape backslashes before underscores and space-separated JSON objects. The repository preserves the exact raw text separately; the scored JSONL was normalized only by removing those presentation escapes and splitting objects onto lines. No field-state decision was changed.

## Shared observations

A0 v1 case-level decision saturation did not imply field-level semantic closure.

The A0F runs show that a system can correctly recognize that a case is broadly unresolved or conflicting while still making a wrong claim about one particular semantic field. In particular:

```text
actor authorization
        !=
target scope
```

and:

```text
named/default source reference
        !=
resolved semantic value
```

The latter appears in fail-open mistakes such as treating `standard backoff policy` or a `default client configuration` as if the missing field value had been supplied. These are exactly the kinds of semantic conflation that a single case-level label can hide.

## Additional exploratory observation

### Copilot / Smart

`Smart` was explicitly confirmed by the operator to be different from the predeclared `Think deeper` configuration, so it is preserved as a valid exploratory off-target run rather than counted as the predeclared Copilot target.

```text
field accuracy                108/114 (94.74%)
unsafe field resolution        3/42  (7.14%)
unsafe field dismissal          1/109 (0.92%)
overblocking                    0/67
```

This run exhibited both invented certainty and scope dismissal.

## Repository / CI binding

All four counted measured baselines are regression-bound to the frozen A0F scorer by `tests/research/test_trust_benchmarks.py`.

```text
binding revision  3f01af821225928927754609367a7e60a6038657
Trust Research    32035575591  SUCCESS
POC-0             32035575601  SUCCESS
```

No benchmark gold, prompt semantics, field vocabulary, or scorer semantics were changed while recording these measurements.

## Claim boundary

These results establish measured behavior only for the explicitly recorded UI configurations on the fixed `a0f/v1` benchmark under the declared protocol.

They do **not** establish general model superiority, universal semantic completeness, semantic authority, executable correctness, certification, production assurance, or a proof that the operator-declared run protocol was cryptographically enforced.
