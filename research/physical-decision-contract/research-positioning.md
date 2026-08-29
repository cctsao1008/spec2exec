# Research Positioning — Spec2Exec, PDC, and Trust Continuity

**Status:** Research positioning note  
**Normative status:** Non-normative  
**Issue:** #70

## 1. Three-level interpretation

The current research should keep three levels separate.

```text
Level 1 — Spec2Exec core
Current validated and actively tested research program.

Level 2 — Physical Decision Contract (PDC)
Externalization probe into runtime physical execution.

Level 3 — Trust Continuity
Higher-order hypothesis about cross-boundary consequential execution.
```

Do not use Level 2 or Level 3 to retrospectively reinterpret accepted Spec2Exec RFCs or validated evidence.

## 2. Current Spec2Exec core

Spec2Exec currently investigates whether semantic-obligation discovery, explicit semantic authority, deterministic verification, artifact binding, and lifecycle-aware evidence can form a defensible trust architecture for AI-generated executable systems.

The current primary empirical program is comparative assurance:

```text
CONV vs LITE vs S2E
```

with `S2E vs LITE` as the primary comparison.

The PDC / Trust Continuity track must not alter that experiment.

## 3. PDC as an externalization probe

PDC asks whether the same discipline survives a different consequential boundary:

```text
Spec2Exec core:
candidate semantics
→ accepted executable behavior

PDC probe:
candidate runtime action
→ admitted physical action
```

The important point is not that physical execution requires a gate. Established Runtime Assurance and control-safety approaches already address runtime intervention.

The research question is whether design-time authority/evidence relationships can remain meaningfully connected to runtime admission and actuation.

## 4. Higher-order Trust Continuity hypothesis

The possible general abstraction is not `specification → executable` and not `AI → physical controller`.

It is:

```text
Candidate consequential decision
        ↓
Authority / Evidence / Assumptions / Identity / Validity
        ↓
Consequential execution
```

A more precise hypothesis is:

> **Can authority, evidence, assumptions, identity, and validity remain explicitly bound as a machine-generated decision moves from authorized intent through executable realization to context-dependent consequential execution?**

The possible contribution is therefore **Trust Continuity across heterogeneous consequential-execution boundaries**, not execution admission itself.

## 5. Continuity dimensions

### Authority continuity

Can each behavior-affecting decision be traced to a valid source of decision authority or explicit delegation?

### Evidence continuity

Can each trust claim identify the evidence, method, assumptions, TCB, scope, and validity that support it without collapsing distinct evidence types into one generic PASS?

### Assumption continuity

Can load-bearing assumptions remain connected to the claims and decisions that depend on them, including invalidation and re-evaluation when the assumptions change?

### Identity continuity

Can the chain identify the exact specification, artifact, runtime instance, proposal, admission decision, and consequential action rather than relying on similarity or implicit identity?

### Validity continuity

Can historical truth remain immutable while current trust/admissibility changes as dependencies, evidence, context, or policy become stale or invalid?

## 6. Candidate non-collapse principles

The current research hypotheses include:

```text
Proposal ≠ Authority
Authority ≠ Admission
Admission ≠ Permanent Validity
Feasibility ≠ Modification Authority
Veto Authority ≠ Fallback Authority
Historical Validity ≠ Current Validity
Evidence Producer ≠ Decision Authority
Deterministic ≠ Correct
Plausibility ≠ Permission
Execution Capability ≠ Execution Permission
Represented Dependencies ≠ Complete Dependencies
```

These are deliberately non-normative until literature review, semantic formalization, and experiments justify them.

## 7. Why `authority` must remain typed

Avoid collapsing different meanings of authority:

```text
Semantic Authority
    who may decide a behavior-defining semantic question

Admission Delegation
    which mechanism may apply a named runtime admission policy

Veto Authority
    who or what may prevent execution

Fallback Authority
    who or what may select a fallback behavior

Execution Authority
    which component may issue the final executable/actuation request

Control Capability / Margin
    physical ability to realize a requested action
```

`Control capability` is not normative authority.

A gate does not become an authority source merely because it evaluates a policy. Its admission role must itself be delegated or otherwise grounded in an authorized system policy.

## 8. Modification is a first-class stress test

Suppose:

```text
proposal u = 8 m/s
```

and a runtime mechanism determines:

```text
u is inadmissible
u' = 3.5 m/s is feasible / safe
```

Three different claims exist:

```text
1. u is inadmissible.
2. u' is feasible or safe under the named model/policy.
3. u' is authorized to execute as the replacement behavior.
```

Neither 1 nor 2 automatically establishes 3.

Therefore distinguish:

```text
REJECT + COUNTER-PROPOSAL
```

from:

```text
AUTHORIZED TRANSFORMATION
```

This distinction must survive comparison with RTA, safety-filter, and delegated-policy literature before it is treated as a contribution.

## 9. Fallback is a separate authority question

Detection, veto, fallback selection, and fallback execution must not silently collapse:

```text
failure detected
        ≠
execution vetoed
        ≠
fallback selected
        ≠
fallback authorized
        ≠
fallback executed
```

A fallback may be technically safe yet still be the wrong mission or governance behavior unless an authorized policy delegates that choice.

## 10. Completeness pressure

The runtime analogue of C0's structural problem is:

> **A runtime admission mechanism cannot invalidate a load-bearing dependency that was never represented.**

Represented state, assumptions, timing, uncertainty, and capability are therefore not proof of complete runtime dependency coverage.

This is expected to be a primary falsification axis rather than a solved property.

## 11. Research boundary

The following are not current claims:

```text
PDC is novel.
PDC is safer than RTA or Simplex.
PDC replaces CBF or safety filters.
PDC guarantees dependency completeness.
PDC guarantees physical safety.
Trust Continuity is a general architecture already demonstrated by Spec2Exec.
Spec2Exec should be redefined today as a general execution-admission platform.
```

## 12. Decision rule for future integration

PDC should remain a separate research track unless it survives:

```text
Gate 1 — non-overlap / literature review
        ↓
Gate 2 — minimal semantic model without circularity
        ↓
Gate 3 — comparative experiment against simpler established compositions
```

Only after evidence survives these gates should RFC-level integration or a broader Spec2Exec thesis be considered.
