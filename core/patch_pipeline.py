# -*- coding: utf-8 -*-
"""
patch_pipeline.py
Unified execution pipeline for ProjectPM Addon Patcher:
- Vanilla Platinum to ProjectPM conversion via xdelta3
- SoulLocke / Soul Link C mod injection / restoration
- Visual+ Battle Backgrounds & 3D Camera mods
- Randomizer tables preservation and restoration across patches
- Save file synchronization (.dsv/.sav)
- Optional custom xDelta patches
"""
import os
import shutil
from typing import Dict, Any, Callable, Optional, Tuple

from core.i18n import t
from core.rom_detector import detect_rom
from core.smart_injector import apply_soullocke, restore_clean_projectpm
from core.visual_patcher import apply_battle_bg_patch, apply_camera_patch
from core.xdelta_engine import apply_xdelta
from core.save_manager import backup_and_sync_save
from core.rand_manager import extract_randomizer_data, clean_vanilla_for_xdelta, restore_randomizer_data


def execute_patch_pipeline(
    rom_path: str,
    output_rom: str,
    options: Dict[str, Any],
    assets_dir: str,
    payloads_dir: str,
    log_cb: Callable[[str], None] = print,
    progress_cb: Optional[Callable[[float, str], None]] = None
) -> Tuple[bool, str]:
    """
    Executes the full patching pipeline synchronously.
    Returns (success, message_or_error).
    """
    def _progress(val: float, msg: str):
        if progress_cb:
            progress_cb(val, msg)
        log_cb(f"[{int(val*100)}%] {msg}")

    temp_clean = None
    temp_base = None
    temp_pre_custom = None

    try:
        if not os.path.isfile(rom_path):
            raise FileNotFoundError(f"ROM source introuvable : {rom_path}")

        _progress(0.05, "Analyse de la ROM source...")
        info = detect_rom(rom_path)
        if not info or not info.is_valid:
            raise ValueError("Le fichier sélectionné n'est pas une ROM Nintendo DS valide (Pokémon Platine).")

        bg_opt = options.get("bg_opt", "none")
        cam_opt = options.get("cam_opt", "none")
        backup_save = options.get("backup_save", True)

        # Multiplayer mode
        mp_enabled = options.get("mp_enabled", False)
        mp_version = options.get("mp_version", "fr")
        if info.has_multiplayer:
            effective_mp = info.mp_lang
        elif mp_enabled:
            effective_mp = mp_version
        else:
            effective_mp = None

        # Addon modes
        sl_enabled = options.get("sl_enabled", False)
        sl_mode = options.get("sl_mode", "apply")
        sl_variant = options.get("sl_variant", "fr")

        out_dir = os.path.dirname(os.path.abspath(output_rom))
        os.makedirs(out_dir, exist_ok=True)

        # 0. Preserve randomizer tables if input is randomized
        _progress(0.15, "Extraction et préservation des tables randomisées...")
        rand_data = extract_randomizer_data(rom_path, log_cb=log_cb)
        if rand_data.get("is_randomized"):
            log_cb(f"[Pipeline] {len(rand_data.get('files', []))} tables randomisées détectées et sauvegardées.")

        working_rom = rom_path

        # 1. Base ROM check: Vanilla -> Multiplayer conversion via xDelta
        if not info.has_multiplayer and effective_mp in ("fr", "en"):
            _progress(0.30, f"Conversion de la ROM Vanilla vers ProjectPM Multiplayer ({effective_mp.upper()})...")
            temp_base = os.path.join(out_dir, f"temp_pm_base_{os.getpid()}.nds")

            if effective_mp == "fr":
                if info.lang == "fr":
                    patch_name = "PlatinumMultiplayerV0.4.5_FR.xdelta"
                else:
                    patch_name = "PlatinumMultiplayerV0.4.5_FR-From-USA.xdelta"
            else:
                patch_name = "PlatinumMultiplayerV0.4.5.xdelta"

            patch_file = os.path.join(assets_dir, "base_patches", patch_name)
            if not os.path.isfile(patch_file):
                raise FileNotFoundError(f"Patch xDelta multijoueur introuvable : {patch_file}")

            clean_src = rom_path
            if rand_data.get("is_randomized"):
                temp_clean = os.path.join(out_dir, f"temp_clean_vanilla_{os.getpid()}.nds")
                clean_src = clean_vanilla_for_xdelta(
                    rom_path, temp_clean, lang=info.lang, assets_dir=assets_dir, log_cb=log_cb
                )

            xd_exe = os.path.join(assets_dir, "xdelta3.exe")
            ok = apply_xdelta(clean_src, patch_file, temp_base, xd_exe, log_cb)
            if not ok:
                raise RuntimeError("Échec de l'application du patch xDelta ProjectPM.")
            working_rom = temp_base

        # 2. Save Backup
        if backup_save:
            _progress(0.45, "Sauvegarde et synchronisation des fichiers .sav / .dsv...")
            try:
                backup_and_sync_save(rom_path, output_rom, log_cb)
            except Exception as e:
                log_cb(f"[Avertissement] Synchronisation sauvegarde ignorée : {e}")

        # 3. Apply Mod / SoulLocke
        _progress(0.60, "Application du mod SoulLink / SoulLocke...")
        if sl_mode == "restore":
            payload_json = os.path.join(payloads_dir, f"soullocke_{info.lang}.json")
            ok = restore_clean_projectpm(working_rom, output_rom, payload_json, log_cb)
            if not ok:
                raise RuntimeError("Échec de la restauration vers ProjectPM d'origine.")
        elif sl_enabled and effective_mp:
            payload_json = os.path.join(payloads_dir, f"soullocke_{sl_variant}.json")
            if not os.path.isfile(payload_json):
                payload_json = os.path.join(payloads_dir, "soullocke_fr.json")
            ok = apply_soullocke(working_rom, output_rom, payload_json, log_cb)
            if not ok:
                raise RuntimeError("Échec de l'injection du payload C SoulLocke.")
        else:
            shutil.copy2(working_rom, output_rom)

        # 4. Clean up intermediate base files
        for f in (temp_clean, temp_base):
            if f and os.path.isfile(f):
                try:
                    os.remove(f)
                except Exception:
                    pass

        # 5. Visual+ Backgrounds
        if bg_opt == "builtin":
            _progress(0.75, "Application des décors de combat Visual+...")
            apply_battle_bg_patch(output_rom, assets_dir, enable=True, log_cb=log_cb)
        elif bg_opt == "off":
            _progress(0.75, "Désactivation des décors de combat Visual+...")
            apply_battle_bg_patch(output_rom, assets_dir, enable=False, log_cb=log_cb)

        # 6. Visual+ 3D Camera
        if cam_opt == "builtin":
            _progress(0.85, "Application de la caméra 3D élargie Visual+...")
            apply_camera_patch(output_rom, enable=True, log_cb=log_cb)
        elif cam_opt == "off":
            _progress(0.85, "Restauration de la caméra par défaut...")
            apply_camera_patch(output_rom, enable=False, log_cb=log_cb)

        # 7. Restore randomizer tables
        if rand_data.get("is_randomized"):
            _progress(0.92, "Réinjection des tables randomisées sur la ROM finale...")
            restore_randomizer_data(output_rom, rand_data, log_cb=log_cb)

        # 8. Custom xDelta patch
        custom_patch = options.get("custom_patch")
        if custom_patch and os.path.isfile(custom_patch):
            _progress(0.95, f"Application du patch personnalisé : {os.path.basename(custom_patch)}...")
            temp_pre_custom = output_rom + f".pre_custom_{os.getpid()}.tmp"
            shutil.copy2(output_rom, temp_pre_custom)
            xd_exe = os.path.join(assets_dir, "xdelta3.exe")
            ok = apply_xdelta(temp_pre_custom, custom_patch, output_rom, xd_exe, log_cb)
            if not ok:
                shutil.copy2(temp_pre_custom, output_rom)
                raise RuntimeError(f"Échec de l'application du patch personnalisé : {os.path.basename(custom_patch)}")
            if os.path.isfile(temp_pre_custom):
                try:
                    os.remove(temp_pre_custom)
                except Exception:
                    pass

        _progress(1.0, "Patch terminé avec succès !")
        return True, "Patch appliqué avec succès !"

    except Exception as e:
        log_cb(f"[ERREUR] {str(e)}")
        return False, str(e)
    finally:
        for f in (temp_clean, temp_base, temp_pre_custom):
            if f and os.path.isfile(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
