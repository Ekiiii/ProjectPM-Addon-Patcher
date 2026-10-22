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
SPLASH_PATH = os.path.join(ASSETS_DIR, "splash.png")
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
        f"--splash={SPLASH_PATH}",
        f"--add-data={os.path.join(ROOT_DIR, 'assets')};assets",
        f"--add-data={os.path.join(ROOT_DIR, 'payloads')};payloads",
        f"--add-data={os.path.join(ROOT_DIR, 'core')};core",
        f"--add-data={os.path.join(ROOT_DIR, 'ui')};ui",
        "--exclude-module=numpy",
        "--exclude-module=scipy",
        "--exclude-module=matplotlib",
        "--exclude-module=pandas",
        "--exclude-module=pytest",
        "--exclude-module=unicorn",
        "--exclude-module=capstone",
        "--exclude-module=keystone",
        "--hidden-import=ndspy",
        "--hidden-import=ndspy.rom",
        "--hidden-import=ndspy.narc",
        "--hidden-import=ndspy.code",
        "--hidden-import=core.exp_share_patcher",
        "--hidden-import=core.hm_patcher",
        "--hidden-import=core.qol_patcher",
        "--hidden-import=core.visual_enhancements",
        "--hidden-import=core.visual_patcher",
        "--hidden-import=core.logger",
        "--hidden-import=core.config_manager",
        "--hidden-import=core.save_manager",
        "--hidden-import=core.lang_switcher",
        "--hidden-import=core.randomizer",
        "--hidden-import=core.rand_manager",
        "--hidden-import=core.smart_injector",
        "--hidden-import=core.patch_pipeline",
        "--hidden-import=core.rom_detector",
        "--hidden-import=core.rom_validator",
        "--hidden-import=webview",
        "--hidden-import=webview.platforms.winforms",
        "--hidden-import=webview.platforms.edgechromium",
        "--hidden-import=clr",
        "--hidden-import=pythonnet",
        "main.py"
    ]

    print("Running PyInstaller...")
    res = subprocess.run(cmd, cwd=ROOT_DIR)
    spec_file = os.path.join(ROOT_DIR, "ProjectPM-Addon-Patcher.spec")
    if os.path.isfile(spec_file):
        try:
            os.remove(spec_file)
        except OSError:
            pass

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

