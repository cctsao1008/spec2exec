# POC-0 — Deterministic Hello Pipeline

POC-0 is the first executable Spec2Exec experiment.

It deliberately contains **no AI synthesis**. The purpose is to test the lower half of the architecture in isolation.

```text
Accepted Hello Specification
        ↓
Manually Constructed SpecIR v0
        ↓
Deterministic Verification
        ↓
C Lowering
        ↓
Host C Compiler
        ↓
Executable
        ↓
Runtime Check
```

## Run

From the repository root:

```bash
make test
make poc0
```

Or directly:

```bash
python3 prototypes/poc0/spec2exec_poc0.py all \
  examples/hello/hello.specir.json \
  --specification examples/hello/specification.json \
  --build-dir build/poc0
```

Generated files are written below `build/poc0/` and are intentionally not committed.

## Current evidence

The verifier checks a deliberately small set of properties and emits `verification.json`. It also explicitly reports properties that are not verified.

POC-0 currently treats C lowering, the host compiler, and the runtime environment as trusted/tested engineering infrastructure rather than formally proven transformations.
