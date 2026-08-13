# RFC 0009 — Native Target Code Generation

- **Status:** Accepted / Architecture Baseline
- **Scope:** Primary executable-generation path
- **Review status:** Closure review complete; no architecture blockers

## Summary

Spec2Exec shall not require a human-oriented programming language or a full C/C++ compiler stack as a mandatory stage between verified SpecIR and executable software.

The primary architecture path is:

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

`Target Assembly` means the assembly language of the selected ISA. An assembler may be replaced by an equivalent mature object emitter when that is the better target-toolchain interface.

## Decision

### 1. Native target generation is the primary path

Spec2Exec targets machine semantics directly. Native target code generation is therefore the primary path from verified SpecIR toward an executable artifact.

C and LLVM remain useful reference and comparison paths, but they are not required architectural intermediates.

### 2. No mandatory `Lowering` architecture stage

The transformation from SpecIR to target instructions necessarily performs lowering in the compiler-theory sense, but `Lowering` is not a mandatory top-level architecture component.

```text
Verified SpecIR
      ↓
Target Code Generation
      ↓
Target Assembly
```

A named `TargetIR` or `MachineIR` is optional. Machine-oriented bookkeeping is not optional once the backend needs it.

Even a minimal backend may need explicit state such as:

```text
SpecIR value → physical register / stack slot
available temporary-register pool
live temporary ownership
ABI argument / return locations
labels / symbolic branch targets
```

For POC-scale backends this state may remain an internal, small, testable data structure rather than a named IR stage.

A backend should promote that bookkeeping into an explicit TargetIR/MachineIR-style representation when one or more become general requirements:

- live values routinely exceed available physical registers;
- spill/reload placement requires non-local reasoning;
- multi-block control-flow graphs with merge points are supported;
- loops require cross-block liveness reasoning;
- multiple call sites require persistent ABI-aware value placement;
- backend state can no longer be validated cleanly as local tables/rules.

Promotion is driven by demonstrated complexity, not by compiler convention alone.

### 3. Machine-independent / target-specific boundary

```text
          MACHINE-INDEPENDENT
────────────────────────────────────
Accepted Specification
        ↓
      SpecIR
        ↓
Deterministic Verification
        ↓
   Verified SpecIR

════════════ TARGET BOUNDARY ════════════

        ↓
Target Code Generation
        ↓
Target Assembly
────────────────────────────────────
            TARGET-SPECIFIC
        ↓
Assembler / Object Emitter
        ↓
Object
        ↓
Linker
        ↓
Executable / Firmware
```

SpecIR remains machine-independent. ISA, ABI, register, calling-convention, stack-frame, instruction-selection, legalization, relocation-facing, and assembly-dialect concerns begin at the target boundary.

### 4. Target Profile and Platform Profile

Target-specific information is selected after SpecIR verification rather than embedded into SpecIR.

A **Target Profile** identifies the processor architecture/ISA, enabled architectural extensions, ABI subset, assembly dialect, object model, and other machine-level assumptions needed by Target Code Generation.

A separate optional **Platform Profile** carries SoC/board details below the ISA level, such as memory layout, startup/image conventions, and linker layout.

```text
SpecIR semantics
      ≠
Target Profile
      ≠
Platform Profile
```

Changing target or platform profile must not silently change the accepted machine-independent meaning of the same verified SpecIR.

See `docs/target-profiles.md`.

### 5. Backend roles and responsibilities

```text
Native target backend
    primary executable-generation path

C backend
    bootstrap / reference / differential-validation path

LLVM backend
    optional optimization / code-generation / comparison path
```

A target does not need a C compiler to be a valid Spec2Exec target.

The Target Code Generator owns, when required by the supported subset:

- SpecIR operation → target instruction selection;
- legalization and immediate/constant materialization;
- register/value placement policy;
- ABI argument and return-value placement;
- caller/callee-save handling when calls are supported;
- stack-frame/spill handling when stack use is supported;
- control-flow labels and branch selection when supported;
- syntactically valid target-assembly emission.

A narrow POC may use fixed or greedy policies, but those policies must be explicit and must not be presented as general register allocation or general ABI support.

The external assembler/object emitter owns assembly parsing, instruction encoding, directives, symbol/relocation creation, and object emission. The external linker owns symbol resolution, relocation application, section/memory placement, and final image construction.

Without a future explicit architecture decision, the Target Code Generator must not implement raw instruction encoding, object-file serialization, relocation processing, cross-object symbol resolution, or linking.

### 6. Minimal target infrastructure and TCB

Practical target support requires sufficient information/tooling for the target ISA semantics and encoding, ABI/calling convention when applicable, required memory/register conventions, object/relocation model when used, assembler/object emitter, and linker/image construction when required.

A full high-level-language compiler is not an inherent prerequisite.

For the primary native path, assembler and linker are explicit downstream trusted or separately checked components unless independent evidence is supplied for those boundaries.

### 7. Semantic-preservation and downstream evidence boundaries

The native semantic-preservation obligation is target-boundary equivalence rather than source-language equivalence:

```text
Accepted Preconditions
        ⇒
SpecIR Observable Semantics
        =
Target ISA Observable Semantics
```

The exact mechanism is target-profile dependent. Evidence must remain model-scoped and identify the target assembly artifact to which it is bound.

The native semantic-preservation claim terminates at Target Assembly unless downstream transformations are separately validated.

The evidence model is refined as:

```text
P3    SpecIR → Target Assembly
P4-A  Target Assembly → Object
P4-L  Object → Linked Executable
P4-R  Linked Executable → Runtime Observation
```

No single PASS may collapse these boundaries. Runtime agreement does not discharge P3.

See RFC 0006 for evidence classes and TCB requirements.

## First Native Target Profile — POC-1C

POC-1C selects this experimental profile:

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

This is a POC Target Profile, not a restriction embedded into SpecIR.

## POC-1C Experimental Split

### POC-1C.A — Native Pipeline Validation

POC-1C.A tests one architectural claim:

> Can verified SpecIR generate native target assembly and an executable artifact without requiring C, LLVM IR, or another high-level-language compiler stage?

It reuses the current bounded-arithmetic semantic core and begins with `safe_add_sub`-class straight-line arithmetic.

Initial target-operation whitelist:

```text
add
sub
```

`mul` is rejected because the POC-1C target profile disables the RISC-V M extension and does not introduce a runtime helper or software-emulation sequence. Any unsupported operation fails closed with an explicit target-generation error.

The code generator must use a minimal register-resource model rather than hard-coded per-example instruction templates. It models argument locations, return location, a temporary-register pool, and acquire/release ownership for intermediates.

Register exhaustion must fail explicitly. POC-1C.A must not silently reuse a live register or introduce an undeclared spill.

The initial integer ABI subset is intentionally narrow:

```text
inputs  → a0, a1, ... as declared
return  → a0
return instruction → ret
```

No general RISC-V ABI claim is made.

The primary native acceptance path does not require a C test harness. A C/LLVM path may still be used separately as a differential reference.

POC-1C.A does not require a general register allocator, spilling, control flow, internal function calls, loops, pointers/heap/arrays, hardware-register semantics, optimization, or a named TargetIR/MachineIR.

### POC-1C.A evidence and bookkeeping

Each transformation boundary must carry its own evidence class. The initial plan is:

```text
SpecIR property verification
    reuse existing model-scoped SpecIR evidence

SpecIR → RV32I assembly
    explicit P3 evidence; initial implementation may be TESTED
    stronger evidence requires a stronger checking mechanism

RV32I assembly → ELF32 object
    TRUSTED; named assembler/version/invocation + exact artifact hashes

ELF32 object → linked RV32I ELF
    TRUSTED; named linker/version/invocation + exact artifact hashes

RV32I ELF execution
    TESTED; named emulator/runtime + declared test domain
```

The backend must also emit a machine-readable bookkeeping artifact containing at least target-profile identity, value→location mapping, ABI-fixed locations, temporary-register pool, high-water mark, and spill count.

That artifact is backend decision evidence, not a mandatory TargetIR/MachineIR.

### POC-1C.B — Native Backend Stress

After POC-1C.A passes, POC-1C.B deliberately stresses the assumptions that made the direct backend small:

```text
B1  multiple live values / forced spill
B2  single branch + single merge
B3  single non-recursive call
```

The experiment measures when backend bookkeeping should be promoted into an explicit TargetIR/MachineIR-style representation. It must not prejudge that result.

## Later Cross-Target Direction

After the first native backend is validated, a later portability experiment should apply the same machine-independent SpecIR to a second ISA family.

Planned order:

```text
POC-1C  RV32I
POC-1D  Cortex-M3 / ARMv7-M
later   Cortex-M4 / ARMv7E-M
```

Cortex-M3 is the preferred first ARM portability target. Cortex-M4 follows as a related ARMv7E-M Target Profile, with any FPU/float-ABI choices declared explicitly.

SoC-specific configuration belongs to Platform Profiles rather than SpecIR.

## Relationship to POC-1A / POC-1B

POC-1A and POC-1B intentionally used generated C to bootstrap and stress the deterministic preservation/evidence architecture. Those experiments remain valid within their recorded scope as reference paths.

## Consequences

This decision moves Spec2Exec beyond a specification frontend for conventional compilers. A native backend makes Spec2Exec responsible for target code-generation decisions that a traditional compiler backend would otherwise own.

The architecture accepts that responsibility deliberately while keeping backend-internal machinery proportional to demonstrated complexity.

## Guardrails

- SpecIR must not absorb ISA-specific details merely to simplify a backend.
- Target-specific semantics begin at the Target Code Generation boundary.
- `Lowering` remains a transformation concept, not a mandatory architecture box.
- A named TargetIR/MachineIR is optional; required machine-oriented bookkeeping must still be explicit and testable.
- Native backend evidence must distinguish semantic checking from assembler, linker, ABI, object-format, emulator, and hardware assumptions.
- Target Code Generation must not reimplement instruction encoding, object writing, relocation processing, or linking without a separate architecture decision.
- Unsupported target operations and resource exhaustion must fail closed.
- A backend should reuse the lowest trustworthy target infrastructure available rather than require a larger compiler stack by default.
