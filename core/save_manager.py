# -*- coding: utf-8 -*-
"""
save_manager.py
Manages safe backups and automatic companion synchronization for:
- Save files (.dsv)
- Randomizer sidecar files (.rand.txt)
- ROM backups before patching
"""
import os
import shutil
import time

def backup_and_sync_save(source_rom, output_rom, log_cb=None):
    """
    Backs up the original ROM and its save file, and copies the save file
    to match the new output ROM's filename.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    source_dir = os.path.dirname(os.path.abspath(source_rom))
    backup_dir = os.path.join(source_dir, "PMBackups")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    src_base = os.path.splitext(os.path.basename(source_rom))[0]
    out_base = os.path.splitext(os.path.basename(output_rom))[0]

    # 1. Backup source ROM
    rom_bak = os.path.join(backup_dir, f"{src_base}.{timestamp}.nds")
    try:
        shutil.copy2(source_rom, rom_bak)
        log(f"[Backup] Saved ROM backup -> PMBackups/{os.path.basename(rom_bak)}")
    except Exception as e:
        log(f"[Backup] Warning: could not backup ROM ({e})")

    # 2. Check and Backup Save files (.dsv and .sav)
    save_candidates = [
        (os.path.join(source_dir, src_base + ".dsv"), ".dsv"),
        (os.path.join(source_dir, "battery", src_base + ".dsv"), ".dsv"),
        (os.path.join(source_dir, src_base + ".sav"), ".sav"),
        (os.path.join(source_dir, "battery", src_base + ".sav"), ".sav"),
    ]

    found_saves = []
    for save_path, ext in save_candidates:
        if os.path.isfile(save_path) and save_path not in [s[0] for s in found_saves]:
            found_saves.append((save_path, ext))

    if found_saves:
        for save_file, ext in found_saves:
            save_bak = os.path.join(backup_dir, f"{src_base}.{timestamp}{ext}")
            try:
                shutil.copy2(save_file, save_bak)
                log(f"[Backup] Saved Save file backup -> PMBackups/{os.path.basename(save_bak)}")
            except Exception as e:
                log(f"[Backup] Warning: could not backup save ({e})")

            # Sync save to new name if names differ
            if src_base != out_base:
                out_save = os.path.join(os.path.dirname(save_file), out_base + ext)
                try:
                    shutil.copy2(save_file, out_save)
                    log(f"[Save] Preserved companion save -> {os.path.basename(out_save)}")
                except Exception as e:
                    log(f"[Save] Warning: could not copy save ({e})")
    else:
        log("[Save] Note: No existing save file (.dsv / .sav) found to backup.")

    # 3. Check and Preserve Randomizer record (.rand.txt)
    src_rand = os.path.join(source_dir, src_base + ".rand.txt")
    if os.path.isfile(src_rand):
        rand_bak = os.path.join(backup_dir, f"{src_base}.{timestamp}.rand.txt")
        try:
            shutil.copy2(src_rand, rand_bak)
        except Exception:
            pass

        if src_base != out_base:
            out_rand = os.path.join(source_dir, out_base + ".rand.txt")
            try:
                shutil.copy2(src_rand, out_rand)
                log(f"[Rand] Preserved randomizer record -> {os.path.basename(out_rand)}")
            except Exception as e:
                log(f"[Rand] Warning: could not copy rand record ({e})")

    return True
