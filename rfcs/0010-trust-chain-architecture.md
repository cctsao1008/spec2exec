# RFC 0010 — Trust-Chain Architecture for AI-Generated Software

- **Status:** Accepted / Project Thesis
- **Scope:** Top-level trust architecture, semantic authority, evidence, deterministic verification, executable realization, and AI synthesis boundaries

## Thesis

Spec2Exec is not primarily an AI coding tool and is not defined by any particular synthesis model.

Its long-term purpose is to provide **trust infrastructure for software whose implementation may be generated, transformed, optimized, or replaced by systems that are not themselves semantic authorities**.

Public architecture thesis:

> **AI proposes. Humans and delegated authority mechanisms authorize semantics. Deterministic systems verify. Evidence justifies trust. Target backends realize accepted semantics.**

Normative form:

> Probabilistic or heuristic systems may propose semantics, but they do not possess semantic authority by default. Accepted semantics cross an explicit authority boundary rooted in declared trust anchors. Deterministic systems establish reproducible claims where such claims are possible. Evidence justifies those claims, and target backends realize accepted semantics as executable behavior.

## Motivation

As software synthesis becomes cheaper, implementation generation is expected to become less scarce than establishing why a particular executable should be trusted.

The central question is therefore:

> **Why should a user trust this exact executable, under these exact assumptions, as an implementation of the semantics that were actually authorized?**

This changes Spec2Exec from a generator-centric architecture into a trust-chain architecture.

## Capability chain

The project is organized around six dependent capabilities:

```text
#1 Trust Architecture
        ↓
#2 Specification / Semantic Authority Model
        ↓
#3 Evidence Architecture
        ↓
#4 Deterministic Verification
        ↓
#5 Target Executable Realization
        ↓
#6 AI Synthesis Quality
```

These are not six interchangeable features.

- **#1–#3 define the trust model and its evidence semantics.**
- **#4 provides deterministic assurance over named properties.**
- **#5 realizes accepted semantics on concrete targets and is accompanied by preservation/observation evidence, but realization itself is not an assurance activity.**
- **#6 is replaceable upstream intelligence. It may improve productivity without becoming authority by capability alone.**

## Layer model

The architecture distinguishes trust, assurance, realization, and intelligence:

```text
                  TRUST LAYER
        #1 Trust Architecture
        #2 Semantic Authority Model
        #3 Evidence Architecture

                ASSURANCE LAYER
        #4 Deterministic Verification
        Preservation / observation evidence
        for realization boundaries

               REALIZATION LAYER
        #5 Target Code Generation
        Assembler / Object / Linker
        Loader / Runtime / Hardware

              INTELLIGENCE LAYER
        #6 AI / search / heuristic synthesis
```

The previous wording that placed **Portable Executable Realization itself inside the Assurance Layer** is superseded by this model. Realization produces artifacts. Assurance produces or evaluates evidence about properties of those artifacts.

## Runtime flow

Representative flow:

```text
Human / Domain / Governance Sources
          │
          ▼
   Candidate Semantics  ◄──── AI / search / heuristics / synthesis
          │
          ▼
Extraction / Interpretation
          │
          ▼
Candidate Semantic Obligations
          │
          ▼
Authority Resolution / Evaluation
          │
          ▼
Deterministic Semantic Authority Gate
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
      Target Realization
          │
          ▼
     Executable / Firmware
          │
          ▼
 Runtime / Emulator / Hardware Observation
```

Trust Architecture and Evidence Architecture span the whole flow rather than appearing as one serial stage.

## Semantic authority

The core distinction is between **proposing semantics** and **authorizing semantics**.

Plausibility is not authority.

Example:

```text
Requirement:
    stop the motor when temperature is too high

Potential semantic obligations:
    threshold
    comparison operator
    sensor-failure behavior
    reaction latency
    restart policy
```

A model may propose values for all of these. A proposal may become accepted executable semantics only through an applicable authority basis.

RFC 0011 is the normative owner of the semantic-authority mechanics, including:

- semantic obligations;
- AuthorityAnchors / Authority TCB;
- delegated authority policies;
- grant kinds;
- executable semantic closure;
- authority-relevant classifications;
- conflict handling;
- attribution assurance;
- immutable acceptance and current validity;
- deterministic fail-closed authority gating.

### Semantic-authority invariant

> **No unresolved, unauthorized, invalid, or silently omitted authority-relevant semantic obligation may cross the accepted-specification boundary and become executable behavior.**

Authority does not recursively prove itself. Authority chains terminate at declared trust anchors, and the anchor/declaration protection mechanism is part of the Authority TCB.

## Trust architecture

Trust Architecture answers:

> **What exactly is being trusted, why, by whom, under what assumptions, and at which boundary?**

The system distinguishes responsibility among components such as:

```text
Human / domain / governance authority
Authority-anchor declaration mechanism
AI / synthesis engine
Deterministic authority evaluator / gate
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
- trusting an assembler does not mean assembler correctness was proven by Spec2Exec;
- a `CHECKED` policy evaluation does not prove that the declared AuthorityAnchor is intrinsically correct.

## Evidence architecture

Trust claims are property-oriented and evidence-bearing.

A mature claim should identify at least:

```text
Claim
├── Subject
├── Property
├── Status
├── Scope
├── Method / Producer
├── Assumptions
├── Trusted Computing Base
├── Source Revision
├── Artifact / Subject Bindings
├── Traceability
└── Cross-validation, when applicable
```

The downstream chain may bind:

```text
Accepted Semantic / Acceptance Record
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

with separate evidence at each boundary.

### Canonical evidence vocabulary

RFC 0006 is the normative owner of evidence classes and extension rules.

The canonical vocabulary is:

```text
PROVEN
CHECKED
TESTED
TESTED_EXHAUSTIVE
MEASURED
ESTIMATED
HUMAN-DECLARED
HUMAN-ACCEPTED
TRUSTED
ASSUMED
ADVISORY
UNRESOLVED
```

These classes are not a universal scalar ranking.

Forbidden equivalences include:

```text
TESTED            != PROVEN
TESTED_EXHAUSTIVE != PROVEN
TRUSTED           != VERIFIED
ASSUMED           != CHECKED
MEASURED          != PROVEN
AUTHORIZED        != evidence status
ACCEPTED          != VERIFIED
```

`TESTED_EXHAUSTIVE` is valid only under RFC 0006's finite-domain, mechanically bound, fully enumerated, observable-failure requirements.

## Typed state separation

Semantic/authority state and evidence strength are separate namespaces.

Examples:

```text
resolution_state   = UNRESOLVED
```

and:

```text
evidence_status    = UNRESOLVED
```

may coexist because the owning types differ. Implementations must not collapse them into one untyped state machine.

Likewise:

```text
authority_validity = AUTHORIZED
```

is a governance state, not an evidence class.

## Deterministic verification

Deterministic verification prevents the trust architecture from becoming governance documentation without technical force.

The separation is:

```text
Probabilistic / heuristic proposal systems
        ↓
Semantic Authority Boundary
        ↓
Accepted Semantics
        ↓
Deterministic Verification Core
```

A deterministic verifier may establish:

> Given these accepted semantics, exact subject bindings, and assumptions, property X holds under method Y.

That statement is reproducible and evidence-bearing. It does not establish every other property of the artifact.

Methods may include schema checks, abstract interpretation, SMT solving, model checking, translation validation, proof-producing transformations, exhaustive execution, or other deterministic methods appropriate to the claim.

## Target executable realization

Verification of an abstract model is not sufficient to establish what a CPU executes.

The realization chain is:

```text
Accepted Specification
        ↓
Verified SpecIR
        ↓
Target Code Generation
        ↓
Target Assembly
        ↓
Object / Link / Executable / Firmware
        ↓
Runtime / Physical Execution
```

Target portability means **semantic portability**: the same accepted semantics are realized across valid target configurations with target-specific evidence and TCB assumptions.

RFC 0009 owns the native-primary realization architecture and the distinction between Target Configuration and Validation Binding.

### Preservation boundaries

RFC 0006 owns the generic and refined evidence vocabulary. RFC 0009 refines the native path as:

```text
P3   Verified SpecIR → Target Assembly
P4-A Target Assembly → Generated Object
P4-H Runtime Harness Assembly → Harness Object
P4-L Objects + Linker Inputs → Linked Executable
P4-R Linked Executable → Runtime Observation
```

Sensitivity experiments are diagnostic evidence and remain separate from semantic-preservation proof.

## AI synthesis quality

AI synthesis quality belongs to the Intelligence Layer and is intentionally replaceable.

Possible synthesis engines include language models, search systems, planners, heuristics, domain-specific models, and future systems.

The trust architecture must remain valid if:

- one model is replaced by another;
- synthesis quality improves or regresses;
- multiple models disagree;
- no AI is used for an artifact.

A weak synthesis engine should increase rejection, unresolved semantics, or human correction. It must not weaken the authority boundary.

Candidate trust-oriented metrics include:

```text
ambiguity detection recall
conflict detection recall
unauthorized-assumption rate
unsafe-resolution rate
unsupported-assumption rate
traceability completeness
first-pass deterministic-verification rate
human correction distance
human intervention rate
unresolved semantic-obligation rate
```

## Long-term invariants

Unless superseded by an explicit Accepted RFC:

1. **AI is not semantic authority by default.**
2. **No unresolved, unauthorized, or silently omitted authority-relevant semantic obligation becomes executable behavior.**
3. **Accepted semantics are the authoritative downstream source for verification and realization.**
4. **Claims presented as deterministic must be reproducible by deterministic methods.**
5. **Every material trust claim identifies subject, property, evidence status, scope, method/producer, assumptions, and trust boundary.**
6. **Evidence binds to exact subjects, artifacts, and revisions.**
7. **Evidence-strength labels are typed and not interchangeable.**
8. **Runtime agreement does not automatically prove compilation/transformation correctness.**
9. **Target portability means semantic portability, not merely source portability.**
10. **AI synthesis engines remain replaceable outside the trusted semantic core unless explicit delegated authority applies.**
11. **Realization activities and assurance evidence remain distinct even when they are produced in one pipeline run.**

## RFC lifecycle

RFC lifecycle and normative dependency rules are defined by RFC 0006 and contribution guidance.

In particular, an Accepted RFC must not silently depend on a Draft RFC for a normative guarantee. A Draft dependency must be informative, self-contained by the Accepted RFC, or explicitly block promotion/closure until resolved.

## Relationship to existing RFCs

- **RFC 0005** preserves the intent-fidelity limitation and delegates typed authority mechanics to RFC 0011.
- **RFC 0006** owns evidence classes, preservation boundaries, typed evidence namespace, and RFC lifecycle/dependency rules.
- **RFC 0009** owns native target realization.
- **RFC 0011** owns semantic-authority state and authority gating.

## Non-goals

Spec2Exec does not claim that it can:

- automatically determine human intent in the general case;
- eliminate all assumptions or uncertainty;
- prove every compiler, assembler, linker, OS, emulator, or hardware component correct;
- make AI synthesis trustworthy or authoritative by declaration alone;
- replace domain authority or certification processes;
- guarantee formal proof for every property;
- require one specific AI model or synthesis engine.

## Strategic consequence

Spec2Exec may succeed at several levels:

```text
Small outcome
    specification → firmware / executable research generator

Medium outcome
    verified/checked code generation + auditable evidence
    for embedded / safety-critical software

Large outcome
    trust infrastructure for AI-generated software
```

Implementation may become disposable. **Accepted semantics and verifiable evidence must not.**
