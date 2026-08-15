# RFC 0006 — Semantic Preservation and Evidence Model

- **Status:** Accepted / Normative Evidence Model
- **Issue:** #54
- **Scope:** Canonical evidence vocabulary, preservation obligations, evidence records, trusted-computing-base disclosure, and evidence/RFC lifecycle rules

## Purpose

Spec2Exec contains multiple transformations between accepted semantics and executable behavior. A PASS at one boundary does not automatically establish preservation across later boundaries, and an authority/governance state is not an evidence-strength label.

This RFC is the **normative owner of evidence classes and preservation-boundary vocabulary**. Target-specific RFCs may refine a generic boundary, but they must not redefine the evidence vocabulary incompatibly or collapse distinct boundaries into one PASS.

## Core rule

Every trust claim must identify, at minimum:

```text
claim id
subject
property
status / evidence class
scope
method / producer
assumptions
trusted computing base, when applicable
source revision
traceability
subject / artifact bindings
```

A summary such as:

```text
VERIFIED = true
```

is insufficient unless it is merely a projection of machine-readable property claims underneath it.

## Typed namespaces

Evidence strength is one namespace among several. Other RFCs own other typed state machines.

Examples:

```text
SemanticResolutionState.UNRESOLVED
AuthorityValidity.AUTHORIZED
AcceptanceState.ACCEPTED
EvidenceStatus.UNRESOLVED
```

The same lexical token may appear in more than one typed namespace. Code, schemas, documentation, and evidence artifacts must make the owning field/type explicit.

In particular:

```text
resolution_state = UNRESOLVED
```

must never be interpreted as the same state machine as:

```text
evidence_status = UNRESOLVED
```

RFC 0011 owns semantic-authority state. This RFC owns evidence strength.

## Canonical evidence vocabulary

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

These labels are **not a total ordering**. A policy must not infer that one label automatically dominates another unless a policy explicitly defines an acceptable evidence profile for the property in question.

### PROVEN

A formal or mathematically justified proof establishes the named property under explicit assumptions and a named proof model/toolchain.

`PROVEN` never means all properties of the subject are proven.

### CHECKED

A deterministic check establishes the named property for the exact bound subject and inputs.

Examples include schema checks, deterministic policy evaluation, hash/revision binding, type checks, and sound static analyses for their declared property.

### TESTED

Execution or experiment provides observations for a declared set of cases. It does not imply exhaustiveness or a general theorem.

### TESTED_EXHAUSTIVE

`TESTED_EXHAUSTIVE` may be used only when all of the following are mechanically established:

1. the declared execution domain is finite;
2. the domain exercised by the test harness is mechanically derived from, or hash/revision bound to, that declared domain;
3. every element of that declared domain is executed exactly as claimed, or equivalent complete enumeration is mechanically established;
4. the property/oracle is bound to an accepted and already represented contract or property;
5. there is an observable failure channel that prevents silent PASS when the property fails;
6. the case count or equivalent coverage measure is mechanically checked;
7. the evidence record identifies the harness/runtime/tool assumptions.

`TESTED_EXHAUSTIVE` is still execution evidence. It does **not** become `PROVEN`, and it does not by itself establish compiler/transformation correctness outside the observed property.

### MEASURED

A physical or runtime quantity is observed with an identified measurement method, instrument/tool, configuration, and uncertainty where relevant.

### ESTIMATED

A value is inferred or approximated from a model, calculation, heuristic, or incomplete observation. The estimation method and assumptions must be named.

### HUMAN-DECLARED

A person or governance process has declared a fact, role, decision, or interpretation, but the system does not claim stronger authentication or deterministic proof of that declaration.

### HUMAN-ACCEPTED

A human/domain authority has explicitly accepted a subject or decision under the represented workflow. This label describes acceptance evidence; it does not make the accepted semantics formally correct.

### TRUSTED

The named component or assumption is part of the Trusted Computing Base for the claim. Its correctness is relied upon rather than established by the current Spec2Exec evidence.

### ASSUMED

The claim depends on an assumption that has not been established by the current evidence chain.

### ADVISORY

The information is guidance, recommendation, heuristic output, or non-binding analysis. It must not be promoted to an authoritative or verified claim merely by being present.

### UNRESOLVED

The evidence chain does not currently establish the property. This evidence status does not by itself define the semantic-resolution state of the underlying specification.

## Extension rule

Downstream RFCs and implementations must use the canonical vocabulary above unless an explicit RFC amendment extends it.

A target-specific RFC may define a **profile or structured qualifier** without creating a new evidence class. For example:

```text
status: TESTED
profile: runtime-sensitivity
```

or:

```text
status: CHECKED
method: deterministic-authority-policy-evaluation
```

New class names that change evidence meaning require an RFC-level extension to this vocabulary.

## Preservation obligations

The generic trust chain is:

```text
Accepted Specification
        ↓  P1
Candidate SpecIR
        ↓  P2
Verified-for-declared-properties SpecIR
        ↓  P3
Target / Lowered Artifact
        ↓  downstream realization boundaries
Executable / Firmware
        ↓
Runtime / Hardware Observation
```

### P1 — Accepted Specification → SpecIR

Question:

> Does the candidate SpecIR represent the accepted specification for the properties being mapped?

Evidence may include requirement identifiers, deterministic field/node linkage, traceability, human/domain acceptance, or formal equivalence when the source specification is formal enough.

P1 does not establish general human-intent fidelity.

### P2 — SpecIR property verification

Question:

> Which declared properties of the SpecIR have actually been checked or proven?

Examples include schema validity, type consistency, range containment, absence of bounded arithmetic overflow, state invariants, units, resource bounds, and timing properties where supported.

A P2 PASS applies only to named properties under named assumptions.

### P3 — Verified SpecIR → Target Artifact

Question:

> Does target realization preserve the accepted SpecIR semantics relevant to the generated target artifact?

For the native-primary architecture, RFC 0009 refines P3 as:

```text
P3   Verified SpecIR → Target Assembly / target artifact
```

Possible evidence includes deterministic lowering tests, translation validation, equivalence checking, proof-producing transformations, or verified lowering passes.

A POC may legitimately classify P3 as `TESTED` while formal preservation remains unproven, provided that limitation is explicit.

## Native downstream refinement

For native target realization, the canonical refinement is:

```text
P3   Verified SpecIR → Target Assembly / target artifact
P4-A Target Assembly → Generated Object
P4-H Runtime Harness Assembly → Harness Object
P4-L Objects + Linker Inputs → Linked Executable
P4-R Linked Executable → Runtime Observation
```

The boundaries have different subjects and Trusted Computing Bases and therefore must not be collapsed.

Typical POC treatment may be:

```text
P3    TESTED or stronger if independently justified
P4-A  TRUSTED external assembler
P4-H  TRUSTED validation-harness assembler path
P4-L  TRUSTED linker / linker-script path
P4-R  TESTED or TESTED_EXHAUSTIVE for the declared runtime property
```

These are examples, not automatic classifications. Every actual claim must still carry its own subject, method, assumptions, and bindings.

### P4-R.sensitivity

Runtime-sensitivity evidence is a **diagnostic validation profile**, not a preservation proof.

Known-bad or trapping controls can demonstrate that the runtime oracle/failure channel reacts to deliberate defects:

```text
Known-bad target mutation
        ↓
Build / execute
        ↓
Observable expected failure
```

This evidence may be recorded as `TESTED` with a sensitivity profile. It does not discharge P3 and must remain separate from the normal P4-R accepted-contract observation.

## Realization is not assurance

Target realization produces artifacts. Preservation evidence justifies claims about those artifacts.

Therefore:

```text
Target Code Generation / Assembly / Link / Load / Execute
        = Realization activities

P3 / P4-* evidence about preservation or observation
        = Assurance evidence
```

An activity does not become an assurance layer merely because evidence accompanies it.

## Evidence record

The normative logical evidence record supports at least:

```text
claim_id
subject
property
status
scope
method
producer
assumptions
trusted_computing_base
source_revision
trace
subject_binding / artifact_bindings
notes
```

Additional method-specific fields are permitted when they do not redefine the canonical status.

Example:

```text
claim_id: P2.no_signed_overflow_ub
subject: safe_add_sub SpecIR
property: no signed overflow in declared domain
status: CHECKED
method: sound interval analysis
producer: poc1c-target-neutral-verifier
source_revision: <git revision>
subject_binding:
  specification_sha256: ...
  specir_sha256: ...
```

## Evidence profiles instead of scalar ranking

Policies may require an acceptable evidence profile such as:

```text
allowed_statuses:
  - CHECKED
required_method_class:
  - deterministic-static-analysis
required_subject_binding:
  - specification_sha256
  - specir_sha256
```

This is preferred to expressions such as:

```text
status >= CHECKED
```

because the canonical classes are not a universal scalar ladder.

RFC 0011 constraint policies should therefore reference an acceptable evidence profile rather than invent a new authority-specific evidence scale.

## Trusted Computing Base

Every proof of concept and every material trust claim must identify the components relied upon but not established by that claim.

Examples may include:

- Python/runtime executing the verifier;
- verifier implementation;
- solver or proof checker;
- target code generator;
- assembler;
- linker and linker script;
- operating system / loader;
- emulator / machine model;
- physical hardware;
- authority-anchor declaration/protection mechanism where an authority claim depends on it.

Naming a TCB component is an honesty boundary. It does not allege that the component is faulty, nor does it mean its correctness was proven.

## Relationship to semantic authority

RFC 0011 owns semantic-authority concepts such as:

```text
resolution_state
authority_validity
acceptance_state
applicability
attribution_assurance
```

These are not evidence classes.

Examples:

```text
authority_validity = AUTHORIZED
attribution_assurance = unauthenticated repository declaration
evidence_status = HUMAN-DECLARED
```

is a coherent record and must not be rewritten as `PROVEN` or `CHECKED` merely because deterministic policy evaluation later confirms that the record matches the declared policy.

A deterministic policy evaluation itself may be `CHECKED`; the authority root it relies upon remains declared/trusted according to its own evidence.

## RFC lifecycle and normative dependencies

Spec2Exec RFCs use the following lifecycle states:

```text
Draft
Accepted
Superseded
Deprecated
```

### Draft

A proposal under review. It may guide experiments but is not a stable normative dependency for an Accepted RFC.

### Accepted

A normative architecture decision. Changes that alter its semantics require an Issue and review appropriate to the change.

### Superseded

A historical RFC whose normative responsibility has moved to another Accepted RFC. It remains useful for design history but must identify the replacement.

### Deprecated

A still-recognized mechanism that should not be used for new work. Deprecation must identify migration or replacement guidance.

### Dependency rule

An Accepted RFC must not silently depend on a Draft RFC for a normative guarantee.

If an Accepted RFC references a Draft RFC, one of the following must be explicit:

1. the reference is informative only; or
2. the Accepted RFC remains self-sufficient for its normative guarantee; or
3. promotion/closure is explicitly blocked until the Draft dependency is accepted or the dependency is otherwise resolved.

This rule permits architecture work to proceed in stages without representing draft semantics as settled evidence.

## Relationship to RFC 0009 and RFC 0010

- RFC 0009 owns native target-realization architecture and refines the generic P3/P4 boundaries without redefining evidence classes.
- RFC 0010 owns the top-level trust-chain thesis and distinguishes Realization activities from Assurance/Preservation Evidence.
- RFC 0011 owns semantic-authority states and consumes the canonical evidence vocabulary from this RFC.

## #54 closure note

Issue #54 reconciled the following architecture drift:

- RFC 0006 and RFC 0009 now share compatible P3/P4-A/P4-H/P4-L/P4-R boundaries;
- `TESTED_EXHAUSTIVE` is normatively defined;
- one canonical evidence vocabulary and extension rule exist;
- typed state namespaces separate RFC 0011 semantic-authority state from evidence strength;
- RFC 0005 no longer owns the mixed authority/evidence state machine and no longer mandates C/LLVM as the primary realization path;
- RFC lifecycle and Draft/Accepted dependency rules are explicit;
- RFC 0010 separates Realization from Assurance/Preservation Evidence;
- RFC 0011 uses RFC 0006 evidence profiles rather than inventing authority-specific evidence classes.

No executable behavior was changed by #54. Therefore #54 required architecture/document consistency review, not a new executable CI baseline.

## No collapsed PASS

The following equivalences are forbidden:

```text
TESTED            != PROVEN
TESTED_EXHAUSTIVE != PROVEN
TRUSTED           != VERIFIED
ASSUMED           != CHECKED
MEASURED          != PROVEN
AUTHORIZED        != evidence status
ACCEPTED          != VERIFIED
```

A trust claim is only as strong as its exact subject, property, method, evidence status, assumptions, TCB, and artifact bindings.

## Research objective

The research question is:

> Can Spec2Exec make semantic-preservation obligations and evidence explicit enough that users can distinguish what is proven, checked, tested, exhaustively observed, measured, estimated, declared, trusted, assumed, advisory, or unresolved at every relevant boundary?

This RFC is normative infrastructure for that question rather than a claim that every boundary is already formally verified.
