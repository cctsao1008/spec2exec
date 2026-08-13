"""POC-1C.A RV32I target validation and code generation."""

from __future__ import annotations

from typing import Any

SPECIR_VERSION = "spec2exec.specir/v0.1"
TARGET_CONFIG_VERSION = "spec2exec.target/v0.1"
SUPPORTED_TYPES = {"i32", "u32"}
SUPPORTED_OPS = {"+": "add", "-": "sub"}
ARG_REGS = [f"a{i}" for i in range(8)]
TEMP_REGS = [f"t{i}" for i in range(7)]


class Poc1CError(Exception):
    pass


def expect(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise Poc1CError(f"{code}: {message}")


def validate_target_config(doc: Any) -> dict[str, Any]:
    expect(isinstance(doc, dict), "E_TARGET_PROFILE", "target configuration must be an object")
    expect(doc.get("target_config_version") == TARGET_CONFIG_VERSION,
           "E_TARGET_PROFILE", f"target_config_version must be {TARGET_CONFIG_VERSION}")
    isa, exe = doc.get("isa_profile"), doc.get("execution_profile")
    expect(isinstance(isa, dict) and isinstance(exe, dict), "E_TARGET_PROFILE",
           "isa_profile and execution_profile must be objects")
    expect(isa.get("architecture") == "riscv", "E_TARGET_PROFILE", "architecture must be riscv")
    expect(isa.get("isa") == "rv32i", "E_TARGET_PROFILE", "POC-1C.A supports rv32i only")
    expect(isa.get("extensions") == [], "E_TARGET_PROFILE", "POC-1C.A requires no ISA extensions")
    expect(exe.get("environment") == "bare-metal", "E_TARGET_PROFILE", "environment must be bare-metal")
    expect(exe.get("abi") == "ilp32-integer-subset", "E_TARGET_ABI", "ABI must be ilp32-integer-subset")
    expect(exe.get("assembly_dialect") == "gnu-riscv", "E_TARGET_PROFILE", "assembly dialect must be gnu-riscv")
    expect(exe.get("object_model") == "elf32-riscv", "E_TARGET_PROFILE", "object model must be elf32-riscv")
    return doc


def validate_codegen_specir(doc: Any) -> dict[str, Any]:
    expect(isinstance(doc, dict) and doc.get("specir_version") == SPECIR_VERSION,
           "E_SPECIR", f"SpecIR version must be {SPECIR_VERSION}")
    fn = doc.get("function")
    expect(isinstance(fn, dict), "E_SPECIR", "function must be an object")
    expect("target" not in fn, "E_SPECIR_TARGET_LEAK",
           "machine-independent SpecIR must not contain function.target")
    expect(isinstance(fn.get("name"), str) and fn["name"], "E_SPECIR", "function.name required")

    inputs = fn.get("inputs")
    expect(isinstance(inputs, list) and inputs, "E_TARGET_ABI", "inputs must be non-empty")
    expect(len(inputs) <= len(ARG_REGS), "E_TARGET_ABI", "POC-1C.A supports at most eight integer arguments")
    symbols, types = set(), set()
    for inp in inputs:
        name, typ = inp.get("id"), inp.get("type")
        expect(isinstance(name, str) and name and name not in symbols, "E_SPECIR", "input ids must be unique")
        expect(typ in SUPPORTED_TYPES, "E_TARGET_ABI", "inputs must be i32 or u32")
        symbols.add(name)
        types.add(typ)
    expect(len(types) == 1, "E_TARGET_ABI", "mixed integer types are outside POC-1C.A")

    output = fn.get("output")
    expect(isinstance(output, dict) and output.get("type") in types, "E_TARGET_ABI",
           "output type must match input type")
    expect(fn.get("overflow_behavior") == "forbidden", "E_TARGET_SEMANTICS",
           "overflow_behavior must be forbidden")

    body = fn.get("body")
    expect(isinstance(body, dict) and body.get("kind") == "expr",
           "E_TARGET_UNSUPPORTED_OPERATION", "expression body required")

    def walk(expr: Any) -> None:
        if isinstance(expr, str):
            expect(expr in symbols, "E_SPECIR", f"unknown symbol {expr}")
            return
        if isinstance(expr, int) and not isinstance(expr, bool):
            raise Poc1CError("E_TARGET_UNSUPPORTED_LITERAL: integer literals are outside POC-1C.A")
        expect(isinstance(expr, dict), "E_TARGET_UNSUPPORTED_OPERATION", "operation node required")
        op, args = expr.get("op"), expr.get("args")
        expect(op in SUPPORTED_OPS, "E_TARGET_UNSUPPORTED_OPERATION", f"unsupported operation {op!r}")
        expect(isinstance(args, list) and len(args) == 2, "E_TARGET_UNSUPPORTED_OPERATION",
               "POC-1C.A operations must be binary")
        walk(args[0])
        walk(args[1])

    walk(body.get("expr"))
    return fn


class RegisterPool:
    def __init__(self) -> None:
        self.registers = list(TEMP_REGS)
        self.available = list(TEMP_REGS)
        self.in_use: list[str] = []
        self.high_water_mark = 0

    def acquire(self) -> str:
        if not self.available:
            raise Poc1CError("E_TARGET_OUT_OF_REGISTERS: temporary register pool exhausted")
        reg = self.available.pop(0)
        self.in_use.append(reg)
        self.high_water_mark = max(self.high_water_mark, len(self.in_use))
        return reg

    def release(self, reg: str) -> None:
        expect(reg in self.in_use, "E_BACKEND_STATE", f"register {reg} is not owned")
        self.in_use.remove(reg)
        self.available.insert(0, reg)


class RV32ICodeGenerator:
    def __init__(self, fn: dict[str, Any], target: dict[str, Any]) -> None:
        self.fn, self.target = fn, target
        self.pool = RegisterPool()
        self.lines: list[str] = []
        self.locations: dict[str, dict[str, Any]] = {}
        self.node = 0
        self.args = {inp["id"]: ARG_REGS[i] for i, inp in enumerate(fn["inputs"])}
        for name, reg in self.args.items():
            self.locations[f"input:{name}"] = {"kind": "abi-argument", "location": reg}

    def compile_expr(self, expr: Any, preferred_dest: str | None = None) -> tuple[str, bool]:
        if isinstance(expr, str):
            source = self.args[expr]
            if preferred_dest is not None and source != preferred_dest:
                # RV32I has no dedicated move instruction. Keep the target assembly
                # inside the base ISA rather than relying on the `mv` pseudo-op.
                self.lines.append(f"    add {preferred_dest}, {source}, zero")
                self.locations[f"expr:{self.node}"] = {
                    "kind": "copy",
                    "op": "add-zero",
                    "source": source,
                    "location": preferred_dest,
                }
                self.node += 1
                return preferred_dest, False
            return source, False
        left, left_owned = self.compile_expr(expr["args"][0])
        right, right_owned = self.compile_expr(expr["args"][1])
        if preferred_dest is not None:
            dest, owned = preferred_dest, False
        elif left_owned:
            dest, owned = left, True
        else:
            dest, owned = self.pool.acquire(), True
        op = SUPPORTED_OPS[expr["op"]]
        self.lines.append(f"    {op} {dest}, {left}, {right}")
        self.locations[f"expr:{self.node}"] = {"kind": "expression", "op": op, "location": dest}
        self.node += 1
        if left_owned and left != dest:
            self.pool.release(left)
        if right_owned and right != dest:
            self.pool.release(right)
        return dest, owned

    def generate(self) -> tuple[str, dict[str, Any]]:
        name = self.fn["name"]
        self.lines += [
            "    .section .text", "    .option norvc",
            f"    .globl {name}", f"    .type {name}, @function", f"{name}:",
        ]
        result, _ = self.compile_expr(self.fn["body"]["expr"], preferred_dest="a0")
        expect(result == "a0", "E_BACKEND_STATE", "result must be in a0")
        self.lines += ["    ret", f"    .size {name}, .-{name}", ""]
        expect(not self.pool.in_use, "E_BACKEND_STATE", f"live temporaries remain: {self.pool.in_use}")
        self.locations["result"] = {"kind": "abi-return", "location": "a0"}
        state = {
            "schema": "spec2exec.backend-state/v0.1",
            "backend": "rv32i-direct-v0.1",
            "target_configuration": self.target,
            "abi_fixed_locations": {"arguments": self.args, "return": "a0"},
            "temporary_register_pool": self.pool.registers,
            "temporary_pool_high_water_mark": self.pool.high_water_mark,
            "spill_count": 0,
            "value_locations": self.locations,
        }
        return "\n".join(self.lines), state
