# Spec2Exec

**Specification-to-Executable Architecture**

> **AI is making software implementation cheap. It is not making software trust cheap.**

Spec2Exec explores specification as the primary human-facing artifact between intent and executable software, with an explicit trust chain from authorized semantics to the exact artifact that runs.

**Current state:** Spec2Exec is a research prototype. The project now demonstrates a narrow **authority-gated RV32I bare-metal path under QEMU**: a bound AuthorityAnchor/policy/semantic-obligation set is checked by a deterministic semantic-authority gate before the existing P1/P2 → SpecIR → native RV32I realization pipeline runs. No AI or LLM component participates in the currently demonstrated executable pipeline. Physical RP2350 / Hazard3 validation remains pending.

The long-term direction is **trust infrastructure for AI-generated software**. The current evidence supports a smaller but concrete claim: a machine-readable, artifact-bound chain from a repository-declared POC authority basis through deterministic authority/verification checks to a native executable and exhaustive observation of its declared runtime contract.

## Why Spec2Exec?

A generated system can compile, pass tests, behave consistently, and even satisfy a formal specification while still implementing semantics that were never explicitly authorized.

Software can therefore fail without containing an obvious coding bug. A program may correctly execute the wrong rule, an incomplete rule, an outdated rule, or a plausible assumption that nobody actually accepted.

```text
implementation correctness
        !=
semantic correctness
        !=
semantic authority
```

**Semantic authority** asks who or what is entitled to decide a semantic question, and whether that decision was actually recorded. That is distinct from whether the decision was internally sensible or implemented correctly.

A bug-free implementation does not imply that the implemented behavior is the right behavior. A formally verified implementation does not, by itself, prove that the formal specification represents the semantics that should have been executed.

Implementations may become cheap and replaceable. **Accepted semantics and the evidence binding them to what runs must not.**

### Why AI raises the stakes

Traditional software development already contains ambiguity, unstated assumptions, and requirement gaps. AI does not create those problems, and the problem is not simply that AI is "worse than humans."

What changes is the **scale and speed** at which interpretation becomes implementation:

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

A synthesis system can turn missing semantics into executable decisions far faster than those decisions can be reviewed one by one. The resulting code may look completely reasonable while hiding choices that were never made authoritative.

The same pattern appears across domains:

| Domain | Example intent | Semantic questions that still need authority |
|---|---|---|
| Medical / healthcare | "Alert when the patient is deteriorating." | What constitutes deterioration? What happens when measurements are missing or conflicting? |
| Aviation | "Switch to the backup source when the primary system fails." | What constitutes failure? What if primary and backup sources disagree or both fail? |
| Security | "Grant access to administrators." | Which role and resources? Which emergency exceptions are permitted? |
| Finance | "Reject suspicious transactions." | What is suspicious? Which threshold and exception policy is authorized? |
| Cloud / distributed systems | "Retry failed requests." | Which failures are retryable? Is the operation safe to repeat and what ends the retry policy? |
| Embedded / robotics / industrial control | "Limit actuator behavior when conditions are unsafe." | Which conditions and limit? What happens when sensing is invalid? |

These examples illustrate where semantic authority matters; they are **not claims of domain qualification**. Spec2Exec is a research project. It is not certified, qualified, assessed, or approved under any medical, automotive, aviation, industrial-safety, security, or other assurance standard, and the current prototype does not produce certification evidence.

Different domains fail in different ways, but the trust question is the same:

> **Who authorized the semantics, what was actually verified, and what evidence binds those claims to the executable that will run?**

## Existing approaches and the composition problem

Spec2Exec does not assume that testing, code review, formal methods, compilers, assurance processes, or runtime validation are ineffective. They are essential, and substantial prior work already addresses individual parts of the trust problem.

| Approach | It can provide evidence about | It does not automatically establish |
|---|---|---|
| Unit / integration testing | Observed behavior for selected cases | Whether the tested semantics were authorized or complete |
| Code review | Whether an implementation appears reasonable and maintainable | Whether every hidden assumption was detected and approved |
| Static analysis | Specific program properties and defect classes | Whether the requirement itself is correct or authoritative |
| Formal verification | Whether a formal artifact satisfies stated properties under assumptions | Whether those stated properties represent the semantics that should have been executed |
| Verified compilation / translation validation | Whether defined source semantics are preserved across a transformation boundary | Whether the source semantics themselves were authorized |
| Assurance cases / certification evidence | Structured claims, arguments, traceability, and evidence for a defined system or process | Automatic binding of every semantic-authority decision to every generated artifact in a build |
| Supply-chain attestation / reproducible builds | Which inputs, tools, provenance, and artifacts participated in a build | Whether the semantics being built were the semantics an authority intended |
| Runtime / hardware testing | What the built artifact actually did under tested conditions | Whether the oracle, domain, assumptions, or semantic authority were complete |

Examples of established work in these areas include assurance-case methods such as GSN/CAE, domain assurance and certification frameworks, verified compilers and translation validation, and provenance systems such as in-toto/SLSA/Sigstore and reproducible builds. Spec2Exec does **not** claim to have invented assurance cases, requirements traceability, verified compilation, provenance, or specification-driven code generation.

The research question is instead one of **composition**:

> Can semantic authority, deterministic verification, artifact binding, non-collapsible evidence classes, and executable realization be composed into a machine-readable, fail-closed specification-to-executable process?

The proposed delta is therefore not another single PASS result. It is to make the trust chain an explicit output of executable generation, with claims bound to exact artifacts and with unsupported claims prevented from silently inheriting stronger evidence from another boundary.

## What Spec2Exec proposes

The architecture separates candidate semantics, authority, verification, realization, and evidence:

```text
Human / Domain / Governance Sources            [research / authority input]
        ↓
Candidate Semantics                            [research]
        ↓
Extraction / Interpretation                    [architecture; narrow POC records implemented]
        ↓
Semantic Obligations + Authority Records       [MVI IMPLEMENTED for POC-1C]
        ↓
Executable Semantic Closure                    [explicit POC enumeration IMPLEMENTED]
        ↓
Complete Authority-Grant Discovery             [MVI IMPLEMENTED]
        ↓
Deterministic Semantic Authority Gate          [MVI IMPLEMENTED]
        ↓
Accepted Specification / Acceptance Record     [MVI IMPLEMENTED]
        ↓
Semantic Synthesis → Candidate SpecIR          [prototype path]
        ↓
Deterministic Verification                     [DEMONSTRATED — limited declared properties]
        ↓
SpecIR after declared checks                   [DEMONSTRATED]
        ↓
Target Realization                             [DEMONSTRATED for RV32I; other targets planned]
        ↓
Executable / Firmware                          [DEMONSTRATED for RV32I validation ELF]
        ↓
Runtime / Emulator / Hardware Observation      [QEMU DEMONSTRATED; physical HW pending]

Across the chain:
Claim ↔ Evidence ↔ Artifact ↔ Tool ↔ Assumption ↔ Provenance
```

The current Semantic Authority Gate is deliberately narrow. It demonstrates the RFC 0011 boundary with one repository-declared AuthorityAnchor, bounded `VALUE` / `VALUE_SET` / `CONSTRAINT` policies, three explicit semantic obligations, one selected build/configuration, an explicitly enumerated closure, complete applicable-grant discovery, fail-closed conflicts/staleness/exclusion, and an authority acceptance record bound into downstream evidence.

It does **not** implement cryptographic identity, quorum/dual approval, redelegation beyond the MVI, rich standards/requirements ingestion, general multi-configuration closure analysis, runtime revocation, or certification workflows. The Authority TCB is explicitly unauthenticated in this POC: its anchor declaration and repository write-access protection are trusted/human-declared inputs rather than cryptographic proof.

The public thesis is:

> **AI proposes. Humans and delegated authority mechanisms authorize semantics. Deterministic systems verify. Evidence justifies trust. Target backends realize accepted semantics.**

Capability alone does not create authority.

See:
- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md) for the project-level thesis;
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md) for the accepted authority baseline;
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md) for canonical evidence vocabulary and boundaries.

## What is demonstrated today

### Semantic-authority MVI

The POC-1C entry path now binds the specification to:

```text
AuthorityAnchor
AuthorityPolicy set
SemanticObligation set
ClosureRecord
Authority manifest + hashes
```

The real authority-gated semantic obligations are:

```text
overflow_behavior = forbidden
input a range = [-100,100]
input b range = [-100,100]
```

The MVI includes:

- one direct human-declared `VALUE` authorization for overflow behavior;
- one delegated `VALUE_SET` policy for the input-domain selection;
- an explicit selected-build authorization;
- a deterministic range `CONSTRAINT` over the closure;
- fail-closed checks for no anchor, cycles, missing/no-policy authority, out-of-grant values, stale revisions, unresolved/conflicting semantics, scope/provenance failure, self-authorization violations, redelegation, classification widening, unbased closure exclusion, selected-configuration authority, cross-policy authority conflict, and closure-constraint violation;
- complete discovery of potentially applicable grants rather than trusting only the binding supplied by the obligation;
- an `A1.semantic_authority_gate` `CHECKED` claim bound into `evidence.json`.

`AUTHORIZED` is a governance state, not an evidence class. The deterministic gate evaluation is `CHECKED`; the POC AuthorityAnchor and repository-protection basis remain human-declared / unauthenticated trust inputs.

### SpecIR

**SpecIR** is the machine-independent intermediate representation used between an accepted specification and target realization. It represents executable semantics, declared ranges, contracts, and trace links that the verifier and backends consume; target-specific machine details are kept outside machine-independent SpecIR.

A real fragment from the RV32I subject:

```json
{
  "postconditions": [
    {
      "id": "POST-RESULT",
      "trace": ["REQ-OPT-001-BEH"],
      "expr": {"op": "==", "args": ["result", {"op": "-", "args": [{"op": "+", "args": ["a", "b"]}, "b"]}]}
    },
    {
      "id": "POST-CONTRACT",
      "trace": ["REQ-OPT-001-EQ"],
      "expr": {"op": "==", "args": ["result", "a"]}
    }
  ],
  "body": {
    "kind": "expr",
    "expr": {"op": "-", "args": [{"op": "+", "args": ["a", "b"]}, "b"]},
    "trace": ["REQ-OPT-001-BEH"]
  }
}
```

The full example is [examples/native-rv32i/safe_add_sub.specir.json](examples/native-rv32i/safe_add_sub.specir.json).

### POC-1C.A worked example

```text
safe_add_sub(a, b) = (a + b) - b

a, b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
contract trace: REQ-OPT-001-EQ
```

Generated RV32I target code:

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

The primary path uses **no generated C, LLVM IR, or other high-level-language compiler stage between SpecIR and target assembly**:

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
P3 RV32I target generation
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

Current evidence report:

| Boundary | Current claim | Meaning |
|---|---|---|
| A1 | `CHECKED` | Deterministic authority evaluation confirms the bound POC anchor/policies/obligations/closure under the declared Authority TCB; this does not authenticate or prove the anchor itself |
| P1 | `CHECKED` | Function identity plus constraint, range, behavior, and contract linkage/traceability against the accepted POC specification |
| P2 | `CHECKED` | Fixed-width type-domain checks, output-range containment, and absence of signed-overflow UB for this i32 subject by blocking sound interval analysis |
| P3 | `TESTED` | SpecIR → generated RV32I assembly has test evidence; this is not a formal compiler-equivalence proof |
| P4-A / P4-H / P4-L | `TRUSTED` | Assembler, harness-object, and linker boundaries are part of the named trusted computing base; Spec2Exec does not claim to have verified those tools |
| P4-R | `TESTED_EXHAUSTIVE` | Every case in the mechanically bound declared finite runtime domain was observed under QEMU `rv32 virt` |
| P4-R.sensitivity | `TESTED` | Known-bad target mutations and a trap probe were required to reach the observable failure channel |

No boundary in the current evidence set carries `PROVEN`: **`TESTED` is not `PROVEN`, `TESTED_EXHAUSTIVE` is not `PROVEN`, and `TRUSTED` is not `VERIFIED`.**

`TESTED_EXHAUSTIVE` is scoped to the accepted contract's declared domain, not the full 32-bit input space. POC-1C.A observes all **40,401** input pairs in `[-100,100] × [-100,100]` under QEMU `rv32 virt`, checking `result == a` for every pair.

For P4-R, QEMU is part of the named TCB: the evidence assumes the QEMU `rv32 virt` machine model correctly represents the exercised RV32I behavior and that the SiFive test-finisher protocol maps the observed PASS/FAIL channel correctly.

Runtime sensitivity controls remain:

```text
wrong-final-operation  → exit 1
wrong-first-operation  → exit 1
trap-path-ebreak       → exit 1
```

### Current tested baseline

The authority-gated baseline is tied to:

```text
source revision   c96f08c46920d80a619ac6be58507e506e0850da
GitHub Actions    run 31879494912
POC-1C tests      50 / 50 PASS
runtime domain    40,401 / 40,401 PASS
safe_add_sub.s    sha256 9e78282830b5e9e87a69b22dc0c358bd07bcff248f04f2709792f45973892a6b
safe_add_sub.o    sha256 027486b5efe99dfc21356d26620f9523316db0e32b1a5266396b96f62f799b7d
safe_add_sub.elf  sha256 fb029132a30d8030128edf8f373978ee1643a220c448fc02d06fc95ad26fffc8
evidence.json     sha256 a8db31ec9e69cd46d2a573768593e51e3da3d1894482ddb4f4f4de2c76757826
```

The target assembly/object/ELF hashes are unchanged from the prior entry-hardening baseline; the authority work changed the trusted entry/evidence chain rather than the generated target behavior for this subject.

See [POC-1C.A validation results](docs/poc1c-results.md) and [GitHub Actions run 31879494912](https://github.com/cctsao1008/spec2exec/actions/runs/31879494912).

CI installs `binutils-riscv64-unknown-elf` and `qemu-system-misc`, then runs:

```sh
make test-poc1c
make poc1c
```

with `POC1C_REQUIRE_RUNTIME=1`, so runtime and sensitivity validation cannot silently disappear when the required emulator/toolchain is unavailable.

The project therefore claims a **working native RV32I emulator baseline with a narrow authority-gated POC entry path and explicit per-boundary evidence**. It does **not** claim a formally verified native compiler, cryptographically authenticated semantic authority, a general authority-management system, certification, or physical-hardware validation.

## Designed and research-next

| Area | Current state |
|---|---|
| Semantic-authority / provenance model | RFC 0011 Accepted; narrow POC-1C MVI implemented and validated under #53 |
| Canonical evidence vocabulary / RFC normalization | RFC 0006 Accepted; #54 CLOSED / COMPLETED |
| Rich authority ingestion, strong identity, multi-config closure | Deferred / future authority work beyond the MVI |
| Hazard3 / RP2350 / Pico 2 physical validation | Pending — [#36](https://github.com/cctsao1008/spec2exec/issues/36) |
| RV32 backend multiple-live-value / forced-spill stress | Next backend experiment — [#37](https://github.com/cctsao1008/spec2exec/issues/37) |
| Arm M-profile and hosted target expansion | Planned — [target profiles](docs/target-profiles.md) |
| AI semantic-resolution benchmark | Research track — [#45](https://github.com/cctsao1008/spec2exec/issues/45) |

### A0 — unsafe semantic resolution

A0 asks a deliberately different AI question from ordinary code-generation benchmarks:

> Can a synthesis system expose unresolved or conflicting semantics instead of inventing a plausible value?

The benchmark uses `RESOLVED`, `UNRESOLVED`, and `CONFLICT` decisions and defines `unsafe_resolution_rate` as a primary metric. A plausible engineering value is still a failure when the authoritative source did not provide or authorize that value.

A0 remains a **research track, not a demonstrated AI result**: no reproducible AI baseline run is currently claimed. The accepted authority architecture now provides the boundary required for future integration, but A0 is not yet part of the demonstrated executable pipeline. See [research/a0-semantic-resolution/](research/a0-semantic-resolution/) and [issue #45](https://github.com/cctsao1008/spec2exec/issues/45).

## Target and validation scope

The demonstrated architectural target is currently **RV32I + bare metal**, validated under QEMU `rv32 virt`. Raspberry Pi Pico 2 / RP2350 with Hazard3 is planned physical validation hardware; it is a validation platform, not an architectural target.

Arm M-profile and hosted x86_64 / AArch64 / RV64 configurations are roadmap work rather than demonstrated portability. The target model and planned configurations live in [docs/target-profiles.md](docs/target-profiles.md) and [docs/phase1-plan.md](docs/phase1-plan.md).

## What Spec2Exec is not

Spec2Exec is not:

- an AI coding assistant or an LLM wrapper;
- a system in which AI output gains semantic authority by being plausible or capable;
- a certified medical, aviation, automotive, industrial-safety, or security system;
- a claim to replace testing, formal methods, assurance cases, verified compilers, certification processes, or supply-chain provenance systems;
- a claim that the current authority MVI is a production governance, identity, or certification system;
- a claim that every boundary is formally proven.

## Where to read next

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md): project thesis, trust/assurance/realization layers, and long-term invariants.
- [RFC 0011 — Semantic Authority, Delegation, and Default Policy](rfcs/0011-semantic-authority-delegation-and-default-policy.md): Accepted semantic-authority baseline and fail-closed gate architecture.
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md): Accepted canonical evidence vocabulary, preservation boundaries, evidence profiles, and RFC lifecycle.
- [RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance](rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md): historical intent-fidelity rationale; authority mechanics are superseded by RFC 0011.
- [RFC 0009 — Native Target Code Generation](rfcs/0009-native-target-code-generation.md): accepted native-target architecture and target / validation separation.
- [POC-1C.A validation results](docs/poc1c-results.md): exact tested subject, authority gate, evidence boundaries, tool versions, hashes, negative controls, and remaining work.
- [Target profiles](docs/target-profiles.md): ISA, execution, ABI, platform, and planned portability model.
- [A0 semantic-resolution benchmark](research/a0-semantic-resolution/): `UNRESOLVED` / `CONFLICT` handling and trust-oriented AI metrics.
- [Issue #49 — active roadmap](https://github.com/cctsao1008/spec2exec/issues/49): current implementation and research workstreams.

## Roadmap snapshot

The first semantic-authority MVI and evidence/RFC normalization workstreams are complete. Current active work now splits between backend scaling (#37), physical validation (#36), the A0 semantic-resolution research track (#45), and later target expansion. Broader authority features such as strong identity, rich external-source ingestion, multi-configuration closure analysis, and enterprise policy management remain explicitly deferred beyond the first POC.

## License

License selection remains intentionally pending.
