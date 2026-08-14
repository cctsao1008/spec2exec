OUTPUT_ARCH(riscv)
ENTRY(_start)

SECTIONS
{
    . = 0x80000000;

    .text : ALIGN(4)
    {
        *(.text.start)
        *(.text*)
    }

    .rodata : ALIGN(4)
    {
        *(.rodata*)
    }

    .data : ALIGN(4)
    {
        *(.data*)
    }

    .bss : ALIGN(4)
    {
        *(.bss*)
        *(COMMON)
    }

    .stack (NOLOAD) : ALIGN(16)
    {
        __stack_bottom = .;
        . = . + 4096;
        __stack_top = .;
    }
}
