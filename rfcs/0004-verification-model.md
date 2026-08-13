# RFC 0004 — Verification Model

- **Status:** Draft

## Principle

**AI proposes; deterministic mechanisms verify what they are actually capable of verifying. Human/domain authorities retain responsibility for intent fidelity where required.**

Spec2Exec must not use the word "verified" without naming the property, mechanism, and evidence class.

## Three correctness layers

### 1. Intent fidelity

Question:

> Does the accepted specification represent what the human/domain authority actually intends?

Primary authority:

- human review;
- domain authority;
- acceptance evidence;
- requirement provenance.

This layer is not generally provable by downstream formal verification.

### 2. Specification / SpecIR correctness

Question:

> Is the candidate SpecIR well-formed, internally consistent, and compliant with declared formal contracts?

Possible mechanisms include structural checks, static analysis, SMT solving, model checking, and theorem proving.

### 3. Implementation conformance

Question:

> Does lowering and compilation preserve the verified SpecIR semantics into the executable artifact?

Possible mechanisms include validated lowering, equivalence checking, compiler validation, verified compilation, tests, and runtime monitors where appropriate.

## Verification classes

### Structural

- schema validity;
- type consistency;
- symbol/interface resolution;
- traceability identifier validity.

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

The architecture may integrate SMT solving, model checking, theorem proving, or verified compilation. It must distinguish proven properties from checked, tested, estimated, assumed, or advisory properties.

## Evidence classes

Verification output should be attributable to an evidence class, for example:

```text
PROVEN
CHECKED
TESTED
MEASURED
ESTIMATED
ASSUMED
ADVISORY
UNRESOLVED
```

The exact vocabulary is draft, but evidence strength must remain explicit.

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

A verifier PASS only applies to the properties and assumptions actually checked. It is not evidence that the original human intent was correct or complete.

## Trust boundary

Semantic synthesis is untrusted candidate generation. A candidate may not cross into the checked/lowering domain until the required deterministic checks for the selected release mode have passed.

```text
Specification
    ↓
AI / synthesis
    ↓
Candidate SpecIR

──── trust boundary ────

Deterministic checks
    ↓
Verified-for-declared-properties SpecIR
    ↓
Lowering
```

## Failure rule

Unknown, unresolved, or unsupported properties must not be silently promoted to verified status. A target/domain policy decides whether such properties block lowering, restrict the artifact to prototype mode, or require additional evidence.
