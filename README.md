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

## 💡 Why this matters

Traditional software development already has ambiguity, unstated assumptions, requirement gaps, and authority conflicts. AI does not create these problems.

What changes is the speed and scale at which interpretation becomes implementation:

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

## 🔐 Four trust shifts

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

These are research propositions and architecture boundaries, not claims that Spec2Exec has solved them generally.

## 🧭 Research hypothesis

> **Spec2Exec investigates whether semantic-obligation discovery, explicit semantic authority, deterministic verification, artifact binding, and lifecycle-aware evidence can form a defensible trust architecture for AI-generated executable systems.**

A stronger version is deliberately open to falsification:

> **As implementation becomes increasingly synthesizable, semantic authority may become a first-class engineering concern.**

Spec2Exec does not assume that its mechanisms are universally necessary, sufficient, or superior to conventional requirements engineering, review, testing, formal methods, assurance cases, provenance systems, or lighter-weight structured workflows.

## AI-facing engineering substrate

Spec2Exec is designed primarily as a **machine-operable engineering substrate for AI-assisted or AI-driven implementation workflows**.

Humans remain responsible for intent, policy, semantic authority, risk acceptance, and assurance review. AI agents may perform obligation discovery, semantic-resolution proposals, synthesis, transformation, optimization, and evidence production through the Spec2Exec trust architecture.

A useful long-term framing is:

> **Spec2Exec is an AI-facing software engineering substrate for turning authorized human intent into trustworthy executable behavior.**

This is an architectural hypothesis, not a claim that human-readable source languages are obsolete or that a bounded implementation demonstrates a fully AI-native software stack.

## The three questions

```text
1. Semantic Obligation Discovery
   What behavior-determining questions must be decided?

2. Semantic Resolution and Authority
   Were those questions resolved without invention,
   and who or what was authorized to decide them?

3. Executable Trust Chain
   What evidence shows that the accepted semantics
   reached this exact executable artifact?
```

This distinction matters because:

```text
implementation correctness
        !=
semantic correctness
        !=
semantic authority
```

A formally verified implementation can still faithfully implement a specification containing the wrong, incomplete, stale, or never-authorized semantics.

## 🧩 Architecture

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
Executable Semantic Closure
        ↓
Semantic Authority
        ↓
Accepted Specification
        ↓
Semantic Synthesis / SpecIR
        ↓
Deterministic Verification / Evidence
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

## 🔬 Evidence discipline

Spec2Exec deliberately avoids collapsing heterogeneous claims into one generic `PASS`.

```text
TESTED ≠ PROVEN
TESTED_EXHAUSTIVE ≠ PROVEN
TRUSTED ≠ VERIFIED
CHECKED ≠ AUTHORIZED
```

Evidence is property-specific and should identify its subject, scope, method, assumptions, trusted computing base, provenance, and artifact binding.

The accepted evidence vocabulary and preservation rules are defined in RFC 0006.

## Evidence boundary

Repository evidence is bounded research evidence. It can support claims about specific authority-gating, semantic representation, deterministic checking, executable realization, evidence composition, lifecycle invalidation, and semantic-obligation measurement experiments.

It does not by itself establish production qualification, certification, universal obligation completeness, universal dependency completeness, general formal proof, or comparative superiority over simpler workflows.

Exact revisions, CI runs, metrics, artifact hashes, benchmark results, and validation details belong in the corresponding research directories, validation documents, and Issues.

## ⚖️ Comparative assurance

Spec2Exec must justify whether its additional structure provides enough incremental assurance to warrant its authoring, review, training, and lifecycle cost.

> **Does Spec2Exec provide enough incremental assurance over simpler structured AI-assisted engineering workflows to justify that additional cost?**

A simpler workflow achieving comparable assurance at materially lower cost would weaken the necessity of the fuller Spec2Exec architecture.

## What Spec2Exec is not

Spec2Exec is not:

- an AI coding assistant or LLM wrapper;
- a system in which plausible AI output gains authority automatically;
- a requirements-management replacement;
- a compiler replacement;
- a claim that human-readable programming languages are obsolete;
- a general formal-verification system;
- a certification replacement;
- a claim that repository identity alone establishes real organizational authority;
- a certified safety-critical system;
- a claim that exhaustive finite-domain testing is formal proof;
- a claim that emulator execution is physical-hardware validation;
- a claim that every semantic obligation or lifecycle dependency can be discovered completely.

## 🧪 Research discipline

Spec2Exec follows three rules:

1. **Ask ambitious questions.**
2. **State evidence narrowly.**
3. **Design experiments that can weaken the thesis.**

A plausible architecture is not evidence.  
A passing implementation is not general validation.  
A useful mechanism is not necessarily worth its cost.

## Architecture references

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md)
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md)
- [RFC 0012 — Lifecycle-Aware Trust Graph](rfcs/0012-lifecycle-aware-trust-graph.md)
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md)

For roadmap, issue history, exact baselines, and research state, see [Issue #49](https://github.com/cctsao1008/spec2exec/issues/49).
