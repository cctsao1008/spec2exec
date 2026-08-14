# Spec2Exec

**Specification-to-Executable Architecture**

> Spec2Exec explores specification as the primary human-facing artifact between intent and executable software.

## Why Spec2Exec?

**AI is making software implementation cheap. It is not making software trust cheap.**

A generated system can compile, pass tests, behave consistently, and even satisfy a formal specification while still implementing semantics that were never explicitly authorized.

That is the trust gap Spec2Exec is designed to address.

Software can fail without containing an obvious coding bug. A program may correctly execute the wrong rule, an incomplete rule, an outdated rule, or a plausible assumption that nobody actually accepted.

```text
implementation correctness
        !=
semantic correctness
        !=
semantic authority
```

A bug-free implementation does not imply that the implemented behavior is the right behavior. A formally verified implementation does not, by itself, prove that the formal specification represents the semantics that should have been executed.

### Why this becomes more important with AI

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

| Domain | Example intent | Semantics that still require authority |
|---|---|---|
| Medical / healthcare | "Alert when the patient is deteriorating." | What counts as deterioration? Which measurements are authoritative? What happens with missing or conflicting sensors? How urgent must the response be? |
| Aviation | "Switch to the backup source when the primary system fails." | What constitutes failure? How long may it persist? What if sources disagree? What state is required if both are unavailable? |
| Security | "Grant access to administrators." | Which role? Which resources? Under what context? What exceptions or emergency paths are permitted? |
| Finance | "Reject suspicious transactions." | What is suspicious? What happens near a threshold? Which exceptions are authorized? |
| Cloud / distributed systems | "Retry failed requests." | Which failures are retryable? How many times? Is the operation idempotent? What happens when the retry budget is exhausted? |
| Embedded / robotics / industrial control | "Limit actuator behavior when conditions are unsafe." | Which conditions? What limit? What if sensing is invalid? How quickly must the system react? |

Different domains fail in different ways, but the trust question is the same:

> **Who authorized the semantics, what was actually verified, and what evidence binds those claims to the executable that will run?**

### Why existing tools are not enough by themselves

Spec2Exec does not assume that testing, code review, formal methods, compilers, or runtime validation are ineffective. They are essential. The problem is that each normally establishes only part of the trust chain.

| Method | It can provide evidence about | It does not automatically establish |
|---|---|---|
| Unit / integration testing | Observed behavior for selected cases | Whether the tested semantics were authorized or complete |
| Code review | Whether an implementation appears reasonable and maintainable | Whether every hidden assumption was detected and approved |
| Static analysis | Specific program properties and defect classes | Whether the requirement itself is correct or authoritative |
| Formal verification | Whether a formal artifact satisfies stated properties under assumptions | Whether those stated properties represent the semantics that should have been executed |
| Compiler / transformation correctness | Whether a transformation preserves defined source semantics | Whether the source semantics themselves were the right semantics |
| Runtime / hardware testing | What the built artifact actually did under tested conditions | Whether the oracle, domain, assumptions, or semantic authority were complete |

The missing piece is not another single PASS result. It is an explicit chain connecting **authorized semantics**, **verification claims**, **evidence**, **exact artifacts**, and **real execution**.

Spec2Exec therefore aims to complement existing engineering tools by connecting their evidence rather than replacing them.

### The Spec2Exec response

```text
Human / Domain Intent
        ↓
Candidate Semantics
        ↓
Ambiguity / Conflict / Missing-Semantics Detection
        ↓
Semantic Authority Gate
        ↓
Accepted Specification
        ↓
Candidate SpecIR
        ↓
Deterministic Verification
        ↓
Verified SpecIR
        ↓
Portable Target Realization
        ↓
Executable / Firmware
        ↓
Runtime / Emulator / Hardware Observation

Across the entire chain:
Claim ↔ Evidence ↔ Artifact ↔ Tool ↔ Assumption ↔ Provenance
```

The goal is not to pretend that every layer is formally proven. The goal is to make it explicit **what is accepted, what is checked, what is tested, what is proven, what is trusted, and what remains unresolved**.

## Project thesis

Spec2Exec is not primarily an AI coding tool and is not defined by any particular synthesis model. Its long-term direction is **trust infrastructure for AI-generated software**: separate proposal from semantic authority, bind accepted semantics to deterministic verification and explicit evidence, and preserve that trust chain into executable behavior.

> **AI proposes. Humans authorize semantics. Deterministic systems verify. Evidence justifies trust. Portable backends execute.**

The normative architecture is more general than human-only approval: semantic authority may also come from accepted parent specifications, standards, certified domain models, system contracts, safety authorities, or other explicit governance sources. AI and other synthesis systems are replaceable proposal engines; they do not gain semantic authority merely by producing plausible or high-quality output.

The project value framework is a trust chain:

```text
#1 Trust Architecture
        ↓
#2 Specification / Semantic Authority Model
        ↓
#3 Evidence Architecture
        ↓
#4 Deterministic Verification
        ↓
#5 Portable Executable Realization
   + Preservation Evidence
        ↓
#6 AI Synthesis Quality
```

The core is #1–#4. Portable realization extends accepted semantics to real machines. AI synthesis quality improves productivity and proposal quality, but remains outside the trusted semantic core by default.

See `rfcs/0010-trust-chain-architecture.md` for the project-level trust thesis and long-term invariants.

## Primary architecture

```text
Human Intent
    ↓
Accepted Specification
    ↓
SpecIR
    ↓
Deterministic Verification
    ↓
Verified SpecIR
    ↓
Target Code Generation
    ↓
Target Assembly
    ↓
Assembler
    ↓
Object
    ↓
Linker
    ↓
Executable / Firmware
```

Native target code generation is the primary path. C and LLVM remain optional reference/comparison paths.

SpecIR remains machine-independent. A concrete executable target is composed from an **ISA Profile**, an **Execution Profile**, and an optional **Platform Profile**. A specific CPU core or development board may be used as validation hardware, but it is not the architectural target unless the generated semantics explicitly depend on that core or platform.

## Target coverage goal

Spec2Exec is intended to be implementable across major CPU ISA families and major execution environments without changing machine-independent SpecIR semantics.

```text
ISA families
    x86_64
    AArch64 / Arm64
    RISC-V RV32 / RV64
    Arm M-profile

Execution environments
    Linux
    Windows
    macOS
    bare metal
```

Not every ISA/OS pair is valid or useful. Each supported target configuration must explicitly identify its ISA, ABI, object/executable model, runtime environment, and platform assumptions.

## Validation platforms

Validation hardware is deliberately separate from architecture coverage.

The planned embedded hardware validation platform is Raspberry Pi Pico 2 / RP2350 because the same SoC can execute with either of two CPU-core families:

```text
RP2350 / Pico 2
├── Hazard3 RISC-V cores
│   └── planned hardware validation of the RV32I bare-metal target path
└── Arm Cortex-M33 cores
    └── planned hardware validation of the Armv8-M Mainline bare-metal target path
```

Pico 2 is therefore a **validation platform**, not a Spec2Exec architecture target.

## Status

```text
POC-0     COMPLETE
POC-1A    COMPLETE
POC-1B    COMPLETE
POC-1C.A  EMULATOR-PASS  RV32I bare-metal native pipeline
          HW-PENDING     Hazard3 / RP2350 / Pico 2 physical validation
POC-1C.B  NEXT-ARCH      RV32 backend stress
POC-1D    PLANNED        Armv8-M Mainline bare-metal cross-target validation
POC-1E    PLANNED        hosted ISA / OS expansion
POC-2     NEXT-SEMANTIC
POC-3     PLANNED
A0        PARALLEL
```

POC-1C.A now has a working C-free native path in CI:

```text
machine-independent SpecIR
    ↓
RV32I code generation
    ↓
GNU assembler
    ↓
ELF32 object
    ↓
GNU linker
    ↓
RV32I ELF
    ↓
QEMU rv32 virt
    ↓
40,401 exhaustive runtime cases
```

The successful baseline records `P3` as `TESTED`, assembler/linker boundaries as `TRUSTED`, and runtime behavior as `TESTED_EXHAUSTIVE`; it does not claim a formally verified native compiler. See `docs/poc1c-results.md`.

POC-1D will validate the Armv8-M Mainline bare-metal path using Cortex-M33 as the initial hardware core. POC-1E begins hosted portability with reusable ISA and Execution Profiles. Initial hosted configurations are planned around x86_64/Linux, x86_64/Windows, AArch64/Linux, and AArch64/macOS, followed by AArch64/Windows and RV64/Linux when practical.

The intended long-term model is:

```text
                         same Verified SpecIR
                                 │
                  ┌──────────────┼──────────────┐
                  ▼              ▼              ▼
               RISC-V           Arm           x86_64
             RV32 / RV64   M-profile/AArch64     │
                  │              │              │
                  └──────────────┼──────────────┘
                                 ▼
                       Execution Profiles
                  Linux / Windows / macOS
                         bare metal
                                 │
                                 ▼
                    optional Platform Profile
                                 │
                                 ▼
                      Executable / Firmware
```

See `rfcs/0010-trust-chain-architecture.md`, `rfcs/0005-trust-intent-fidelity-and-specification-acceptance.md`, `rfcs/0006-semantic-preservation-and-evidence-model.md`, `rfcs/0009-native-target-code-generation.md`, `docs/target-profiles.md`, `docs/phase1-plan.md`, and `docs/poc1c-results.md`.

## License

License selection remains intentionally pending.
