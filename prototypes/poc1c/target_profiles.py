RV32I_BAREMETAL = {
    "target_config_version": "spec2exec.target/v0.1",
    "isa_profile": {
        "architecture": "riscv",
        "isa": "rv32i",
        "extensions": [],
    },
    "execution_profile": {
        "environment": "bare-metal",
        "abi": "ilp32-integer-subset",
        "assembly_dialect": "gnu-riscv",
        "object_model": "elf32-riscv",
    },
}
