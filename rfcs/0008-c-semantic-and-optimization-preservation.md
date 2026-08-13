# RFC 0008 — C Semantic and Optimization Preservation

- **Status:** Draft / Experimental
- **Scope:** POC-1B reference path

POC-1B tests contract-level preservation when compiler optimization changes the internal structure of generated C.

The experiment uses `(a + b) - b` with bounded `i32` inputs and the accepted contract `result == a`.

Evidence is separated by boundary:

```text
P3-A  32-bit BitVec translation model       SOLVER_PROVEN
P3-B  generated C contract via CBMC          MODEL_CHECKED
P4    optimized executable, 40,401 cases    TESTED_EXHAUSTIVE
```

P3-A uses separate queries for domain satisfiability, arithmetic safety, encoder cross-checking, result equivalence, and harness sensitivity. It is explicitly scoped to a restricted emitted-expression model.

P3-B checks the generated C at the function boundary and retains the accepted contract identifier. It does not require SpecIR nodes to survive optimization.

Clang `-O0` is used to observe the original add/sub structure and `-O2` to demonstrate that the structure can disappear. This observation is not itself a semantic proof.

Evidence records exact artifact hashes. P2 interval analysis and P3-A BitVec safety analysis cross-validate each other. Generated integer literals use type-aware forms so the experimental 32-bit model is not silently widened by C literal typing.

This POC does not claim compiler correctness, machine-code equivalence, target ABI correctness, hardware semantics, or human intent fidelity.

## Architecture role after RFC 0009

The C path is now explicitly a bootstrap/reference/differential-validation path rather than the mandatory Spec2Exec executable-generation architecture.

The primary architecture proceeds from verified SpecIR to native target code generation and target assembly. POC-1B remains useful evidence about semantic preservation, optimization, artifact binding, and traceability precisely because it demonstrates the additional semantic burden introduced by a high-level C intermediary.

No POC-1B result is invalidated by RFC 0009; only the architectural role of generated C has changed.
