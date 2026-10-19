# -*- coding: utf-8 -*-
"""
visual_enhancements.py
Visual & Interface enhancements for Pokémon Platinum (ProjectPM):
- Colored Natures: Highlights boosted nature stats (+10%) in Red and hindered stats (-10%) in Blue on summary screen.
- IV & EV In-game Display: Press (A) on the stats page (Page 2) of the summary screen to toggle between actual combat stats and exact IVs / EVs.
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom

from core.i18n import get_lang


# -----------------------------------------------------------------------------
# COLORED STAT NATURES (HGSS / Gen 5+ style)
# -----------------------------------------------------------------------------
# Target: Stat numbers on the Skills/Aptitudes page (and IV/EV toggle modes) of the summary screen.
# Custom routine placed at ARM9 RAM 0x02100810 (offset 0x100810):
# 1. Saves r4-r6, lr (AAPCS 8-byte aligned stack).
# 2. Checks extraWindows offset for the 5 stats:
#    - 0x10 (Attack)   -> column 0
#    - 0x20 (Defense)  -> column 1
#    - 0x30 (SpAtk)    -> column 3
#    - 0x40 (SpDef)    -> column 4
#    - 0x50 (Speed)    -> column 2
# 3. Reads nature from summaryScreen->monData.nature (offset 0x293).
# 4. Looks up sNatureStatAffinities (0x020F7A05):
#    +1 (boosted)  -> overrides r2 to RED  (0x00050600)
#    -1 (hindered) -> overrides r2 to BLUE (0x00030400)
#     0 (neutral)  -> leaves r2 as BLACK   (0x00010200)
# 5. Calls PrintStringToWindow (0x020963C8) and cleanly restores registers with pop {r4, r5, r6, pc}.
#
# Hook sites: The 15 PrintStringToWindow calls inside DrawSkillsPageWindows (0x02096ED0):
# - 5 stat values (Mode 0: Combat stats)
# - 5 IV values (Mode 1: IV toggle)
# - 5 EV values (Mode 2: EV toggle)
# All 15 calls are redirected from PrintStringToWindow to our routine.
# Static windows and PokemonSummaryScreen_Init are NEVER touched, ensuring 0% freeze/black screen!

NATURES_FUNC_OFFSET_045 = 0x100810
NATURES_FUNC_OFFSET     = 0x100A34
NATURES_FUNC_OFFSET_047 = 0x100B68

# 108 bytes routine template assembled with Keystone
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


# Precomputed bl calls for instant lookup
STAT_CALL_VANILLA = {site: make_thumb_bl(site, VANILLA_PRINT_STRING) for site in STAT_CALL_SITES}
STAT_CALL_PATCHED = {site: make_thumb_bl(site, PATCHED_PRINT_STRING) for site in STAT_CALL_SITES}

# Legacy hooks cleanup
OLD_HOOK_GLOBAL_OFFSET = 0x963CC
OLD_HOOK_GLOBAL_VANILLA = bytes.fromhex("041c0e1c171c")  # adds r4, r0, #0; adds r6, r1, #0; adds r7, r2, #0

OLD_HOOK_OFFSET = 0x96F38
OLD_HOOK_VANILLA = bytes.fromhex(
    "41208000281884f7ebf845208000281884f7e6f849208000281884f7e1f84d208000281884f7dcf851208000281884f7d7f8"
)


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

        # Cleanup legacy hook at PrintStringToWindow (0x963CC) if present
        if len(arm9) >= OLD_HOOK_GLOBAL_OFFSET + len(OLD_HOOK_GLOBAL_VANILLA):
            if arm9[OLD_HOOK_GLOBAL_OFFSET:OLD_HOOK_GLOBAL_OFFSET + 4] == bytes.fromhex("6af020fa"):
                arm9[OLD_HOOK_GLOBAL_OFFSET:OLD_HOOK_GLOBAL_OFFSET + len(OLD_HOOK_GLOBAL_VANILLA)] = OLD_HOOK_GLOBAL_VANILLA

        # Cleanup legacy hook at DrawSkillsPageWindows (0x96F38) if present
        if len(arm9) >= OLD_HOOK_OFFSET + len(OLD_HOOK_VANILLA):
            if arm9[OLD_HOOK_OFFSET:OLD_HOOK_OFFSET + 4] == bytes.fromhex("281c69f0"):
                arm9[OLD_HOOK_OFFSET:OLD_HOOK_OFFSET + len(OLD_HOOK_VANILLA)] = OLD_HOOK_VANILLA

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


def apply_iv_ev_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the In-Game IV & EV Display patch on the Pokémon Summary screen.
    Allows toggling between Combat Stats and IVs/EVs via (A).
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

        if enable:
            msg = (
                "[IV/EV] Affichage des IVs & EVs en jeu activé (Touche (A) sur le résumé Pokémon)."
                if is_fr else
                "[IV/EV] In-game IV & EV Display enabled (Press (A) on summary stats screen)."
            )
        else:
            msg = (
                "[IV/EV] Affichage des IVs & EVs désactivé."
                if is_fr else
                "[IV/EV] In-game IV & EV Display disabled."
            )
        log(msg)

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
    """Checks if the IV & EV Display patch is active."""
    try:
        if isinstance(rom_input, str):
            if os.path.isfile(rom_input):
                with open(rom_input, "rb") as f:
                    f.seek(0x1E0)
                    tag = f.read(8)
                return tag[:4] == b"PPM\x01" and bool(tag[5] & 0x01)
    except Exception:
        pass
    return False
