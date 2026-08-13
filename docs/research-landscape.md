# Research Landscape

Spec2Exec sits at the intersection of several established research areas. Its individual ingredients are not new; the architectural integration and the proposed role of specification as the primary engineering interface are the focus.

## Program synthesis

Program synthesis studies automatic construction of programs from specifications or constraints. Relevant lines include syntax-guided synthesis (SyGuS) and solver-aided synthesis.

## Sketching / partial programs

Systems such as Sketch allow programmers to provide partial structure while a synthesizer fills implementation holes. Spec2Exec generalizes the question: can even the synthesis-oriented programming syntax cease to be the primary human interface?

## Verification-aware languages

Languages and systems such as Dafny combine executable programs with specifications, contracts, and machine-checked verification. They demonstrate that specifications can participate directly in the software toolchain.

## Verified compilation

CompCert demonstrates that compiler transformations themselves can be formally verified. This is relevant to the trusted lower portion of a Spec2Exec pipeline.

## LLVM / MLIR

LLVM and MLIR provide mature reusable infrastructure for intermediate representations, lowering, optimization, and target code generation. Spec2Exec should build above such infrastructure rather than replace it.

## AI-assisted verified synthesis

Recent work increasingly combines LLM generation with formal specifications, static analysis, symbolic verification, or proof systems. This supports a core Spec2Exec principle: probabilistic synthesis should operate inside deterministic verification boundaries.

## Model-based development

Model-based engineering already treats structured behavioral models as primary design artifacts in some domains and can generate implementation code. Spec2Exec should learn from this history, especially traceability, code-generation qualification, and the danger of overly restrictive modeling notations.

## Research gap explored by Spec2Exec

The project investigates a complete architecture in which:

```text
human intent
→ specification
→ semantic synthesis
→ non-human-oriented SpecIR
→ deterministic verification
→ conventional lowering/backend
→ executable
```

Particular attention is given to engineering semantics often external to normal source code: timing, physical units, resource bounds, hardware interfaces, state transitions, failure behavior, and safety constraints.
