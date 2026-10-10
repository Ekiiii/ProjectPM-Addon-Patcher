# -*- coding: utf-8 -*-
"""
bridge.py
PyWebView JS-Python Bridge for ProjectPM Addon Patcher & Randomizer:
- Exposes bidirectional APIs for ROM detection, patching pipeline, and randomizer
- Background async threading with real-time webview callback evaluation
- Native Windows File Dialogs (Open ROM, Save ROM, Select Patches)
- Seed generator & share code encoder/decoder
- Automatic backup management and GitHub updates
"""
import os
import sys
import json
import random
import threading
import webbrowser
import ctypes
from typing import Dict, Any, Optional

import webview

from core.i18n import t, set_lang, get_lang, TRANSLATIONS
from core.rom_detector import detect_rom
from core.patch_pipeline import execute_patch_pipeline
from core.randomizer import (
    randomize_rom,
    encode_coop_code,
    encode_world_code,
    decode_share_code,
    species_name,
    species_id,
    MAX_SPECIES_ID,
    RAND_LEGENDARIES
)
from core.updater import CURRENT_VERSION, check_for_updates_async, GITHUB_REPO
from core.logger import get_physical_logger, open_logs_folder, log_info, log_warning, log_error
from core.config_manager import load_config, save_config, update_config_key


class PatcherBridge:
    def __init__(self, root_dir: str):
        self._root_dir = root_dir
        self._assets_dir = os.path.join(root_dir, "assets")
        self._payloads_dir = os.path.join(root_dir, "payloads")
        self._window: Optional[webview.Window] = None
        self._is_maximized = False
        self._is_patching = False
        self._is_randomizing = False

    def set_window(self, window: webview.Window):
        self._window = window

    def _eval_js(self, js: str):
        """Safely evaluates JavaScript in the active webview window."""
        if self._window:
            try:
                self._window.evaluate_js(js)
            except Exception as e:
                print(f"[Bridge JS Error] {e}")

    # =========================================================================
    # APP INITIALIZATION & LOCALIZATION
    # =========================================================================
    def init_app(self) -> Dict[str, Any]:
        """Returns startup configuration, translations, and initial seeds."""
        cfg = load_config()
        if cfg.get("language"):
            set_lang(cfg["language"])
        cur_lang = get_lang()

        coop_seed = str(random.randint(1000000000, 9999999999))
        world_seed = str(random.randint(1000000000, 9999999999))

        init_coop_code = encode_coop_code({
            'coop_seed': coop_seed,
            'trainers': False,
            'types': False,
            'abilities': False,
            'movesets': False,
            'coop_noleg': False,
            'coop_simstr': False
        })

        init_world_code = encode_world_code({
            'seed': world_seed,
            'wilds': False,
            'mode': 'area_1to1',
            'rule': 'none',
            'noleg': False,
            'starters': False,
            'statics': False,
            'battles': False,
            'gifts': False,
            'trade_get': False,
            'trade_want': False,
            'wild_special': False,
            'gba_slots': False,
            'shiny': 8
        })

        # Format translations for frontend
        trans = {}
        for key, dict_val in TRANSLATIONS.items():
            trans[key] = dict_val.get(cur_lang, dict_val.get("en", key))

        return {
            "version": CURRENT_VERSION,
            "lang": cur_lang,
            "has_selected_language": cfg.get("has_selected_language", False),
            "saved_config": cfg,
            "translations": trans,
            "pokemon_names": self.get_pokemon_names(cur_lang),
            "initial_coop": {
                "seed": coop_seed,
                "code": init_coop_code
            },
            "initial_world": {
                "seed": world_seed,
                "code": init_world_code
            },
            "app_root": self._root_dir.replace("\\", "/")
        }

    def get_pokemon_names(self, lang: str = "fr") -> Dict[str, str]:
        """Loads Pokémon names dictionary directly without frontend fetch CORS."""
        json_file = f"pokemon_names_{lang}.json"
        path = os.path.join(self._root_dir, "ui", "web", "assets", json_file)
        if not os.path.isfile(path):
            path = os.path.join(self._root_dir, "ui", "web", "assets", "pokemon_names_fr.json")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def set_language(self, lang: str) -> Dict[str, Any]:
        """Switches UI language, persists selection, and returns updated translations."""
        set_lang(lang)
        update_config_key("language", lang)
        update_config_key("has_selected_language", True)
        trans = {}
        for key, dict_val in TRANSLATIONS.items():
            trans[key] = dict_val.get(lang, dict_val.get("en", key))
        return {
            "translations": trans,
            "pokemon_names": self.get_pokemon_names(lang)
        }

    def save_app_config(self, cfg_data: Dict[str, Any]) -> bool:
        """Saves user preferences (ROM paths, settings) to disk."""
        return save_config(cfg_data)

    # =========================================================================
    # NATIVE WINDOW CONTROLS & SEAMLESS DRAG
    # =========================================================================
    def window_drag(self):
        """No-op: pywebview-drag-region provides smooth native window dragging."""
        pass

    def window_minimize(self):
        """Minimizes the application window."""
        try:
            if self._window:
                self._window.minimize()
        except Exception as e:
            print(f"[Window Minimize Error] {e}")

    def window_toggle_maximize(self):
        """Toggles between maximized and restored window state."""
        try:
            if self._window:
                if self._is_maximized:
                    self._window.restore()
                    self._is_maximized = False
                else:
                    self._window.maximize()
                    self._is_maximized = True
        except Exception as e:
            print(f"[Window Maximize Error] {e}")

    def window_close(self):
        """Closes the application."""
        try:
            if self._window:
                self._window.destroy()
        except Exception as e:
            print(f"[Window Close Error] {e}")

    # =========================================================================
    # FILE DIALOGS
    # =========================================================================
    def browse_source_rom(self) -> Optional[str]:
        """Opens native file picker for selecting source Nintendo DS ROM."""
        if not self._window:
            return None
        file_types = ('Nintendo DS ROMs (*.nds)', 'All Files (*.*)')
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )
        if result and len(result) > 0:
            return os.path.abspath(result[0]).replace("\\", "/")
        return None

    def browse_save_rom(self, default_name: str = "") -> Optional[str]:
        """Opens native save file picker for destination ROM."""
        if not self._window:
            return None
        file_types = ('Nintendo DS ROM (*.nds)',)
        result = self._window.create_file_dialog(
            webview.SAVE_DIALOG,
            save_filename=default_name or "ProjectPM_modded.nds",
            file_types=file_types
        )
        if result:
            p = result if isinstance(result, str) else result[0]
            if not p.lower().endswith(".nds"):
                p += ".nds"
            return os.path.abspath(p).replace("\\", "/")
        return None

    def browse_patch_file(self) -> Optional[str]:
        """Opens native file picker for xDelta patch files."""
        if not self._window:
            return None
        file_types = ('xDelta Patches (*.xdelta)', 'All Files (*.*)')
        result = self._window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )
        if result and len(result) > 0:
            return os.path.abspath(result[0]).replace("\\", "/")
        return None

    # =========================================================================
    # ROM DETECTION & BADGES
    # =========================================================================
    def analyze_rom(self, rom_path: str) -> Dict[str, Any]:
        """Performs deep binary analysis on ROM and returns badges and state."""
        if not rom_path or not os.path.isfile(rom_path):
            log_warning(f"analyze_rom called with invalid path: {rom_path}")
            return {"valid": False, "error": t("err_file_not_found")}

        try:
            log_info(f"Analyzing ROM: {rom_path}")
            info = detect_rom(rom_path)
            if not info or not info.is_valid:
                log_warning(f"ROM detection failed or invalid: {rom_path}")
                return {
                    "valid": False,
                    "error": t("err_invalid_rom")
                }
            log_info(f"ROM detected: game={info.game_title}, lang={info.lang}, mp={info.has_multiplayer} ({info.mp_lang}), sl={info.has_soullocke} ({info.soullocke_variant}), rand={info.is_randomized}")

            # Generate suggested output name
            dir_name = os.path.dirname(os.path.abspath(rom_path))
            base_no_ext = os.path.splitext(os.path.basename(rom_path))[0]
            if info.has_soullocke:
                sug_name = f"{base_no_ext}_Clean.nds"
            elif info.has_multiplayer:
                sug_name = f"{base_no_ext}_Modded.nds"
            else:
                sug_name = f"ProjectPM_{info.lang.upper()}_Multiplayer.nds"
            sug_path = os.path.join(dir_name, sug_name).replace("\\", "/")

            # Persist last selected ROM paths
            try:
                update_config_key("last_source_rom", rom_path)
                update_config_key("last_output_rom", sug_path)
            except Exception:
                pass

            cur_l = get_lang()
            badges = []

            # 1. Base Game Badge
            if info.lang == "fr":
                badges.append({
                    "key": "badge_platine_fr",
                    "label": t("badge_platine_fr"),
                    "color": "blue"
                })
            else:
                badges.append({
                    "key": "badge_platine_us",
                    "label": t("badge_platine_us"),
                    "color": "blue"
                })

            # 2. Multiplayer Badge
            if info.has_multiplayer:
                mp_key = "badge_mp_active_fr" if info.mp_lang == "fr" else "badge_mp_active_en"
                badges.append({
                    "key": mp_key,
                    "label": t(mp_key),
                    "color": "emerald"
                })
            else:
                badges.append({
                    "key": "badge_mp_none",
                    "label": t("badge_mp_none"),
                    "color": "slate"
                })

            # 3. SoulLocke Badge
            if info.has_soullocke:
                badges.append({
                    "key": "badge_sl_active",
                    "label": t("badge_sl_active"),
                    "color": "purple"
                })
            else:
                badges.append({
                    "key": "badge_sl_none",
                    "label": t("badge_sl_none"),
                    "color": "slate"
                })

            # 4. Randomizer Badge
            if info.is_randomized:
                badges.append({
                    "key": "badge_rand_yes",
                    "label": t("badge_rand_yes"),
                    "color": "amber"
                })
            else:
                badges.append({
                    "key": "badge_rand_no",
                    "label": t("badge_rand_no"),
                    "color": "slate"
                })

            # 5. Visual+ Badges
            if info.has_visualplus_bg:
                badges.append({
                    "key": "badge_vbg_yes",
                    "label": t("badge_vbg_yes"),
                    "color": "cyan"
                })
            if info.has_visualplus_cam:
                badges.append({
                    "key": "badge_vcam_yes",
                    "label": t("badge_vcam_yes"),
                    "color": "cyan"
                })

            # 6. Multi Exp Badge
            if info.has_exp_share:
                badges.append({
                    "key": "badge_exp_share_yes",
                    "label": t("badge_exp_share_yes"),
                    "color": "emerald"
                })
            else:
                badges.append({
                    "key": "badge_exp_share_no",
                    "label": t("badge_exp_share_no"),
                    "color": "slate"
                })

            return {
                "valid": True,
                "path": rom_path.replace("\\", "/"),
                "filename": os.path.basename(rom_path),
                "game": info.game_title,
                "game_code": info.game_code,
                "lang": info.lang,
                "has_multiplayer": info.has_multiplayer,
                "mp_version": info.mp_version,
                "mp_lang": info.mp_lang,
                "has_soullocke": info.has_soullocke,
                "soullocke_variant": info.soullocke_variant,
                "is_randomized": info.is_randomized,
                "has_visualplus_bg": info.has_visualplus_bg,
                "has_visualplus_cam": info.has_visualplus_cam,
                "has_exp_share": bool(info.has_exp_share),
                "size_mb": round(os.path.getsize(rom_path) / (1024 * 1024), 1),
                "suggested_output": sug_path,
                "badges": badges
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}

    # =========================================================================
    # SHARE CODES & SEEDS
    # =========================================================================
    def generate_coop_code(self, settings: Dict[str, Any]) -> Dict[str, str]:
        """Encodes or generates a PMC-XXXX-XXXX Co-op code."""
        if not settings.get('coop_seed'):
            settings['coop_seed'] = str(random.randint(1000000000, 9999999999))
        code = encode_coop_code(settings)
        return {"code": code, "seed": str(settings['coop_seed'])}

    def generate_world_code(self, settings: Dict[str, Any]) -> Dict[str, str]:
        """Encodes or generates a PMW-XXXX-XXXX Personal/World code."""
        if not settings.get('seed'):
            settings['seed'] = str(random.randint(1000000000, 9999999999))
        code = encode_world_code(settings)
        return {"code": code, "seed": str(settings['seed'])}

    def decode_code(self, code_str: str) -> Dict[str, Any]:
        """Decodes a share code (PMC or PMW) into its settings dict."""
        settings, err = decode_share_code(code_str)
        if err:
            return {"success": False, "error": err}
        return {"success": True, "settings": settings}

    # =========================================================================
    # PATCHING PIPELINE EXECUTION
    # =========================================================================
    def run_patching(self, in_rom: str, out_rom: str, options: Dict[str, Any]):
        """Runs the patcher pipeline in a background thread."""
        if self._is_patching:
            return {"success": False, "error": t("err_patching_in_progress")}

        self._is_patching = True

        def _worker():
            try:
                def _log(msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onPatchLog({escaped});")

                def _prog(val: float, msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onPatchProgress({val}, {escaped});")

                phys_log = get_physical_logger(_log)
                phys_log(f"Starting patch pipeline: input='{in_rom}', output='{out_rom}'")
                phys_log(f"Options: {json.dumps(options)}")

                ok, res_msg = execute_patch_pipeline(
                    rom_path=in_rom,
                    output_rom=out_rom,
                    options=options,
                    assets_dir=self._assets_dir,
                    payloads_dir=self._payloads_dir,
                    log_cb=phys_log,
                    progress_cb=_prog
                )
                phys_log(f"Patch pipeline complete: ok={ok}, res_msg='{res_msg}'")
                escaped_res = json.dumps(res_msg)
                self._eval_js(f"window.onPatchComplete({json.dumps(ok)}, {escaped_res});")
            except Exception as e:
                log_error(f"Unhandled error in patch worker: {e}", exc=e)
                escaped_res = json.dumps(str(e))
                self._eval_js(f"window.onPatchComplete(false, {escaped_res});")
            finally:
                self._is_patching = False

        t_thread = threading.Thread(target=_worker, daemon=True)
        t_thread.start()
        return {"started": True}

    # =========================================================================
    # RANDOMIZER EXECUTION
    # =========================================================================
    def run_randomizer(self, in_rom: str, out_rom: str, settings: Dict[str, Any]):
        """Runs the randomizer engine in a background thread."""
        if self._is_randomizing:
            return {"success": False, "error": t("err_randomizing_in_progress")}

        self._is_randomizing = True

        def _worker():
            try:
                def _log(msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onRandLog({escaped});")

                phys_log = get_physical_logger(_log)
                start_msg = "=== Starting Project PM Randomization ===" if get_lang() == "en" else "=== Démarrage de la Randomisation Project PM ==="
                phys_log(start_msg)
                phys_log(f"Input: '{in_rom}', Output: '{out_rom}'")
                phys_log(f"Settings: {json.dumps(settings)}")

                ok, summary = randomize_rom(
                    rom_path=in_rom,
                    out_path=out_rom,
                    settings=settings,
                    log=phys_log
                )
                phys_log(f"Randomizer finished: ok={ok}")

                # Format starters display names
                starters_info = []
                if ok and 'starters' in summary:
                    for sid in summary['starters']:
                        starters_info.append({
                            "id": sid,
                            "name": species_name(sid)
                        })

                payload = {
                    "ok": ok,
                    "starters": starters_info,
                    "coop_code": summary.get('coop_code', ''),
                    "world_code": summary.get('world_code', ''),
                    "coop_seed": summary.get('coop_seed', ''),
                    "seed": summary.get('seed', ''),
                    "report_file": f"{os.path.basename(out_rom)}.rand.txt" if ok else ""
                }
                self._eval_js(f"window.onRandComplete({json.dumps(payload)});")
            except Exception as e:
                log_error(f"Unhandled error in randomizer worker: {e}", exc=e)
                self._eval_js(f"window.onRandComplete({json.dumps({'ok': False, 'error': str(e)})});")
            finally:
                self._is_randomizing = False

        t_thread = threading.Thread(target=_worker, daemon=True)
        t_thread.start()
        return {"started": True}

    # =========================================================================
    # EXTERNAL ACTIONS & UPDATES
    # =========================================================================
    def open_external_url(self, url: str):
        """Opens web link in the user's default browser or folder in explorer."""
        if url.startswith("http://") or url.startswith("https://"):
            webbrowser.open(url)
        else:
            self.open_backups_folder(url)

    def open_backups_folder(self, rom_path: Optional[str] = None):
        """Opens the PMBackups directory in Windows Explorer."""
        from core.save_manager import open_backups_folder
        open_backups_folder(rom_path)

    def open_logs_folder(self):
        """Opens the physical on-disk logs directory in Windows Explorer."""
        open_logs_folder()

    def check_for_updates(self):
        """Checks GitHub releases for latest version in background."""
        def _cb(available: bool, latest_ver: str, release_data: Optional[Dict[str, Any]] = None, err: Optional[str] = None):
            payload = {
                "available": bool(available),
                "current": CURRENT_VERSION,
                "latest": latest_ver or CURRENT_VERSION,
                "notes": release_data.get("body", "") if isinstance(release_data, dict) else "",
                "url": release_data.get("html_url", "") if isinstance(release_data, dict) else f"https://github.com/{GITHUB_REPO}/releases",
                "error": err
            }
            self._eval_js(f"window.onUpdateCheckResult({json.dumps(payload)});")

        check_for_updates_async(_cb, current_ver=CURRENT_VERSION)
        return {"checking": True}
