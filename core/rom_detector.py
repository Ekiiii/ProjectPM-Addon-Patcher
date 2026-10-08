# -*- coding: utf-8 -*-
"""
rom_detector.py
Analyzes and classifies Nintendo DS Pokémon Platinum ROMs:
- Language detection (US / FR)
- Version detection (Vanilla / ProjectPM 0.4.5)
- Active mod detection (SoulLocke, Visual+ BG, Visual+ 3D Camera)
- Companion save files (.dsv) and randomizer files (.rand.txt)
"""
import os
import hashlib
import struct
import base64
import ndspy.rom

KNOWN_HASHES = {
    # Vanilla Platinum
    "38914619d0e2e505ea99994cb1783cf6cb79ea29": {"type": "vanilla_us", "name": "Vanilla Platinum (USA Rev 1)"},
    "f4448555e5dfad41763740e53a25cb8ec89ef239": {"type": "vanilla_fr", "name": "Vanilla Platinum (France)"},
    # ProjectPM FR 0.4.5
    "7914acff08156d4c2be6d7babb275afe2d60a3b0": {"type": "projectpm_fr", "name": "ProjectPM 0.4.5 (FR - Standard)"},
    "534992df5165d8ed182da8b922da09614fd70022": {"type": "projectpm_fr", "name": "ProjectPM 0.4.5 (FR - Visual+)"},
}

CAM_VANILLA_B64 = b"vAEAALkBAAC6AQAAKgEAAOQBAACAAAAADwIAAEsAAADBrikAAtYAAAAAAAAAAMEFAGAJAABAOADBrikAYs8AAAAAAAAAAMEFAGAJAABAOABMNyAAItkAAAAAAAAAAHAHAGAJAABAOADBrikAAtYAAAAAAAAAAMEFAGAJAABAOACbuGEAYtwAAAAAAAABAIECAGAJAABwbAAFyBMAA9YAAAAAAAAAAAEMAKAAAAAAPwDfKDYAA8wAAAAAAAAAAIEEADAHAABQTADBrikAA9YAAAAAAAAAAMEFAJAJAABwQADBbikA480AAAAAAAAAAAEHAGAJAACgQACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACxJUsAw9QAAAAAAAAAAEEDAGAJAAAgbQBVPSoA49YAAAAAAAAAAMEFAGAOAABwRgA/6SMAA9MAAAAAAAAAAMEGAGAJAABAOABMNyAAA94AAAAAAAAAAHAHAGAJAABAOABllwoARMgAAAAAAAAAAAEVAKAAAAAAPwDf3igAItkAAAAAAAAAAPAFAGAJAABAOADArhQAAtYAAAAAAAAAAAELAGAJAABAOAA="
CAM_VISUAL_B64  = b"vAEAALkBAAC6AQAAKgEAAOQBAACAAAAADwIAAEsAAACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOACsWRYAI+MAAAAAAAAAALAKAGAJAABAOADArhQAAtYAAAAAAAAAAAELAGAJAABAOAA="

CAM_VANILLA_BYTES = base64.b64decode(CAM_VANILLA_B64)
CAM_VISUAL_BYTES = base64.b64decode(CAM_VISUAL_B64)

class RomInfo:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.exists = os.path.isfile(path)
        self.size = os.path.getsize(path) if self.exists else 0
        self.sha1 = ""
        self.game_title = ""
        self.game_code = ""
        self.lang = "en"           # "en" or "fr"
        self.category = "unknown"   # "projectpm", "vanilla", "unknown"
        self.display_name = ""
        
        # Mod states
        self.is_soullocke = False
        self.has_visual_bg = False
        self.has_visual_cam = False
        
        # Save & Rand
        self.companion_save = None
        self.has_rand_sidecar = False
        self.rand_file = None
        
        if self.exists:
            self._analyze()

    def _analyze(self):
        try:
            with open(self.path, "rb") as f:
                header = f.read(32)
                f.seek(0)
                h = hashlib.sha1()
                # Hash in chunks
                while chunk := f.read(1024 * 1024):
                    h.update(chunk)
                self.sha1 = h.hexdigest()

            # Parse header
            if len(header) >= 16:
                self.game_title = header[:12].decode("latin-1", errors="ignore").rstrip("\x00")
                self.game_code = header[12:16].decode("latin-1", errors="ignore")
                
            if "CPUF" in self.game_code:
                self.lang = "fr"
            elif "CPUE" in self.game_code:
                self.lang = "en"

            # Check known hash
            known = KNOWN_HASHES.get(self.sha1.lower())
            if known:
                self.category = "vanilla" if "vanilla" in known["type"] else "projectpm"
                self.display_name = known["name"]
                if "_fr" in known["type"]:
                    self.lang = "fr"
                elif "_us" in known["type"]:
                    self.lang = "en"
            else:
                # Deduce from header and overlays
                if "POKEMON PL" in self.game_title:
                    if self.size >= 134217728:
                        self.category = "projectpm"
                        # Check filename hints
                        low_path = self.path.lower()
                        if "fr" in low_path or "france" in low_path:
                            self.lang = "fr"
                        self.display_name = f"ProjectPM ({'FR' if self.lang == 'fr' else 'USA'})"
                    else:
                        self.category = "vanilla"
                        self.display_name = f"Pokémon Platinum ({'FR' if self.lang == 'fr' else 'USA'})"

            # Check mods by loading ndspy
            rom = ndspy.rom.NintendoDSRom.fromFile(self.path)
            
            # Check SoulLocke: Hook H1 at 0x02055FA8 (offset in arm9 = 0x02055FA8 - 0x02000000 = 0x55FA8)
            arm9 = rom.arm9
            if len(arm9) > 0x55FA8 + 4:
                h1_bytes = arm9[0x55FA8: 0x55FA8 + 4]
                if h1_bytes == bytes.fromhex("89f36af9"):
                    self.is_soullocke = True
                    self.display_name += " [SoulLocke Active]"

            # Check Visual+ Battle BG: file 159 pl_batt_bg.narc
            if len(rom.files) > 159 and rom.files[159]:
                bg_size = len(rom.files[159])
                if bg_size > 1000000:
                    self.has_visual_bg = True

            # Check Visual+ 3D Camera: check presence of camera byte tables
            with open(self.path, "rb") as f:
                content = f.read()
                if CAM_VISUAL_BYTES in content:
                    self.has_visual_cam = True

            # Companion Save File (.dsv)
            base_no_ext = os.path.splitext(self.path)[0]
            dsv_candidate = base_no_ext + ".dsv"
            if os.path.isfile(dsv_candidate):
                self.companion_save = dsv_candidate
            else:
                # Check battery/ subdirectory (melonDS / DeSmuME)
                parent = os.path.dirname(self.path)
                bat_dsv = os.path.join(parent, "battery", os.path.basename(base_no_ext) + ".dsv")
                if os.path.isfile(bat_dsv):
                    self.companion_save = bat_dsv

            # Companion Randomizer (.rand.txt)
            rand_candidate = base_no_ext + ".rand.txt"
            if os.path.isfile(rand_candidate):
                self.has_rand_sidecar = True
                self.rand_file = rand_candidate

        except Exception as e:
            self.display_name = f"Error reading ROM ({e})"

def detect_rom(path):
    return RomInfo(path)
