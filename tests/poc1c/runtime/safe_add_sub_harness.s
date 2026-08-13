    .section .text.start
    .option norvc
    .globl _start
    .type _start, @function
_start:
    addi s0, zero, -100

.L_outer:
    addi s1, zero, -100

.L_inner:
    add a0, s0, zero
    add a1, s1, zero
    jal ra, safe_add_sub
    bne a0, s0, .L_fail

    addi s1, s1, 1
    addi t0, zero, 101
    blt s1, t0, .L_inner

    addi s0, s0, 1
    addi t0, zero, 101
    blt s0, t0, .L_outer

.L_pass:
    lui t0, 0x100
    lui t1, 0x5
    addi t1, t1, 0x555
    sw t1, 0(t0)

.L_halt_pass:
    jal zero, .L_halt_pass

.L_fail:
    lui t0, 0x100
    lui t1, 0x3
    addi t1, t1, 0x333
    sw t1, 0(t0)

.L_halt_fail:
    jal zero, .L_halt_fail

    .size _start, .-_start
