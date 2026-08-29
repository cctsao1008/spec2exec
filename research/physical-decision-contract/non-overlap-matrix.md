# PDC / Trust Continuity Non-Overlap Matrix v0.1

**Status:** Working research matrix  
**Normative status:** Non-normative  
**Issue:** #70

## Purpose

This matrix is designed to prevent the Physical Decision Contract / Trust Continuity research track from claiming novelty for responsibilities already covered by established approaches.

The comparison is intentionally hostile to the PDC hypothesis.

The question is not:

> Is PDC different in vocabulary?

It is:

> **Does PDC retain a non-trivial responsibility that is not already provided, with equivalent semantics and lower complexity, by established approaches or their straightforward composition?**

## Compared approaches

```text
1. Spec2Exec core
2. Runtime Assurance / Simplex
3. Safety Filters / Control Barrier Functions
4. Assume-Guarantee / Contract-Based CPS
5. Agent Authorization / Runtime Governance / Provenance
6. Proposed PDC / Trust Continuity
```

The entries below are research judgments, not claims of exhaustive literature coverage.

## Responsibility matrix

| Responsibility | Spec2Exec core | RTA / Simplex | Safety Filter / CBF | Assume-Guarantee CPS | Agent Authorization / Governance | PDC / Trust Continuity hypothesis |
|---|---|---|---|---|---|---|
| Runtime unsafe-action blocking | Not primary | Strong | Strong | Partial | Partial | Proposed, not differentiating |
| Runtime action modification | Not primary | Strong | Strong | Partial | Possible | Proposed, not differentiating alone |
| Physical safe-set / constraint reasoning | Not primary | Strong | Core | Strong under model | Limited | Mechanism-dependent |
| Explicit environmental assumptions | Strong lifecycle relevance | Partial–Strong | Model-dependent | Core | Policy/context-dependent | Core input, not differentiating alone |
| Compositional assume-guarantee reasoning | Limited | Partial | Limited | Core | Limited | Possible, not current claim |
| Runtime validity / monitoring | Lifecycle-oriented | Core | Core | Possible | Core in governance systems | Core input, not differentiating alone |
| Evidence-backed trust claims | Core | Partial | Usually limited | Partial | Provenance/audit often strong | Proposed cross-boundary binding |
| Exact artifact binding | Core | Usually not central | Usually not central | Not normally central | May bind software/action identity | Candidate continuity dimension |
| Semantic decision authority | Core | Usually outside scope | Outside scope | Contract authority usually assumed externally | Strong for delegated actions | Inherited semantic basis |
| Runtime proposal authorization | Partial | Architectural assumption | Outside scope | Interface can encode | Core in agent governance | Not differentiating alone |
| Runtime execution admission | Not primary | Core | Core | Can support | Core in some governance systems | Not differentiating alone |
| Modification authority distinct from feasibility | Delegation model can express | Often implicit in architecture | Usually filter is pre-authorized | Can encode if modeled | Can encode delegated transforms | **TC3 candidate** |
| Fallback authority distinct from veto | Semantic authority can express | Often predesigned backup path | Usually outside focus | Can encode if modeled | Can encode policy | **TC3 candidate** |
| Historical validity distinct from current validity | Core via lifecycle trust | Partly implicit in runtime state | State-dependent | Assumption-dependent | Context/policy dependent | Candidate continuity dimension |
| Design-time authority → exact artifact → runtime action trace | Stops at executable/runtime evidence | Weak/not central | Weak/not central | Partial | Strong on runtime authorization/provenance, weaker on design-time semantic origin | **TC1/TC2 candidate** |
| Cross-boundary assumption invalidation | Core design/build lifecycle | Local runtime handling strong | Local state/model handling strong | Strong when modeled | Context/policy invalidation possible | **TC4 candidate** |
| Dependency completeness treated as explicit epistemic risk | C0/RFC0012 structural concern | Usually bounded by safety model | Usually bounded by model/safe-set | Contract completeness remains external problem | Policy/action vocabulary completeness remains external | Major unresolved risk |

## Candidate residual claims

### TC1 — Semantic-to-runtime capability binding

**Question**

Can a runtime proposal class be bound to the semantic authority that authorized the exact executable/runtime role to possess that proposal capability?

**Potential overlap**

- capability-based authorization;
- delegated agent permissions;
- contract-based interface definitions;
- policy-bound action schemas.

**Residual claim survives only if**

Spec2Exec-style semantic authority contributes something beyond ordinary API/action permission, such as explicit provenance from behavior-defining semantic obligation through accepted specification and exact artifact to runtime proposal capability.

**Kill condition**

If existing authorization/provenance systems already provide equivalent semantic-origin binding without additional PDC machinery, TC1 should be removed.

---

### TC2 — Artifact/runtime/actuation identity continuity

**Question**

Can exact identity remain bound across:

```text
accepted semantics
→ artifact
→ runtime instance
→ proposal
→ admission decision
→ consequential action
```

**Potential overlap**

- software supply-chain provenance;
- attestation;
- agent action receipts;
- runtime provenance;
- safety-case configuration control.

**Residual claim survives only if**

cross-boundary identity linking materially changes trust decisions or failure detection rather than merely producing a richer audit log.

**Kill condition**

If ordinary attestation + provenance + action logging gives equivalent trust semantics and operational value, TC2 should be removed or reduced to an implementation composition note.

---

### TC3 — Authority-preserving intervention

**Question**

When a runtime mechanism shows that proposed action `u` is unsafe and replacement `u'` is feasible/safe, what establishes authority to execute `u'`?

Distinguish:

```text
u rejected; u' offered as counter-proposal
```

from:

```text
u transformed to u' under explicit delegated authority
```

Also distinguish:

```text
veto authority
```

from:

```text
fallback-selection authority
```

**Potential overlap**

- pre-authorized Simplex backup controller;
- safety-filter transformation policies;
- supervisory control;
- delegated action-rewriting policies;
- contract-based refinement.

**Residual claim survives only if**

the explicit normative separation exposes real ambiguity or prevents incorrect behavior that existing designs commonly leave implicit and cannot represent cleanly without additional structure.

**Kill condition**

If valid RTA/safety-filter architectures already treat intervention and fallback as sufficiently explicit delegated policies, with no measurable ambiguity or assurance gap, TC3 should be removed.

---

### TC4 — Cross-boundary assumption invalidation

**Question**

Can a load-bearing assumption be linked across:

```text
design-time semantic decision
→ assurance claim
→ artifact/capability
→ runtime dependency
→ current admission decision
```

such that invalidation propagates without rewriting historical truth?

**Potential overlap**

- assume-guarantee contracts;
- runtime monitors;
- dynamic assurance cases;
- configuration/lifecycle assurance;
- runtime safety cases;
- adaptive system assurance.

**Residual claim survives only if**

cross-boundary lineage enables selective invalidation/reuse or catches stale trust that local runtime monitors and design-time assurance artifacts do not expose when used separately.

**Kill condition**

If existing dynamic assurance + contract/runtime-monitor frameworks already provide equivalent dependency lineage and invalidation semantics, TC4 should be removed.

## Cross-cutting existential risk — dependency completeness

Even if TC1–TC4 remain non-overlapping, PDC can still fail if the runtime dependency model creates false confidence.

The central problem is:

```text
represented dependency set
        ≠
complete load-bearing dependency set
```

Therefore an all-green PDC evaluation must never be interpreted as proof that every physical dependency has been represented.

A future semantic model must distinguish at least:

```text
known represented dependency
known-unrepresented dependency
unknown / unresolved dependency coverage
explicit out-of-scope dependency
```

without pretending that `UNKNOWN` can be eliminated generically.

## Current non-novel responsibilities

Unless later evidence shows otherwise, do not claim research novelty for:

```text
runtime action gating
constraint checking
safe-set filtering
backup-controller switching
assumption/guarantee contracts
runtime validity windows
state freshness checks
uncertainty fields
provenance recording
delegated runtime authorization
safety vetoes
```

## Current strongest hypothesis

The most defensible working hypothesis is:

> **A non-trivial research contribution may exist in preserving typed trust continuity — authority, evidence, assumptions, identity, and validity — across the transition from design-time semantic authorization through exact executable realization to context-dependent runtime execution.**

This remains unresolved.

## Decision rule

For each of TC1–TC4, future literature review should produce one of:

```text
KEEP
    clear residual responsibility remains

NARROW
    only a smaller subclaim remains

COMPOSE
    existing approaches provide the semantics; document composition only

DROP
    no meaningful residual claim remains
```

No PDC schema or prototype should be treated as research-justified until this matrix has survived that process.
