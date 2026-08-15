# Spec2Exec Semantic Review

**Subject:** `payment-retry`  
**Candidate:** `PAY-CANDIDATE-ACCEPTED`  
**MERGE GATE:** **ACCEPTED**

| Semantic obligation | Candidate value | Status | Impact |
|---|---:|---|---|
| `retry_count` | `3` | **AUTHORIZED** | HIGH |
| `retry_on_http_500` | `true` | **AUTHORIZED** | HIGH |
| `retry_on_timeout` | `false` | **AUTHORIZED** | HIGH |
| `backoff_policy` | `exponential` | **AUTHORIZED** | MEDIUM |
| `request_timeout_ms` | `2000` | **AUTHORIZED** | MEDIUM |
| `idempotency_requirement` | `true` | **AUTHORIZED** | CRITICAL |
| `terminal_failure_behavior` | `surface_failure` | **AUTHORIZED** | HIGH |

## Constraint checks

- `PAY-CONSTRAINT-IDEMPOTENCY` — **CHECKED** (applies=true)

## Authority adapter

- CODEOWNERS path: `examples/payment-retry/`
- Required owner: `@cctsao1008`
- Repository owners: `@cctsao1008`
- Attribution: `repository-declared` / `unauthenticated`

> CODEOWNERS is an adapter into the RFC 0011 authority model, not semantic authority by itself.
