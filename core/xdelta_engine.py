# -*- coding: utf-8 -*-
"""
xdelta_engine.py
Secure wrapper around xdelta3 for base ROM patching (Vanilla -> ProjectPM).
"""
import os
import subprocess

def apply_xdelta(source_rom, patch_file, output_rom, xdelta_exe, log_cb=None):
    def log(msg):
        if log_cb:
            log_cb(msg)

    if not os.path.isfile(source_rom):
        log(f"[xDelta] Error: Source ROM not found ({source_rom})")
        return False
    if not os.path.isfile(patch_file):
        log(f"[xDelta] Error: Patch file not found ({patch_file})")
        return False
    if not os.path.isfile(xdelta_exe):
        log(f"[xDelta] Error: xdelta3 executable not found ({xdelta_exe})")
        return False

    cmd = [xdelta_exe, "-d", "-f", "-s", source_rom, patch_file, output_rom]
    log(f"[xDelta] Running: {os.path.basename(patch_file)} on {os.path.basename(source_rom)}...")
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            err = res.stderr.strip() or res.stdout.strip()
            log(f"[xDelta] Failed: {err}")
            return False
        log(f"[xDelta] Successfully generated: {os.path.basename(output_rom)}")
        return True
    except Exception as e:
        log(f"[xDelta] Exception: {e}")
        return False
