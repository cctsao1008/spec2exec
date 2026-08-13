# Architecture

## Reference pipeline

```text
┌──────────────────────────────────────┐
│ Human Intent                         │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Specification                        │
│ - behavior                           │
│ - constraints                        │
│ - interfaces                         │
│ - timing / resources when applicable │
│ - safety / invariants when applicable│
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Semantic Synthesis                   │
│ - AI/LLM                             │
│ - solvers / planners (optional)      │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ SpecIR                               │
│ machine-oriented formal contract     │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Deterministic Verification           │
│ - type / unit checks                 │
│ - invariants                         │
│ - range / resource checks            │
│ - control-flow / safety checks       │
│ - timing checks where feasible       │
└──────────────┬───────────────────────┘
               │ FAIL → diagnostics → synthesis loop
               ▼ PASS
┌──────────────────────────────────────┐
│ Lowering                             │
│ SpecIR → MLIR / LLVM IR / C          │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Conventional Compiler Infrastructure │
│ optimization / codegen / ABI / object│
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Executable Artifact                  │
│ ELF / firmware ELF / BIN / PE / etc. │
└──────────────────────────────────────┘
```

## Boundary 1: Intent → Specification

Natural language is allowed to be incomplete and ambiguous. Specification is not. The system must identify unresolved ambiguity rather than silently invent requirements.

## Boundary 2: Specification → SpecIR

Semantic synthesis may be probabilistic. The output must nevertheless conform to a formal schema and explicit semantic rules.

## Boundary 3: SpecIR → Verified SpecIR

This is the correctness boundary. AI confidence is not evidence. Verification results must be deterministic and machine-checkable to the degree supported by the domain.

## Boundary 4: Verified SpecIR → Executable

Lowering should use mature compiler infrastructure wherever possible. Spec2Exec should not duplicate solved backend problems.

## Feedback loop

```text
AI synthesis → SpecIR → verifier
     ▲                    │
     └──── diagnostics ◄──┘
```

The verifier provides structured failures. The synthesizer may revise the candidate, but only a passing verifier state can continue to lowering.

## Traceability

Every generated artifact should retain identifiers allowing a runtime or compile-time finding to trace back toward:

```text
Executable behavior
    ↑
Lowered IR
    ↑
SpecIR node
    ↑
Specification clause
    ↑
Requirement / intent source
```
