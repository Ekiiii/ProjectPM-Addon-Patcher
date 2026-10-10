# -*- coding: utf-8 -*-
"""
config_manager.py
Persistent User Configuration & State Subsystem for ProjectPM Addon Patcher.
Stores user preferences on disk in `config.json`:
- Chosen UI language & first-launch prompt flag
- Last selected Source ROM & Destination ROM paths
- Preferred patching & randomizer options
"""
import os
import sys
import json
import threading
from typing import Dict, Any, Optional

_config_lock = threading.Lock()

def get_app_dir() -> str:
    """Returns directory of executable or script root."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_config_path() -> str:
    """Returns absolute path to config.json."""
    return os.path.join(get_app_dir(), "config.json")

def get_default_config() -> Dict[str, Any]:
    """Returns default configuration schema."""
    return {
        "language": None,
        "has_selected_language": False,
        "last_source_rom": "",
        "last_output_rom": "",
        "visual_bg": True,
        "visual_cam": True,
        "backup_save": True,
        "addon_mode": "soullink",
        "mp_mode": "fr",
        "team_exp_share": False
    }

def load_config() -> Dict[str, Any]:
    """Loads configuration from config.json, returning defaults if not found."""
    cfg = get_default_config()
    cfg_path = get_config_path()

    with _config_lock:
        if os.path.isfile(cfg_path):
            try:
                with open(cfg_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if isinstance(saved, dict):
                        cfg.update(saved)
            except Exception as e:
                print(f"[Config Load Error] {e}")
    return cfg

def save_config(data: Dict[str, Any]) -> bool:
    """Saves dictionary to config.json atomically."""
    cfg_path = get_config_path()
    with _config_lock:
        try:
            # Merge with current
            current = get_default_config()
            if os.path.isfile(cfg_path):
                try:
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                        if isinstance(loaded, dict):
                            current.update(loaded)
                except Exception:
                    pass

            current.update(data)

            # Write temp then atomic rename
            tmp_path = cfg_path + ".tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(current, f, indent=2, ensure_ascii=False)
            
            if os.path.exists(cfg_path):
                os.replace(tmp_path, cfg_path)
            else:
                os.rename(tmp_path, cfg_path)
            return True
        except Exception as e:
            print(f"[Config Save Error] {e}")
            return False

def update_config_key(key: str, val: Any) -> bool:
    """Helper to update a single config key."""
    return save_config({key: val})
