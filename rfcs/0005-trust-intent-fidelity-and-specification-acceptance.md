# RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance

- **Status:** Superseded / Historical for authority mechanics
- **Superseded by:** RFC 0011 — Semantic Authority, Delegation, and Default Policy
- **Scope retained:** Intent-fidelity limitation and historical rationale for separating human/domain intent from accepted semantics

## Historical purpose

This RFC established a core Spec2Exec limitation:

> Correct implementation of a formal specification does not prove that the specification expresses the right human or domain intent.

That limitation remains valid.

A pipeline may be internally consistent and still produce the wrong behavior if accepted semantics are wrong:

```text
Human/domain intent: shut down motor above 90 degC
        ↓
Incorrect specification: shut down above 120 degC
        ↓
Formally consistent SpecIR
        ↓
Correct target realization
        ↓
Executable for the wrong requirement
```

Downstream verification does not repair an intent/specification mismatch.

## Normative ownership after supersession

The original RFC mixed semantic knowledge, derivation, acceptance, and verification concepts. Those mechanics are no longer normative here.

Current ownership is:

```text
RFC 0011
    semantic obligations
    resolution_state
    authority_validity
    acceptance_state
    applicability
    AuthorityAnchors / Authority TCB
    delegated authority
    executable semantic closure
    deterministic authority gate

RFC 0006
    canonical evidence classes
    typed evidence namespace
    preservation boundaries
    evidence profiles
    RFC lifecycle/dependency rules

RFC 0009
    native-primary target realization
```

The historical single-axis list:

```text
KNOWN
ASSUMED
DERIVED
UNRESOLVED
ACCEPTED
VERIFIED
```

is explicitly **non-normative** because it mixed multiple independent state machines.

## Intent-fidelity boundary retained

Even a complete RFC 0011 authority chain cannot prove that declared trust anchors represent the ultimately correct human/domain intent.

Spec2Exec therefore preserves this boundary:

```text
Human / Domain Intent
        ↓
Declared Authority TCB
        ↓
Authorized / Accepted Semantics
        ↓
Deterministic Verification
        ↓
Target Realization
```

The Authority TCB is declared/trusted at the project boundary. It is not recursively proven by Spec2Exec.

## Trust principle retained

Semantic synthesis is untrusted by default.

AI, search, heuristics, planners, solvers, and other synthesis mechanisms may propose candidate semantics. Proposal quality does not create semantic authority.

RFC 0011 defines how candidate semantics become authorized/accepted. RFC 0006 defines how claims about that process are evidenced.

## Realization-path correction

The historical Phase-0 sketch that mandated:

```text
Lowering
  ↓
C or LLVM IR
  ↓
Existing compiler backend
```

is superseded.

RFC 0009 defines the current native-primary path:

```text
Verified SpecIR
        ↓
Target Code Generation
        ↓
Target Assembly
        ↓
Assembler
        ↓
Object
        ↓
Linker
        ↓
Executable / Firmware
```

C and LLVM remain optional reference/comparison paths.

## Non-goals retained

Spec2Exec does not claim to:

- read a person's mind;
- automatically prove general specification completeness;
- eliminate human/domain responsibility for authority roots;
- treat verifier success as proof of intent fidelity;
- eliminate all assumptions or uncertainty;
- make untrusted synthesis authoritative by capability alone.

## Historical research question

The original research question remains useful:

> Can uncertainty, provenance, semantic authority, deterministic verification, and implementation conformance be represented explicitly enough that unverified or unauthorized semantics do not silently become executable truth?

RFC 0011 and RFC 0006 now provide the normative architecture for answering it.
