# Phase 1 Plan — Minimal SpecIR and Deterministic Pipeline

- **Status:** Active
- **POC-0:** complete
- **POC-1A:** complete and evidence-hardened
- **POC-1B:** complete for the initial host-C reference experiment
- **Next architecture experiment:** POC-1C.A — RV32I Native Pipeline Proof
- **Following architecture stress experiment:** POC-1C.B — Native Backend Stress
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

The hardened implementation distinguishes:

```text
P2.no_signed_overflow_ub
P2.no_unsigned_wraparound
```

P3-A uses a model-scoped 32-bit bit-vector claim:

```text
P3A.restricted_emitted_expression_equivalence = SOLVER_PROVEN
semantic_model = fixed-width-bitvector-v1
```

Its recorded obligations are:

```text
Q0 domain_non_vacuous       SAT
Q1 no_overflow_or_wrap      UNSAT
Q2 encoder_cross_check      UNSAT
Q3 result_equivalence       UNSAT
Q4 harness_sensitivity      SAT
```

P2 interval analysis and P3-A bit-vector safety cross-validate each other. For `safe_add`, P4 executes all 10,201 accepted input pairs and records `TESTED_EXHAUSTIVE`.

## POC-1B — C Semantic and Optimization Preservation

POC-1B adds an independent C-aware reference path using CBMC.

```text
function: safe_add_sub
body:     (a + b) - b
a,b:      i32 [-100,100]
overflow: forbidden
contract: result == a
```

The first successful CI run recorded:

```text
P3-A BitVec model             SOLVER_PROVEN
P3-B generated-C contract     MODEL_CHECKED
Clang -O0 add/sub count       2
Clang -O2 add/sub count       0
P4 exhaustive cases           40,401
POC-1B result                 PASS
```

This remains valid reference-path evidence. It does not make generated C a mandatory final architecture stage. See RFC 0008 and RFC 0009.

## POC-1C target profile

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

The target choice is experiment-specific and must not leak into machine-independent SpecIR.

## POC-1C.A — RV32I Native Pipeline Proof

POC-1C.A proves the architectural point before adding backend stress complexity:

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

The code generator must not be a per-example assembly template. It must include a minimal resource model such as:

```text
argument register locations
return register location
temporary register pool
acquire / release ownership for intermediate values
```

POC-1C.A explicitly does not require:

```text
general register allocation
spill/reload
branches / CFG
function calls
loops / recursion
pointers / heap / arrays
hardware registers / interrupts
TargetIR / MachineIR as a named stage
optimization
```

### POC-1C.A evidence goals

Evidence should keep transformation boundaries separate:

```text
SpecIR semantic verification
SpecIR → RV32I assembly preservation evidence
assembly artifact identity
assembly → object toolchain evidence
object → ELF linker evidence
ELF emulator/runtime behavior evidence
```

Assembler and linker assumptions must be explicit; executable behavior must not inherit a Target-Assembly proof automatically.

### POC-1C.A go criteria

Proceed to backend stress only if:

- valid bounded-arithmetic SpecIR emits RV32I assembly with no hand-edited intermediate artifacts;
- code generation uses a generic temporary-register resource model rather than example-name hardcoding;
- the unmodified assembler accepts the emitted assembly;
- the unmodified linker produces the target ELF;
- runtime/emulator results agree with SpecIR semantics over the declared test domain;
- artifact hashes bind the verified SpecIR, emitted assembly, object, and linked ELF where practical;
- no object writer, instruction encoder, relocation engine, or linker logic is introduced into the Target Code Generator.

## POC-1C.B — Native Backend Stress

POC-1C.B deliberately attacks the direct backend after the minimal architecture path works.

Planned stress sequence:

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive function call
```

These cases test the first backend failure cliffs identified by hostile review: value-location pressure, cross-block consistency, and ABI/stack handling.

POC-1C.B may use deliberately simple fixed or greedy policies. The goal is not to build a general compiler backend; the goal is to determine when internal bookkeeping becomes too complex to remain local.

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

POC-1C.B must report that pressure rather than hiding an ad hoc IR inside increasingly fragile code-generation logic.

## A0 — Semantic Resolution

A0 remains independent from executable generation. The benchmark/scoring harness exists; model baselines have not yet been run.

## POC-2 — State Machine

POC-2 remains the next semantic-complexity experiment. It introduces persistent finite-state behavior and measures transition correctness, invariant burden, solver scaling, evidence coverage, and SpecIR maintenance cost without simultaneously adding timing or hardware semantics.

POC-1C and POC-2 answer different questions:

```text
POC-1C  validates the native target architecture
POC-2   validates behavioral-state semantics
```

A named MachineIR must not be introduced merely because POC-2 contains state; it should be introduced when backend control-flow/liveness complexity actually triggers the RFC 0009 escalation criteria.

## POC-3 — Thermal Motor Protection

POC-3 remains the first domain-significant embedded/control experiment, adding physical quantities, timing, fault/recovery behavior, provenance, and unresolved-requirement handling.

## Falsification orientation

The project should continue measuring engineering effort, defect detection, traceability, verification coverage, change propagation, and maintenance burden. A technically working pipeline is not sufficient evidence of value if its specification/verifier/backend complexity outweighs the benefits.
