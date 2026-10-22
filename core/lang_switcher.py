"""
lang_switcher.py
Swaps localized data files between English and French on ProjectPM ROMs.
"""
import os
import pickle
import lzma
import ndspy.rom

def switch_projectpm_lang(src_rom: str, dst_rom: str, target_lang: str, assets_dir: str = None, log_cb=None) -> bool:
    """
    Converts a ProjectPM ROM between English ('en') and French ('fr').
    Returns True on success.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    if not os.path.isfile(src_rom):
        log(f"[LangSwitcher] Error: Source ROM not found: {src_rom}")
        return False

    if not assets_dir:
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

    pack_name = "lang_fr.pack" if target_lang.lower() == "fr" else "lang_en.pack"
    pack_path = os.path.join(assets_dir, "lang_packs", pack_name)

    if not os.path.isfile(pack_path):
        log(f"[LangSwitcher] Error: Language pack not found: {pack_path}")
        return False

    lang_name = "Français" if target_lang.lower() == "fr" else "English"
    log(f"[LangSwitcher] Applying {lang_name} language pack ({pack_name})...")

    try:
        with open(pack_path, "rb") as f:
            pack_data = pickle.loads(lzma.decompress(f.read()))

        rom = ndspy.rom.NintendoDSRom.fromFile(src_rom)

        if "arm9" in pack_data:
            rom.arm9 = pack_data["arm9"]
        if "arm9OverlayTable" in pack_data:
            rom.arm9OverlayTable = pack_data["arm9OverlayTable"]

        # Inject the localized and core files
        for idx, data in pack_data.items():
            if isinstance(idx, int) and idx < len(rom.files):
                rom.files[idx] = data

        rom_bytes = bytearray(rom.save())
        if len(rom_bytes) < 134217728:
            rom_bytes.extend(b"\xff" * (134217728 - len(rom_bytes)))

        os.makedirs(os.path.dirname(os.path.abspath(dst_rom)), exist_ok=True)
        with open(dst_rom, "wb") as f:
            f.write(rom_bytes)

        log(f"[LangSwitcher] SUCCESS: Switched ProjectPM multiplayer base to {lang_name}!")
        return True

    except Exception as e:
        log(f"[LangSwitcher] ERROR during language switch: {e}")
        return False
