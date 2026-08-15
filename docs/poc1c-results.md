# POC-1C — RV32I Native Pipeline Validation Results

- **POC-1C.A native emulator baseline:** CLOSED / PASS
- **POC-1C.B entry hardening:** COMPLETE
- **Semantic-authority MVI:** IMPLEMENTED / PASS for the bounded POC-1C subject
- **Target configuration:** RV32I + bare metal
- **Validation platform:** QEMU `rv32 virt`
- **Physical hardware validation:** pending
- **Latest authority-gated tested revision:** `c96f08c46920d80a619ac6be58507e506e0850da`
- **GitHub Actions run:** `31879494912`
- **POC-1C tests:** 50 / 50 PASS

## What is validated

The current supported POC-1C CLI path now exercises:

```text
Candidate POC Specification
        ↓
Bound Authority Manifest
        ↓
Deterministic Semantic Authority Gate
        ↓
Authority Acceptance Record
        ↓
Target-neutral P1 / P2 verification
        ↓
Machine-independent SpecIR
        ↓
RV32I Target Code Generator
        ↓
RV32I assembly
        ↓
GNU assembler (-march=rv32i -mabi=ilp32)
        ↓
Generated ELF32 RISC-V object
        ↓
Trusted bare-metal validation harness
        ↓
GNU linker
        ↓
Validation ELF
        ↓
QEMU rv32 virt
        ↓
40,401-case exhaustive accepted-contract observation
```

No generated C, LLVM IR, or another high-level-language compiler stage participates between SpecIR and target assembly in the primary path.

The generated Spec2Exec target object remains RV32I-only. The trusted validation harness uses Zicsr only to install `mtvec` for the observable diagnostic trap path; this does not widen generated target semantics.

## Test subject

```text
safe_add_sub(a, b) = (a + b) - b

a,b ∈ [-100,100]
overflow_behavior = forbidden
accepted runtime contract: result == a
contract trace: REQ-OPT-001-EQ
```

The generated target code remains:

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

Runtime validation observes accepted semantics, not instruction-tree identity. A semantically equivalent target program may have a different instruction structure.

## Semantic-authority MVI

RFC 0011 defines the accepted semantic-authority baseline. The first executable implementation is intentionally small and tied to the real POC-1C subject.

### Bound authority records

The specification binds:

```text
examples/optimization-preservation/authority/manifest.json
```

which hash-binds:

```text
anchor.json
policies.json
obligations.json
closure.json
```

The POC authority set contains:

- one `AuthorityAnchor`: `ANCHOR-POC1C-PROJECT`;
- an explicit repository-declared / unauthenticated anchor-protection mechanism;
- a selected-build `VALUE` authorization;
- a direct human-declared `VALUE` authorization for `overflow_behavior = forbidden`;
- a delegated `VALUE_SET` policy for each input range;
- a deterministic `CONSTRAINT` requiring selected input ranges to stay inside `[-100,100]`;
- an explicit executable semantic closure containing all three semantic obligations.

### Semantic obligations

```text
AUTH-OVF-001   REQ-OPT-001-OVF       overflow_behavior = forbidden
AUTH-DOMAIN-A  REQ-OPT-001-A.range   a ∈ [-100,100]
AUTH-DOMAIN-B  REQ-OPT-001-B.range   b ∈ [-100,100]
```

The authority gate checks exact specification locators, policy revisions, attribution mechanisms, classification bases, closure completeness, applicable-grant completeness, and constraint satisfaction before the base P1/P2 pipeline is entered.

### Semantic completeness

The explicit `ClosureRecord` must account for every candidate semantic-obligation record as either included or excluded. Exclusion requires an authorized or deterministic basis.

The MVI therefore rejects a candidate that disappears from authority gating merely because an untrusted classification says it is not applicable.

### Authority completeness

Authority evaluation discovers potentially applicable policies from the full bound policy set rather than trusting only the policy ID supplied by an obligation.

For each obligation it records:

```text
authority_bindings_used
authority_grants_evaluated
authority_grants_applicable
authority_grants_rejected_as_inapplicable + basis
```

If one applicable grant allows the selected value while another applicable grant contradicts it, the MVI fails closed with an authority conflict rather than silently selecting the favorable binding.

### Authority TCB limitation

The POC anchor and repository write-access protection are **human-declared / unauthenticated trust inputs**. The deterministic gate can `CHECK` that exact records, revisions, hashes, scopes, and grants satisfy the declared authority model; it does not prove that the project owner identity or repository protection is cryptographically authenticated.

No claim of certification, cryptographic approval, enterprise policy management, quorum, or general authority completeness outside the explicitly enumerated POC subject is made.

## Authority fail-closed coverage

The 22 authority tests cover positive and negative cases including:

```text
bound record set                                             ACCEPTED
human-declared VALUE + delegated VALUE_SET                  ACCEPTED
closure CONSTRAINT                                           CHECKED
manifest component tamper                                    REJECTED
missing anchor                                               REJECTED
authority policy cycle                                       REJECTED
missing bound policy                                         REJECTED
value outside delegated VALUE_SET                            REJECTED
stale policy revision                                        REJECTED
stale anchor revision                                        REJECTED
UNRESOLVED obligation                                        REJECTED
semantic CONFLICT                                            REJECTED
scope mismatch                                               REJECTED
missing provenance                                           REJECTED
self-authorization policy violation                          REJECTED
redelegation in MVI                                          REJECTED
missing authority-relevant classification basis              REJECTED
closure exclusion without basis                              REJECTED
selected configuration without authority policy              REJECTED
contradictory applicable authority grant                     REJECTED
POTENTIALLY_STALE authority dependency                       REJECTED
closure constraint violation                                 REJECTED
```

Representative structured categories include:

```text
E_AUTH_NO_ANCHOR
E_AUTH_CYCLE
E_AUTH_UNRESOLVED
E_AUTH_CONFLICT
E_AUTH_AUTHORITY_CONFLICT
E_AUTH_NO_POLICY
E_AUTH_SCOPE
E_AUTH_VALUE_OUT_OF_SET
E_AUTH_SELF_AUTHORIZATION
E_AUTH_REDELEGATION
E_AUTH_PROVENANCE
E_AUTH_ATTRIBUTION
E_AUTH_POTENTIALLY_STALE
E_AUTH_CONSTRAINT
E_AUTH_CLOSURE
```

The exact code names remain implementation details; the fail-closed categories are architecture-significant.

## Evidence boundary A1

The authority-gated path adds a new evidence claim before P1/P2:

```text
A1.semantic_authority_gate
status: CHECKED
method: deterministic-authority-gate-v0.1
```

The claim is bound to:

- the accepted POC specification hash;
- authority-manifest hash;
- anchor/policies/obligations/closure component hashes;
- the generated authority acceptance record hash;
- source files for the authority evaluator/wrapper/schema;
- the declared Authority TCB and attribution limitations.

`A1 = CHECKED` means the deterministic evaluator accepted the exact bound authority records under the declared POC model. It does **not** mean the AuthorityAnchor itself is `PROVEN` or authenticated.

## Existing P1/P2/P3/P4 evidence boundaries

The result deliberately does not collapse the pipeline into one PASS:

```text
A1                bound POC authority model → acceptance     CHECKED
P1/P2             specification / SpecIR obligations         CHECKED
P3                SpecIR → generated RV32I assembly          TESTED
P4-A              generated assembly → generated object      TRUSTED
P4-H              validation harness → harness object        TRUSTED
P4-L              bound objects + linker script → ELF        TRUSTED
P4-R              linked ELF → accepted contract             TESTED_EXHAUSTIVE
P4-R.sensitivity  known-bad controls → failure channel       TESTED
```

`P3` is not a formal equivalence proof. `P4-R` means the linked validation executable satisfied `result == a` for every input pair in the mechanically bound `[-100,100] × [-100,100]` domain. Runtime agreement does not prove compiler correctness.

RFC 0006 is the canonical owner of the evidence vocabulary. `TESTED_EXHAUSTIVE` remains execution evidence and is not `PROVEN`.

## Backend invariants

The direct backend still records/enforces:

```text
arguments                    a0..a7
return                       a0
temporary register pool      t0..t6
spill count                  0 for POC-1C.A
callee-saved policy          forbidden without explicit save/restore
preferred_dest policy        root-only
temporary high-water mark    1 for safe_add_sub
```

Until explicit save/restore support exists, generated code fails closed if it touches `s0..s11`, `sp`, `gp`, or `tp`. `preferred_dest` remains root-only so recursive placement cannot silently overwrite a still-live ABI argument.

## Entry-hardening safeguards retained

The earlier POC-1C hardening remains active:

- QEMU SiFive finisher FAIL encodes process exit code `1`;
- negative controls require exact expected failure status;
- runtime sensitivity is separately recorded as `P4-R.sensitivity`;
- two non-equivalent target-code mutations are assembled, linked, executed, and required to exit `1`;
- an `ebreak` mutation exercises the synchronous-trap path and exits `1`;
- runtime case-counter initialization/increment/final assertion is mechanically bound;
- harness matching strips comments and checks the required execution skeleton;
- runtime contract is a verified specification clause;
- P1/P2 remain target-neutral;
- Target Configuration selects generated-code assembler flags/link mode;
- generated-code and harness assembler flags remain distinct;
- source revision and working-tree cleanliness are recorded;
- `run.py`, workflow, harness, linker script, backend/pipeline/verifier/authority sources, target configuration, tools, invocations, authority records, and generated artifacts are evidence-bound.

## Bare-metal runtime infrastructure

```text
linker script
    reserves 4096-byte aligned stack region
    exports __stack_top

_start
    initializes sp
    installs mtvec

trap handler
    uses the SiFive test-finisher failure channel
    exits QEMU with status 1
```

The trap path is dynamically tested with an `ebreak` probe.

## CI coverage

GitHub Actions run `31879494912` executes **50 tests** plus the full native pipeline and QEMU runtime/sensitivity path.

The test count includes the previous 28 verifier/backend/runtime tests plus 22 authority-specific tests.

CI uses:

```text
POC1C_REQUIRE_RUNTIME=1
```

so runtime and sensitivity checks cannot silently skip because QEMU/toolchain dependencies are unavailable.

The POC-1C workflow path filters now also include:

```text
examples/optimization-preservation/**
spec/schemas/authority-v0.1.schema.json
```

so changes to authority records or the authority schema trigger the validation workflow.

## Toolchain and target binding

Successful CI environment remains:

```text
GitHub runner OS          Ubuntu 24.04.x
Python                    3.12.x
GNU assembler             2.42
GNU linker                2.42
QEMU                      8.2.2
```

Validated target bindings:

```text
Architectural target
    ISA Profile           riscv / rv32i / extensions=[]
    Execution Profile     bare-metal / ilp32-integer-subset / elf32-riscv

Generated target object
    assembler flags       -march=rv32i -mabi=ilp32

Trusted validation harness
    assembler flags       -march=rv32i_zicsr -mabi=ilp32
    Zicsr purpose         mtvec installation only

Linker
    flags                 -m elf32lriscv
```

## Runtime-domain and sensitivity result

```text
a range                   [-100,100]
b range                   [-100,100]
expected cases            40,401
observed cases            40,401
runtime oracle            result == a
runtime oracle kind       accepted-contract-observation
contract trace            REQ-OPT-001-EQ
failure status            1
```

Sensitivity observations from run `31879494912`:

```text
wrong-final-operation     exit 1
wrong-first-operation     exit 1
trap-path-ebreak          exit 1
```

## Authority-gated successful-run artifact bindings

Tested revision:

```text
c96f08c46920d80a619ac6be58507e506e0850da
```

Key generated SHA-256 values:

```text
target-config.json
9160ba245268499fd22d4537efb586d61eceb9719290670553d6bf4a393d750b

safe_add_sub.s
9e78282830b5e9e87a69b22dc0c358bd07bcff248f04f2709792f45973892a6b

safe_add_sub.o
027486b5efe99dfc21356d26620f9523316db0e32b1a5266396b96f62f799b7d

safe_add_sub.elf
fb029132a30d8030128edf8f373978ee1643a220c448fc02d06fc95ad26fffc8

backend-state.json
62ea82ccd47f5d587866b9f2aac25cc7d934f4963df723e16fbfe702e15b377c

evidence.json
a8db31ec9e69cd46d2a573768593e51e3da3d1894482ddb4f4f4de2c76757826
```

The generated assembly/object/ELF hashes are unchanged from the earlier entry-hardening baseline. The authority work changed the entry/evidence chain, not the target behavior for this subject.

The run also binds the authority-manifest and its exact components into `evidence.json`.

## Validation binding

Completed:

```text
validation kind: emulator
emulator:        qemu-system-riscv32
machine:         virt
architectural target: RV32I + bare metal
```

Planned physical validation remains separate:

```text
validation kind: hardware
CPU core:        Hazard3 RISC-V
SoC:             RP2350
board:           Raspberry Pi Pico 2
```

Pico 2 is validation hardware, not an architectural target. Physical Hazard3/RP2350 execution is not part of this evidence set.

## Current limitations

The authority MVI is not a general authority-management platform. Specifically, the tested baseline does not provide:

- cryptographic signature/identity binding;
- quorum or dual approval;
- redelegation/delegation depth beyond the fail-closed MVI;
- cross-anchor precedence resolution beyond fail-closed conflict;
- rich requirements/standards/AI extraction adapters;
- multi-configuration executable-closure inference;
- runtime/post-deployment revocation enforcement;
- enterprise authority-policy lifecycle;
- certification or regulatory qualification.

The explicit POC closure and repository-declared Authority TCB are research limitations, not hidden assumptions.

## Remaining work

POC-1C.A and its entry-hardening baseline remain complete. The semantic-authority MVI is now validated for the current subject.

The next backend experiment remains:

```text
#37 — multiple live values / forced spills
```

Other non-blocking follow-ups include:

```text
end-to-end unsigned-32 validation
register-pressure-aware expression ordering
future constant/immediate legalization
physical Hazard3 / RP2350 validation
optional linked-image disassembly / ISA audit
broader authority ingestion / authentication beyond the MVI
```

## Result

POC-1C now demonstrates a working **authority-gated, C-free executable-generation path** for the declared RV32I subset through native target assembly and conventional assembler/linker tooling, with deterministic authority checks over a bounded POC authority model and exhaustive emulator-side accepted-contract observation over the declared runtime domain.

This does not upgrade P3 to a formal compiler-correctness proof, authenticate the project AuthorityAnchor cryptographically, certify the software, or constitute physical-hardware validation.
