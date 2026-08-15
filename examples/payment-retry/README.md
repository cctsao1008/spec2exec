# Payment Retry — Semantic Authority / Review POC

This example is intentionally understandable without compiler knowledge.

## Failure story

```text
Requirement:
Retry failed payment requests.

AI candidate:
Retry 5 times.

Question:
Who authorized 5?
```

The implementation can be internally correct and fully tested while still carrying a semantic decision that nobody authorized.

This POC keeps the existing `safe_add_sub` fixture unchanged. `safe_add_sub` remains useful for deterministic executable/evidence regression; payment retry is the human-facing semantic-authority example.

## Files

- `requirement.json` — source requirement plus explicitly structured candidate fields.
- `authority-policy.json` — bounded repository-declared authority policy for the demo.
- `unsafe-candidate.json` — intentionally contains an unauthorized value and an unresolved semantic obligation.
- `accepted-candidate.json` — all declared obligations are resolved and authorized under the demo policy.
- `.github/CODEOWNERS` — repository ownership input consumed by the GitHub authority adapter.
- `prototypes/semantic_review/review.py` — deterministic semantic review / Markdown renderer.

## Semantic obligations

The example surfaces:

- retry count;
- retryable HTTP 500 behavior;
- retry-on-timeout behavior;
- backoff policy;
- request timeout;
- idempotency requirement;
- terminal failure behavior.

The policy is deliberately narrow. Plausibility does not grant authority.

## Unsafe review

Expected shape:

```text
Spec2Exec Semantic Review

retry_count = 5            UNAUTHORIZED
retry_on_http_500 = true   AUTHORIZED
retry_on_timeout = ?       UNRESOLVED

MERGE GATE: BLOCKED
```

## Accepted review

The corrected candidate selects only values granted by the bound demo policy and satisfies the idempotency constraint, so the deterministic review returns `ACCEPTED`.

## GitHub / CODEOWNERS limitation

The CODEOWNERS adapter is a **repository identity/ownership adapter**, not the RFC 0011 authority architecture itself.

The demo reports attribution as repository-declared and unauthenticated. It does not claim that GitHub identity, CODEOWNERS, or repository write access is cryptographically sufficient for production authority.

Future adapters may bind OIDC, signed commits, organization roles, or enterprise identity while preserving the RFC 0011 authority model.
