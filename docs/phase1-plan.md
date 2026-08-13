# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **Next architecture experiment:** POC-1C.A — RV32I Native Pipeline Validation
- **Following architecture stress experiment:** POC-1C.B — Native Backend Stress
- **Later portability experiment:** POC-1D — Cross-Target Generation
- **Next semantic experiment:** POC-2 — State Machine
- **Parallel research:** A0 — Adversarial Semantic Resolution

## Objective

Phase 1 tests the deterministic lower half without connecting AI to executable generation.

Following RFC 0009, the primary architecture is:

```text
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

C and LLVM are optional reference/comparison paths rather than mandatory architecture stages.

## POC-1A — Bounded Integer Semantics

POC-1A uses `i32/u32`, straight-line `+ - *`, ranges, pre/postconditions, traceability, and `overflow_behavior = forbidden`.

The hardened implementation distinguishes signed-overflow and unsigned-wrap obligations. P3-A uses a model-scoped 32-bit bit-vector claim and `safe_add` retains exhaustive binary-behavior evidence for 10,201 accepted input pairs.

## POC-1B — C Semantic and Optimization Preservation

POC-1B uses generated C as a reference path for `safe_add_sub(a,b) = (a + b) - b`, with `a,b ∈ [-100,100]` and contract `result == a`.

The completed experiment carries separate BitVec, CBMC, optimization-observation, and executable-test evidence. It remains valid reference-path evidence; it does not make generated C mandatory in the final architecture.

## POC-1C Target Profile

The first native target is intentionally chosen to minimize incidental ISA complexity:

```text
ISA:            RISC-V RV32I base integer
M extension:    OFF
C extension:    OFF
A extension:    OFF
F/D extensions: OFF
Privileged ISA: outside the semantic target
ABI subset:     integer arguments / integer return only
Assembly:       GNU RISC-V syntax
Object model:   ELF32 RISC-V
```

The target choice is experiment-specific and must not leak into machine-independent SpecIR. See `docs/target-profiles.md`.

## POC-1C.A — RV32I Native Pipeline Validation

POC-1C.A tests the architectural claim before adding backend-stress complexity:

```text
Verified SpecIR
      ↓
RV32I Target Code Generator
      ↓
RV32I Target Assembly
      ↓
Existing Unmodified Assembler
      ↓
ELF32 Object
      ↓
Existing Unmodified Linker
      ↓
RV32I ELF
      ↓
Emulator / Runtime Evidence
```

Initial semantic scope reuses the bounded-arithmetic core and begins with `safe_add_sub`-class straight-line integer expressions.

### Operation support

For the first RV32I-only implementation, the target generator supports only SpecIR operations that are explicitly implemented and valid for the selected target profile.

Initial whitelist:

```text
add
sub
```

`mul` is rejected because POC-1C disables the RISC-V M extension and does not introduce a runtime helper or software-emulation sequence. Any unsupported operation must fail closed with an explicit target-generation error.

### Minimal resource model

The code generator must not be a per-example assembly template. It must include a minimal resource model:

```text
argument register locations
return register location
temporary register pool
acquire / release ownership for intermediate values
```

The first implementation uses a bounded temporary-register pool. Register exhaustion must fail explicitly; 1C.A must not silently reuse a live register or introduce an undeclared spill.

### Initial ABI subset

POC-1C.A supports an intentionally narrow integer ABI boundary:

```text
integer input arguments → a0, a1, ... as declared
integer return value    → a0
function return         → ret
```

No claim of general RISC-V ABI support is made.

The native acceptance path does not require a C test harness. A minimal assembly/runtime harness may be used so the primary native path remains independent of a high-level-language compiler. A C/LLVM path may still be used separately as a differential reference.

### Explicit non-requirements

POC-1C.A does not require:

```text
general register allocation
spill/reload
branches / CFG
function calls inside generated code
loops / recursion
pointers / heap / arrays
hardware registers / interrupts
TargetIR / MachineIR as a named stage
optimization
```

### Evidence classes and boundaries

POC-1C.A must keep its transformation boundaries separate:

```text
SpecIR property verification
    existing model-scoped SpecIR evidence

SpecIR → RV32I assembly preservation
    explicit P3 evidence class determined by the implemented checker
    initial implementation may be TESTED; stronger claims require a stronger mechanism

RV32I assembly → ELF32 object
    TRUSTED
    named assembler + version + invocation + exact artifact hashes

ELF32 object → linked RV32I ELF
    TRUSTED
    named linker + version + invocation + exact artifact hashes

RV32I ELF execution
    TESTED
    named emulator/runtime + version + declared test domain
```

Runtime/emulator agreement does not discharge the SpecIR→assembly preservation obligation.

The initial POC-1C.A trusted computing base must identify the Spec2Exec prototype/runtime environment, named assembler, named linker, and named emulator/runtime used for execution checks.

### Backend bookkeeping artifact

The code generator must emit a machine-readable bookkeeping artifact so backend pressure is measurable rather than subjective.

At minimum it records:

```text
target profile identity
SpecIR value → register/location mapping
ABI-fixed argument / return locations
temporary-register pool
temporary-pool high-water mark
spill count (must remain zero in 1C.A)
```

This artifact is backend decision evidence, not a mandatory TargetIR/MachineIR.

### POC-1C.A go criteria

Proceed to backend stress only if:

- valid supported bounded-arithmetic SpecIR emits RV32I assembly with no hand-edited intermediate artifacts;
- unsupported operations fail explicitly;
- code generation uses a generic temporary-register resource model rather than example-name hardcoding;
- register exhaustion fails explicitly and no silent spill/reuse occurs;
- the declared ABI subset is enforced;
- the unmodified assembler accepts the emitted assembly;
- the unmodified linker produces the target ELF;
- runtime/emulator results agree with SpecIR semantics over the declared test domain;
- exact artifact hashes bind the verified SpecIR, emitted assembly, object, linked ELF, and evidence records;
- the bookkeeping artifact is emitted and records register pressure;
- no object writer, instruction encoder, relocation engine, or linker logic is introduced into the Target Code Generator.

## POC-1C.B — Native Backend Stress

POC-1C.B deliberately attacks the direct backend after the minimal architecture path works.

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive function call
```

These cases test value-location pressure, cross-block consistency, and ABI/stack handling. The goal is not to build a general compiler backend; the goal is to determine when internal bookkeeping becomes too complex to remain local.

### TargetIR / MachineIR escalation rule

A named TargetIR/MachineIR remains optional until evidence shows it is useful. Promotion should be considered when one or more become general backend requirements:

```text
live values routinely exceed physical registers
spill/reload requires non-local reasoning
multi-block CFGs with merges become supported
loops require cross-block liveness
multiple call sites require persistent ABI-aware value placement
backend state becomes difficult to test as local tables/rules
```

POC-1C.B must report that pressure using the same bookkeeping/evidence model rather than hiding an ad hoc IR inside increasingly fragile code-generation logic.

## POC-1D — Cross-Target Generation

After the first native backend is validated, a later portability experiment should test the same machine-independent SpecIR against a second ISA family.

Initial planned sequence:

```text
POC-1C  RV32I
POC-1D  Cortex-M3 / ARMv7-M
later   Cortex-M4 / ARMv7E-M profile
```

The purpose is to test whether the same verified SpecIR can remain unchanged while target-specific semantics move through a selected Target Profile.

Cortex-M3 is the preferred first ARM portability target because it provides embedded relevance without introducing an FPU profile. Cortex-M4 follows as a related ARMv7E-M target, with FPU/float ABI declared explicitly when used.

SoC-specific memory maps, startup rules, and linker layouts belong to a separate optional Platform Profile rather than SpecIR. See `docs/target-profiles.md`.

## A0 — Semantic Resolution

A0 remains independent from executable generation. The benchmark/scoring harness exists; model baselines have not yet been run.

## POC-2 — State Machine

POC-2 remains the next semantic-complexity experiment. It introduces persistent finite-state behavior and measures transition correctness, invariant burden, solver scaling, evidence coverage, and SpecIR maintenance cost without simultaneously adding timing or hardware semantics.

A named MachineIR must not be introduced merely because POC-2 contains state; it should be introduced when backend control-flow/liveness complexity actually triggers the RFC 0009 escalation criteria.

## POC-3 — Thermal Motor Protection

POC-3 remains the first domain-significant embedded/control experiment, adding physical quantities, timing, fault/recovery behavior, provenance, and unresolved-requirement handling.

## Falsification orientation

The project should continue measuring engineering effort, defect detection, traceability, verification coverage, change propagation, and maintenance burden. A technically working pipeline is not sufficient evidence of value if its specification/verifier/backend complexity outweighs the benefits.
