# Hello Example — POC-0

The first Spec2Exec proof of concept validates deterministic toolchain plumbing. It intentionally does **not** use AI semantic synthesis.

## Accepted behavior

```text
program.name = "hello"
target = "linux-x86_64"
stdout = "Hello, world!\n"
exit_status = 0
```

For POC-0, this small example specification is treated as the accepted source of truth.

## Experimental pipeline

```text
Accepted Specification
  ↓
Manually Constructed Candidate SpecIR
  ↓
Loader / Parser
  ↓
Deterministic Verifier
  ↓
C or LLVM IR lowering
  ↓
Existing toolchain
  ↓
Linux ELF executable
  ↓
Runtime output / exit-status check
```

Manual construction of Candidate SpecIR is allowed only as a Phase 1 test fixture. It is not the intended long-term Spec2Exec development interface.

## POC-0 verifies

- deterministic SpecIR loading;
- structural / semantic checks defined by the minimal subset;
- lowering mechanics;
- host compiler integration;
- reproducible runtime behavior;
- traceability from generated artifact toward the accepted example requirement.

## POC-0 does not verify

- AI semantic synthesis quality;
- specification completeness;
- general intent fidelity;
- timing, concurrency, safety, hardware, or control semantics;
- the broader claim that specification-centric development scales better than programming-language-centric development.

Those questions belong to later experiments.
