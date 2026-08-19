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

## Why now?

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

That motivates a different class of questions:

```text
Old question:
Did we implement the specification correctly?

Additional questions:
What behavior-determining questions should have been surfaced?
Which semantics were supplied, inferred, or invented?
Who or what was authorized to decide them?
Did the accepted semantics reach this exact artifact?
Is the evidence that justified trust still current?
```

## Four trust shifts

Spec2Exec is built around several distinctions that are easy to collapse in ordinary software workflows:

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

## Research hypothesis

> **Spec2Exec investigates whether semantic-obligation discovery, explicit semantic authority, deterministic verification, artifact binding, and lifecycle-aware evidence can form a defensible trust architecture for AI-generated executable systems.**

A stronger version of the hypothesis is deliberately open to falsification:

> **As implementation becomes increasingly synthesizable, semantic authority may become a first-class engineering concern.**

Spec2Exec does not assume that its mechanisms are universally necessary, sufficient, or superior to conventional requirements engineering, review, testing, formal methods, assurance cases, or provenance systems. Comparative assurance and engineering overhead remain research questions.

## AI-facing engineering substrate

Spec2Exec is designed primarily as a **machine-operable engineering substrate for AI-assisted or AI-driven implementation workflows**.

Humans remain responsible for intent, policy, semantic authority, risk acceptance, and assurance review. AI agents may perform obligation discovery, semantic-resolution proposals, synthesis, transformation, optimization, and evidence production through the Spec2Exec trust architecture.

A useful long-term framing is:

> **Spec2Exec is an AI-facing software engineering substrate for turning authorized human intent into trustworthy executable behavior.**

This is an architectural hypothesis, not a claim that human-readable source languages are obsolete, that C/C++/Rust must disappear from engineering workflows, or that the current prototype has demonstrated a fully AI-native software stack.

## The three questions

Spec2Exec separates three problems that ordinary code review can easily collapse:

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

## Trust-chain overview

For a first-pass mental model:

```text
Requirement / Intent
        ↓
Semantic Obligation Discovery
        ↓
Semantic Resolution / Conflict Exposure
        ↓
Executable Semantic Closure
        ↓
Semantic Authority
        ↓
Deterministic Verification / Evidence
        ↓
Target Realization
```

Completeness is cross-cutting rather than a single pipeline pass. **C0 obligation completeness** studies whether authority-relevant questions were surfaced at all, while **RFC 0011 Semantic Completeness** prevents known authority-relevant obligations from silently disappearing from the executable semantic closure.

## Architecture

The more detailed architecture separates candidate semantics, authority, verification, realization, and evidence:

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
Extraction / Interpretation
        ↓
Semantic Obligations + Authority Records
        ↓
Semantic Resolution / Conflict Handling
        ↓
Executable Semantic Closure
        ↓
Complete Authority-Grant Discovery
        ↓
Deterministic Semantic Authority Gate
        ↓
Accepted Specification / Acceptance Record
        ↓
Semantic Synthesis
        ↓
Candidate SpecIR
        ↓
Deterministic Verification
        ↓
Verified SpecIR
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

Accepted architecture references:

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md)
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md)
- [RFC 0012 — Lifecycle-Aware Trust Graph](rfcs/0012-lifecycle-aware-trust-graph.md) — **Accepted / Lifecycle Trust Baseline**
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md)

RFC 0012 is deliberately cross-cutting: assumptions, dependency completeness, defeaters, invalidation, ProjectionPolicy-gated current-trust projection, and re-assurance are modeled as lifecycle-bearing trust relationships rather than as another serial compiler stage.

## What this looks like

One human-facing workflow POC uses the payment-retry story:

```text
Spec2Exec Semantic Review

retry_count = 5            UNAUTHORIZED
retry_on_http_500 = true   AUTHORIZED
retry_on_timeout = ?       UNRESOLVED

MERGE GATE: BLOCKED
```

See the [blocked semantic review](examples/payment-retry/unsafe-review.md), the [accepted review](examples/payment-retry/accepted-review.md), and the [payment-retry example](examples/payment-retry/README.md).

This workflow POC is deliberately narrower than a production GitHub integration. Its CODEOWNERS mapping is a **repository-declared, unauthenticated attribution input** into the authority policy; CODEOWNERS is not semantic authority by itself. Live GitHub App/check-run posting, cryptographic identity, quorum approval, OIDC, and enterprise identity integration remain future work.

## What is demonstrated today

Spec2Exec is a research prototype, not a production assurance platform.

### 1. Authority-gated native executable path

The existing POC-1C path demonstrates a narrow authority-gated RV32I bare-metal flow under QEMU:

```text
Candidate POC Specification + bound authority manifest
        ↓
A1 deterministic Semantic Authority Gate
        ↓
Authority Acceptance Record
        ↓
P1 / P2 deterministic checks
        ↓
Machine-independent SpecIR
        ↓
P3 native RV32I target generation
        ↓
GNU assembler / linker
        ↓
RV32I validation ELF
        ↓
QEMU rv32 virt
        ↓
40,401 exhaustive accepted-contract observations
```

Current validated baseline:

```text
source revision   c96f08c46920d80a619ac6be58507e506e0850da
GitHub Actions    31879494912
POC-1C tests      50 / 50 PASS
runtime domain    40,401 / 40,401 PASS
safe_add_sub.s    sha256 9e78282830b5e9e87a69b22dc0c358bd07bcff248f04f2709792f45973892a6b
safe_add_sub.o    sha256 027486b5efe99dfc21356d26620f9523316db0e32b1a5266396b96f62f799b7d
safe_add_sub.elf  sha256 fb029132a30d8030128edf8f373978ee1643a220c448fc02d06fc95ad26fffc8
evidence.json     sha256 a8db31ec9e69cd46d2a573768593e51e3da3d1894482ddb4f4f4de2c76757826
```

See [POC-1C validation results](docs/poc1c-results.md).

### 2. Explicit non-collapsible evidence

The native path does not collapse everything into a single PASS:

| Boundary | Current claim | Meaning |
|---|---|---|
| A1 | `CHECKED` | Deterministic authority evaluation accepted the exact bound POC records under the declared Authority TCB; this does not authenticate/prove the anchor itself |
| P1 | `CHECKED` | Specification/trace/contract linkage checks |
| P2 | `CHECKED` | Declared fixed-width/range/overflow obligations for the POC subject |
| P3 | `TESTED` | SpecIR → generated RV32I assembly has test evidence; no formal compiler-equivalence proof is claimed |
| P4-A / P4-H / P4-L | `TRUSTED` | Assembler, harness-object, and linker boundaries are named trusted infrastructure |
| P4-R | `TESTED_EXHAUSTIVE` | Every input pair in the mechanically bound finite runtime domain was observed under QEMU |
| P4-R.sensitivity | `TESTED` | Known-bad target mutations and a trap probe exercise the failure channel |

No current native boundary carries `PROVEN`:

> **`TESTED` is not `PROVEN`, `TESTED_EXHAUSTIVE` is not `PROVEN`, and `TRUSTED` is not `VERIFIED`.**

### 3. Existing-compiler evidence composition

Spec2Exec is **not a compiler replacement**. The repository also demonstrates that its evidence model can compose with conventional compiler infrastructure:

```text
Accepted POC Specification
        ↓
SpecIR checks
        ↓
generated C
        ↓
host C compiler
        ↓
executable
        ↓
runtime observation
```

The experiment records separate claims:

```text
CGEN.specir_to_c          TESTED
CC.c_to_executable        TRUSTED
CRUN.runtime_observation  TESTED
CRUN.sensitivity          TESTED
```

See [Existing-Compiler Realization Experiment](docs/existing-compiler-integration.md) and [issue #60](https://github.com/cctsao1008/spec2exec/issues/60).

### 4. Bounded lifecycle Trust Graph validation

The first executable slice of RFC 0012 is validated under closed issue #62 for `PAYMENT-RETRY-SAFETY`.

The primary lifecycle result is deliberately counterintuitive:

```text
Payment API v7
    → CURRENT

Payment API v7 → v8
client artifact byte-identical
    → provider assumption BASIS_STALE
    → REVALIDATION_REQUIRED
    → BLOCKED

policy-accepted v8 revalidation
    → fresh property/context projection CURRENT
```

The same client artifact SHA-256 is bound across these scenarios:

```text
95018cb2c86bb1bea9cffb89e12ee31c711a26de159a1dcdacee21ce8b2b4c72
```

Validated revision `797c0e4497e6fb9355236f659b96bf4e7870ecdc`; GitHub Actions run `31907601851`; lifecycle tests `29 / 29 PASS`.

This is bounded validation evidence, not formal proof of RFC 0012, universal dependency completeness, production payment assurance, certification, or a generic Trust Graph platform. See [bounded lifecycle Trust Graph validation](docs/lifecycle-trust-validation.md).

## Current research tracks

The benchmark tracks are intentionally separate from semantic authority and executable evidence.

### A0 — unsafe semantic resolution

> When a semantic question is incomplete, ambiguous, or contradictory, does a system expose uncertainty — or invent a plausible answer?

A0 v1 is a frozen cross-domain case-level benchmark. One protocol-bound measured external-model baseline under #45 matched all 24 A0 v1 decision labels with `unsafe_resolution_rate = 0/14` on the unresolved/conflict subset.

See [A0](research/a0-semantic-resolution/) and the [measured baseline report](research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816-report.md).

### A0F — held-out field-level semantic resolution

A0F supplies a fixed semantic-field vocabulary and asks the evaluated system to classify every field as:

```text
RESOLVED
UNRESOLVED
CONFLICT
NOT_APPLICABLE
```

`a0f/v1` contains 24 held-out cases and 114 field classifications. Under #64, four predeclared UI configurations have operator-declared fresh/blinded measured baselines. Their field accuracies range from `109/114` to `113/114`; their unsafe-resolution profiles differ and are intentionally not collapsed into a universal model ranking.

See [A0F](research/a0-field-resolution/) and the [A0F v1 cross-model measured report](research/a0-field-resolution/baselines/a0f-v1-cross-model-20260817-report.md).

### C0 — semantic-obligation discovery / completeness

> **Did the system notice all of the authority-relevant questions that should have been surfaced at all?**

An authority gate cannot reject an obligation that was never discovered.

C0 remains distinct from A0F because C0 does not supply the semantic-field vocabulary. Its gold sets are benchmark-specific review oracles, not claims of universal real-world specification completeness.

See [C0](research/semantic-obligation-completeness/) and [issue #57](https://github.com/cctsao1008/spec2exec/issues/57).

The research boundary is:

```text
A0:  Did we invent the answer at case level?
A0F: Given explicit semantic fields, did we classify them safely?
C0:  Did we discover the authority-relevant questions in the first place?
RFC 0011: Was the selected answer authorized?
Executable Semantic Closure: Does it affect this selected build?
```

## Next research phase — Comparative assurance

The current architecture has reached a bounded proof-of-method stage. The next primary research question is no longer only whether Spec2Exec can reach executable behavior under a bounded trust architecture.

It is:

> **Does Spec2Exec provide enough incremental assurance over simpler structured AI-assisted engineering workflows to justify its additional authoring, review, training, and lifecycle cost?**

The planned comparative design distinguishes:

- `CONV` — conventional AI-assisted engineering;
- `LITE` — lightweight structured semantic control;
- `S2E` — the Spec2Exec workflow.

The primary comparison is `S2E` versus `LITE`; `S2E` versus `CONV` is secondary.

The design is intentionally capable of falsifying a stronger Spec2Exec claim: if a substantially simpler structured workflow achieves comparable assurance with materially lower engineering cost, the necessity of the fuller Spec2Exec architecture would be weakened.

The comparative study is designed to examine semantic escape, safe-release yield, discovery adequacy, authoring/review cost, traceability, and lifecycle revalidation behavior without collapsing these outcomes into a single scalar assurance score.

## Cross-domain examples

Different domains expose the same kind of trust boundary:

| Domain | Example intent | Questions that still need authority |
|---|---|---|
| Medical / healthcare | "Alert when the patient is deteriorating." | What constitutes deterioration? What if measurements are missing/conflicting? |
| Aviation | "Switch to backup when primary fails." | What constitutes failure? What if both sources disagree/fail? |
| Security | "Grant access to administrators." | Which role? Which resources? Which exceptions? |
| Finance | "Retry failed payments." | Which failures? How many retries? Is the operation idempotent? |
| Cloud / distributed | "Retry transient requests." | Which errors, timeout, backoff, budget, terminal behavior? |
| Embedded / robotics | "Reduce output when unsafe." | Which threshold, output limit, sensor-failure behavior, recovery rule? |

These examples illustrate semantic-authority questions. They are **not claims of domain qualification**.

## Existing approaches and the composition question

Spec2Exec does not claim that testing, formal methods, code review, requirements engineering, assurance cases, verified compilation, provenance systems, or certification are ineffective. They address important parts of the problem.

| Approach | It can provide evidence about | It does not automatically establish |
|---|---|---|
| Unit / integration testing | Observed behavior for selected cases | Whether the tested semantics were authorized or complete |
| Code review | Implementation reasonableness | Whether every hidden semantic assumption was surfaced and approved |
| Static analysis | Specific program properties | Whether the requirement itself is authoritative |
| Formal verification | Satisfaction of stated formal properties | Whether those properties are the semantics that should have been executed |
| Verified compilation / translation validation | Preservation of defined source semantics | Whether the source semantics were authorized |
| Assurance / certification evidence | Structured claims, arguments, traceability | Automatic semantic-authority binding for every generated decision |
| Supply-chain provenance / reproducible builds | Inputs, tools, provenance, artifacts | Whether the semantics being built were the authorized semantics |
| Runtime / hardware testing | What an artifact did under tested conditions | Whether the oracle, domain, assumptions, or authority were complete |

The research question is one of composition:

> **Can semantic-obligation discovery, semantic authority, deterministic verification, artifact binding, non-collapsible evidence classes, and executable realization be composed into a fail-closed machine-readable workflow?**

Spec2Exec does not claim to have invented requirements traceability, assurance cases, provenance, formal verification, verified compilers, or specification-driven generation.

## What Spec2Exec is not

Spec2Exec is not:

- an AI coding assistant or an LLM wrapper;
- a system in which plausible AI output gains authority automatically;
- a requirements-management replacement;
- a compiler replacement;
- a claim that human-readable programming languages are obsolete or unnecessary;
- a general formal-verification system;
- a certification replacement;
- a claim that CODEOWNERS or repository identity is sufficient real-world organizational authority;
- a certified medical, aviation, automotive, financial, industrial-safety, or security system;
- a claim that exhaustive finite-domain testing is formal proof;
- a claim that QEMU execution is physical-hardware validation;
- a claim that every semantic obligation in a real-world system can currently be discovered completely;
- a claim that every material lifecycle dependency can currently be discovered completely.

## Target and validation scope

**Target realization is a validation substrate for executable trust boundaries, not the primary research objective.** Expanding backend coverage is therefore subordinate to trust questions that require it.

The demonstrated native architectural target is currently **RV32I + bare metal**, validated under QEMU `rv32 virt`.

Raspberry Pi Pico 2 / RP2350 with Hazard3 remains planned physical validation hardware; it is a validation platform, not the architectural target.

Arm M-profile and hosted x86_64 / AArch64 / RV64 configurations remain roadmap work. See [target profiles](docs/target-profiles.md).

## Current workstreams

### Active research

| Area | Current state |
|---|---|
| Comparative assurance / bootstrapping cost | protocol design at freeze-candidate stage; compares `CONV`, `LITE`, and `S2E`, with `S2E` vs `LITE` primary |
| C0 discovery adequacy | `c0/v1` benchmark/scorer/control fixtures implemented under #57; scaling and independent assessment remain research priorities |
| Lifecycle revalidation economics | RFC 0012 baseline and bounded lifecycle experiment exist; comparative change-impact and revalidation cost remain active research questions |
| A0 / A0F measurement infrastructure | frozen benchmark tracks retained as bounded regression and measurement infrastructure; not treated as universal model rankings |

### Validated bounded baselines

| Area | Current state |
|---|---|
| Semantic-authority / provenance | RFC 0011 Accepted; narrow authority-gated POC-1C MVI validated under #53 |
| Evidence vocabulary / RFC normalization | RFC 0006 Accepted; #54 completed |
| Lifecycle-aware Trust Graph | RFC 0012 Accepted; bounded implementation/validation #62 closed with 29 / 29 lifecycle tests |
| Payment-retry semantic POC | deterministic BLOCKED/ACCEPTED examples implemented under #58 |
| GitHub semantic diff / CODEOWNERS adapter | deterministic workflow POC implemented under #59; live GitHub App integration deferred |
| Existing-compiler evidence composition | host-C experiment implemented/tested under #60 |
| Hostile-review umbrella | mapped F-01 through F-13 workstreams closed under #52 |

### Deferred / supporting realization work

| Area | Current state |
|---|---|
| Hazard3 / RP2350 hardware validation | pending under #36; useful for physical closure, not the current primary research blocker |
| RV32 forced-spill experiment | backend work remains available under #37; expand only when a trust question requires it |
| Strong identity / OIDC / signatures / quorum | deferred future authority work |
| Broader backend coverage | Arm M-profile and hosted x86_64 / AArch64 / RV64 remain supporting roadmap work rather than the primary research axis |

## Where to read next

For the fastest introduction:

- [Payment-retry semantic-authority example](examples/payment-retry/README.md)
- [Blocked semantic diff](examples/payment-retry/unsafe-review.md)
- [Bounded lifecycle Trust Graph validation](docs/lifecycle-trust-validation.md)
- [A0 measured baseline — Claude Opus 5 / High](research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816-report.md)
- [A0F v1 cross-model measured baselines](research/a0-field-resolution/baselines/a0f-v1-cross-model-20260817-report.md)
- [C0 semantic-obligation completeness benchmark](research/semantic-obligation-completeness/)

For architecture and evidence:

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md)
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md)
- [RFC 0012 — Lifecycle-Aware Trust Graph](rfcs/0012-lifecycle-aware-trust-graph.md)
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md)
- [RFC 0009 — Native Target Code Generation](rfcs/0009-native-target-code-generation.md)
- [POC-1C validation results](docs/poc1c-results.md)
- [Existing-compiler integration](docs/existing-compiler-integration.md)
- [Issue #49 — active roadmap](https://github.com/cctsao1008/spec2exec/issues/49)

## Roadmap direction

The earlier phase asked whether the trust architecture could exist as an executable, evidence-bound system. The repository now contains bounded proof-of-method results for authority gating, semantic-resolution/discovery research infrastructure, target realization, evidence composition, and lifecycle-aware trust.

The current phase asks a harder question:

```text
Can the architecture exist?
        ↓
bounded proof-of-method
        ↓
Does it provide enough incremental assurance
        to justify its additional cost?
        ↓
CONV vs LITE vs S2E
        ↓
semantic escape / safe-release yield
obligation discovery / traceability
bootstrapping / review / training cost
lifecycle revalidation cost
```

`a0/v1` and `c0/v1` remain frozen measured/research baselines. A0F is a separately versioned held-out track and must not be used to rewrite A0 v1 after observing A0 results. Future benchmark-semantic revisions likewise require explicit versioning and an Issue rather than silent mutation.

Native backend experiments remain useful when they test a specific realization or trust boundary, but the project does not need to become a full production compiler. Backend expansion is therefore driven by research need rather than by target-count growth.

## License

License selection remains intentionally pending.