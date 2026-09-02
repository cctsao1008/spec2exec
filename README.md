# Spec2Exec

**Specification-to-Executable Architecture**  
**Trust infrastructure for AI-generated executable systems**

> **AI can correctly implement a decision that nobody ever authorized.**

Consider a simple requirement:

```text
Requirement:
Retry failed payment requests.

AI candidate:
Retry 5 times.

Question:
Who authorized 5?
```

**The question is not whether `5` is reasonable. The question is whether anyone had authority to choose it.**

The code can compile. The tests can pass. Five retries may even sound reasonable.

But if nobody or no authorized policy selected `5`, the implementation has silently converted a missing semantic decision into executable behavior.

**Spec2Exec explores how to prevent unstated, unresolved, or unauthorized semantic decisions from silently becoming software behavior — and how to bind the resulting trust claims to the exact artifact that runs.**

> **AI is making software implementation cheap. It is not making software trust cheap.**

## Why this matters

Traditional software development already has ambiguity, unstated assumptions, requirement gaps, and authority conflicts. AI increases the speed and scale at which interpretation becomes implementation:

```text
vague or incomplete intent
        ↓
AI-assisted interpretation / synthesis
        ↓
many behavior-determining decisions
        ↓
working implementation
        ↓
executable behavior
```

As implementation becomes increasingly synthesizable, the engineering bottleneck can move upstream: from producing behavior toward deciding, exposing, authorizing, verifying, and maintaining trust in the semantics that behavior realizes.

## Four trust shifts

```text
1. CORRECT IMPLEMENTATION ≠ AUTHORIZED SEMANTICS

   A system may faithfully implement a behavior
   that nobody had authority to choose.

2. KNOWN OBLIGATIONS ≠ COMPLETE OBLIGATIONS

   An authority gate cannot reject a semantic question
   that was never discovered in the first place.

3. DOWNSTREAM PASS ≠ UPSTREAM AUTHORITY

   Compilation, testing, or verification cannot
   retroactively authorize an earlier semantic decision.

4. UNCHANGED ARTIFACT ≠ CURRENT TRUST

   The same artifact bytes can lose current trust when
   assumptions, dependencies, policies, evidence, or
   governing context become stale or invalid.
```

## Research hypothesis

> **Spec2Exec investigates whether semantic-obligation discovery, explicit semantic authority, deterministic verification, artifact binding, and lifecycle-aware evidence can form a defensible trust architecture for AI-generated executable systems.**

As implementation becomes increasingly synthesizable, semantic authority may become a first-class engineering concern.

## AI-facing engineering substrate

Spec2Exec is designed primarily as a **machine-operable engineering substrate for AI-assisted or AI-driven implementation workflows**.

Humans and governance mechanisms define intent, policy, authority roots and delegation, risk acceptance, and assurance expectations. AI agents and tools may discover obligations, propose semantic resolutions, synthesize, transform, optimize, verify, and produce evidence through the Spec2Exec trust architecture.

Machine-to-machine handoff does not create authority. Agreement does not turn an unsupported semantic choice into an authorized one, and unresolved or conflicting semantics must not disappear merely because another agent or tool continues the workflow.

```text
AGREEMENT ≠ AUTHORITY
LOCAL PASS ≠ PRESERVED SEMANTICS
```

> **Spec2Exec is an AI-facing software engineering substrate for turning authorized human intent into trustworthy executable behavior.**

## The three questions

```text
1. Semantic Obligation Discovery
   What behavior-determining questions must be decided?

2. Semantic Resolution and Authority
   Were those questions resolved without invention,
   and who or what was authorized to decide them?

3. Executable Trust Chain
   What evidence shows that the accepted semantics
   reached this exact executable artifact,
   and whether that evidence remains applicable?
```

```text
implementation correctness
        !=
semantic correctness
        !=
semantic authority
```

A formally verified implementation can still faithfully implement a specification containing the wrong, incomplete, stale, or never-authorized semantics.

## Architecture

```text
Human / Domain / Governance Sources
        ↓
Intent / Requirements / Policy / Authority
        ↓
AI-assisted semantic processing
        ↓
Candidate Semantics
        ↓
Semantic Obligation Discovery
        ↓
Semantic Resolution / Conflict Exposure
        ↓
Conservative Executable Semantic Closure
        ↓
Authority Discovery / Evaluation
        ↓
Deterministic Semantic Authority Gate
        ↓
Accepted Specification
        ↓
Semantic Synthesis
        ↓
Candidate / Verified SpecIR
        ↓
Target Realization
        ↓
Executable / Firmware
        ↓
Runtime / Emulator / Hardware Observation

Across the chain:
Claim ↔ Evidence ↔ Artifact ↔ Tool ↔ Assumption ↔ Provenance
```

The project-level thesis is:

> **AI proposes. Humans and delegated authority mechanisms authorize semantics. Deterministic systems verify. Evidence justifies trust. Target backends realize accepted semantics.**

Capability, plausibility, convention, and low impact do not create semantic authority.

## Evidence discipline

Spec2Exec keeps evidence property-specific rather than collapsing heterogeneous claims into one generic `PASS`.

```text
TESTED ≠ PROVEN
TESTED_EXHAUSTIVE ≠ PROVEN
TRUSTED ≠ VERIFIED
CHECKED evidence ≠ semantic authority
```

Evidence identifies its subject, scope, method, assumptions, trusted computing base, provenance, and artifact binding.

The accepted evidence vocabulary and preservation rules are defined in RFC 0006.

## Architecture references

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md)
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md)
- [RFC 0012 — Lifecycle-Aware Trust Graph](rfcs/0012-lifecycle-aware-trust-graph.md)
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md)
