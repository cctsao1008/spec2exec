# RFC 0010 — Trust-Chain Architecture for AI-Generated Software

- **Status:** Accepted / Project Thesis
- **Scope:** Top-level trust architecture, semantic authority, evidence, verification, executable realization, and AI synthesis boundaries

## Thesis

Spec2Exec is not primarily an AI coding tool and is not defined by any particular synthesis model.

Its long-term purpose is to provide **trust infrastructure for software whose implementation may be generated, transformed, optimized, or replaced by systems that are not themselves semantic authorities**.

Public architecture thesis:

> **AI proposes. Humans authorize semantics. Deterministic systems verify. Evidence justifies trust. Portable backends execute.**

The normative form is more general:

> Probabilistic or heuristic systems may propose semantics, but they do not possess semantic authority by default. Accepted semantics cross an explicit authority boundary. Deterministic systems establish reproducible claims where such claims are possible. Evidence justifies those claims, and portable backends realize accepted semantics as executable behavior.

## Motivation

As software synthesis becomes cheaper, implementation generation is expected to become less scarce than establishing why a particular executable should be trusted.

The central Spec2Exec question is therefore not only:

> Can a system generate executable software from a specification?

It is also:

> **Why should a user trust this exact executable, under these exact assumptions, as an implementation of the semantics that were actually authorized?**

This changes the project from a generator-centric architecture into a trust-chain architecture.

## Value framework as a trust chain

The project is organized around six dependent capabilities rather than six parallel features:

```text
#1 Trust Architecture
        ↓
#2 Specification / Semantic Authority Model
        ↓
#3 Evidence Architecture
        ↓
#4 Deterministic Verification
        ↓
#5 Portable Executable Realization
   + Preservation Evidence
        ↓
#6 AI Synthesis Quality
```

The dependency is conceptual:

- **#1–#4 form the trusted core.**
- **#5 realizes accepted semantics on concrete execution targets and must preserve the trust chain.**
- **#6 is an upstream intelligence capability that may improve productivity and proposal quality, but does not gain semantic authority merely by being accurate or capable.**

AI quality affects productivity. It does not define authority.

## Layer model

The same capabilities can be grouped into three architectural layers:

```text
                 TRUST LAYER
        #1 Trust Architecture
        #2 Semantic Authority Model
        #3 Evidence Architecture

               ASSURANCE LAYER
        #4 Deterministic Verification
        #5 Portable Executable Realization
           + Preservation Evidence

             INTELLIGENCE LAYER
        #6 AI Synthesis Quality
```

The Intelligence Layer may execute early in the runtime workflow, but it remains outside the trusted semantic core unless an explicit domain policy grants authority to a particular source.

## Runtime flow

A representative runtime flow is:

```text
Human / Domain Sources
          │
          ▼
   Candidate Semantics  ◄──── AI / search / heuristics / synthesis
          │
          ▼
┌──────────────────────────────┐
│   Semantic Authority Gate    │
│ ambiguity / conflict /       │
│ provenance / acceptance      │
└──────────────┬───────────────┘
               │
               ▼
      Accepted Specification
               │
               ▼
      Semantic Synthesis
               │
               ▼
         Candidate SpecIR
               │
               ▼
    Deterministic Verification
               │
               ▼
         Verified SpecIR
               │
               ▼
 Portable Target Realization
               │
               ▼
     Executable / Firmware
               │
               ▼
 Runtime / Emulator / Hardware Observation
```

Trust Architecture and Evidence Architecture span the entire flow rather than appearing as one serial stage.

## Semantic authority

The most important distinction in the architecture is between **proposing semantics** and **authorizing semantics**.

A synthesis system may infer a plausible interpretation, but plausibility is not authority.

For example:

```text
Requirement:
    stop the motor when temperature is too high

Unresolved semantics may include:
    threshold
    comparison operator
    sampling interval
    sensor-failure behavior
    debounce / filtering
    reaction latency
    restart policy
```

A model may propose values for all of these, but no proposal may silently become authoritative executable behavior.

### Authority boundary

The required flow is:

```text
Human intent / domain requirement
        ↓
Candidate interpretation
        ↓
ambiguity / conflict / missing-semantics detection
        ↓
Authority Resolution
        ↓
Accepted Semantics
```

The architecture must preserve the distinction between candidate, assumed, unresolved, derived, and accepted semantics.

### Authority sources

Human acceptance is the primary authority mechanism in current prototypes, but the architecture is not permanently restricted to a single human approval action.

Possible authority sources include:

- a human developer or system engineer;
- a safety or certification authority;
- a regulatory or standards requirement;
- an accepted parent specification;
- a certified domain model;
- an approved interface or system contract;
- a formal governance workflow.

The authority source, provenance, revision, and acceptance state must remain representable.

### Semantic-authority invariant

> **No unresolved or unauthorized semantic assumption may silently cross the authority boundary and become executable behavior.**

If a required semantic decision lacks authority, the preferred result is an explicit `UNRESOLVED` or blocked state rather than a plausible invented value.

RFC 0005 defines the intent-fidelity and specification-acceptance boundary in more detail.

## Trust architecture

Trust Architecture answers:

> **What exactly is being trusted, why, by whom, under what assumptions, and at which boundary?**

The system must distinguish responsibility among components such as:

```text
Human / domain authority
AI / synthesis engine
Deterministic verifier
Target code generator
Assembler
Linker
Runtime / loader
Emulator
Physical hardware
```

No downstream PASS may retroactively grant authority or proof to an upstream claim that was never established.

Examples:

- verifier success does not prove human intent fidelity;
- runtime agreement does not automatically prove code-generation preservation;
- emulator execution does not equal physical-hardware validation;
- trusting an assembler does not mean assembler correctness was proven by Spec2Exec.

## Evidence architecture

A correctness statement is not a sufficient trust artifact by itself.

Trust claims must be represented as evidence-bearing records or graphs that connect claims to exact subjects and their provenance.

A mature claim should be able to identify at least:

```text
Claim
├── Subject
├── Property
├── Status
├── Scope
├── Evidence
├── Method
├── Tool / Version
├── Assumptions
├── Trusted Computing Base
├── Source Revision
├── Artifact Bindings / Hashes
├── Traceability
└── Cross-validation, when applicable
```

This produces a machine-readable chain such as:

```text
Accepted Requirement Clause
        ↓
Accepted Specification Hash
        ↓
Verified SpecIR Hash
        ↓
Generated Assembly Hash
        ↓
Object Hash
        ↓
Executable Hash
        ↓
Runtime / Hardware Observation
```

with a separate evidence status at each transformation boundary.

### Evidence strength is not boolean

Spec2Exec must not collapse all assurance into:

```text
VERIFIED = true
```

Evidence classes remain property- and boundary-specific. RFC 0006 defines the general evidence model. Current implementations additionally use more specific statuses such as `TESTED_EXHAUSTIVE` where the executed domain is mechanically bounded and fully enumerated.

Typical distinctions include:

```text
PROVEN
CHECKED
TESTED
TESTED_EXHAUSTIVE
MEASURED
HUMAN-DECLARED
HUMAN-ACCEPTED
TRUSTED
ASSUMED
UNRESOLVED
```

The following equivalences are forbidden:

```text
TESTED  != PROVEN
TRUSTED != VERIFIED
ASSUMED != CHECKED
MEASURED != PROVEN
```

A trust claim is only as strong as its named evidence, scope, assumptions, and TCB.

## Deterministic verification

Deterministic verification prevents the Trust Layer from becoming governance documentation without technical force.

The separation is:

```text
Probabilistic / heuristic frontend
        ↓
Semantic Authority Boundary
        ↓
Accepted Semantics
        ↓
Deterministic Core
```

AI may answer:

> "This is probably what the specification means."

A deterministic verifier may answer:

> "Given these accepted semantics and assumptions, property X holds under method Y."

The second statement is repeatable and evidence-bearing; it does not depend on the verifier merely judging that the result looks reasonable.

Verification methods may include schema checks, abstract interpretation, SMT solving, model checking, translation validation, proof-producing transformations, exhaustive execution, or other deterministic methods appropriate to the property.

## Portable executable realization

Verification of an abstract model is not sufficient to establish what a CPU actually executes.

The realization chain is:

```text
Accepted Specification
        ↓
Verified SpecIR
        ↓
Target Semantics
        ↓
Target Assembly / Machine Representation
        ↓
Object / Executable / Firmware
        ↓
Runtime / Physical Execution
```

Portable executable generation is valuable when the **same accepted semantics** can be realized across multiple targets while preserving explicit target-specific evidence:

```text
                    same Verified SpecIR
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           RV32I       Armv8-M       x86_64
              │            │            │
              └────────────┼────────────┘
                           ▼
                 target-specific evidence
```

This is **semantic portability**, not merely source portability.

RFC 0009 defines the native target-code-generation boundary and the distinction between Target Configuration and Validation Binding.

## AI synthesis quality

AI synthesis quality belongs to the Intelligence Layer and is intentionally replaceable.

Possible synthesis engines include hosted or local language models, search systems, planners, heuristics, domain-specific models, and future systems not yet known.

The trust architecture must remain valid if:

- one model is replaced by another;
- synthesis quality improves dramatically;
- synthesis quality temporarily regresses;
- multiple models disagree;
- no AI is used for a particular artifact.

A weak synthesis engine should cause more rejection, unresolved semantics, or human correction. It must not weaken the authority boundary.

### Trust-oriented AI metrics

Spec2Exec should evaluate synthesis quality using metrics that reflect semantic discipline rather than only compilation or test-pass rate.

Candidate metrics include:

```text
ambiguity detection recall
conflict detection recall
unauthorized-assumption rate
unsupported-assumption rate
specification completeness
traceability completeness
first-pass deterministic-verification rate
human correction distance
human intervention rate
unresolved semantic-obligation rate
```

A model with a slightly lower first-pass completion rate may be preferable if it makes fewer unauthorized semantic assumptions and exposes ambiguity more reliably.

## Long-term invariants

The following are project-level invariants unless superseded by an explicit RFC:

1. **AI is not semantic authority by default.**
2. **No unresolved semantic assumption silently becomes executable behavior.**
3. **Accepted semantics are the authoritative truth source for downstream verification and realization.**
4. **Claims presented as deterministic must be reproducible by deterministic methods.**
5. **Every trust claim identifies its evidence, scope, assumptions, subject, producer/method, and trust boundary.**
6. **Evidence binds to exact subjects, artifacts, and revisions.**
7. **Evidence-strength labels are not interchangeable.** `TESTED` is not `PROVEN`; `TRUSTED` is not `VERIFIED`; `ASSUMED` is not `CHECKED`.
8. **Runtime agreement does not automatically prove compilation or transformation correctness.**
9. **Target portability means semantic portability, not merely source portability.**
10. **AI synthesis engines are replaceable components outside the trusted semantic core.**

## Relationship to existing RFCs

This RFC is a top-level synthesis of existing architecture decisions. It does not replace their detailed obligations.

- **RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance** defines the boundary between human/domain intent, ambiguity resolution, and accepted specification.
- **RFC 0006 — Semantic Preservation and Evidence Model** defines preservation obligations, evidence classes, and no-collapsed-PASS policy.
- **RFC 0009 — Native Target Code Generation** defines the native executable-generation boundary, Target Configuration, Validation Binding, and target-specific evidence boundaries.

Where this RFC is intentionally more general than RFC 0005, `Authority Resolution` includes human/domain acceptance as the current primary mechanism while allowing authoritative standards, parent specifications, contracts, and approved governance sources to be represented explicitly.

## Non-goals

This RFC does not claim that Spec2Exec can:

- automatically determine human intent in the general case;
- eliminate all assumptions or uncertainty;
- prove every compiler, assembler, linker, operating system, emulator, or hardware component correct;
- make AI synthesis trustworthy by declaration;
- replace domain authority or certification processes;
- guarantee formal proof for every property;
- require one specific AI model or synthesis engine.

## Strategic consequence

Spec2Exec may succeed at several levels:

```text
Small outcome
    specification → firmware / executable research generator

Medium outcome
    verified code generation + auditable evidence
    for embedded / safety-critical software

Large outcome
    trust infrastructure for AI-generated software
```

The large outcome is the strategic direction because it remains valuable even as implementation generation becomes inexpensive and synthesis engines become interchangeable.

Implementation may become disposable. **Accepted semantics and verifiable evidence must not.**
