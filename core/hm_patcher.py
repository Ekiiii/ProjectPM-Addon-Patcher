"""
hm_patcher.py
Free HMs & Poké-Rider patch for Pokémon Platinum (ProjectPM).
Allows using field moves on overworld obstacles with the required Gym Badge
and removes the HM move deletion restriction in ARM9.
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom

from core.i18n import get_lang

# ARM9 offsets and addresses (0.4.6 defaults, with 0.4.5 compatibility)
ADDR_FALLBACK = 0x02058CC4
OFF_FALLBACK  = 0x58CC4
LEN_FALLBACK  = 92

PATCH_FALLBACK = bytes.fromhex(
    "10b50c1c07a309211888904204d19978201cfff7bdff10bd04330139f4d1002010bd00bf"
    "0f0001001300020039000300460005007f0007009400ff00f9000000af010600b0010400"
    + "c046" * 10
)
VANILLA_FALLBACK_047 = bytes.fromhex(
    "70b50e1c141c4c210022051c20f0dcfe002801d0002070bd281c0521002220f0d3fe0004"
    "0b4b020c0021188882420ad15888844207d106224a430749301c895cfff7a6ff70bd491c"
    "9b1d1229edd3002070bdc046b0390f02b4390f02"
)
VANILLA_FALLBACK = bytes.fromhex(
    "70b50e1c141c4c210022051c20f0e0fe002801d0002070bd281c0521002220f0d7fe0004"
    "0b4b020c0021188882420ad15888844207d106224a430749301c895cfff7a6ff70bd491c"
    "9b1d1229edd3002070bdc0467c380f0280380f02"
)
VANILLA_FALLBACK_045 = bytes.fromhex(
    "70b50e1c141c4c210022051c20f06afe002801d0002070bd281c0521002220f061fe0004"
    "0b4b020c0021188882420ad15888844207d106224a430749301c895cfff7a6ff70bd491c"
    "9b1d1229edd3002070bdc04658360f025c360f02"
)

ADDR_FORGET = 0x02083608
OFF_FORGET  = 0x83608
LEN_FORGET  = 4

PATCH_FORGET   = bytes.fromhex("00207047")
VANILLA_FORGET = bytes.fromhex("084a0023")


def _get_hm_params(arm9: bytes):
    import struct
    if len(arm9) >= 0xBB0:
        bss = struct.unpack_from("<I", arm9, 0xBAC)[0]
        if bss == 0x021094E0:
            return 0x58E00, 0x8373C, VANILLA_FALLBACK_047
        if bss == 0x02109180:
            return 0x58B5C, 0x833B4, VANILLA_FALLBACK_045
    return OFF_FALLBACK, OFF_FORGET, VANILLA_FALLBACK


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
        off_fallback, off_forget, _ = _get_hm_params(arm9)
        if len(arm9) < off_forget + LEN_FORGET:
            return False

        has_fallback = (arm9[off_fallback:off_fallback + 4] == PATCH_FALLBACK[:4])
        has_forget   = (arm9[off_forget:off_forget + 4] == PATCH_FORGET)
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
        off_fallback, off_forget, van_fallback = _get_hm_params(arm9)
        if len(arm9) < off_forget + LEN_FORGET:
            log("[CS Libres] Error: ARM9 binary is too short.")
            return False

        if enable:
            arm9[off_fallback:off_fallback + LEN_FALLBACK] = PATCH_FALLBACK
            arm9[off_forget:off_forget + LEN_FORGET] = PATCH_FORGET
            msg = (
                "[Mods] CS Libres & Poké-Rider: Activé (Utilisation directe avec 'A' et oubli libre des CS)."
                if is_fr else
                "[Mods] Free HMs & Poké-Rider: Enabled (Direct interaction with 'A' and free HM forgetting)."
            )
        else:
            arm9[off_fallback:off_fallback + LEN_FALLBACK] = van_fallback
            arm9[off_forget:off_forget + LEN_FORGET] = VANILLA_FORGET
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
