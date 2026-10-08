# -*- coding: utf-8 -*-
"""
visual_patcher.py
Handles Visual+ Battle Backgrounds and Visual+ 3D Camera patching:
- In-place 3D Camera table replacement (reversible via CAM_VANILLA_BYTES and CAM_VISUAL_BYTES)
- NARC injection / reversion for detailed HD Battle Backgrounds (visualplus_battlebg.narc / standard_battlebg.narc)
"""
import os
import base64
import ndspy.rom

CAM_VISUAL_B64  = b"rFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCg=="
CAM_VANILLA_B64 = b"wa4pAALWAAAAAAAAAADBBQBgCQAAQDgAwa4pAGLPAAAAAAAAAADBBQBgCQAAQDgATDcgACLZAAAAAAAAAABwBwBgCQAAQDgAwa4pAALWAAAAAAAAAADBBQBgCQAAQDgAm7hhAGLcAAAAAAAAAQCBAgBgCQAAcGwABcgTAAPWAAAAAAAAAAABDACgAAAAAD8A3yg2AAPMAAAAAAAAAACBBAAwBwAAUEwAwa4pAAPWAAAAAAAAAADBBQCQCQAAcEAAwW4pAOPNAAAAAAAAAAABBwBgCQAAoEAArFkWACPjAAAAAAAAAACwCgBgCQAAQDgAsSVLAMPUAAAAAAAAAABBAwBgCQAAIG0AVT0qAOPWAAAAAAAAAADBBQBgDgAAcEYAP+kjAAPTAAAAAAAAAADBBgBgCQAAQDgATDcgAAPeAAAAAAAAAABwBwBgCQAAQDgAZZcKAETIAAAAAAAAAAABFQCgAAAAAD8A394oACLZAAAAAAAAAADwBQ=="

CAM_VANILLA_BYTES = base64.b64decode(CAM_VANILLA_B64)[:376]
CAM_VISUAL_BYTES = base64.b64decode(CAM_VISUAL_B64)[:376]

def apply_camera_patch(rom_path, enable=True, log_cb=None):
    """
    Applies (enable=True) or removes (enable=False) the Visual+ 3D Camera patch directly in the ROM.
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
            
        # Fallback check through ndspy overlay 5
        try:
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
            ovs = rom.loadArm9Overlays()
            if 5 in ovs:
                ov5_data = bytearray(ovs[5].data)
                ov_idx = ov5_data.find(target)
                if ov_idx != -1:
                    ov5_data[ov_idx : ov_idx + len(target)] = replacement
                    ovs[5].data = bytes(ov5_data)
                    rom.saveArm9Overlays(ovs)
                    rom_bytes = bytearray(rom.save())
                    if len(rom_bytes) < 134217728:
                        rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))
                    with open(rom_path, "wb") as f:
                        f.write(rom_bytes)
                    log(f"[Camera] {action} Visual+ 3D Camera successfully via Overlay 5.")
                    return True
                elif replacement in ov5_data:
                    log(f"[Camera] 3D Camera is already {'enabled' if enable else 'disabled'}.")
                    return True
        except Exception as e:
            log(f"[Camera] Overlay check warning: {e}")

        log("[Camera] Could not locate camera preset table in ROM.")
        return False

    data[idx : idx + len(target)] = replacement
    with open(rom_path, "wb") as f:
        f.write(data)

    log(f"[Camera] {action} Visual+ 3D Camera successfully at 0x{idx:08X}.")
    return True

def apply_battle_bg_patch(rom_path, assets_dir, enable=True, log_cb=None):
    """
    Injects (enable=True) or removes (enable=False) Visual+ Battle Backgrounds NARC into file 159 (pl_batt_bg.narc).
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    narc_name = "visualplus_battlebg.narc" if enable else "standard_battlebg.narc"
    narc_path = os.path.join(assets_dir, narc_name)
    if not os.path.isfile(narc_path):
        log(f"[Visual+] Error: {narc_name} not found in {assets_dir}.")
        return False

    rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    
    target_id = 159
    try:
        found_id = rom.filenames.idOf("battle/graphic/pl_batt_bg.narc")
        if found_id is not None:
            target_id = found_id
    except Exception:
        pass

    if len(rom.files) <= target_id:
        log("[Visual+] Error: Invalid ROM file table (missing battle bg).")
        return False

    with open(narc_path, "rb") as f:
        new_narc = f.read()

    rom.files[target_id] = new_narc
    try:
        rom.setFileByName("battle/graphic/pl_batt_bg.narc", new_narc)
    except Exception:
        pass

    action_text = "Injected HD Battle Backgrounds (Visual+)." if enable else "Reverted to Standard Battle Backgrounds."
    log(f"[Visual+] {action_text}")

    # Save
    rom_bytes = bytearray(rom.save())
    if len(rom_bytes) < 134217728:
        rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))

    with open(rom_path, "wb") as f:
        f.write(rom_bytes)

    return True
