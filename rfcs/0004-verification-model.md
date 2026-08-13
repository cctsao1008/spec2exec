# RFC 0004 — Verification Model

- **Status:** Draft

## Principle

**AI proposes; verifier decides.**

## Verification classes

### Structural

- schema validity;
- type consistency;
- symbol/interface resolution.

### Semantic

- range constraints;
- unit consistency;
- state-transition validity;
- invariants;
- ownership/concurrency rules.

### Domain-specific

- timing budgets;
- bounded resource usage;
- safety transitions;
- control-domain constraints.

### Formal proof where feasible

The architecture may integrate SMT solving, model checking, theorem proving, or verified compilation. It must distinguish proven properties from tested, estimated, or advisory properties.

## Synthesis loop

```text
candidate SpecIR
      ↓
 verifier
  ┌───┴────┐
FAIL      PASS
 │          │
structured  ↓
diagnostic lowering
 │
 └→ synthesizer
```
