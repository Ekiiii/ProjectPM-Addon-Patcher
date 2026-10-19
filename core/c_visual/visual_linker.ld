OUTPUT_FORMAT("elf32-littlearm", "elf32-bigarm", "elf32-littlearm")
OUTPUT_ARCH(arm)
ENTRY(Hook1_FieldUpdate)

MEMORY
{
    VISUAL (rwx) : ORIGIN = 0x023DE000, LENGTH = 0x1000
}

SECTIONS
{
    .visual : {
        KEEP(*(.data.state))
        . = ALIGN(4);
        KEEP(*(.text.trampolines))
        *(.text*)
        *(.rodata*)
        *(.data*)
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
    } > VISUAL

    __visual_end = .;

    /DISCARD/ : {
        *(.comment)
        *(.ARM.attributes)
        *(.ARM.exidx*)
    }
}
