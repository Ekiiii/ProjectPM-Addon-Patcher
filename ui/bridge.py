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
from core.updater import CURRENT_VERSION, check_for_updates_async


class PatcherBridge:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.assets_dir = os.path.join(root_dir, "assets")
        self.payloads_dir = os.path.join(root_dir, "payloads")
        self.window: Optional[webview.Window] = None
        self._is_patching = False
        self._is_randomizing = False

    def set_window(self, window: webview.Window):
        self.window = window

    def _eval_js(self, js: str):
        """Safely evaluates JavaScript in the active webview window."""
        if self.window:
            try:
                self.window.evaluate_js(js)
            except Exception as e:
                print(f"[Bridge JS Error] {e}")

    # =========================================================================
    # APP INITIALIZATION & LOCALIZATION
    # =========================================================================
    def init_app(self) -> Dict[str, Any]:
        """Returns startup configuration, translations, and initial seeds."""
        cur_lang = get_lang()
        coop_seed = str(random.randint(1000000000, 9999999999))
        world_seed = str(random.randint(1000000000, 9999999999))

        init_coop_code = encode_coop_code({
            'coop_seed': coop_seed,
            'trainers': True,
            'types': True,
            'abilities': True,
            'movesets': True,
            'coop_noleg': True,
            'coop_simstr': False
        })

        init_world_code = encode_world_code({
            'seed': world_seed,
            'wilds': True,
            'mode': 'area_1to1',
            'rule': 'similar_strength',
            'noleg': True,
            'starters': True,
            'statics': True,
            'shiny': 64
        })

        # Format translations for frontend
        trans = {}
        for key, dict_val in TRANSLATIONS.items():
            trans[key] = dict_val.get(cur_lang, dict_val.get("en", key))

        return {
            "version": CURRENT_VERSION,
            "lang": cur_lang,
            "translations": trans,
            "initial_coop": {
                "seed": coop_seed,
                "code": init_coop_code
            },
            "initial_world": {
                "seed": world_seed,
                "code": init_world_code
            },
            "app_root": self.root_dir.replace("\\", "/")
        }

    def set_language(self, lang: str) -> Dict[str, str]:
        """Switches UI language and returns updated translations."""
        set_lang(lang)
        trans = {}
        for key, dict_val in TRANSLATIONS.items():
            trans[key] = dict_val.get(lang, dict_val.get("en", key))
        return trans

    # =========================================================================
    # FILE DIALOGS
    # =========================================================================
    def browse_source_rom(self) -> Optional[str]:
        """Opens native file picker for selecting source Nintendo DS ROM."""
        if not self.window:
            return None
        file_types = ('Nintendo DS ROMs (*.nds)', 'All Files (*.*)')
        result = self.window.create_file_dialog(
            webview.OPEN_DIALOG,
            allow_multiple=False,
            file_types=file_types
        )
        if result and len(result) > 0:
            return os.path.abspath(result[0]).replace("\\", "/")
        return None

    def browse_save_rom(self, default_name: str = "") -> Optional[str]:
        """Opens native save file picker for destination ROM."""
        if not self.window:
            return None
        file_types = ('Nintendo DS ROM (*.nds)',)
        result = self.window.create_file_dialog(
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
        if not self.window:
            return None
        file_types = ('xDelta Patches (*.xdelta)', 'All Files (*.*)')
        result = self.window.create_file_dialog(
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
            return {"valid": False, "error": "Fichier introuvable"}

        try:
            info = detect_rom(rom_path)
            if not info or not info.is_valid:
                return {
                    "valid": False,
                    "error": "Ce fichier n'est pas une ROM Pokémon Platine valide."
                }

            # Generate suggested output name
            dir_name = os.path.dirname(os.path.abspath(rom_path))
            base_no_ext = os.path.splitext(os.path.basename(rom_path))[0]
            if info.has_multiplayer:
                sug_name = f"{base_no_ext}_Modded.nds"
            else:
                sug_name = f"ProjectPM_{info.lang.upper()}_Multiplayer.nds"
            sug_path = os.path.join(dir_name, sug_name).replace("\\", "/")

            badges = []
            # Base game badge
            badges.append({
                "label": f"Pokémon Platine ({info.lang.upper()})",
                "color": "blue"
            })

            # Multiplayer badge
            if info.has_multiplayer:
                badges.append({
                    "label": f"Multiplayer v{info.mp_version} ({info.mp_lang.upper()})",
                    "color": "emerald"
                })
            else:
                badges.append({
                    "label": "Vanilla Platine (Non patché)",
                    "color": "slate"
                })

            # SoulLocke badge
            if info.has_soullocke:
                badges.append({
                    "label": f"SoulLocke ({info.soullocke_variant.upper()})",
                    "color": "purple"
                })

            # Randomizer badge
            if info.is_randomized:
                badges.append({
                    "label": "ROM Randomisée",
                    "color": "amber"
                })

            # Visual+ Badges
            if info.has_visualplus_bg:
                badges.append({
                    "label": "Visual+ Décors Actifs",
                    "color": "cyan"
                })
            if info.has_visualplus_cam:
                badges.append({
                    "label": "Visual+ Caméra 3D",
                    "color": "cyan"
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
            return {"success": False, "error": "Un processus de patch est déjà en cours."}

        self._is_patching = True

        def _worker():
            try:
                def _log(msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onPatchLog({escaped});")

                def _prog(val: float, msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onPatchProgress({val}, {escaped});")

                ok, res_msg = execute_patch_pipeline(
                    rom_path=in_rom,
                    output_rom=out_rom,
                    options=options,
                    assets_dir=self.assets_dir,
                    payloads_dir=self.payloads_dir,
                    log_cb=_log,
                    progress_cb=_prog
                )
                escaped_res = json.dumps(res_msg)
                self._eval_js(f"window.onPatchComplete({json.dumps(ok)}, {escaped_res});")
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
            return {"success": False, "error": "Une randomisation est déjà en cours."}

        self._is_randomizing = True

        def _worker():
            try:
                def _log(msg: str):
                    escaped = json.dumps(msg)
                    self._eval_js(f"window.onRandLog({escaped});")

                _log("=== Démarrage de la Randomisation Project PM ===")
                ok, summary = randomize_rom(
                    rom_path=in_rom,
                    out_path=out_rom,
                    settings=settings,
                    log=_log
                )

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
        """Opens web link in the user's default browser."""
        webbrowser.open(url)

    def check_for_updates(self):
        """Checks GitHub releases for latest version in background."""
        def _cb(available: bool, latest_ver: str, release_data: Dict[str, Any]):
            payload = {
                "available": available,
                "current": CURRENT_VERSION,
                "latest": latest_ver or CURRENT_VERSION,
                "notes": release_data.get("body", "") if release_data else "",
                "url": release_data.get("html_url", "") if release_data else ""
            }
            self._eval_js(f"window.onUpdateCheckResult({json.dumps(payload)});")

        check_for_updates_async(_cb)
        return {"checking": True}
