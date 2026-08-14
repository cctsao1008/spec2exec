# Spec2Exec

**Specification-to-Executable Architecture**

> **AI is making software implementation cheap. It is not making software trust cheap.**

Spec2Exec explores specification as the primary human-facing artifact between intent and executable software, with an explicit trust chain from accepted semantics to the exact artifact that runs.

**Current state:** Spec2Exec is a research prototype. The project currently demonstrates the downstream half of that chain for a narrow RV32I bare-metal subject under QEMU. The semantic-authority gate is designed but not yet implemented. No AI or LLM component participates in the currently demonstrated executable pipeline. Physical RP2350 / Hazard3 validation remains pending.

The long-term direction is **trust infrastructure for AI-generated software**. Today, the evidence supports a smaller but concrete claim: a machine-generated, artifact-bound, per-boundary evidence chain from an accepted POC specification to a native executable and exhaustive observation of its declared runtime contract.

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

The project architecture deliberately separates research, designed components, and demonstrated components:

```text
Human / Domain Intent                         [research input]
        ↓
Candidate Semantics                           [research]
        ↓
Ambiguity / Conflict / Missing-Semantics      [research]
Detection
        ↓
Semantic Authority Gate                       [DESIGNED — not yet implemented, #53]
        ↓
Accepted Specification                       [current POC uses a minimal acceptance record]
        ↓
Semantic Synthesis → Candidate SpecIR         [prototype path]
        ↓
Deterministic Verification                    [DEMONSTRATED — limited declared properties]
        ↓
SpecIR after declared checks                  [DEMONSTRATED]
        ↓
Target Realization                            [DEMONSTRATED for RV32I; other targets planned]
        ↓
Executable / Firmware                         [DEMONSTRATED for RV32I validation ELF]
        ↓
Runtime / Emulator / Hardware Observation     [QEMU DEMONSTRATED; physical HW pending]

Across the chain:
Claim ↔ Evidence ↔ Artifact ↔ Tool ↔ Assumption ↔ Provenance
```

The **Semantic Authority Gate is the central architectural commitment and is not yet implemented**. The current POC starts from a specification carrying a minimal `accepted-for-poc` record; stronger authority provenance, revision, delegation, revocation, and fail-closed `UNRESOLVED` / `CONFLICT` handling are tracked in [issue #53](https://github.com/cctsao1008/spec2exec/issues/53).

The public thesis remains:

> **AI proposes. Humans authorize semantics. Deterministic systems verify. Evidence justifies trust. Portable backends execute.**

The normative architecture is broader than human-only approval: future authority may be represented by accountable standards, accepted parent specifications, certified domain models, contracts, or explicit governance sources. Capability alone does not grant semantic authority.

See [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md) for the project-level thesis and long-term invariants.

## What is demonstrated today

### SpecIR

**SpecIR** is the machine-independent intermediate representation used between an accepted specification and target realization. It represents the executable semantics, declared ranges, contracts, and trace links that the verifier and backends consume; target-specific machine details are kept outside machine-independent SpecIR.

A real fragment from the current RV32I subject is shown below. It includes both postconditions and the executable body; the full document also carries inputs, output/ranges, overflow behavior, preconditions, and top-level trace metadata.

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

The current native test subject is deliberately small:

```text
safe_add_sub(a, b) = (a + b) - b

a, b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
contract trace: REQ-OPT-001-EQ
```

The generated RV32I target code, shown with the canonical generated formatting, is:

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

The primary executable-generation path uses **no generated C, LLVM IR, or other high-level-language compiler stage between SpecIR and target assembly**:

```text
Accepted POC Specification
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

For the current POC-1C evidence report:

| Boundary | Current claim | Meaning |
|---|---|---|
| P1 | `CHECKED` | Function identity plus constraint, range, behavior, and contract linkage/traceability against the accepted POC specification |
| P2 | `CHECKED` | Fixed-width type-domain checks, output-range containment, and absence of signed-overflow UB for this i32 subject by blocking sound interval analysis |
| P3 | `TESTED` | SpecIR → generated RV32I assembly has test evidence; this is not a formal compiler-equivalence proof |
| P4-A / P4-H / P4-L | `TRUSTED` | Assembler, harness-object, and linker boundaries are part of the named trusted computing base; Spec2Exec does not claim to have verified those tools |
| P4-R | `TESTED_EXHAUSTIVE` | Every case in the mechanically bound declared finite runtime domain was observed under QEMU `rv32 virt` |
| P4-R.sensitivity | `TESTED` | Known-bad target mutations and a trap probe were required to reach the observable failure channel |

No boundary in the current POC-1C evidence set carries `PROVEN`: **`TESTED` is not `PROVEN`, and `TRUSTED` is not `VERIFIED`**.

`TESTED_EXHAUSTIVE` is scoped to the accepted contract's declared domain, not the full 32-bit input space. POC-1C.A observes all **40,401** input pairs in `[-100,100] × [-100,100]` under QEMU `rv32 virt`, checking `result == a` for every pair.

For P4-R, QEMU is also part of the named trusted computing base: the evidence assumes that the QEMU `rv32 virt` machine model correctly represents the exercised RV32I behavior and that the SiFive test-finisher protocol maps the observed PASS/FAIL channel correctly.

The runtime evidence also includes negative controls:

```text
wrong-final-operation  → exit 1
wrong-first-operation  → exit 1
trap-path-ebreak       → exit 1
```

This fail-closed / sensitivity evidence matters because a runtime oracle that cannot detect a known-bad implementation cannot support a meaningful success claim.

The successful entry-hardening baseline is tied to:

```text
source revision   65b346be4478b08a984d20b36cc47b901539371b
GitHub Actions    run 31765577964
POC-1C tests      28 / 28 PASS
safe_add_sub.elf  sha256 fb029132a30d8030128edf8f373978ee1643a220c448fc02d06fc95ad26fffc8
evidence.json     sha256 7600bd471e949d961f9c0639f59bb5fd2408677c8197cbc98d0ad28be9921fa9
```

See the [POC-1C.A validation results](docs/poc1c-results.md) and [GitHub Actions run 31765577964](https://github.com/cctsao1008/spec2exec/actions/runs/31765577964) for the complete evidence set.

On the Ubuntu CI runner, the RV32I toolchain/emulator prerequisites are installed as `binutils-riscv64-unknown-elf` and `qemu-system-misc`, then CI runs:

```sh
make test-poc1c
make poc1c
```

with `POC1C_REQUIRE_RUNTIME=1`, so the runtime and sensitivity path cannot silently disappear because the required emulator/toolchain is unavailable.

The project therefore claims a **working native RV32I emulator baseline with explicit per-boundary evidence**. It does **not** claim a formally verified native compiler, physical-hardware validation, or a completed semantic-authority mechanism.

## Designed and research-next

The project deliberately distinguishes implemented evidence from planned trust capabilities:

| Area | Current state |
|---|---|
| Rich semantic-authority / provenance model | Designed / open — [#53](https://github.com/cctsao1008/spec2exec/issues/53) |
| Canonical evidence vocabulary and RFC boundary normalization | Architecture work open — [#54](https://github.com/cctsao1008/spec2exec/issues/54) |
| Hazard3 / RP2350 / Pico 2 physical validation | Pending — [#36](https://github.com/cctsao1008/spec2exec/issues/36) |
| RV32 backend multiple-live-value / forced-spill stress | Next backend experiment — [#37](https://github.com/cctsao1008/spec2exec/issues/37) |
| Arm M-profile and hosted target expansion | Planned — [target profiles](docs/target-profiles.md) |
| AI semantic-resolution benchmark | Research track — [#45](https://github.com/cctsao1008/spec2exec/issues/45) |

### A0 — unsafe semantic resolution

A0 asks a deliberately different AI question from ordinary code-generation benchmarks:

> Can a synthesis system expose unresolved or conflicting semantics instead of inventing a plausible value?

The benchmark track uses `RESOLVED`, `UNRESOLVED`, and `CONFLICT` decisions and defines `unsafe_resolution_rate` as a primary metric. Its key guardrail is that a plausible engineering value is still a failure when the authoritative source did not provide or authorize that value.

A0 is currently a **research track, not a demonstrated AI result**: no reproducible baseline run is yet claimed, and A0 remains disconnected from executable generation until the semantic-authority gate is strong enough to reject unresolved, conflicting, unauthorized, or stale semantics. See [research/a0-semantic-resolution/](research/a0-semantic-resolution/) and [issue #45](https://github.com/cctsao1008/spec2exec/issues/45).

## Target and validation scope

The demonstrated architectural target is currently **RV32I + bare metal**, validated under QEMU `rv32 virt`. Raspberry Pi Pico 2 / RP2350 with Hazard3 is planned physical validation hardware; it is a validation platform, not an architectural target.

Arm M-profile and hosted x86_64 / AArch64 / RV64 configurations are roadmap work rather than demonstrated portability. The full target model, ISA / Execution / Platform Profile separation, and planned configurations live in [docs/target-profiles.md](docs/target-profiles.md) and [docs/phase1-plan.md](docs/phase1-plan.md).

## What Spec2Exec is not

Spec2Exec is not:

- an AI coding assistant or an LLM wrapper;
- a system in which AI output gains semantic authority by being plausible or capable;
- a certified medical, aviation, automotive, industrial-safety, or security system;
- a claim to replace testing, formal methods, assurance cases, verified compilers, certification processes, or supply-chain provenance systems;
- a claim that the current prototype implements the complete trust architecture or that every boundary is formally proven.

## Where to read next

- [RFC 0010 — Trust-Chain Architecture](rfcs/0010-trust-chain-architecture.md): project thesis, trust layers, semantic authority, long-term invariants.
- [RFC 0005 — Trust, Intent Fidelity, and Specification Acceptance](rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md): draft authority / acceptance boundary; currently being reconciled with newer architecture work.
- [RFC 0006 — Semantic Preservation and Evidence Model](rfcs/0006-semantic-preservation-and-evidence-model.md): draft evidence model; boundary and vocabulary normalization is tracked in #54.
- [RFC 0009 — Native Target Code Generation](rfcs/0009-native-target-code-generation.md): accepted native-target architecture and target / validation separation.
- [POC-1C.A validation results](docs/poc1c-results.md): exact tested subject, evidence boundaries, tool versions, hashes, negative controls, and remaining work.
- [Target profiles](docs/target-profiles.md): ISA, execution, ABI, platform, and planned portability model.
- [A0 semantic-resolution benchmark](research/a0-semantic-resolution/): `UNRESOLVED` / `CONFLICT` handling and trust-oriented AI metrics.
- [Issue #49 — active roadmap](https://github.com/cctsao1008/spec2exec/issues/49): current implementation and research workstreams.

## Roadmap snapshot

Current active work is split between backend scaling and trust-chain hardening. POC-1C.B continues RV32 backend stress, while #53, #54, and A0 address the still-unimplemented semantic-authority and trust-oriented research layers. Arm M-profile, hosted portability, and physical RP2350 validation remain planned or pending.

## License

License selection remains intentionally pending.