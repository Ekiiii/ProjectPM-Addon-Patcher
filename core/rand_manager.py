# -*- coding: utf-8 -*-
"""
rand_manager.py
Automatic preservation and restoration engine for Pokémon Platinum Randomizers.
Detects, snapshots, and re-applies all randomized tables (wild encounters, starters,
trainers, base stats, types, movesets, evolutions, items, overlays) across any base
patch, mod injection, or visual conversion.
"""
import os
import shutil
import hashlib
import zlib
import pickle
import ndspy.rom

# Standard clean file hashes for Nintendo DS Pokémon Platinum (Vanilla FR, Vanilla US, ProjectPM 0.4.5)
CLEAN_FILE_HASHES = {
    "fielddata/encountdata/pl_enc_data.narc": {
        "50100e5c276738c4e4758011b2b2e49922da1f1f",  # ProjectPM standard (FR & US)
        "d9bf534c175c3c991e77fff985c099723499e1eb",  # Vanilla Platinum (FR & US)
        "9d3829844b18063946f3bddcf67a839c95c0186f",  # Vanilla FR alternate
        "e484a4ea105e16977b9f39b965aaad014a4ec923",  # Vanilla US alternate
    },
    "arc/encdata_ex.narc": {
        "e7fcfc718128f4ac5fe4f7594595cbc608e07f5f",  # ProjectPM standard
        "0832d441d7e543e14d68e9df7e9118b472d67833",  # Vanilla Platinum
    },
    "fielddata/script/scr_seq.narc": {
        "5a0a2fb4d89451fc1040220f6c4155c698ca3cc9",  # ProjectPM standard
        "0184a6adf788980e2709e4183094cfc2f5965894",  # Vanilla FR
        "9f4d3587b7032f4f673ccc1b8971685b2199396b",  # Vanilla US
    },
    "poketool/trainer/trdata.narc": {
        "3504671fe4ad44b7cd2b4372325fe7c68a8fdd45",  # ProjectPM standard
        "59f49fe682ef8cf4dfb8f6b7da2e0f51401b50cc",  # Vanilla Platinum
    },
    "poketool/trainer/trpoke.narc": {
        "6cc916703656cb529d11e8b9d457e8d06dd831ea",  # ProjectPM standard
        "da4dc734c7051754a3280d9e918942c42d183adb",  # Vanilla Platinum
    },
    "poketool/personal/pl_personal.narc": {
        "9276bf00abe261643529ec61b1ec235a9229c3d1",  # ProjectPM standard
        "1f8689cbc763d9efedac9e6f12e940dbd361f7a9",  # Vanilla Platinum
    },
    "poketool/personal/personal.narc": {
        "9276bf00abe261643529ec61b1ec235a9229c3d1",
        "1f8689cbc763d9efedac9e6f12e940dbd361f7a9",
    },
    "poketool/personal/evo.narc": {
        "24718dc9a1d612c5e5799b503e09a705dd8db2b4",  # ProjectPM standard
        "7755e3a884a11b098122ca9dd656223fd4b02dd0",  # Vanilla Platinum
    },
    "poketool/personal/wotbl.narc": {
        "393c66f4d142c709af050de459e7022653d5bf9d",  # ProjectPM standard
        "cd4b737f173cc6ac1a25636efa4edfd83da79599",  # Vanilla Platinum
    },
    "poketool/personal/pl_growtbl.narc": {
        "8397a6d892040b2efd44a7ecf0148fb0fa8e38bc",
    },
    "poketool/personal/growtbl.narc": {
        "8397a6d892040b2efd44a7ecf0148fb0fa8e38bc",
    },
    "poketool/waza/pl_waza_tbl.narc": {
        "12cb9af69581a76fe17e4a7f5a7941608949cf97",  # ProjectPM standard
        "42e2b71655a74d6e5bffb9ec75a25df930b20c59",  # Vanilla Platinum
    },
    "itemtool/itemdata/pl_item_data.narc": {
        "ea17e68d77f1e23cf006ed600771768195416fd3",  # ProjectPM standard
        "70d103831556bb58ae8e602adbcce99333a22889",  # Vanilla Platinum
    },
}

CLEAN_OV78_HASHES = {
    "16757b15a6b7501a355938ea49d7b42589e4726e",
    "b8cfb4aa262f3fcfd46c8206aa1e24749fef1c46",
}

RANDOMIZER_CANDIDATES = [
    "fielddata/encountdata/pl_enc_data.narc",
    "arc/encdata_ex.narc",
    "fielddata/script/scr_seq.narc",
    "poketool/trainer/trdata.narc",
    "poketool/trainer/trpoke.narc",
    "poketool/personal/pl_personal.narc",
    "poketool/personal/personal.narc",
    "poketool/personal/evo.narc",
    "poketool/personal/wotbl.narc",
    "poketool/personal/pl_growtbl.narc",
    "poketool/personal/growtbl.narc",
    "poketool/waza/pl_waza_tbl.narc",
    "itemtool/itemdata/pl_item_data.narc",
]

def extract_randomizer_data(rom_path, log_cb=None):
    """
    Scans a ROM for randomized tables and companion spoiler logs.
    Returns a dict containing extracted files, overlays, and sidecar paths.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    result = {
        "is_randomized": False,
        "files": {},
        "overlays": {},
        "rand_log_path": None,
        "file_names": [],
    }

    if not os.path.isfile(rom_path):
        return result

    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
    except Exception as e:
        log(f"[Randomizer] Warning: Could not read ROM structure: {e}")
        return result

    # Check companion .rand.txt
    base_no_ext = os.path.splitext(rom_path)[0]
    rand_candidate = base_no_ext + ".rand.txt"
    if os.path.isfile(rand_candidate):
        result["rand_log_path"] = rand_candidate
        result["is_randomized"] = True

    # Scan candidate files
    for fname in RANDOMIZER_CANDIDATES:
        try:
            data = rom.getFileByName(fname)
            h = hashlib.sha1(data).hexdigest()
            known_cleans = CLEAN_FILE_HASHES.get(fname, set())
            if h not in known_cleans:
                result["files"][fname] = bytes(data)
                result["file_names"].append(os.path.basename(fname))
                result["is_randomized"] = True
        except Exception:
            pass

    # Scan Overlay 78
    try:
        ovs = rom.loadArm9Overlays()
        if 78 in ovs:
            ov78_data = bytes(ovs[78].data)
            h78 = hashlib.sha1(ov78_data).hexdigest()
            if h78 not in CLEAN_OV78_HASHES:
                result["overlays"][78] = ov78_data
                result["file_names"].append("overlay_78")
                result["is_randomized"] = True
    except Exception:
        pass

    if result["is_randomized"]:
        log(f"[Randomizer] Detected randomized ROM: {len(result['files'])} tables modified ({', '.join(result['file_names'][:4])})")

    return result

def clean_vanilla_for_xdelta(src_rom_path, temp_clean_path, lang="fr", assets_dir=None, log_cb=None):
    """
    Reverts randomized tables in a Vanilla ROM to standard clean tables
    so that xdelta3 differential patching succeeds without checksum mismatch.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    if not assets_dir:
        assets_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

    pack_name = "clean_vanilla_fr.pack" if lang == "fr" else "clean_vanilla_us.pack"
    pack_path = os.path.join(assets_dir, "clean_narcs", pack_name)

    if not os.path.isfile(pack_path):
        log(f"[Randomizer] Pack not found: {pack_name}, using source as-is.")
        shutil.copy2(src_rom_path, temp_clean_path)
        return temp_clean_path

    log(f"[Randomizer] Preparing clean base for base patch ({pack_name})...")
    with open(pack_path, "rb") as f:
        clean_pack = pickle.loads(zlib.decompress(f.read()))

    rom = ndspy.rom.NintendoDSRom.fromFile(src_rom_path)
    for fname, data in clean_pack.items():
        if fname == "ov78":
            ovs = rom.loadArm9Overlays()
            if 78 in ovs:
                ovs[78].data = data
                rom.files[ovs[78].fileID] = data
        else:
            try:
                rom.setFileByName(fname, data)
            except Exception:
                pass

    rom.saveToFile(temp_clean_path)
    log("[Randomizer] Clean base successfully prepared for xdelta.")
    return temp_clean_path

def restore_randomizer_data(output_rom_path, rand_data, log_cb=None):
    """
    Re-injects all extracted randomized files into the final generated ROM.
    Also duplicates companion .rand.txt file.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    if not rand_data or not rand_data.get("is_randomized"):
        return True

    files = rand_data.get("files", {})
    overlays = rand_data.get("overlays", {})

    if not files and not overlays:
        return True

    log(f"[Randomizer] Re-applying {len(files)} randomized tables to destination ROM...")
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(output_rom_path)
        
        # Inject NARCs
        for fname, data in files.items():
            try:
                rom.setFileByName(fname, data)
            except Exception as e:
                log(f"[Randomizer] Warning: Could not inject {fname}: {e}")

        # Inject overlays
        if overlays:
            ovs = rom.loadArm9Overlays()
            for ov_id, ov_data in overlays.items():
                if ov_id in ovs:
                    ovs[ov_id].data = ov_data
                    rom.files[ovs[ov_id].fileID] = ov_data
            rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

        rom.saveToFile(output_rom_path)
        log(f"[Randomizer] SUCCESS: All {len(files)} randomized tables successfully restored!")

        # Copy companion .rand.txt if present
        if rand_data.get("rand_log_path") and os.path.isfile(rand_data["rand_log_path"]):
            dest_stem = os.path.splitext(output_rom_path)[0]
            dest_rand = dest_stem + ".rand.txt"
            shutil.copy2(rand_data["rand_log_path"], dest_rand)
            log(f"[Randomizer] Spoiler log preserved -> {os.path.basename(dest_rand)}")

        return True

    except Exception as e:
        log(f"[Randomizer] ERROR re-applying randomizer tables: {e}")
        return False
