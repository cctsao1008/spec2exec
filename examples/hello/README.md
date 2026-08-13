# Hello Example

The first Spec2Exec proof of concept should generate a Linux executable from a minimal specification without requiring a human-authored general-purpose source program as the source of truth.

Conceptual specification:

```text
program.name = "hello"
target = "linux-x86_64"
stdout = "Hello, world!\n"
exit_status = 0
```

Expected pipeline:

```text
Specification
  ↓
SpecIR
  ↓
Verifier
  ↓
C or LLVM IR lowering
  ↓
Existing toolchain
  ↓
ELF executable
```
