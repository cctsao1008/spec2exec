# Terminology

## Intent

Human-level desired outcome. May be incomplete, contextual, or ambiguous.

## Specification

A sufficiently explicit statement of required behavior and constraints. It is the primary human-facing engineering artifact in Spec2Exec.

## Semantic Synthesis

The transformation from specification into formal program semantics. AI may be a synthesis engine, but AI is not the correctness authority.

## SpecIR

**Specification Intermediate Representation.** A machine-oriented, human-inspectable formal representation preserving implementation semantics and relevant engineering contracts.

## Verification

Deterministic checks or proofs establishing specified properties of SpecIR. Verification may combine static analysis, symbolic methods, SMT solving, model checking, theorem proving, or domain-specific analyzers.

## Lowering

Progressive transformation from SpecIR into lower-level compiler representations while preserving required semantics.

## Backend

Conventional target-specific compiler infrastructure responsible for code generation, optimization, ABI compliance, object generation, and related machine-level tasks.

## Executable

The final runnable or loadable artifact, such as ELF, PE, Mach-O, firmware ELF/BIN, WebAssembly, or another target-specific form.

## Source of truth

The authoritative project artifact. In Spec2Exec, the goal is for specification plus formalized semantics and verification evidence—not generated source code—to become the principal source of truth.
