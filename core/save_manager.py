# -*- coding: utf-8 -*-
"""
save_manager.py
Robust and automatic backup and companion synchronization system for:
- Emulator Save files (.sav, .dsv) across all common emulator folder structures
- Randomizer companion files (.rand.txt)
- Safe ROM backups before patching and modification
"""
import os
import glob
import shutil
import time
import subprocess
import sys
from typing import List, Tuple, Optional, Callable

from core.i18n import get_lang


def get_backup_dir(rom_path: str) -> str:
    """Returns absolute path to PMBackups directory for the given ROM path."""
    rom_dir = os.path.dirname(os.path.abspath(rom_path)) if rom_path else os.getcwd()
    return os.path.join(rom_dir, "PMBackups")


def find_existing_saves(rom_path: str) -> List[Tuple[str, str]]:
    """
    Finds all existing .sav and .dsv files for a given ROM path.
    Scans:
    - Root ROM directory
    - Subdirectories: battery/, Backup/, backup/, saves/, Save/
    - Filename variations: <base>.sav, <base>.dsv, <base>.nds.sav, <base>.nds.dsv, <base>.nds_Modded.sav
    Returns a deduplicated list of (full_file_path, extension).
    """
    if not rom_path or not os.path.isfile(rom_path):
        return []

    rom_dir = os.path.dirname(os.path.abspath(rom_path))
    rom_filename = os.path.basename(rom_path)
    base_name = os.path.splitext(rom_filename)[0]

    prefixes = [base_name, rom_filename, f"{rom_filename}_Modded", f"{base_name}.nds_Modded"]
    extensions = [".sav", ".dsv", ".SAV", ".DSV"]
    subdirs = ["", "battery", "Backup", "backup", "saves", "Save", os.path.join("saves", "battery")]

    found = []
    seen_real_paths = set()

    for sub in subdirs:
        check_dir = os.path.join(rom_dir, sub) if sub else rom_dir
        if not os.path.isdir(check_dir):
            continue

        # Prevent searching inside PMBackups itself to avoid re-backing up backups
        if os.path.basename(os.path.normpath(check_dir)).lower() == "pmbackups":
            continue

        for prefix in prefixes:
            for ext in extensions:
                candidate = os.path.join(check_dir, prefix + ext)
                if os.path.isfile(candidate):
                    try:
                        sz = os.path.getsize(candidate)
                        if sz > 0:
                            real_path = os.path.realpath(candidate)
                            if real_path not in seen_real_paths:
                                seen_real_paths.add(real_path)
                                found.append((candidate, ext.lower()))
                    except Exception:
                        pass

    return found


def backup_and_sync_save(source_rom: str, output_rom: str, log_cb: Optional[Callable[[str], None]] = None) -> bool:
    """
    Safely backs up all original save files (.sav/.dsv) and the ROM before any
    modification (patching, SoulLocke injection, or randomization).
    Also synchronizes companion save files to match the output ROM.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    if not source_rom or not os.path.isfile(source_rom):
        return False

    is_fr = (get_lang() == "fr")
    src_dir = os.path.dirname(os.path.abspath(source_rom))
    out_dir = os.path.dirname(os.path.abspath(output_rom)) if output_rom else src_dir
    src_base = os.path.splitext(os.path.basename(source_rom))[0]
    out_base = os.path.splitext(os.path.basename(output_rom))[0] if output_rom else src_base

    src_backup_dir = os.path.join(src_dir, "PMBackups")
    os.makedirs(src_backup_dir, exist_ok=True)
    if out_dir != src_dir:
        os.makedirs(os.path.join(out_dir, "PMBackups"), exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # =========================================================================
    # 1. ROM BACKUP (with automatic cleanup of older ROM backups to save disk)
    # =========================================================================
    rom_bak = os.path.join(src_backup_dir, f"{src_base}.{timestamp}.nds")
    try:
        shutil.copy2(source_rom, rom_bak)
        if is_fr:
            log(f"[Sauvegarde ROM] Copie de secours créée -> PMBackups/{os.path.basename(rom_bak)}")
        else:
            log(f"[ROM Backup] Saved ROM backup -> PMBackups/{os.path.basename(rom_bak)}")

        # Clean older .nds backups in PMBackups keeping the 3 most recent
        all_nds_baks = sorted(glob.glob(os.path.join(src_backup_dir, f"{src_base}.*.nds")), key=os.path.getmtime)
        if len(all_nds_baks) > 3:
            for old_bak in all_nds_baks[:-3]:
                try:
                    os.remove(old_bak)
                except Exception:
                    pass
    except Exception as e:
        log(f"[Backup] Warning: could not backup ROM ({e})")

    # =========================================================================
    # 2. SOURCE SAVES SEARCH & BACKUP (.sav / .dsv)
    # =========================================================================
    source_saves = find_existing_saves(source_rom)
    backed_up_count = 0
    seen_bak_names = set()

    for save_path, ext in source_saves:
        save_stem = os.path.splitext(os.path.basename(save_path))[0]
        # Distinguish subfolder saves (e.g. Backup/ProjectPM.sav -> Backup_ProjectPM)
        parent_sub = os.path.basename(os.path.dirname(save_path))
        if parent_sub.lower() in ("backup", "battery", "saves", "save") and save_stem == src_base:
            save_stem = f"{parent_sub}_{save_stem}"

        bak_filename = f"{save_stem}.{timestamp}{ext}"
        if bak_filename in seen_bak_names:
            bak_filename = f"{save_stem}_{backed_up_count+1}.{timestamp}{ext}"
        seen_bak_names.add(bak_filename)

        save_bak = os.path.join(src_backup_dir, bak_filename)
        try:
            shutil.copy2(save_path, save_bak)
            sz_kb = os.path.getsize(save_bak) // 1024
            backed_up_count += 1
            if is_fr:
                log(f"[Sauvegarde] Copie de secours sécurisée -> PMBackups/{os.path.basename(save_bak)} ({sz_kb} Ko)")
            else:
                log(f"[Save] Backup safely stored -> PMBackups/{os.path.basename(save_bak)} ({sz_kb} KB)")
        except Exception as e:
            log(f"[Backup] Warning: could not backup save {os.path.basename(save_path)} ({e})")

    # =========================================================================
    # 3. DESTINATION SAVES BACKUP (if output_rom already exists with a save)
    # =========================================================================
    if output_rom and os.path.abspath(source_rom) != os.path.abspath(output_rom):
        dest_saves = find_existing_saves(output_rom)
        out_backup_dir = os.path.join(out_dir, "PMBackups")
        os.makedirs(out_backup_dir, exist_ok=True)
        seen_dst_names = set()

        for d_save, ext in dest_saves:
            d_stem = os.path.splitext(os.path.basename(d_save))[0]
            parent_sub = os.path.basename(os.path.dirname(d_save))
            if parent_sub.lower() in ("backup", "battery", "saves", "save") and d_stem == out_base:
                d_stem = f"{parent_sub}_{d_stem}"

            d_filename = f"{d_stem}.{timestamp}{ext}"
            if d_filename in seen_dst_names:
                d_filename = f"{d_stem}_{backed_up_count+1}.{timestamp}{ext}"
            seen_dst_names.add(d_filename)

            d_bak = os.path.join(out_backup_dir, d_filename)
            try:
                shutil.copy2(d_save, d_bak)
                sz_kb = os.path.getsize(d_bak) // 1024
                backed_up_count += 1
                if is_fr:
                    log(f"[Sauvegarde] Sauvegarde existante de la cible sécurisée -> PMBackups/{os.path.basename(d_bak)} ({sz_kb} Ko)")
                else:
                    log(f"[Save] Existing destination save backed up -> PMBackups/{os.path.basename(d_bak)} ({sz_kb} KB)")
            except Exception as e:
                log(f"[Backup] Warning: could not backup destination save ({e})")

    if backed_up_count == 0:
        if is_fr:
            log("[Sauvegarde] Note : Aucune sauvegarde existante (.sav / .dsv) détectée pour cette ROM.")
        else:
            log("[Save] Note: No existing save file (.sav / .dsv) found to backup.")

    # =========================================================================
    # 4. COMPANION SAVE SYNCHRONIZATION
    # =========================================================================
    # If source ROM has a save and target ROM has a different name, copy the save
    # so player can immediately resume playing the newly patched/modded ROM!
    if source_saves and src_base != out_base:
        primary_save, ext = source_saves[0]
        target_save = os.path.join(out_dir, f"{out_base}{ext}")
        try:
            shutil.copy2(primary_save, target_save)
            if is_fr:
                log(f"[Sauvegarde] Sauvegarde synchronisée pour la nouvelle ROM -> {os.path.basename(target_save)}")
            else:
                log(f"[Save] Preserved companion save -> {os.path.basename(target_save)}")
        except Exception as e:
            log(f"[Save] Warning: could not copy companion save ({e})")

    # =========================================================================
    # 5. RANDOMIZER RECORD PRESERVATION (.rand.txt)
    # =========================================================================
    src_rand = os.path.join(src_dir, src_base + ".rand.txt")
    if not os.path.isfile(src_rand) and os.path.isfile(source_rom + ".rand.txt"):
        src_rand = source_rom + ".rand.txt"

    if os.path.isfile(src_rand):
        rand_bak = os.path.join(src_backup_dir, f"{src_base}.{timestamp}.rand.txt")
        try:
            shutil.copy2(src_rand, rand_bak)
        except Exception:
            pass

        if src_base != out_base:
            out_rand = os.path.join(out_dir, out_base + ".nds.rand.txt")
            try:
                shutil.copy2(src_rand, out_rand)
                if is_fr:
                    log(f"[Randomizer] Journal des tables préservé -> {os.path.basename(out_rand)}")
                else:
                    log(f"[Rand] Preserved randomizer record -> {os.path.basename(out_rand)}")
            except Exception as e:
                log(f"[Rand] Warning: could not copy rand record ({e})")

    return True


def open_backups_folder(rom_path: Optional[str] = None) -> bool:
    """
    Opens the PMBackups directory in Windows Explorer.
    """
    folder = get_backup_dir(rom_path) if rom_path else os.path.join(os.getcwd(), "PMBackups")
    os.makedirs(folder, exist_ok=True)

    try:
        if sys.platform == "win32":
            os.startfile(folder)
        else:
            subprocess.Popen(["xdg-open", folder])
        return True
    except Exception as e:
        print(f"[Backup Error] Failed to open folder {folder}: {e}")
        try:
            subprocess.Popen(["explorer", folder])
            return True
        except Exception:
            return False
