# Spec2Exec

**Specification-to-Executable Architecture**

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

The code can compile. The tests can pass. Five retries may even sound reasonable.

But if nobody or no authorized policy selected `5`, the implementation has silently converted a missing semantic decision into executable behavior.

**Spec2Exec explores how to prevent unstated, unresolved, or unauthorized semantic decisions from silently becoming software behavior — and how to bind the resulting trust claims to the exact artifact that runs.**

> **AI is making software implementation cheap. It is not making software trust cheap.**

## What this looks like

The repository now contains a small GitHub-oriented semantic-review POC built around the payment-retry story:

```text
Spec2Exec Semantic Review

retry_count = 5            UNAUTHORIZED
retry_on_http_500 = true   AUTHORIZED
retry_on_timeout = ?       UNRESOLVED

MERGE GATE: BLOCKED
```

See the [blocked semantic review](examples/payment-retry/unsafe-review.md), the [accepted review](examples/payment-retry/accepted-review.md), and the [payment-retry example](examples/payment-retry/README.md).

This workflow POC is deliberately narrower than a production GitHub integration. Its CODEOWNERS mapping is a **repository-declared, unauthenticated attribution input** into the authority policy; CODEOWNERS is not semantic authority by itself. Live GitHub App/check-run posting, cryptographic identity, quorum approval, OIDC, and enterprise identity integration remain future work.

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

The more detailed ASCII diagrams and RFC text below remain the more precise descriptions of architecture, state, evidence boundaries, and implementation status.

## Current research tracks

### A0 — unsafe semantic resolution

A0 asks:

> When a semantic question is incomplete, ambiguous, or contradictory, does a system expose uncertainty — or invent a plausible answer?

Its primary trust-oriented metric is `unsafe_resolution_rate`.

For example:

```text
"Retry failed payment requests."
→ retry_count = 3
```

is an unsafe resolution when the source or an applicable authority policy never supplied or delegated `3`.

A0 v1 contains cross-domain cases for motor safety, sensors, timing, payment retry, access control, cloud retry, hardware semantics, and related cases. It now has one measured blinded external-model baseline under closed issue #45: the Claude web UI configuration labeled `Opus 5` with `High` effort matched all 24 A0 v1 decision labels, with `unsafe_resolution_rate = 0/14` on the unresolved/conflict subset. This is a benchmark-specific measured result, **not** a claim of general model quality, universal semantic completeness, semantic authority, certification, or exact correctness of every free-form explanation field. See the [measured baseline report](research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816-report.md).

See [A0](research/a0-semantic-resolution/) and [issue #45](https://github.com/cctsao1008/spec2exec/issues/45).

### A0F — held-out field-level semantic resolution

A0F was added after A0 v1 decision-level results began to saturate on strong models. Instead of asking for one case-level decision, each held-out case supplies a fixed semantic-field vocabulary and asks the system to classify every field as:

```text
RESOLVED
UNRESOLVED
CONFLICT
NOT_APPLICABLE
```

This separates several behaviors that a case-level A0 label cannot distinguish:

```text
Did the system safely avoid inventing one missing field?
Did it over-block fields that were already explicit?
Did it identify the exact conflicting field?
Did it recognize a field that is explicitly outside the case semantics?
```

A0F v1 contains 24 held-out cases and 114 field classifications. Its scorer reports `field_accuracy`, `case_exact_match`, `unsafe_field_resolution_rate`, `overblocking_rate`, per-state accuracy/recall, and per-domain/per-case detail. The benchmark has deterministic oracle, unsafe-always-resolve, and over-conservative controls.

A0F is **not C0**: the field vocabulary is supplied to the evaluated system, so A0F measures field-level resolution discipline rather than open-ended semantic-obligation discovery. No measured external-model A0F quality is currently claimed; such a run must use a fresh blinded context with only the A0F evaluation prompt/input.

See [A0F](research/a0-field-resolution/) and [issue #63](https://github.com/cctsao1008/spec2exec/issues/63).

### C0 — semantic-obligation discovery / completeness

C0 asks the harder upstream question:

> **Did the system notice all of the authority-relevant questions that should have been surfaced at all?**

An authority gate cannot reject an obligation that was never discovered.

For:

```text
When motor temperature becomes unsafe, reduce motor output.
```

a benchmark oracle may require the system to surface questions such as:

```text
temperature_threshold
reduced_output_limit
sensor_missing_behavior
sensor_invalid_behavior
hysteresis
recovery_condition
update_period
```

C0 v1 reports:

- `obligation_recall`
- `unsafe_omission_rate`
- `spurious_obligation_rate`
- `high_impact_recall`

The gold sets are benchmark-specific review oracles, not claims that a real regulated specification has been proven complete.

See [C0](research/semantic-obligation-completeness/) and [issue #57](https://github.com/cctsao1008/spec2exec/issues/57).

The distinction is:

```text
A0:  Did we invent the answer at case level?
A0F: Given an explicit field vocabulary, which fields are resolved,
     unresolved, conflicting, or not applicable?
C0:  Did we discover the authority-relevant questions in the first place?
RFC 0011: Was the selected answer authorized?
Executable Semantic Closure: Does it affect this selected build?
```

## Architecture

The architecture separates candidate semantics, authority, verification, realization, and evidence:

```text
Human / Domain / Governance Sources
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

See:

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md)
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md)
- [RFC 0012 — Lifecycle-Aware Trust Graph](rfcs/0012-lifecycle-aware-trust-graph.md) — **Accepted / Lifecycle Trust Baseline**
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md)

RFC 0012 extends the architecture in a deliberately cross-cutting direction: assumptions, dependency completeness, defeaters, invalidation, ProjectionPolicy-gated current-trust projection, and re-assurance are modeled as lifecycle-bearing trust relationships rather than new serial compiler stages. The architecture baseline is Accepted; its first bounded executable validation is complete under [issue #62](https://github.com/cctsao1008/spec2exec/issues/62). See the [bounded lifecycle Trust Graph validation](docs/lifecycle-trust-validation.md).

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
GNU assembler
        ↓
ELF32 object
        ↓
GNU linker + validation harness
        ↓
RV32I validation ELF
        ↓
QEMU rv32 virt
        ↓
40,401 exhaustive accepted-contract observations
```

The authority-gated semantic obligations are deliberately small:

```text
overflow_behavior = forbidden
input a range = [-100,100]
input b range = [-100,100]
```

The MVI includes a repository-declared `AuthorityAnchor`, bounded `VALUE` / `VALUE_SET` / `CONSTRAINT` policies, selected-build authorization, an explicit executable semantic closure, complete applicable-grant discovery, cross-policy conflict checks, stale-revision handling, provenance checks, and fail-closed authority evaluation before SpecIR synthesis.

`AUTHORIZED` is a governance state, not an evidence class. The deterministic authority evaluation is `CHECKED`; the POC AuthorityAnchor and repository protection remain human-declared / unauthenticated trust inputs.

### 2. Native RV32I realization without generated C/LLVM

The deterministic regression fixture remains:

```text
safe_add_sub(a, b) = (a + b) - b

a, b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
```

Its generated RV32I target code is:

```asm
    .section .text
    .option norvc
    .globl safe_add_sub
    .type safe_add_sub, @function
safe_add_sub:
    add t0, a0, a1
    sub a0, t0, a1
    ret
    .size safe_add_sub, .-safe_add_sub
```

This path uses **no generated C, LLVM IR, or other high-level-language compiler stage between SpecIR and target assembly**.

The current validated baseline is:

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

### 3. Explicit non-collapsible evidence

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

### 4. GitHub-oriented semantic-diff workflow POC

The payment-retry workflow demonstrates a deterministic, human-readable semantic review with a bounded CODEOWNERS adapter.

The unsafe candidate is blocked because it contains both an unauthorized decision and an unresolved obligation. A corrected candidate is accepted under the demo policy.

This is a **workflow POC following RFC 0011 principles**, not a replacement for the validated POC-1C authority-record evaluator and not a claim that CODEOWNERS is sufficient production authority.

The shared trust-research workflow validates A0/A0F/C0 scorer controls, the measured A0 baseline regression, semantic-review/CODEOWNERS fail-closed behavior, the bounded lifecycle experiment, and the existing-compiler experiment. The A0F infrastructure revision `43f2e761f311282671f47068f60c33cf73d9ac64` passed Trust Research run `31913085179`.

### 5. Existing-compiler evidence composition

Spec2Exec is **not a compiler replacement**.

The repository also demonstrates that the evidence model can compose with conventional compiler infrastructure:

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

The exact compiler version/invocation and generated artifacts are evidence-bound. A known-bad generated-C mutation must be detected by the runtime oracle.

This experiment does not claim the host compiler is verified. It demonstrates that Spec2Exec's trust/evidence model can remain explicit when realization is delegated to an existing compiler.

See [Existing-Compiler Realization Experiment](docs/existing-compiler-integration.md) and [issue #60](https://github.com/cctsao1008/spec2exec/issues/60).

### 6. Bounded lifecycle Trust Graph validation

The first executable slice of RFC 0012 is validated under closed issue #62 for the property `PAYMENT-RETRY-SAFETY`.

The three primary scenarios bind the same client artifact SHA-256:

```text
95018cb2c86bb1bea9cffb89e12ee31c711a26de159a1dcdacee21ce8b2b4c72
```

and demonstrate:

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

The validated implementation revision is `797c0e4497e6fb9355236f659b96bf4e7870ecdc`. GitHub Actions run `31907601851` completed successfully with 29 / 29 lifecycle tests, including all mandatory fail-closed controls from #62. The experiment preserves RFC 0011 as the semantic-authority owner and RFC 0006 as the evidence-status owner.

This is bounded validation evidence, not formal proof of RFC 0012, universal dependency completeness, production payment assurance, certification, or a generic Trust Graph platform. See [bounded lifecycle Trust Graph validation](docs/lifecycle-trust-validation.md).

## Why AI raises the stakes

Traditional software development already has ambiguity, unstated assumptions, requirement gaps, and authority conflicts. AI does not create these problems.

What changes is the speed and scale at which interpretation becomes implementation:

```text
vague or incomplete intent
        ↓
seconds
        ↓
many inferred decisions and assumptions
        ↓
working implementation
        ↓
executable behavior
```

A synthesis system can turn missing semantics into implementation decisions much faster than humans can notice and authorize them one by one.

Different domains expose the same trust problem:

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
- a general formal-verification system;
- a certification replacement;
- a claim that CODEOWNERS or repository identity is sufficient real-world organizational authority;
- a certified medical, aviation, automotive, financial, industrial-safety, or security system;
- a claim that exhaustive finite-domain testing is formal proof;
- a claim that QEMU execution is physical-hardware validation;
- a claim that every semantic obligation in a real-world system can currently be discovered completely;
- a claim that every material lifecycle dependency can currently be discovered completely.

## Target and validation scope

The demonstrated native architectural target is currently **RV32I + bare metal**, validated under QEMU `rv32 virt`.

Raspberry Pi Pico 2 / RP2350 with Hazard3 remains planned physical validation hardware; it is a validation platform, not the architectural target.

Arm M-profile and hosted x86_64 / AArch64 / RV64 configurations remain roadmap work. See [target profiles](docs/target-profiles.md).

## Current workstreams

| Area | Current state |
|---|---|
| Semantic-authority / provenance | RFC 0011 Accepted; narrow authority-gated POC-1C MVI validated under #53 |
| Evidence vocabulary / RFC normalization | RFC 0006 Accepted; #54 completed |
| A0 unsafe semantic resolution | `a0/v1` frozen benchmark/scorer/control fixtures plus one blinded measured Opus 5 / High baseline; #45 closed |
| A0F field-level semantic resolution | `a0f/v1` held-out 24-case / 114-field benchmark, scorer, blinded protocol, and controls implemented under #63; infrastructure CI green; no measured external-model A0F result yet |
| C0 obligation discovery / completeness | `c0/v1` benchmark/scorer/control fixtures implemented under #57 |
| Payment-retry semantic POC | deterministic BLOCKED/ACCEPTED examples implemented under #58 |
| GitHub semantic diff / CODEOWNERS adapter | deterministic workflow POC implemented under #59; live GitHub App integration deferred |
| Existing-compiler evidence composition | host-C experiment implemented/tested under #60 |
| Lifecycle-aware Trust Graph | RFC 0012 Accepted; architecture #61 closed; bounded payment-retry lifecycle implementation/validation #62 closed with 29 / 29 lifecycle tests and green CI |
| Hostile-review umbrella | mapped F-01 through F-13 workstreams closed under #52 |
| RV32 forced-spill experiment | backend work remains available under #37 |
| Hazard3 / RP2350 hardware validation | pending under #36 |
| Strong identity / OIDC / signatures / quorum | deferred future authority work |

## Where to read next

For the fastest introduction:

- [Payment-retry semantic-authority example](examples/payment-retry/README.md)
- [A0 measured baseline — Claude Opus 5 / High](research/a0-semantic-resolution/baselines/claude-opus-5-high-20260816-report.md)
- [A0F held-out field-level semantic-resolution benchmark](research/a0-field-resolution/)
- [C0 semantic-obligation completeness benchmark](research/semantic-obligation-completeness/)
- [Bounded lifecycle Trust Graph validation](docs/lifecycle-trust-validation.md)
- [Blocked semantic diff](examples/payment-retry/unsafe-review.md)

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

The project now has three deliberately separate scaling axes:

```text
Research axis
    A0 unsafe case-level resolution
        ↓
    A0F field-level resolution discipline
        ↓
    C0 open-ended obligation discovery/completeness
        ↓
    authority
        ↓
    evidence

Lifecycle trust axis
    property-scoped dependencies
        ↓
    dependency completeness
        ↓
    assumptions / defeaters
        ↓
    invalidation / selective reuse
        ↓
    re-assurance

Workflow axis
    semantic diff
        ↓
    repository identity / CODEOWNERS adapter
        ↓
    CI merge gate
        ↓
    future stronger identity / approval mechanisms
```

`a0/v1` and `c0/v1` remain frozen measured/research baselines. A0F is a separately versioned held-out track and must not be used to rewrite A0 v1 after observing A0 results. Future benchmark-semantic revisions likewise require explicit versioning and an Issue rather than silent mutation.

Native backend experiments remain useful for testing realization boundaries, but the project does not need to become a full production compiler to validate the trust architecture. Existing-compiler integration is an explicit first step toward demonstrating that the same evidence model can span multiple realization strategies.

## License

License selection remains intentionally pending.