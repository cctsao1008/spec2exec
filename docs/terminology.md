# Terminology

## Intent

Human-level desired outcome. May be incomplete, contextual, or ambiguous.

## Specification

A sufficiently explicit statement of required behavior and constraints. It is the primary human-facing engineering artifact in Spec2Exec.

## Semantic Synthesis

The transformation from specification into formal program semantics. AI may be a synthesis engine, but AI is not the correctness authority.

## SpecIR

**Specification Intermediate Representation.** A machine-oriented, human-inspectable formal representation preserving implementation semantics and relevant engineering contracts. SpecIR is machine-independent and is not a target ISA representation.

## Verification

Deterministic checks or proofs establishing named properties of SpecIR or another declared artifact. Verification may combine static analysis, symbolic methods, SMT solving, model checking, theorem proving, or domain-specific analyzers. Evidence must identify the property, mechanism, scope, assumptions, and artifact.

## Lowering

A transformation from a higher-level representation to a lower-level one while preserving required semantics. In Spec2Exec, `Lowering` is a useful compiler-theory term but is not a mandatory top-level architecture stage.

## Target Profile

A machine-specific configuration selected after SpecIR verification. A target profile identifies the processor architecture/ISA, enabled architectural extensions, ABI/calling-convention subset, assembly dialect, object model, and other code-generation assumptions required by a backend.

Target profiles must not change the machine-independent meaning of SpecIR.

## Platform Profile

Optional SoC/board-specific information below the ISA level, such as memory map, Flash/RAM placement, startup environment, linker layout, or device-specific image requirements. A platform profile is distinct from a target profile: many SoCs may share the same CPU/ISA target profile.

## Target Code Generator

The target-specific Spec2Exec component that maps verified SpecIR semantics to target assembly. Depending on the supported subset it may own instruction selection, legalization, register/value placement, ABI handling, stack/control-flow rules, and assembly emission.

It does not own instruction binary encoding, object-file serialization, relocation processing, or linking unless a future architecture decision explicitly changes that boundary.

## Assembler

An external target tool that parses target assembly, encodes instructions, processes assembly directives, creates relocation records, and emits object files.

## Linker

An external target tool that resolves symbols, applies relocations, lays out sections/memory, and produces the linked executable or firmware image.

## Backend

A target-specific implementation of SpecIR-to-target code generation. In the primary native path, the backend ends at target assembly; object generation belongs to the external assembler/object emitter and final image construction belongs to the linker.

## Executable

The final runnable or loadable artifact, such as ELF, PE, Mach-O, firmware ELF/BIN, WebAssembly, or another target-specific form.

## Source of truth

The authoritative project artifact. In Spec2Exec, the goal is for accepted specification plus formalized semantics and verification evidence—not generated source or assembly—to become the principal source of truth.
