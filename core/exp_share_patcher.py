# -*- coding: utf-8 -*-
"""
exp_share_patcher.py
In-game Shared Team EXP mod for Pokémon Platinum (ProjectPM):
- Distributes battle experience to all party Pokémon (Gen 6+ EXP Share / EXP ALL style)
- Active battlers on the field receive full 100% experience reward
- Non-combatant bench Pokémon receive balanced 50% partial experience
- Fainted (HP=0) and max-level (Lv100) Pokémon are safely skipped
- Seamlessly integrates into Overlay 16 battle engine
"""
import os
from typing import Optional, Callable, Union
import ndspy.rom
import ndspy.code

from core.i18n import get_lang

# Patch definitions for Overlay 16 (RAM base 0x0224A700)
# Point 1: In BtlCmd_CalcExpGain: force 100%/50% calculation
# 0x022516a2: '20d0' (beq) -> '20e0' (b)
ADDR_PT1 = 0x022516A2
VANILLA_PT1 = bytes.fromhex("20d0")
PATCH_PT1   = bytes.fromhex("20e0")

# Point 2: In BtlCmd_CalcExpGain: calculate sharedExp = gainedExp / 2
# 0x022516f2 (26 bytes)
ADDR_PT2 = 0x022516F2
VANILLA_PT2 = bytes.fromhex("281c9c300068002803d1281c01219c3001600020a035286003e0")
PATCH_PT2   = bytes.fromhex("002800d10120086004314008002800d10120086005e0c046c046")

# Point 3: In BattleScript_GetExpTask: loop through all party slots
# 0x02258d88 (4 bytes): '332810d0' -> '11e0c046'
ADDR_PT3 = 0x02258D88
VANILLA_PT3 = bytes.fromhex("332810d0")
PATCH_PT3   = bytes.fromhex("11e0c046")

# Point 4: In Case 0 of GetExpTask: give gainedExp to battlers and sharedExp to bench
# 0x02258f5c (30 bytes)
ADDR_PT4 = 0x02258F5C
VANILLA_PT4 = bytes.fromhex("03d009989c3000680e900698332806d10998a030099001680e9840180e90")
PATCH_PT4   = bytes.fromhex("03d009989c30006802e00998a03000680e9004e0c046c046c046c046c046")


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
        base = ov16.ramAddress
        off3 = ADDR_PT3 - base
        if off3 + 2 > len(ov16.data):
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

        off1 = ADDR_PT1 - base
        off2 = ADDR_PT2 - base
        off3 = ADDR_PT3 - base
        off4 = ADDR_PT4 - base

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
