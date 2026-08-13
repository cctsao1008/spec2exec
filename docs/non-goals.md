# Non-Goals

Spec2Exec does **not** initially aim to:

1. Replace all programming languages.
2. Build a new CPU ISA.
3. Reimplement LLVM or GCC backends.
4. Generate raw machine code directly from natural language without formal intermediate checks.
5. Treat an LLM answer as proof of correctness.
6. Define a universal specification language for every software domain in the first version.
7. Solve arbitrary software synthesis at production scale in the first prototype.
8. Hide generated behavior from engineers.
9. Eliminate source-level interoperability with existing C/C++/Rust or other ecosystems.
10. Claim formal verification for properties the selected verifier cannot actually prove.

The initial objective is narrower: establish a coherent architecture, formal boundaries, and a small end-to-end proof of concept.
