# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **Phase 0 architecture definition:** complete for the initial prototype baseline
- **POC-0:** complete
- **Next experiment:** POC-1 — Bounded Arithmetic

## Objective

Phase 1 tests the lower half of the Spec2Exec architecture **without AI**.

The goal is not to demonstrate intelligent synthesis. The goal is to establish that a small formal SpecIR can be loaded, deterministically checked, lowered through an existing compiler toolchain, and traced back to an accepted specification.

## Hypothesis under test

```text
Accepted Specification
      ↓
Manually Constructed Candidate SpecIR
      ↓
Deterministic Verification
      ↓
Lowering
      ↓
Existing Compiler Backend
      ↓
Executable
```

If this path cannot be made clear, deterministic, inspectable, and traceable, adding AI would only hide architectural problems.

## POC-0 — Hello World

**Status: Complete**

Purpose: verify toolchain plumbing and the minimum evidence/traceability path.

Implemented path:

```text
examples/hello/specification.json
      ↓
examples/hello/hello.specir.json
      ↓
prototypes/poc0/spec2exec_poc0.py
      ↓
verification + C lowering
      ↓
host C compiler
      ↓
build/poc0/hello
      ↓
runtime stdout / exit-status check
```

Expected externally observable behavior:

```text
stdout: "Hello, world!\n"
exit status: 0
```

POC-0 does **not** validate the broader Spec2Exec thesis. It validates only the deterministic mechanics needed for later experiments.

## POC-0 evidence boundary

The initial prototype CHECKS:

- supported SpecIR v0 structure;
- operation identifiers and operation kind;
- traceability scope;
- exit-status range;
- accepted requirement trace linkage;
- accepted specification ↔ SpecIR stdout linkage;
- accepted specification ↔ SpecIR exit-status linkage;
- runtime stdout and exit status during the experiment.

It does NOT currently prove:

- human intent fidelity;
- general specification completeness;
- lowering semantic equivalence;
- host C compiler correctness;
- machine-code semantic equivalence.

## POC-1 — Bounded Arithmetic

Purpose: introduce actual semantic contracts.

Candidate capabilities:

- scalar types;
- function inputs / outputs;
- preconditions;
- postconditions;
- bounded ranges;
- deterministic rejection of invalid examples.

## POC-2 — State Machine

Purpose: introduce behavioral state semantics.

Candidate capabilities:

- named states;
- events;
- guarded transitions;
- invalid-transition rejection;
- state invariants.

## POC-3 — Thermal Motor Protection

Purpose: first example that exercises domain semantics beyond ordinary generated source code.

Candidate capabilities:

- physical units;
- thresholds;
- timing duration;
- safe output value;
- fault state;
- unresolved requirement handling;
- provenance and specification acceptance.

Example behaviors may include:

```text
temperature >= 90 degC for 100 ms → MOTOR_OFF
sensor invalid for 3 samples       → MOTOR_OFF
MOTOR_OFF                          → manual reset required
```

The exact requirements must be explicitly accepted before being treated as authoritative example semantics.

## Phase 1 architecture constraints

- No LLM or AI is required in POC-0 through the initial verifier/lowering path.
- Candidate SpecIR may be manually constructed as a test fixture.
- Manual SpecIR construction is not the intended long-term development interface.
- Generated C is a lowering artifact and not the source of truth.
- A verifier PASS must identify which properties were checked.
- Unsupported properties must remain explicit.
- Traceability identifiers must survive into generated artifacts where practical.
- Semantic-preservation evidence follows RFC 0006.

## Experimental SpecIR scope

The first SpecIR subset is deliberately small. POC-0 represents only a program with ordered stdout operations, process exit status, and traceability identifiers.

Do not add timing, concurrency, hardware, ownership, or theorem-proving constructs until a POC requires them.

## POC-0 implementation sequence

1. Define accepted Hello specification. **Done.**
2. Define experimental SpecIR v0 document. **Done.**
3. Define structural/semantic validation rules. **Done.**
4. Implement deterministic loader/verifier. **Done.**
5. Implement lowering to C. **Done.**
6. Compile with host C toolchain and execute. **Done.**
7. Emit explicit verification evidence. **Done.**
8. Add negative verification tests. **Done.**
9. Reproduce the same path in GitHub Actions CI. **Done — first run passed.**
10. Only after the deterministic path is stable, consider direct LLVM IR/MLIR lowering and later AI semantic synthesis.

## POC-0 exit criteria

All initial POC-0 exit criteria are satisfied:

- one accepted example specification exists;
- one experimental SpecIR representation exists;
- valid SpecIR deterministically passes validation;
- intentionally invalid SpecIR deterministically fails;
- lowering generates a buildable intermediate artifact;
- an existing compiler produces a Linux executable;
- execution produces exactly the expected stdout and exit status;
- the build is reproducible through repository commands and GitHub Actions CI;
- verification evidence clearly states what was and was not verified.

The next Phase 1 task is POC-1, where SpecIR must begin carrying actual semantic contracts rather than only deterministic plumbing.
