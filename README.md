# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec explores specification as the primary human-facing artifact between intent and executable software.

## Research question

```text
Must manually authored programming-language source remain the primary
interface between human intent and executable software?
```

Spec2Exec treats this as a hypothesis to test, not a conclusion already established.

## Architecture

```text
Human Intent
    ↓
Accepted Specification
    ↓
SpecIR
    ↓
Deterministic Verification
    ↓
Preservation Evidence
    ↓
Lowering / Compiler Backend
    ↓
Executable
```

Three correctness boundaries remain distinct: intent fidelity, specification/SpecIR correctness, and implementation conformance. No single PASS is allowed to imply all three.

SpecIR is formal and machine-oriented. It is optimized for synthesis → verification → lowering and is not intended to become a mandatory human-authored general-purpose source language.

## Status

```text
POC-0   Hello / deterministic plumbing                       COMPLETE
POC-1A  Bounded integer semantics + evidence hardening       COMPLETE
POC-1B  C semantic / optimization preservation               COMPLETE
POC-2   State machine                                        NEXT
POC-3   Embedded/control example                             PLANNED
A0      Adversarial semantic-resolution benchmark            PARALLEL
```

AI semantic synthesis remains disconnected from executable generation while the deterministic path is tested independently.

## POC-1A

Current subset:

```text
i32 / u32
+ - *
ranges and pre/postconditions
overflow_behavior = forbidden
straight-line expressions
traceability
```

After hostile review, the original bare `PROVEN` wording was removed. Hardened P3-A evidence is model-scoped:

```text
P3A.restricted_emitted_expression_equivalence = SOLVER_PROVEN
semantic_model = fixed-width-bitvector-v1

Q0 domain_non_vacuous       SAT
Q1 no_overflow_or_wrap      UNSAT
Q2 encoder_cross_check      UNSAT
Q3 result_equivalence       UNSAT
Q4 harness_sensitivity      SAT
```

P2 interval analysis and P3-A bit-vector analysis cross-check arithmetic safety. Exact artifact hashes bind evidence to the generated source that is compiled.

`safe_add` retains `TESTED_EXHAUSTIVE` evidence for all 10,201 accepted input pairs.

## POC-1B

```text
safe_add_sub(a,b) = (a + b) - b
a,b ∈ [-100,100]
additional contract: result == a
```

POC-1B adds an independent CBMC check of the generated C and observes Clang optimization without requiring internal nodes to survive.

First successful CI evidence:

```text
P3-A restricted BitVec model      SOLVER_PROVEN
P3-B generated-C contract         MODEL_CHECKED
Clang -O0 add/sub count           2
Clang -O2 add/sub count           0
P4 optimized executable           TESTED_EXHAUSTIVE (40,401 cases)
```

The optimization observation carries no proof claim by itself. The experiment supports only the narrow result that, for this bounded straight-line case, contract-level evidence does not require one-to-one structural identity.

## Run

POC-1A v2 requires Python 3, a host C compiler, and `z3-solver==4.13.0.0`.

```bash
python prototypes/poc1/spec2exec_poc1_v2.py all examples/bounded-arithmetic/safe_add.specir.json --specification examples/bounded-arithmetic/specification.json --build-dir build/poc1-v2
```

POC-1B additionally requires CBMC and Clang.

```bash
python prototypes/poc1b/spec2exec_poc1b.py examples/optimization-preservation/safe_add_sub.specir.json --specification examples/optimization-preservation/specification.json --build-dir build/poc1b
```

CI: `.github/workflows/poc1-hardening.yml`

## Documents

```text
docs/architecture.md
docs/phase1-plan.md
rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md
rfcs/0006-semantic-preservation-and-evidence-model.md
rfcs/0007-bounded-integer-semantics.md
rfcs/0008-c-semantic-and-optimization-preservation.md
research/a0-semantic-resolution/README.md
```

## License

License selection remains intentionally pending.
