# -*- coding: utf-8 -*-
"""
updater.py
Handles automatic updates via GitHub Releases:
- Queries https://api.github.com/repos/Ekiiii/ProjectPM-Addon-Patcher/releases/latest
- Compares semantic versions
- Downloads new executable in chunks with progress reporting
- Validates binary signature (PE MZ header)
- Performs atomic process handoff and restart on Windows
"""
import os
import sys
import tempfile
import threading
import urllib.request
import json
import subprocess
import time

CURRENT_VERSION = "v1.0.5"
GITHUB_REPO = "Ekiiii/ProjectPM-Addon-Patcher"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def parse_version(v_str):
    """
    Parses a version string like 'v1.0.2' into an integer tuple (1, 0, 2).
    """
    clean = str(v_str).lstrip("vV").strip()
    parts = []
    for x in clean.split("."):
        try:
            parts.append(int(x))
        except ValueError:
            parts.append(0)
    return tuple(parts)

def is_newer_version(latest_tag, current_ver=CURRENT_VERSION):
    """
    Returns True if latest_tag is strictly newer than current_ver.
    """
    return parse_version(latest_tag) > parse_version(current_ver)

def check_for_updates_sync(current_ver=CURRENT_VERSION, timeout=5.0):
    """
    Synchronously queries GitHub Releases API for the latest release.
    Returns:
        tuple (is_available: bool, latest_tag: str, release_data: dict, error_msg: str or None)
    """
    try:
        req = urllib.request.Request(
            RELEASES_URL,
            headers={
                "User-Agent": "ProjectPM-Addon-Patcher",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                latest_tag = data.get("tag_name", "").strip()
                newer = is_newer_version(latest_tag, current_ver)
                return newer, latest_tag, data, None
            else:
                return False, current_ver, None, f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        if e.code == 403:
            return False, current_ver, None, "GitHub API rate limit reached. Please try again later."
        return False, current_ver, None, f"HTTP Error {e.code}"
    except urllib.error.URLError:
        return False, current_ver, None, "Unable to reach GitHub. Please check your internet connection."
    except Exception as e:
        return False, current_ver, None, str(e)

def check_for_updates_async(callback=None, current_ver=CURRENT_VERSION):
    """
    Queries GitHub API in a background daemon thread.
    Calls callback with the results once complete, supporting both modern
    and legacy callback signatures without crashing.
    """
    def _run():
        avail, latest_tag, data, err = check_for_updates_sync(current_ver)
        if not callback:
            return

        # Attempt modern callback: callback(available, latest_ver, release_data, error_msg)
        try:
            callback(avail, latest_tag, data, err)
            return
        except TypeError:
            pass

        # Attempt 3-argument callback: callback(available, latest_ver, release_data)
        try:
            callback(avail, latest_tag, data)
            return
        except TypeError:
            pass

        # Attempt legacy callback: callback(tag, html_url, asset_url, asset_size)
        try:
            if avail and data:
                html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                asset_url = None
                asset_size = 0
                for asset in data.get("assets", []):
                    if asset.get("name", "").lower() == "projectpm-addon-patcher.exe":
                        asset_url = asset.get("browser_download_url")
                        asset_size = asset.get("size", 0)
                        break
                callback(latest_tag, html_url, asset_url, asset_size)
        except Exception as ex:
            print(f"[Updater Callback Error] {ex}")

    t = threading.Thread(target=_run, daemon=True)
    t.start()

def download_update_chunked(asset_url, target_path, expected_size=0, progress_cb=None, cancel_event=None):
    """
    Downloads the binary in chunks, reporting progress (downloaded, total, percent).
    Validates binary header before completing.
    Returns (True, None) on success or (False, error_message).
    """
    try:
        req = urllib.request.Request(
            asset_url,
            headers={"User-Agent": "ProjectPM-Addon-Patcher"}
        )
        
        # Download to a temporary partial file first
        part_path = target_path + ".part"
        if os.path.exists(part_path):
            try:
                os.remove(part_path)
            except OSError:
                pass

        with urllib.request.urlopen(req, timeout=30.0) as resp:
            total_size = int(resp.headers.get("Content-Length", expected_size or 0))
            downloaded = 0
            chunk_size = 64 * 1024  # 64 KB chunks

            with open(part_path, "wb") as f:
                while True:
                    if cancel_event and cancel_event.is_set():
                        f.close()
                        try:
                            os.remove(part_path)
                        except OSError:
                            pass
                        return False, "cancelled"

                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_cb:
                        percent = int((downloaded / total_size * 100)) if total_size > 0 else 0
                        progress_cb(downloaded, total_size, percent)

        # Integrity verification: check minimum size and Windows MZ header
        if not os.path.isfile(part_path) or os.path.getsize(part_path) < 1024 * 1024:
            return False, "Downloaded file is corrupted or too small"

        with open(part_path, "rb") as f:
            header = f.read(2)
            if header != b"MZ":
                return False, "Invalid binary signature (not a valid Windows executable)"

        # Atomic rename to final target path
        if os.path.exists(target_path):
            try:
                os.remove(target_path)
            except OSError:
                pass
        os.replace(part_path, target_path)
        return True, None

    except Exception as e:
        return False, str(e)

def apply_update_and_restart(update_file_path):
    """
    Spawns a detached process handoff script to replace the running executable
    and restart the newly updated version.
    Returns (True, None) or (False, reason).
    """
    is_frozen = getattr(sys, "frozen", False)
    if not is_frozen:
        return False, "dev_mode"

    current_exe = os.path.abspath(sys.executable)
    if not os.path.isfile(update_file_path):
        return False, "update_file_missing"

    # Create temporary batch handoff script
    bat_content = """@echo off
ping 127.0.0.1 -n 3 > nul
:retry
move /y "%~1" "%~2" > nul 2>&1
if errorlevel 1 (
    ping 127.0.0.1 -n 2 > nul
    goto retry
)
start "" "%~2"
del "%~f0"
"""
    bat_path = os.path.join(tempfile.gettempdir(), f"pm_updater_{int(time.time())}.bat")
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
    except Exception as e:
        return False, f"Failed to write updater script: {e}"

    # Detached process flags on Windows
    detached_flags = 0
    if os.name == "nt":
        detached_flags = subprocess.CREATE_NEW_PROCESS_GROUP
        if hasattr(subprocess, "DETACHED_PROCESS"):
            detached_flags |= subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(
            ["cmd.exe", "/c", bat_path, update_file_path, current_exe],
            creationflags=detached_flags,
            close_fds=True
        )
    except Exception as e:
        return False, f"Failed to launch update handoff: {e}"

    # Terminate current application cleanly to release file lock
    sys.exit(0)
