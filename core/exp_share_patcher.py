"""
exp_share_patcher.py
Team EXP Share patch for Pokémon Platinum (ProjectPM).
Gives 100% EXP to active battlers and 50% EXP to non-fainted bench Pokémon in Overlay 16.
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom
import ndspy.code

from core.i18n import get_lang

# Patch definitions for Overlay 16 (0.4.6 RAM base 0x0224A920, 0.4.5 RAM base 0x0224A700)
# Point 1: In BtlCmd_CalcExpGain: force 100%/50% calculation
ADDR_PT1 = 0x022518EA
VANILLA_PT1 = bytes.fromhex("20d0")
PATCH_PT1   = bytes.fromhex("20e0")

# Point 2: In BtlCmd_CalcExpGain: calculate sharedExp = gainedExp / 2
ADDR_PT2 = 0x0225193A
VANILLA_PT2 = bytes.fromhex("281c9c300068002803d1281c01219c3001600020a035286003e0")
PATCH_PT2   = bytes.fromhex("002800d10120086004314008002800d10120086005e0c046c046")

# Point 3: In BattleScript_GetExpTask: loop through all party slots
ADDR_PT3 = 0x02258FFC
VANILLA_PT3 = bytes.fromhex("332810d0")
PATCH_PT3   = bytes.fromhex("11e0c046")

# Point 4: In Case 0 of GetExpTask: give gainedExp to battlers and sharedExp to bench
ADDR_PT4 = 0x022591D0
VANILLA_PT4 = bytes.fromhex("03d009989c3000680e900698332806d10998a030099001680e9840180e90")
PATCH_PT4   = bytes.fromhex("03d009989c30006802e00998a03000680e9004e0c046c046c046c046c046")


def _get_exp_share_offsets(base: int):
    if base == 0x0224AAE0:
        return (
            0x02251AAE - base,
            0x02251AFE - base,
            0x022591C0 - base,
            0x02259394 - base,
        )
    if base == 0x0224A700:
        return (
            0x022516A2 - base,
            0x022516F2 - base,
            0x02258D88 - base,
            0x02258F5C - base,
        )
    return (
        ADDR_PT1 - base,
        ADDR_PT2 - base,
        ADDR_PT3 - base,
        ADDR_PT4 - base,
    )


def is_exp_share_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """
    Checks if the Shared Team EXP mod is currently active in the given ROM.
    """
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        ovs = rom.loadArm9Overlays([16])
        if 16 not in ovs:
            return False
        ov16 = ovs[16]
        _, _, off3, _ = _get_exp_share_offsets(ov16.ramAddress)
        if off3 < 0 or off3 + 2 > len(ov16.data):
            return False
        return ov16.data[off3:off3 + 2] == PATCH_PT3[:2]
    except Exception:
        return False


def apply_exp_share_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Shared Team EXP modification on Overlay 16 of the ROM.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Multi Exp] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        ovs = rom.loadArm9Overlays()
        if 16 not in ovs:
            log("[Multi Exp] Error: Overlay 16 (Battle engine) not found in ROM.")
            return False

        ov16 = ovs[16]
        base = ov16.ramAddress
        data = bytearray(ov16.data)

        off1, off2, off3, off4 = _get_exp_share_offsets(base)

        if enable:
            data[off1:off1 + len(PATCH_PT1)] = PATCH_PT1
            data[off2:off2 + len(PATCH_PT2)] = PATCH_PT2
            data[off3:off3 + len(PATCH_PT3)] = PATCH_PT3
            data[off4:off4 + len(PATCH_PT4)] = PATCH_PT4
            msg = "[Mods] Exp. Partagée d'équipe: Activée avec succès (100% actif / 50% équipe)." if is_fr else "[Mods] Shared Team EXP: Enabled successfully (100% active / 50% team)."
        else:
            data[off1:off1 + len(VANILLA_PT1)] = VANILLA_PT1
            data[off2:off2 + len(VANILLA_PT2)] = VANILLA_PT2
            data[off3:off3 + len(VANILLA_PT3)] = VANILLA_PT3
            data[off4:off4 + len(VANILLA_PT4)] = VANILLA_PT4
            msg = "[Mods] Exp. Partagée d'équipe: Désactivée (Comportement vanilla restauré)." if is_fr else "[Mods] Shared Team EXP: Disabled (Vanilla behavior restored)."

        ov16.data = bytes(data)
        ovs[16] = ov16
        rom.files[ov16.fileID] = ov16.data
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

        if save_path:
            rom_bytes = bytearray(rom.save())
            if len(rom_bytes) < 134217728:
                rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))
            with open(save_path, "wb") as f:
                f.write(rom_bytes)

        log(msg)
        return True
    except Exception as e:
        log(f"[Multi Exp] Error applying patch: {e}")
        return False
