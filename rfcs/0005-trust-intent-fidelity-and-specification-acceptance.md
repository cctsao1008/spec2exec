# RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance

- **Status:** Draft / Transitional
- **Scope:** Intent fidelity and the boundary between human/domain intent and accepted semantics
- **Normative ownership note:** RFC 0011 owns typed semantic-authority state once accepted; RFC 0006 owns evidence classes; RFC 0009 owns the native-primary realization path

## Problem

Formal verification can establish that an artifact satisfies a formal specification, but it cannot generally establish that the formal specification represents what a human or domain authority actually intended.

A pipeline may be internally consistent and still produce the wrong behavior if the accepted semantics are wrong:

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

## Decision

Spec2Exec separates:

```text
Intent fidelity
Semantic authority / acceptance
Specification-to-SpecIR correctness
Implementation conformance
```

No single PASS state may imply all of these unless separate evidence exists for each applicable claim.

## Architecture boundary

The intent/authority boundary is conceptually:

```text
Human / Domain Sources
        ↓
Draft / Candidate Semantics
        ↓
Ambiguity / Conflict / Missing-Semantics Detection
        ↓
Authority Resolution
        ↓
Accepted Specification
        ↓
Semantic Synthesis (untrusted)
        ↓
Candidate SpecIR
        ↓
Deterministic Verification
        ↓
Verified SpecIR
        ↓
Target Realization
```

RFC 0011 refines the authority-resolution portion with AuthorityAnchors, policies, semantic obligations, executable semantic closure, delegated defaults, and a deterministic fail-closed authority gate.

## Human / domain authority

A human or domain authority may be one authority source, but Spec2Exec does not require every semantic obligation to be manually approved one-by-one.

Authority may originate from declared trust anchors and be delegated through explicit, scoped policy. Examples include:

- an individual project owner for a POC;
- a system engineer for an embedded product;
- an approved contract or parent specification;
- a safety/governance authority;
- a standards/regulatory source selected by project governance;
- a formal workflow or delegated authority policy.

The important property is not that an authority source is human. The important property is that the authority basis, scope, revision, delegation, and acceptance remain explicit and auditable.

## Ambiguity and uncertainty

This RFC no longer defines one mixed state list such as:

```text
KNOWN
ASSUMED
DERIVED
UNRESOLVED
ACCEPTED
VERIFIED
```

That older list combined knowledge state, derivation, semantic resolution, acceptance, and evidence strength on one axis and is therefore **not normative**.

Typed ownership is now:

```text
RFC 0011:
    resolution_state
    authority_validity
    acceptance_state
    applicability

RFC 0006:
    evidence_status
```

A required semantic obligation that is unresolved, conflicting, unauthorized, or otherwise invalid for the selected build must fail closed before executable SpecIR synthesis according to RFC 0011.

## Provenance

Authority-relevant semantics should retain provenance sufficient to distinguish source material, extraction/interpretation, authority, and evidence.

Logical information includes:

```text
requirement / semantic-obligation id
source artifact
source revision / hash
source locator
extraction / interpretation record
authority binding / policy revision
acceptance record
current validity context
traceability to SpecIR and downstream artifacts
```

The objective is not administrative overhead. It is to prevent an AI-derived or tool-derived assumption from becoming indistinguishable from authorized semantics.

## Trust principle

**Semantic synthesis is untrusted by default.**

AI, search, heuristics, planners, solvers, and other synthesis mechanisms may propose candidate semantics. Proposal quality does not itself create semantic authority.

A deterministic checker may establish that a recorded authority exercise satisfies a declared policy, but that `CHECKED` evidence does not prove the authority root itself. RFC 0006 owns those evidence distinctions.

## Intent fidelity boundary

Even a complete RFC 0011 authority chain cannot prove that the declared trust anchors themselves represent the ultimately correct human/domain intent.

Spec2Exec therefore names the boundary honestly:

```text
Declared Authority TCB
        ↓
Authorized Semantics
        ↓
Deterministic Verification / Evidence
```

The Authority TCB is trusted/declared at the project boundary. It is not recursively proven by Spec2Exec.

## Realization path

The older Phase-0 sketch that mandated:

```text
Lowering
  ↓
C or LLVM IR
  ↓
Existing compiler backend
```

is no longer normative.

The current primary realization architecture is defined by RFC 0009:

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

C and LLVM remain optional reference/comparison paths rather than mandatory stages.

## Relationship to RFC 0011

RFC 0011 is the intended normative successor for semantic-authority and specification-acceptance mechanics.

Once RFC 0011 is Accepted, this RFC should be marked **Superseded / Historical** for those mechanics while remaining a useful statement of the intent-fidelity limitation:

> Correct implementation of accepted semantics does not prove that the accepted semantics were the right human/domain intent.

## Non-goals

Spec2Exec does not claim to:

- read a person's mind;
- automatically prove general specification completeness;
- eliminate human/domain responsibility for authority roots;
- treat verifier success as proof of intent fidelity;
- eliminate all assumptions or uncertainty;
- make untrusted synthesis authoritative by accuracy alone.

## Research objective

The research question remains:

> Can uncertainty, provenance, semantic authority, deterministic verification, and implementation conformance be represented explicitly enough that unverified or unauthorized semantics do not silently become executable truth?
