# -*- coding: utf-8 -*-
"""
rom_detector.py
Analyzes and classifies Nintendo DS Pokémon Platinum ROMs:
- Language detection (US / FR)
- Version detection (Vanilla / ProjectPM 0.4.5)
- Active mod detection:
  * Multiplayer Base (ProjectPM overlay 122 & discovery magic)
  * SoulLocke C mod (ARM9 Hook H1)
  * Randomizer (file 331 pl_enc_data.narc & .rand.txt)
  * Visual+ Battle Backgrounds (file 159 pl_batt_bg.narc)
  * Visual+ 3D Camera (overlay 5 camera parameters table)
- Companion save files (.dsv) and randomizer files (.rand.txt)
"""
import os
import hashlib
import struct
import base64
import ndspy.rom
import ndspy.narc

KNOWN_HASHES = {
    # Vanilla Platinum
    "38914619d0e2e505ea99994cb1783cf6cb79ea29": {"type": "vanilla_us", "name": "Vanilla Platinum (USA Rev 1)"},
    "0862ec35b24de5c7e2dcb88c9eea0873110d755c": {"type": "vanilla_us", "name": "Vanilla Platinum (USA Rev 1)"},
    "f4448555e5dfad41763740e53a25cb8ec89ef239": {"type": "vanilla_fr", "name": "Vanilla Platinum (France)"},
    "41ea92f794560e347cd9509f5ec9e9d479a4bbf1": {"type": "vanilla_fr", "name": "Vanilla Platinum (France)"},
    # ProjectPM FR 0.4.5
    "7914acff08156d4c2be6d7babb275afe2d60a3b0": {"type": "projectpm_fr", "name": "ProjectPM 0.4.5 (FR - Standard)"},
    "534992df5165d8ed182da8b922da09614fd70022": {"type": "projectpm_fr", "name": "ProjectPM 0.4.5 (FR - Visual+)"},
    # ProjectPM USA 0.4.5
    "13a17485f168f7c66a8632598929ffb9232be252": {"type": "projectpm_us", "name": "ProjectPM 0.4.5 (USA)"},
}

STANDARD_ENC_HASHES = {
    "50100e5c276738c4e4758011b2b2e49922da1f1f",  # ProjectPM standard (both US and FR)
    "9d3829844b18063946f3bddcf67a839c95c0186f",  # Vanilla Platinum France
    "e484a4ea105e16977b9f39b965aaad014a4ec923",  # Vanilla Platinum USA
}

FR_BATTLE_UI_HASH = "b87bbe5bf36e0d420552ba0d488f58285ec9d275"

CAM_VISUAL_B64  = b"rFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCgBgCQAAQDgArFkWACPjAAAAAAAAAACwCg=="
CAM_VANILLA_B64 = b"wa4pAALWAAAAAAAAAADBBQBgCQAAQDgAwa4pAGLPAAAAAAAAAADBBQBgCQAAQDgATDcgACLZAAAAAAAAAABwBwBgCQAAQDgAwa4pAALWAAAAAAAAAADBBQBgCQAAQDgAm7hhAGLcAAAAAAAAAQCBAgBgCQAAcGwABcgTAAPWAAAAAAAAAAABDACgAAAAAD8A3yg2AAPMAAAAAAAAAACBBAAwBwAAUEwAwa4pAAPWAAAAAAAAAADBBQCQCQAAcEAAwW4pAOPNAAAAAAAAAAABBwBgCQAAoEAArFkWACPjAAAAAAAAAACwCgBgCQAAQDgAsSVLAMPUAAAAAAAAAABBAwBgCQAAIG0AVT0qAOPWAAAAAAAAAADBBQBgDgAAcEYAP+kjAAPTAAAAAAAAAADBBgBgCQAAQDgATDcgAAPeAAAAAAAAAABwBwBgCQAAQDgAZZcKAETIAAAAAAAAAAABFQCgAAAAAD8A394oACLZAAAAAAAAAADwBQ=="

CAM_VANILLA_BYTES = base64.b64decode(CAM_VANILLA_B64)[:376]
CAM_VISUAL_BYTES = base64.b64decode(CAM_VISUAL_B64)[:376]

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
        self.rom_version = 0
        self.is_usa_rev1 = False
        self.is_france = False
        self.category = "unknown"   # "projectpm", "vanilla", "unknown"
        self.display_name = ""
        
        # Multiplayer Base state
        self.has_multiplayer = False
        self.mp_lang = "en"        # "en" or "fr"
        
        # Mod states
        self.is_soullocke = False
        self.is_nuzlocke = False
        self.is_randomized = False
        self.has_visual_bg = False
        self.has_visual_cam = False
        self.has_exp_share = False
        self.has_free_hms = False
        self.has_infinite_tms = False
        self.has_fast_text = False
        self.has_trade_evos = False
        self.has_fast_hp = False
        self.has_type_eff = False
        self.has_fast_transitions = False
        self.has_level_scaling = False
        self.has_lr_shortcuts = False
        self.has_battle_inspector = False
        self.has_iv_ev = False
        self.has_colored_natures = False
        
        # Save & Rand
        self.companion_save = None
        self.has_rand_sidecar = False
        self.rand_file = None
        
        if self.exists:
            self._analyze()

    @property
    def is_valid(self) -> bool:
        return self.exists and (
            "POKEMON PL" in self.game_title
            or self.category in ("vanilla", "projectpm")
            or self.game_code.startswith("CPU")
            or self.has_multiplayer
        )

    @property
    def has_soullocke(self) -> bool:
        return self.is_soullocke

    @property
    def has_nuzlocke(self) -> bool:
        return self.is_nuzlocke

    @property
    def soullocke_variant(self) -> str:
        return self.lang

    @property
    def has_visualplus_bg(self) -> bool:
        return self.has_visual_bg

    @property
    def has_visualplus_cam(self) -> bool:
        return self.has_visual_cam

    @property
    def mp_version(self) -> str:
        return "0.4.5"

    def _analyze(self):
        try:
            with open(self.path, "rb") as f:
                header = f.read(32)
                f.seek(0)
                h = hashlib.sha1()
                while chunk := f.read(1024 * 1024):
                    h.update(chunk)
                self.sha1 = h.hexdigest()

            # Parse header
            if len(header) >= 16:
                self.game_title = header[:12].decode("latin-1", errors="ignore").rstrip("\x00")
                self.game_code = header[12:16].decode("latin-1", errors="ignore")
            if len(header) >= 0x20:
                self.rom_version = header[0x1E]
                
            if "CPUF" in self.game_code:
                self.lang = "fr"
                self.is_france = True
            elif "CPUE" in self.game_code:
                self.lang = "en"
                if self.rom_version == 1:
                    self.is_usa_rev1 = True

            # Check known hash first
            known = KNOWN_HASHES.get(self.sha1.lower())
            if known:
                self.category = "vanilla" if "vanilla" in known["type"] else "projectpm"
                self.display_name = known["name"]
                if "_fr" in known["type"]:
                    self.lang = "fr"
                    self.is_france = True
                elif "_us" in known["type"]:
                    self.lang = "en"
                    self.is_usa_rev1 = True

            # Read full ROM content for pattern checks
            with open(self.path, "rb") as f:
                content = f.read()

            # Check Multiplayer Base presence
            idx = 0
            while True:
                pos1 = content.find(b"\x34\x12\xfe\xca", idx)
                if pos1 == -1:
                    break
                start_search = max(0, pos1 - 64)
                end_search = min(len(content), pos1 + 64)
                if b"\xfe\xca\x78\x56" in content[start_search:end_search]:
                    self.has_multiplayer = True
                    self.category = "projectpm"
                    break
                idx = pos1 + 1

            # Parse ndspy ROM structure
            rom = ndspy.rom.NintendoDSRom.fromFile(self.path)

            # Overlay 122 check (ProjectPM Multiplayer Overlay)
            ovs = rom.loadArm9Overlays()
            if 122 in ovs:
                self.has_multiplayer = True
                self.category = "projectpm"

            # Determine Language precisely via internal text bank (msgdata/pl_msg.narc file 412)
            detected_lang = None
            try:
                msg_data = rom.getFileByName("msgdata/pl_msg.narc")
                if msg_data:
                    narc = ndspy.narc.NARC(msg_data)
                    if len(narc.files) > 412:
                        raw = narc.files[412]
                        count, seed = struct.unpack("<HH", raw[:4])
                        if count >= 2:
                            off, length = struct.unpack("<II", raw[12:20])
                            s = (seed * 765 * 2) & 0xFFFF
                            s |= (s << 16)
                            length ^= s
                            if length == 11:
                                detected_lang = "fr"
                            elif length == 10:
                                detected_lang = "en"
            except Exception:
                pass

            if detected_lang:
                self.lang = detected_lang
                self.is_france = (detected_lang == "fr")
                self.is_usa_rev1 = (detected_lang == "en" and self.rom_version == 1)
            elif "CPUF" in self.game_code:
                self.lang = "fr"
                self.is_france = True
            elif len(rom.files) > 158 and rom.files[158] and hashlib.sha1(rom.files[158]).hexdigest() == FR_BATTLE_UI_HASH:
                self.lang = "fr"
                self.is_france = True
            elif "fr" in self.filename.lower() or "france" in self.filename.lower() or "french" in self.filename.lower():
                self.lang = "fr"
                self.is_france = True
            elif "CPUE" in self.game_code:
                self.lang = "en"
                if self.rom_version == 1:
                    self.is_usa_rev1 = True

            self.mp_lang = self.lang

            if self.has_multiplayer:
                if not self.display_name:
                    self.display_name = f"ProjectPM 0.4.5 ({'Français' if self.lang == 'fr' else 'English'})"
            else:
                if not self.display_name:
                    if "POKEMON PL" in self.game_title:
                        self.category = "vanilla"
                        if self.lang == "fr":
                            self.display_name = "Vanilla Platine (France)"
                        else:
                            rev_str = "USA Rev 1" if self.rom_version == 1 else f"USA Rev {self.rom_version}"
                            self.display_name = f"Vanilla Platinum ({rev_str})"
                    else:
                        self.display_name = f"Custom ROM ({self.game_title})"

            # Check SoulLocke / Nuzlocke: Hook H1 at 0x02055FA8 (arm9 offset 0x55FA8)
            arm9 = rom.arm9
            has_h1 = False
            if len(arm9) > 0x55FA8 + 4:
                h1_bytes = arm9[0x55FA8 : 0x55FA8 + 4]
                if h1_bytes != bytes.fromhex("6850301c") and len(h1_bytes) == 4 and (h1_bytes[1] & 0xF0) == 0xF0:
                    has_h1 = True

            base_no_ext = os.path.splitext(self.path)[0]

            # Check Randomizer: If ROM matches an exact clean vanilla or stock ProjectPM hash, it is NOT randomized
            if self.sha1.lower() in KNOWN_HASHES:
                self.is_randomized = False
            else:
                # Check Randomizer via sidecar, filename, or candidate NARC tables
                rand_candidate = base_no_ext + ".rand.txt"
                if not os.path.isfile(rand_candidate) and os.path.isfile(self.path + ".rand.txt"):
                    rand_candidate = self.path + ".rand.txt"
                if os.path.isfile(rand_candidate):
                    self.has_rand_sidecar = True
                    self.rand_file = rand_candidate
                    self.is_randomized = True

                if "random" in self.filename.lower() or "rand" in self.filename.lower():
                    self.is_randomized = True

                if len(rom.files) > 331 and rom.files[331]:
                    enc_hash = hashlib.sha1(rom.files[331]).hexdigest()
                    if enc_hash not in STANDARD_ENC_HASHES:
                        self.is_randomized = True

                # Use rand_manager scanner for deep check
                try:
                    from core.rand_manager import extract_randomizer_data
                    rand_check = extract_randomizer_data(self.path)
                    if rand_check["is_randomized"]:
                        self.is_randomized = True
                except Exception:
                    pass

            # Check Visual+ Battle BG: file 159 pl_batt_bg.narc > 1MB
            if len(rom.files) > 159 and rom.files[159]:
                bg_size = len(rom.files[159])
                if bg_size > 1000000:
                    self.has_visual_bg = True

            # Check Visual+ 3D Camera: check presence of camera byte tables
            if CAM_VISUAL_BYTES in content:
                self.has_visual_cam = True
            elif 5 in ovs and CAM_VISUAL_BYTES in ovs[5].data:
                self.has_visual_cam = True

            # Check PPM Header Tag at 0x1E0 (persisted by patcher)
            if len(content) > 0x1E8 and content[0x1E0:0x1E4] == b"PPM\x01":
                qol_f = content[0x1E4]
                vis_f = content[0x1E5]
                mode_f = content[0x1E6]
                qol2_f = content[0x1E7]
                if (qol_f & 0x01): self.has_exp_share = True
                if (qol_f & 0x02): self.has_free_hms = True
                if (qol_f & 0x04): self.has_trade_evos = True
                if (qol_f & 0x08): self.has_infinite_tms = True
                if (qol_f & 0x10): self.has_fast_hp = True
                if (qol_f & 0x20): self.has_type_eff = True
                if (qol_f & 0x40): self.has_fast_transitions = True
                if (qol_f & 0x80): self.has_level_scaling = True
                if (vis_f & 0x01): self.has_iv_ev = True
                if (vis_f & 0x02): self.has_colored_natures = True
                if (vis_f & 0x04): self.has_visual_bg = True
                if (vis_f & 0x08): self.has_visual_cam = True
                if (qol2_f & 0x01): self.has_lr_shortcuts = True
                if (qol2_f & 0x02): self.has_battle_inspector = True

                if mode_f == 2:
                    self.is_nuzlocke = True
                    self.is_soullocke = False
                elif mode_f == 1:
                    self.is_soullocke = True
                    self.is_nuzlocke = False
                elif mode_f == 0:
                    self.is_soullocke = False
                    self.is_nuzlocke = False

            # If H1 hook is present but mode was not set by header tag, detect via filename or msg 1301
            if has_h1 and not self.is_soullocke and not self.is_nuzlocke:
                if "nuzlocke" in self.filename.lower():
                    self.is_nuzlocke = True
                elif "soullocke" in self.filename.lower() or "soullink" in self.filename.lower():
                    self.is_soullocke = True
                else:
                    try:
                        from core.smart_injector import unpack_bank
                        msg_data = rom.getFileByName("msgdata/pl_msg.narc")
                        if msg_data:
                            narc = ndspy.narc.NARC(msg_data)
                            if len(narc.files) > 368:
                                ik, cl = unpack_bank(narc.files[368])
                                if len(cl) > 1301:
                                    chars = cl[1301][0]
                                    if chars and chars[0] == 0x0138:  # 'N' -> Nuzlocke
                                        self.is_nuzlocke = True
                                    else:
                                        self.is_soullocke = True
                    except Exception:
                        self.is_soullocke = True

            # Check Shared Team EXP mod
            try:
                from core.exp_share_patcher import is_exp_share_active
                if is_exp_share_active(rom):
                    self.has_exp_share = True
            except Exception:
                pass

            # Check Free HMs & Poké-Rider mod
            try:
                from core.hm_patcher import is_hm_patch_active
                if is_hm_patch_active(rom):
                    self.has_free_hms = True
            except Exception:
                pass

            # Check Infinite TMs
            try:
                from core.qol_patcher import is_infinite_tms_active
                if is_infinite_tms_active(rom):
                    self.has_infinite_tms = True
            except Exception:
                pass

            # Check Trade Evos
            try:
                from core.qol_patcher import is_trade_evos_active
                if is_trade_evos_active(rom):
                    self.has_trade_evos = True
            except Exception:
                pass

            # Check Fast HP/EXP
            try:
                from core.qol_patcher import is_fast_healthbar_active
                if is_fast_healthbar_active(rom):
                    self.has_fast_hp = True
            except Exception:
                pass

            # Check Move Type Effectiveness
            try:
                from core.qol_patcher import is_type_effectiveness_active
                self.has_type_eff = is_type_effectiveness_active(rom)
            except Exception:
                pass

            # Check Fast Transitions
            try:
                from core.qol_patcher import is_fast_transitions_active
                if is_fast_transitions_active(rom):
                    self.has_fast_transitions = True
            except Exception:
                pass

            # Check Level Scaling
            try:
                from core.qol_patcher import is_level_scaling_active
                if is_level_scaling_active(rom):
                    self.has_level_scaling = True
            except Exception:
                pass

            # Check L/R Shortcuts
            try:
                from core.qol_patcher import is_lr_shortcuts_active
                if is_lr_shortcuts_active(rom):
                    self.has_lr_shortcuts = True
            except Exception:
                pass

            # Check Battle Inspector
            try:
                from core.qol_patcher import is_battle_inspector_active
                if is_battle_inspector_active(rom):
                    self.has_battle_inspector = True
            except Exception:
                pass

            # Check IV/EV & Colored Natures
            try:
                from core.visual_enhancements import is_colored_natures_active, is_iv_ev_active
                if is_colored_natures_active(rom):
                    self.has_colored_natures = True
                if is_iv_ev_active(rom):
                    self.has_iv_ev = True
            except Exception:
                pass

            # Companion Save Files (.dsv and .sav)
            dsv_candidate = base_no_ext + ".dsv"
            sav_candidate = base_no_ext + ".sav"
            parent = os.path.dirname(self.path)
            bat_dsv = os.path.join(parent, "battery", os.path.basename(base_no_ext) + ".dsv")
            bat_sav = os.path.join(parent, "battery", os.path.basename(base_no_ext) + ".sav")

            found_saves = []
            for candidate in (dsv_candidate, sav_candidate, bat_dsv, bat_sav):
                if os.path.isfile(candidate) and candidate not in found_saves:
                    found_saves.append(candidate)

            if found_saves:
                self.companion_save = found_saves[0]
                self.all_companion_saves = found_saves

        except Exception as e:
            self.display_name = f"Error reading ROM ({e})"

def detect_rom(path):
    return RomInfo(path)
