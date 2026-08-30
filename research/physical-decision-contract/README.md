# Physical Decision Contract / Trust Continuity

**Status:** Research hypothesis / externalization probe  
**Issue:** #70 — Trust Continuity / Physical Decision Contract  
**Normative status:** Not an RFC; not accepted architecture  
**Priority:** P2  
**Relationship to #69:** Separate; does not modify the Comparative Assurance protocol

## Research question

> **After accounting for established Runtime Assurance, safety-filter, contract-based CPS, authorization, provenance, and assurance approaches, does a useful cross-boundary Trust Continuity problem remain?**

Current hierarchy:

```text
Spec2Exec core
    = current validated research program

PDC
    = physical-runtime externalization probe

Trust Continuity
    = higher-order research hypothesis
```

The possible contribution is **not execution admission itself**. The hypothesis is whether authority, evidence, assumptions, identity, and validity can remain explicitly bound as execution crosses from authorized software semantics into context-dependent consequential action.

## Current candidate claims

- **TC1 — Semantic-to-runtime capability binding**
- **TC2 — Artifact/runtime/actuation identity continuity**
- **TC3 — Authority-preserving intervention**
- **TC4 — Cross-boundary assumption invalidation**

These are research candidates, not accepted Spec2Exec invariants or novelty claims.

## Current work

1. Compare TC1–TC4 against established approaches.
2. Mark each claim `KEEP`, `NARROW`, `COMPOSE`, or `DROP`.
3. Only if a non-trivial residual survives, define a minimal semantic model.
4. Do not implement schema or prototype before those gates pass.

## Documents

- [`research-positioning.md`](research-positioning.md) — detailed hypothesis, boundaries, and non-collapse principles.
- [`non-overlap-matrix.md`](non-overlap-matrix.md) — comparison against established approaches and candidate residual claims.
- [Issue #70](https://github.com/cctsao1008/spec2exec/issues/70) — active research tracking.

## Explicit non-claims

PDC / Trust Continuity is currently:

```text
NOT an RFC
NOT accepted architecture
NOT part of #69
NOT a novelty claim
NOT an implementation commitment
```

Accepted Spec2Exec RFCs remain unchanged.