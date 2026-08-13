# Phase 1 Plan — Minimal SpecIR and Deterministic Hello Pipeline

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

Purpose: verify toolchain plumbing only.

Required path:

```text
accepted hello specification
      ↓
experimental SpecIR document
      ↓
loader / parser
      ↓
schema + semantic verifier
      ↓
C or LLVM IR lowering
      ↓
system compiler
      ↓
Linux ELF executable
      ↓
runtime output check
```

Expected externally observable behavior:

```text
stdout: "Hello, world!\n"
exit status: 0
```

POC-0 does **not** validate the broader Spec2Exec thesis. It validates only the deterministic mechanics needed for later experiments.

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
- Generated C, if used, is a lowering artifact and not the source of truth.
- A verifier PASS must identify which properties were checked.
- Unsupported properties must remain explicit.
- Traceability identifiers must survive into generated artifacts where practical.

## Experimental SpecIR scope

The first SpecIR subset should be deliberately small. POC-0 needs only enough semantics to represent a program with ordered operations, stdout output, process exit, and traceability identifiers.

Do not add timing, concurrency, hardware, ownership, or theorem-proving constructs until a POC requires them.

## Suggested implementation order

1. Define an experimental SpecIR document for Hello World.
2. Define deterministic structural validation rules.
3. Implement a loader and verifier.
4. Implement lowering to C as the simplest backend bridge.
5. Compile with the host C toolchain to ELF.
6. Execute and check stdout / exit status.
7. Preserve traceability metadata in generated comments or sidecar evidence.
8. Add negative tests that must be rejected by the verifier.
9. Only after the deterministic path is stable, evaluate direct LLVM IR or MLIR lowering.
10. Introduce AI semantic synthesis later as an untrusted producer of the same candidate SpecIR.

## Exit criteria for POC-0

POC-0 is complete when:

- one accepted example specification exists;
- one experimental SpecIR representation exists;
- valid SpecIR deterministically passes validation;
- intentionally invalid SpecIR deterministically fails;
- lowering generates a buildable intermediate artifact;
- the existing compiler produces a Linux ELF executable;
- execution produces exactly the expected stdout and exit status;
- the build can be reproduced from the accepted specification and SpecIR test fixture;
- verification evidence clearly states what was and was not verified.
