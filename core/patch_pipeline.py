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
import re
import shutil
from typing import Dict, Any, Callable, Optional, Tuple

from core.i18n import t
from core.rom_detector import detect_rom
from core.smart_injector import apply_soullocke, restore_clean_projectpm
from core.visual_patcher import apply_battle_bg_patch, apply_camera_patch
from core.xdelta_engine import apply_xdelta
from core.save_manager import backup_and_sync_save
from core.rand_manager import (
    extract_randomizer_data,
    clean_vanilla_for_xdelta,
    clean_projectpm_for_xdelta,
    restore_randomizer_data
)
from core.lang_switcher import switch_projectpm_lang


def resolve_base_patch(target_mp: str, source_lang: str, assets_dir: str) -> str:
    """
    Finds the appropriate xDelta patch for converting Vanilla to Multiplayer.
    Dynamically scans assets/base_patches for the highest matching version,
    seamlessly supporting 0.4.5, 0.4.6, 0.5.0, etc.
    """
    base_dir = os.path.join(assets_dir, "base_patches")
    if not os.path.isdir(base_dir):
        return ""
    if target_mp == "fr":
        if source_lang == "fr":
            pattern = re.compile(r"^PlatinumMultiplayerV(.*)_FR\.xdelta$", re.IGNORECASE)
            fallback = "PlatinumMultiplayerV0.4.5_FR.xdelta"
        else:
            pattern = re.compile(r"^PlatinumMultiplayerV(.*)_FR-From-USA\.xdelta$", re.IGNORECASE)
            fallback = "PlatinumMultiplayerV0.4.5_FR-From-USA.xdelta"
    else:
        pattern = re.compile(r"^PlatinumMultiplayerV(?!.*FR)(.*)\.xdelta$", re.IGNORECASE)
        fallback = "PlatinumMultiplayerV0.4.5.xdelta"

    candidates = [f for f in os.listdir(base_dir) if pattern.match(f)]
    if candidates:
        candidates.sort(reverse=True)
        return candidates[0]
    return fallback


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

        _progress(0.05, t("progress_analyzing"))
        info = detect_rom(rom_path)
        if not info or not info.is_valid:
            raise ValueError(t("err_invalid_rom"))

        bg_opt = options.get("bg_opt", "none")
        cam_opt = options.get("cam_opt", "none")
        backup_save = options.get("backup_save", True)
        team_exp_share = options.get("team_exp_share", False)
        if team_exp_share:
            log_cb("[Mods] Exp. Partagée d'équipe: Activée (Partage de l'expérience de combat avec toute l'équipe).")

        # Multiplayer mode
        mp_enabled = options.get("mp_enabled", True)
        mp_version = options.get("mp_version", "fr")
        if not mp_enabled or mp_version == "none":
            effective_mp = None
        else:
            effective_mp = mp_version  # "fr" or "en"

        # Addon modes
        sl_enabled = options.get("sl_enabled", False)
        sl_mode = options.get("sl_mode", "apply")
        sl_variant = options.get("sl_variant", effective_mp or "fr")

        out_dir = os.path.dirname(os.path.abspath(output_rom))
        os.makedirs(out_dir, exist_ok=True)

        # 0. Preserve randomizer tables if input is randomized
        _progress(0.15, t("progress_extract_rand"))
        rand_data = extract_randomizer_data(rom_path, log_cb=log_cb)
        if rand_data.get("is_randomized"):
            log_cb(f"[Pipeline] {len(rand_data.get('files', []))} randomized tables detected & safely snapshotted.")

        working_rom = rom_path

        # 1. Base ROM handling:
        # Case A: Vanilla -> Multiplayer conversion via xDelta
        # Case B: Already Multiplayer -> Language switch (e.g. US -> FR or FR -> US)
        if not info.has_multiplayer and effective_mp in ("fr", "en"):
            _progress(0.30, t("progress_convert_mp", effective_mp.upper()))
            temp_base = os.path.join(out_dir, f"temp_pm_base_{os.getpid()}.nds")

            patch_name = resolve_base_patch(effective_mp, info.lang, assets_dir)
            patch_file = os.path.join(assets_dir, "base_patches", patch_name)
            if not os.path.isfile(patch_file):
                raise FileNotFoundError(f"Patch xDelta not found: {patch_file}")

            clean_src = rom_path
            if rand_data.get("is_randomized"):
                temp_clean = os.path.join(out_dir, f"temp_clean_vanilla_{os.getpid()}.nds")
                clean_src = clean_vanilla_for_xdelta(
                    rom_path, temp_clean, lang=info.lang, assets_dir=assets_dir, log_cb=log_cb
                )

            xd_exe = os.path.join(assets_dir, "xdelta3.exe")
            ok = apply_xdelta(clean_src, patch_file, temp_base, xd_exe, log_cb)
            if not ok:
                raise RuntimeError("Failed to apply ProjectPM xDelta base patch.")
            working_rom = temp_base

        elif info.has_multiplayer and effective_mp in ("fr", "en") and effective_mp != info.mp_lang:
            src_lang = info.mp_lang
            dst_lang = effective_mp
            _progress(0.30, t("progress_switch_mp", src_lang.upper(), dst_lang.upper()))
            log_cb(f"[Pipeline] Switching Multiplayer language: {src_lang.upper()} -> {dst_lang.upper()}")
            temp_base = os.path.join(out_dir, f"temp_pm_switch_lang_{os.getpid()}.nds")

            # Determine appropriate patch based on current ROM characteristics
            if src_lang == "en" and dst_lang == "fr":
                patch_name = "ProjectPM_USA_to_FR.xdelta"
            else:
                if info.has_visual_bg or info.has_visual_cam:
                    patch_name = "ProjectPM_FR_VisualPlus_to_USA.xdelta"
                else:
                    patch_name = "ProjectPM_FR_to_USA.xdelta"

            patch_file = os.path.join(assets_dir, "base_patches", patch_name)
            xd_exe = os.path.join(assets_dir, "xdelta3.exe")

            clean_src = working_rom
            temp_clean_sl = None
            temp_clean_rand = None

            # If SoulLocke active, clean hooks for xdelta
            if info.is_soullocke:
                temp_clean_sl = os.path.join(out_dir, f"temp_clean_sl_{os.getpid()}.nds")
                payload_json = os.path.join(payloads_dir, f"soullocke_{src_lang}.json")
                if not os.path.isfile(payload_json):
                    payload_json = os.path.join(payloads_dir, "soullocke_fr.json")
                if restore_clean_projectpm(clean_src, temp_clean_sl, payload_json, log_cb=log_cb):
                    clean_src = temp_clean_sl

            # If randomized, clean tables for xdelta
            if rand_data.get("is_randomized"):
                temp_clean_rand = os.path.join(out_dir, f"temp_clean_rand_{os.getpid()}.nds")
                clean_src = clean_projectpm_for_xdelta(
                    clean_src, temp_clean_rand, lang=src_lang, assets_dir=assets_dir, log_cb=log_cb
                )

            patched_ok = False
            if os.path.isfile(patch_file):
                patched_ok = apply_xdelta(clean_src, patch_file, temp_base, xd_exe, log_cb)

            # Fallback: if xdelta failed (custom mod / non-standard base), use smart file-swap
            if not patched_ok:
                log_cb("[Pipeline] Notice: Applying Direct Localized Translation Engine...")
                src_for_swap = clean_src if (clean_src and os.path.isfile(clean_src)) else working_rom
                patched_ok = switch_projectpm_lang(
                    src_for_swap, temp_base, target_lang=dst_lang, assets_dir=assets_dir, log_cb=log_cb
                )

            # Cleanup intermediate xdelta clean files
            for f in (temp_clean_sl, temp_clean_rand):
                if f and os.path.isfile(f) and f != temp_base:
                    try:
                        os.remove(f)
                    except Exception:
                        pass

            if not patched_ok or not os.path.isfile(temp_base):
                raise RuntimeError(f"Failed to switch ProjectPM multiplayer language ({src_lang.upper()} -> {dst_lang.upper()}).")

            working_rom = temp_base
            log_cb(f"[Pipeline] Multiplayer language successfully switched to {dst_lang.upper()}!")

        # 2. Save Backup
        if backup_save:
            _progress(0.45, t("progress_save_backup"))
            try:
                backup_and_sync_save(rom_path, output_rom, log_cb)
            except Exception as e:
                log_cb(f"[Warning] Save sync skipped: {e}")

        # 3. Apply Mod / SoulLocke
        effective_sl_lang = effective_mp or info.lang
        if sl_mode == "restore":
            _progress(0.60, t("progress_restore_projectpm"))
            payload_json = os.path.join(payloads_dir, f"soullocke_{info.lang}.json")
            if not os.path.isfile(payload_json):
                payload_json = os.path.join(payloads_dir, f"soullocke_{sl_variant}.json")
            if not os.path.isfile(payload_json):
                payload_json = os.path.join(payloads_dir, "soullocke_fr.json")
            ok = restore_clean_projectpm(working_rom, output_rom, payload_json, log_cb)
            if not ok:
                raise RuntimeError("Failed to restore clean ProjectPM ROM.")
        elif sl_enabled and effective_mp:
            _progress(0.60, t("progress_apply_soullocke"))
            payload_json = os.path.join(payloads_dir, f"soullocke_{effective_sl_lang}.json")
            if not os.path.isfile(payload_json):
                payload_json = os.path.join(payloads_dir, "soullocke_fr.json")
            ok = apply_soullocke(working_rom, output_rom, payload_json, log_cb)
            if not ok:
                raise RuntimeError("Failed to inject SoulLocke C payload.")
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
            _progress(0.75, t("progress_apply_visual_bg"))
            apply_battle_bg_patch(output_rom, assets_dir, enable=True, log_cb=log_cb)
        elif bg_opt == "off":
            _progress(0.75, t("progress_disable_visual_bg"))
            apply_battle_bg_patch(output_rom, assets_dir, enable=False, log_cb=log_cb)

        # 6. Visual+ 3D Camera
        if cam_opt == "builtin":
            _progress(0.85, t("progress_apply_visual_cam"))
            apply_camera_patch(output_rom, enable=True, log_cb=log_cb)
        elif cam_opt == "off":
            _progress(0.85, t("progress_restore_visual_cam"))
            apply_camera_patch(output_rom, enable=False, log_cb=log_cb)

        # 6b. Shared Team EXP Mod
        from core.exp_share_patcher import apply_exp_share_patch, is_exp_share_active
        if team_exp_share:
            _progress(0.88, t("exp_share_title"))
            apply_exp_share_patch(output_rom, enable=True, log_cb=log_cb)
        elif is_exp_share_active(output_rom):
            _progress(0.88, t("exp_share_title"))
            apply_exp_share_patch(output_rom, enable=False, log_cb=log_cb)

        # 7. Custom xDelta patch (applied before final randomizer restoration)
        custom_patch = options.get("custom_patch")
        if custom_patch and os.path.isfile(custom_patch):
            _progress(0.90, t("progress_apply_custom", os.path.basename(custom_patch)))
            temp_pre_custom = output_rom + f".pre_custom_{os.getpid()}.tmp"
            shutil.copy2(output_rom, temp_pre_custom)
            xd_exe = os.path.join(assets_dir, "xdelta3.exe")
            ok = apply_xdelta(temp_pre_custom, custom_patch, output_rom, xd_exe, log_cb)
            if not ok:
                shutil.copy2(temp_pre_custom, output_rom)
                raise RuntimeError(f"Failed to apply custom patch: {os.path.basename(custom_patch)}")
            if os.path.isfile(temp_pre_custom):
                try:
                    os.remove(temp_pre_custom)
                except Exception:
                    pass

        rand_enabled = options.get("rand_enabled", False)
        rand_settings = options.get("rand_settings")

        # 8. Integrated Randomizer execution OR Guaranteed Re-application at the VERY END
        if rand_enabled and rand_settings:
            _progress(0.95, t("progress_running_rand"))
            from core.randomizer import randomize_rom
            ok, r_summary = randomize_rom(
                in_rom=output_rom,
                out_rom=output_rom,
                settings=rand_settings,
                log=log_cb
            )
            if not ok:
                raise RuntimeError(t("err_rand_failed"))
            log_cb(f"[Randomizer] Successfully generated companion summary: {os.path.basename(output_rom)}.rand.txt")
        elif rand_data.get("is_randomized"):
            # Source ROM already had randomization and user didn't generate new ones:
            # Re-apply all preserved randomizer tables at the VERY END so no prior patch can alter them!
            _progress(0.95, t("progress_restore_rand"))
            log_cb(f"[Randomizer] Existing randomization detected ({len(rand_data.get('files', {}))} tables): re-applying at the end of patching to ensure 100% preservation...")
            restore_randomizer_data(output_rom, rand_data, log_cb=log_cb)

        _progress(1.0, t("progress_success"))
        return True, t("progress_success")


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
