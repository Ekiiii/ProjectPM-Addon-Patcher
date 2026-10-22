"""
visual_enhancements.py
Visual and UI patches for Pokémon Platinum (ProjectPM):
- Colored Natures: Highlights boosted stats (+10%) in red and lowered stats (-10%) in blue on the summary screen.
- IV & EV In-Game Display: Press (A) on the stats page (Page 2) of the summary screen to toggle between combat stats, IVs, and EVs.
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom

from core.i18n import get_lang


# Colored Stat Natures (Summary Screen)
# Hooks the 15 PrintStringToWindow calls in DrawSkillsPageWindows (5 combat stats, 5 IVs, 5 EVs)
# and sets the text palette color according to sNatureStatAffinities (+1 -> Red, -1 -> Blue, 0 -> Black).

NATURES_FUNC_OFFSET_045 = 0x100810
NATURES_FUNC_OFFSET     = 0x100A34
NATURES_FUNC_OFFSET_047 = 0x100B68

NATURES_FUNC_PATCHED = bytes.fromhex(
    "70b59524a4000459002c26d00d1b102d08d0202d08d0302d0ad0402d0ad0502d04d01ae0002506e0012504e0022502e0032500e00425292424010334045d182c0bd8052674436419054e3457002c01dc02db02e0034a00e0034a95f7adfd70bd057a0f020006050000040300"
)

VANILLA_PRINT_STRING_045 = 0x020963C8
PATCHED_PRINT_STRING_045 = 0x02100810
VANILLA_PRINT_STRING     = 0x0209661C
PATCHED_PRINT_STRING     = 0x02100A34
VANILLA_PRINT_STRING_047 = 0x02096750
PATCHED_PRINT_STRING_047 = 0x02100B68

STAT_CALL_SITES_045 = [
    0x0209702E, 0x02097052, 0x02097076, 0x0209709C, 0x020970C0,  # IVs (Atk, Def, SpA, SpD, Spe)
    0x0209710C, 0x02097132, 0x02097156, 0x0209717A, 0x0209719E,  # EVs (Atk, Def, SpA, SpD, Spe)
    0x020971FA, 0x0209721E, 0x02097244, 0x020972AA, 0x020972D0,  # Combat Stats (Atk, Def, SpA, SpD, Spe)
]
STAT_CALL_SITES     = [s + 0x254 for s in STAT_CALL_SITES_045]
STAT_CALL_SITES_047 = [s + 0x134 for s in STAT_CALL_SITES]


def make_thumb_bl(from_addr: int, to_addr: int) -> bytes:
    diff = to_addr - (from_addr + 4)
    offset = diff >> 1
    hw1 = 0xF000 | ((offset >> 11) & 0x7FF)
    hw2 = 0xF800 | (offset & 0x7FF)
    return bytes([hw1 & 0xFF, hw1 >> 8, hw2 & 0xFF, hw2 >> 8])


def _get_natures_params(arm9: bytes):
    import struct
    bss = struct.unpack_from("<I", arm9, 0xBAC)[0] if len(arm9) >= 0xBB0 else 0
    if bss == 0x021094E0:
        func_off = NATURES_FUNC_OFFSET_047
        func_addr = PATCHED_PRINT_STRING_047
        van_print = VANILLA_PRINT_STRING_047
        sites = STAT_CALL_SITES_047
        aff_table = 0x020F7D5D
    elif bss == 0x02109180:
        func_off = NATURES_FUNC_OFFSET_045
        func_addr = PATCHED_PRINT_STRING_045
        van_print = VANILLA_PRINT_STRING_045
        sites = STAT_CALL_SITES_045
        aff_table = 0x020F7A05
    else:
        func_off = NATURES_FUNC_OFFSET
        func_addr = PATCHED_PRINT_STRING
        van_print = VANILLA_PRINT_STRING
        sites = STAT_CALL_SITES
        aff_table = 0x020F7C29

    fn_buf = bytearray(NATURES_FUNC_PATCHED)
    fn_buf[0x5A:0x5E] = make_thumb_bl(func_addr + 0x5A, van_print)
    struct.pack_into("<I", fn_buf, 0x60, aff_table)
    van_calls = {s: make_thumb_bl(s, van_print) for s in sites}
    pat_calls = {s: make_thumb_bl(s, func_addr) for s in sites}
    return func_off, bytes(fn_buf), sites, van_calls, pat_calls


def apply_colored_natures_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes Colored Stat Natures (+Red for boosted, -Blue for hindered) on the Pokémon Summary screen.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Natures] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        arm9 = bytearray(rom.arm9)
        func_off, func_bytes, sites, van_calls, pat_calls = _get_natures_params(arm9)

        if enable:
            if len(arm9) < func_off + len(func_bytes):
                log("[Natures] Error: ARM9 binary too small.")
                return False

            # Inject the nature color handler function
            arm9[func_off:func_off + len(func_bytes)] = func_bytes

            # Redirect stat printing calls in DrawSkillsPageWindows
            for site, patched_bl in pat_calls.items():
                offset = site - 0x02000000
                arm9[offset:offset + 4] = patched_bl

            msg = (
                "[Natures] Natures colorées activées (+Rouge / -Bleu sur l'écran résumé Pokémon)."
                if is_fr else
                "[Natures] Colored stat natures enabled (+Red / -Blue on Pokémon summary screen)."
            )
            log(msg)
        else:
            # Restore vanilla bl calls
            for site, vanilla_bl in van_calls.items():
                offset = site - 0x02000000
                arm9[offset:offset + 4] = vanilla_bl

            if len(arm9) >= func_off + len(func_bytes):
                arm9[func_off:func_off + len(func_bytes)] = b"\x00" * len(func_bytes)

            msg = (
                "[Natures] Natures colorées désactivées (affichage standard restauré)."
                if is_fr else
                "[Natures] Colored natures disabled (standard display restored)."
            )
            log(msg)

        rom.arm9 = bytes(arm9)
        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Natures] Exception: {e}")
        return False


IVEV_OFFSETS = {
    "045": {"toggle": 0x8FA60, "check1": 0x96EDA, "check2": 0x96FE4},
    "046": {"toggle": 0x8FCB4, "check1": 0x9712E, "check2": 0x97238},
    "047": {"toggle": 0x8FDE8, "check1": 0x97262, "check2": 0x9736C},
}

IVEV_DISABLED_TOGGLE = bytes.fromhex("00207047")  # movs r0, #0; bx lr
IVEV_DISABLED_CHECK  = bytes.fromhex("0020")      # movs r0, #0
IVEV_ENABLED_TOGGLE  = bytes.fromhex("18b583b0")  # push {r3, r4, lr}; sub sp, #12
IVEV_ENABLED_CHECK   = bytes.fromhex("285c")      # ldrb r0, [r5, r0]


def _get_ivev_params(rom: ndspy.rom.NintendoDSRom, arm9: bytes) -> dict:
    try:
        ov16 = rom.loadArm9Overlays().get(16)
        if ov16:
            if ov16.ramAddress == 0x0224A700:
                return IVEV_OFFSETS["045"]
            elif ov16.ramAddress == 0x0224A920:
                return IVEV_OFFSETS["046"]
            elif ov16.ramAddress == 0x0224AAE0:
                return IVEV_OFFSETS["047"]
    except Exception:
        pass

    import struct
    bss = struct.unpack_from("<I", arm9, 0xBAC)[0] if len(arm9) >= 0xBB0 else 0
    if bss == 0x02109180 or len(arm9) == 0x109858:
        return IVEV_OFFSETS["045"]
    elif bss == 0x021093A0 or len(arm9) == 0x109A78:
        return IVEV_OFFSETS["046"]
    return IVEV_OFFSETS["047"]


def apply_iv_ev_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the In-Game IV & EV Display patch on the Pokémon Summary screen.
    Allows toggling between Combat Stats and IVs/EVs via (A).
    Supports versions 0.4.5, 0.4.6, and 0.4.7 via real ARM9 binary toggles.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[IV/EV] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        arm9 = bytearray(rom.arm9)
        params = _get_ivev_params(rom, arm9)
        toggle_off = params["toggle"]
        check1_off = params["check1"]
        check2_off = params["check2"]

        if len(arm9) < max(toggle_off + 4, check2_off + 2):
            log("[IV/EV] Error: ARM9 binary too small.")
            return False

        if enable:
            arm9[toggle_off:toggle_off + 4] = IVEV_ENABLED_TOGGLE
            arm9[check1_off:check1_off + 2] = IVEV_ENABLED_CHECK
            arm9[check2_off:check2_off + 2] = IVEV_ENABLED_CHECK
            msg = (
                "[IV/EV] Affichage des IVs & EVs en jeu activé (Touche (A) sur le résumé Pokémon)."
                if is_fr else
                "[IV/EV] In-game IV & EV Display enabled (Press (A) on summary stats screen)."
            )
        else:
            arm9[toggle_off:toggle_off + 4] = IVEV_DISABLED_TOGGLE
            arm9[check1_off:check1_off + 2] = IVEV_DISABLED_CHECK
            arm9[check2_off:check2_off + 2] = IVEV_DISABLED_CHECK
            msg = (
                "[IV/EV] Affichage des IVs & EVs désactivé."
                if is_fr else
                "[IV/EV] In-game IV & EV Display disabled."
            )
        log(msg)

        rom.arm9 = bytes(arm9)
        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[IV/EV] Exception: {e}")
        return False


def is_colored_natures_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Colored Stat Natures patch is active in ARM9."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        arm9 = rom.arm9
        _, _, sites, _, pat_calls = _get_natures_params(arm9)
        primary_site = sites[10]  # Attack combat stat
        offset = primary_site - 0x02000000
        if len(arm9) < offset + 4:
            return False
        return arm9[offset:offset + 4] == pat_calls[primary_site]
    except Exception:
        return False


def is_iv_ev_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the IV & EV Display patch is active in ARM9."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        arm9 = rom.arm9
        params = _get_ivev_params(rom, arm9)
        toggle_off = params["toggle"]
        check1_off = params["check1"]

        if len(arm9) >= check1_off + 2:
            if arm9[toggle_off:toggle_off + 4] == IVEV_DISABLED_TOGGLE:
                return False
            if arm9[toggle_off:toggle_off + 4] == IVEV_ENABLED_TOGGLE and arm9[check1_off:check1_off + 2] == IVEV_ENABLED_CHECK:
                return True

        if isinstance(rom_input, str) and os.path.isfile(rom_input):
            with open(rom_input, "rb") as f:
                f.seek(0x1E0)
                tag = f.read(8)
            return tag[:4] == b"PPM\x01" and bool(tag[5] & 0x01)
    except Exception:
        pass
    return False
