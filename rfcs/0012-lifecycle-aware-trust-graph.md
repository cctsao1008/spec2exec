# RFC 0012 — Lifecycle-Aware Trust Graph

- **Status:** Draft / Proposed — Revision 2, projection-policy-hardened closure candidate
- **Issue:** #61
- **Scope:** first-class assumptions, dependency completeness, defeaters/residual doubt, typed dependency edges, deterministic trust invalidation, projection-policy-gated context-bound current-trust projection, and re-assurance across revision-bound claims and artifacts

## Summary

Spec2Exec already models a trust chain from candidate semantics to accepted semantics, verification, realization, and exact executable artifacts. It also already records assumptions, revisions, traceability, semantic-authority state, Trusted Computing Base components, and artifact hashes.

The lifecycle gap is not another realization stage. It is that material trust dependencies can change, become unsupported, be newly discovered as defective, or remain historically true while no longer justifying current use.

This RFC proposes a cross-cutting **Trust Graph** that makes four questions first-class:

1. **Dependency completeness:** what does a gated property claim materially depend on, and what basis supports the claim that material dependencies were not silently omitted?
2. **Assumption lifecycle:** what claims depend on an assumption, under which bound context, and what happens when its support/basis/context changes?
3. **Defeaters / residual doubt:** what concrete reasons could defeat a trust claim, which have been resolved, and which remain explicit limitations under an authorized residual-disposition decision?
4. **Trust invalidation / re-assurance:** when a requirement, authority basis, assumption, TCB component, tool, context, policy, dependency, or artifact changes — or when new adverse knowledge is discovered — which property claims remain current, which require revalidation, and which historical evidence may still be reused?

The Trust Graph is **not a new serial compiler stage** and does not replace the current executable semantic path.
