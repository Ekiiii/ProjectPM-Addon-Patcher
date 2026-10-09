# -*- coding: utf-8 -*-
"""
updater.py
Checks for updates on GitHub Releases asynchronously:
- Queries https://api.github.com/repos/Ekiiii/ProjectPM-Addon-Patcher/releases/latest
- Non-blocking, fails gracefully when offline
"""
import threading
import urllib.request
import json

CURRENT_VERSION = "v1.0.2"
GITHUB_REPO = "Ekiiii/ProjectPM-Addon-Patcher"
RELEASES_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

def check_for_updates_async(on_update_found_cb=None):
    """
    Runs GitHub API query in background thread.
    """
    def _run():
        try:
            req = urllib.request.Request(
                RELEASES_URL,
                headers={"User-Agent": "ProjectPM-Addon-Patcher"}
            )
            with urllib.request.urlopen(req, timeout=3.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    latest_tag = data.get("tag_name", "").strip()
                    html_url = data.get("html_url", f"https://github.com/{GITHUB_REPO}/releases")
                    
                    if latest_tag and latest_tag != CURRENT_VERSION:
                        # Simple version comparison
                        if on_update_found_cb:
                            on_update_found_cb(latest_tag, html_url)
        except Exception:
            # Silent fail if offline or repo not yet published
            pass

    t = threading.Thread(target=_run, daemon=True)
    t.start()
