# -*- coding: utf-8 -*-
"""
visual_patcher.py
Handles Visual+ Battle Backgrounds and Visual+ 3D Camera patching:
- In-place 3D Camera table replacement (reversible)
- NARC injection for detailed HD Battle Backgrounds
"""
import os
import base64
import ndspy.rom

CAM_VANILLA_B64 = b"vAEAALkBAAC6AQAAKgEAAOQBAACAAAAADwIAAEsAAADBrikAAtYAAAAAAAAAAMEFAGAJAABAOADBrikAYs8AAAAAAAAAAMEFAGAJAABAOABMNyAAItkAAAAAAAAAAHAHAGAJAABAOADBrikAAtYAAAAAAAAAAMEFAGAJAABAOACbuGEAYtwAAAAAAAABAIECAGAJAABwbAAFyBMAA9YAAAAAAAAAAAEMAKAAAAAAPwDfKDYAA8wAAAAAAAAAAIEEADAHAABQTADBrikAA9YAAAAAAAAAAMEFAJAJAABwQADBbikA480AAAAAAAAAAAEHAGAJAACgQACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACxJUsAw9QAAAAAAAAAAEEDAGAJAAAgbQBVPSoA49YAAAAAAAAAAMEFAGAOAABwRgA/6SMAA9MAAAAAAAAAAMEGAGAJAABAOABMNyAAA94AAAAAAAAAAHAHAGAJAABAOABllwoARMgAAAAAAAAAAAEVAKAAAAAAPwDf3igAItkAAAAAAAAAAPAFAGAJAABAOADArhQAAtYAAAAAAAAAAAELAGAJAABAOAA="
CAM_VISUAL_B64  = b"vAEAALkBAAC6AQAAKgEAAOQBAACAAAAADwIAAEsAAACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOADArhQAAtYAAAAAAAAAAAELAGAJAABAOAA="

CAM_VANILLA_BYTES = base64.b64decode(CAM_VANILLA_B64)
CAM_VISUAL_BYTES = base64.b64decode(CAM_VISUAL_B64)

def apply_camera_patch(rom_path, enable=True, log_cb=None):
    """
    Applies or removes the Visual+ 3D Camera patch directly in the ROM.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    with open(rom_path, "rb") as f:
        data = bytearray(f.read())

    target = CAM_VANILLA_BYTES if enable else CAM_VISUAL_BYTES
    replacement = CAM_VISUAL_BYTES if enable else CAM_VANILLA_BYTES
    action = "Applied" if enable else "Reverted"

    idx = data.find(target)
    if idx == -1:
        if replacement in data:
            log(f"[Camera] 3D Camera is already {'enabled' if enable else 'disabled'}.")
            return True
        log("[Camera] Could not locate camera preset table in ROM.")
        return False

    # Check for second match
    if data.find(target, idx + len(target)) != -1:
        log("[Camera] Multiple camera tables found. Operation aborted for safety.")
        return False

    data[idx: idx + len(target)] = replacement
    with open(rom_path, "wb") as f:
        f.write(data)

    log(f"[Camera] {action} Visual+ 3D Camera successfully at 0x{idx:08X}.")
    return True

def apply_battle_bg_patch(rom_path, assets_dir, enable=True, log_cb=None):
    """
    Injects or reverts Visual+ Battle Backgrounds NARC into file 159 (pl_batt_bg.narc).
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    narc_path = os.path.join(assets_dir, "visualplus_battlebg.narc")
    if enable and not os.path.isfile(narc_path):
        log(f"[Visual+] Error: {narc_path} not found.")
        return False

    rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    if len(rom.files) <= 159:
        log("[Visual+] Error: Invalid ROM file table (missing battle bg).")
        return False

    if enable:
        with open(narc_path, "rb") as f:
            new_narc = f.read()
        rom.files[159] = new_narc
        # Also update by name if present
        try:
            rom.setFileByName("battle/graphic/pl_batt_bg.narc", new_narc)
        except Exception:
            pass
        log("[Visual+] Injected HD Battle Backgrounds (Visual+).")
    else:
        log("[Visual+] Keeping vanilla battle backgrounds.")

    # Save
    rom_bytes = bytearray(rom.save())
    # Pad to 128MB standard if needed
    if len(rom_bytes) < 134217728:
        rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))

    with open(rom_path, "wb") as f:
        f.write(rom_bytes)

    return True
