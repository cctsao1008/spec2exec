# SpecIR

This directory tracks the normative direction for the Spec2Exec intermediate representation.

## Current status

**Experimental SpecIR v0** is now instantiated by POC-0. It is intentionally tiny and must not be treated as a stable language or public compatibility contract.

The first machine-readable schema is:

```text
spec/schemas/specir-v0.schema.json
```

The POC-0 instance is:

```text
examples/hello/hello.specir.json
```

## v0 semantic scope

SpecIR v0 currently models only:

- one program;
- a program identifier and name;
- a host-C lowering target;
- ordered `stdout.write` operations;
- process exit status;
- traceability identifiers.

It intentionally excludes timing, concurrency, hardware, units, ownership, arbitrary functions, state machines, and theorem-proving constructs.

## Design rule

SpecIR may have formal syntax and semantics, but it is not intended to become the mandatory human-authored general-purpose source language. It is optimized for synthesis, verification, traceability, and lowering.
