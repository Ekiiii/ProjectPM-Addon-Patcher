# -*- coding: utf-8 -*-
"""
build_exe.py
Compiles ProjectPM Addon Patcher into a standalone Windows .exe using PyInstaller.
"""
import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "PM.ico")
DIST_DIR = os.path.join(ROOT_DIR, "dist")
BUILD_DIR = os.path.join(ROOT_DIR, "build")

def build():
    print("=== Compiling ProjectPM Addon Patcher to Standalone .exe ===")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=ProjectPM-Addon-Patcher",
        f"--icon={ICON_PATH}",
        f"--add-data={os.path.join(ROOT_DIR, 'assets')};assets",
        f"--add-data={os.path.join(ROOT_DIR, 'payloads')};payloads",
        f"--add-data={os.path.join(ROOT_DIR, 'core')};core",
        f"--add-data={os.path.join(ROOT_DIR, 'ui')};ui",
        "--hidden-import=PIL",
        "--hidden-import=PIL.Image",
        "--hidden-import=PIL.ImageTk",
        "--hidden-import=ndspy",
        "--hidden-import=ndspy.rom",
        "--hidden-import=ndspy.narc",
        "--hidden-import=ndspy.code",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=clr",
        "--hidden-import=pythonnet",
        os.path.join(ROOT_DIR, "main.py")
    ]

    print("Running PyInstaller...")
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    if res.returncode != 0:
        print("ERROR: PyInstaller compilation failed.")
        sys.exit(1)

    exe_path = os.path.join(DIST_DIR, "ProjectPM-Addon-Patcher.exe")
    if os.path.isfile(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n[OK] Compilation successful!")
        print(f"Standalone executable generated: {exe_path} ({size_mb:.2f} MB)")
    else:
        print("ERROR: Output executable not found.")
        sys.exit(1)

if __name__ == "__main__":
    build()
