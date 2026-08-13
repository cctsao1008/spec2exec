# Hello Example — POC-0

This example is the first deterministic Spec2Exec pipeline experiment.

## Authoritative example artifacts

```text
specification.json   accepted POC specification
hello.specir.json    manually constructed experimental SpecIR v0
```

The accepted behavior is:

```text
stdout: "Hello, world!\n"
exit status: 0
```

The prototype checks that the SpecIR trace references the accepted requirement and that the SpecIR stdout/exit behavior matches the accepted specification.

## Pipeline

```text
Accepted Specification
  ↓
SpecIR v0
  ↓
POC-0 Verifier
  ↓
Generated C
  ↓
Host C Toolchain
  ↓
Executable
  ↓
Runtime Output Check
```

## Run

From the repository root:

```bash
make test
make poc0
```

POC-0 validates toolchain plumbing and a minimal evidence model. It does not prove the general Spec2Exec thesis, general specification completeness, lowering equivalence, or compiler correctness.
