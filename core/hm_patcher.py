# -*- coding: utf-8 -*-
"""
hm_patcher.py
In-game Free HMs & Poké-Rider mod for Pokémon Platinum (Project PM):
- Allows field moves (Cut, Rock Smash, Strength, Surf, Waterfall, Rock Climb, Flash, Defog)
  to be used directly on overworld obstacles by pressing 'A' without teaching them to any Pokémon,
  as long as the player has obtained the required Gym Badge.
- Removes the HM move deletion restriction, allowing players to freely forget or overwrite
  any HM with TMs or level-up moves without visiting the Move Deleter in Canalave City.
- Completely self-contained within ARM9 binary modifications.
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom

from core.i18n import get_lang

# ARM9 offsets and addresses
ADDR_FALLBACK = 0x02058B5C
OFF_FALLBACK  = 0x58B5C
LEN_FALLBACK  = 92

PATCH_FALLBACK = bytes.fromhex(
    "10b50c1c07a309211888904204d19978201cfff7bdff10bd04330139f4d1002010bd00bf"
    "0f0001001300020039000300460005007f0007009400ff00f9000000af010600b0010400"
    + "c046" * 10
)
VANILLA_FALLBACK = bytes.fromhex(
    "70b50e1c141c4c210022051c20f06afe002801d0002070bd281c0521002220f061fe0004"
    "0b4b020c0021188882420ad15888844207d106224a430749301c895cfff7a6ff70bd491c"
    "9b1d1229edd3002070bdc04658360f025c360f02"
)

ADDR_FORGET = 0x020833B4
OFF_FORGET  = 0x833B4
LEN_FORGET  = 4

PATCH_FORGET   = bytes.fromhex("00207047")
VANILLA_FORGET = bytes.fromhex("084a0023")


def is_hm_patch_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """
    Checks if the Free HMs & Poké-Rider patch is currently active in the given ROM.
    """
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        arm9 = rom.arm9
        if len(arm9) < OFF_FORGET + LEN_FORGET:
            return False

        has_fallback = (arm9[OFF_FALLBACK:OFF_FALLBACK + 4] == PATCH_FALLBACK[:4])
        has_forget   = (arm9[OFF_FORGET:OFF_FORGET + 4] == PATCH_FORGET)
        return has_fallback and has_forget
    except Exception:
        return False


def apply_hm_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Free HMs & Poké-Rider modification on ARM9 of the ROM.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[CS Libres] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        arm9 = bytearray(rom.arm9)
        if len(arm9) < OFF_FORGET + LEN_FORGET:
            log("[CS Libres] Error: ARM9 binary is too short.")
            return False

        if enable:
            arm9[OFF_FALLBACK:OFF_FALLBACK + LEN_FALLBACK] = PATCH_FALLBACK
            arm9[OFF_FORGET:OFF_FORGET + LEN_FORGET] = PATCH_FORGET
            msg = (
                "[Mods] CS Libres & Poké-Rider: Activé (Utilisation directe avec 'A' et oubli libre des CS)."
                if is_fr else
                "[Mods] Free HMs & Poké-Rider: Enabled (Direct interaction with 'A' and free HM forgetting)."
            )
        else:
            arm9[OFF_FALLBACK:OFF_FALLBACK + LEN_FALLBACK] = VANILLA_FALLBACK
            arm9[OFF_FORGET:OFF_FORGET + LEN_FORGET] = VANILLA_FORGET
            msg = (
                "[Mods] CS Libres & Poké-Rider: Désactivé (Comportement vanilla restauré)."
                if is_fr else
                "[Mods] Free HMs & Poké-Rider: Disabled (Vanilla behavior restored)."
            )

        rom.arm9 = bytes(arm9)

        if save_path:
            rom_bytes = bytearray(rom.save())
            if len(rom_bytes) < 134217728:
                rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))
            with open(save_path, "wb") as f:
                f.write(rom_bytes)

        log(msg)
        return True
    except Exception as e:
        log(f"[CS Libres] Error applying patch: {e}")
        return False
