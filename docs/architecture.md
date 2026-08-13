# Architecture

## Reference pipeline

```text
┌──────────────────────────────────────┐
│ Human Intent                         │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Draft Specification                  │
│ - behavior                           │
│ - constraints                        │
│ - interfaces                         │
│ - timing / resources when applicable │
│ - safety / invariants when applicable│
│ - assumptions / unresolved semantics │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Semantic Resolution                  │
│ - AI/LLM                             │
│ - solvers / planners (optional)      │
│ - ambiguity exposure                 │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Resolved Specification               │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Human / Domain Specification Gate    │
│ - intent fidelity review             │
│ - assumptions / unresolved review    │
│ - acceptance authority               │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Accepted Specification               │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Semantic Synthesis                   │
│ UNTRUSTED candidate generation       │
└──────────────────┬───────────────────┘
                   ▼
┌──────────────────────────────────────┐
│ Candidate SpecIR                     │
│ machine-oriented formal contract     │
└──────────────────┬───────────────────┘
                   ▼
════════════ deterministic trust boundary ════════════
                   ▼
┌──────────────────────────────────────┐
│ Deterministic Verification           │
│ - schema / type / unit checks        │
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

## Correctness is layered

Spec2Exec distinguishes three different questions:

### Intent fidelity

Does the accepted specification represent what the human/domain authority actually intends?

This is primarily an acceptance and provenance problem. Downstream verification cannot generally prove it.

### Specification / SpecIR correctness

Is the formal representation well-formed, internally consistent, and compliant with the declared contracts?

This is the primary deterministic verification domain.

### Implementation conformance

Does lowering and compilation preserve the verified SpecIR semantics into the executable artifact?

This requires validated lowering, compiler evidence, tests, equivalence checks, or verified compilation as appropriate.

## Boundary 1: Intent → Draft Specification

Human intent may be incomplete and ambiguous. The system must preserve that fact instead of prematurely converting uncertainty into authoritative semantics.

## Boundary 2: Draft → Accepted Specification

Semantic resolution may propose missing structure, expose ambiguity, and derive candidates. Safety-critical or externally observable requirements must not be silently invented. Where intent fidelity matters, a human/domain authority accepts the resolved specification.

## Boundary 3: Accepted Specification → Candidate SpecIR

Semantic synthesis may be probabilistic and is treated as untrusted. The output must conform to a formal schema and explicit semantic rules before it can enter the checked domain.

## Boundary 4: Candidate SpecIR → Verified-for-declared-properties SpecIR

AI confidence is not evidence. Verification results must be deterministic and machine-checkable to the degree supported by the domain. A PASS only applies to named properties under named assumptions.

## Boundary 5: Verified SpecIR → Executable

Lowering should use mature compiler infrastructure wherever possible. Spec2Exec should not duplicate solved backend problems, but it must preserve traceability and distinguish validated transformations from merely trusted ones.

## Feedback loops

```text
semantic resolution → unresolved item → human/domain review

semantic synthesis → candidate SpecIR → verifier
       ▲                              │
       └──────── diagnostics ◄────────┘
```

## Uncertainty and evidence

The architecture must distinguish statuses such as declared, derived, assumed, unresolved, accepted, and verified. It must also distinguish evidence strength such as proven, checked, tested, measured, estimated, advisory, or unresolved.

The exact vocabulary remains subject to RFC refinement.

## Traceability

Every generated artifact should retain identifiers allowing runtime or compile-time findings to trace back toward:

```text
Executable behavior
    ↑
Lowered IR
    ↑
SpecIR node
    ↑
Accepted specification clause
    ↑
Requirement / decision / assumption
    ↑
Authority / provenance
```

## Fundamental limitation

Spec2Exec does not claim to solve the general intent problem or automatically prove specification completeness. Its architectural objective is to ensure that uncertainty, assumptions, and unverified semantics do not silently become indistinguishable from accepted and verified executable truth.
