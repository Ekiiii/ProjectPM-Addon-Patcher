"""
smart_injector.py
Injects or reverts the SoulLocke / Nuzlocke C payload via the Nitro-SDK autoload table,
installs ARM9 and Overlay 16 hooks, and updates msgdata/pl_msg.narc strings.
"""
import os
import re
import json
import struct
import ndspy.rom
import ndspy.narc
import ndspy.code

ARM9_BASE = 0x02000000
OV16_RAM  = 0x0224AAE0
ROM_TARGET_SIZE = 134217728  # 128 MB

VANILLA_ARM9_LEN = 0x109BB8
MODULE_PARAMS_OFF = 0x0BA0
VANILLA_MODULE_PARAMS = (0x02109BA0, 0x02109BB8, 0x021094E0, 0x021094E0, 0x021E0600, 0x00000000)
AUTOLOAD_LIST_OFF = 0x109BA0
VANILLA_AUTOLOAD_LIST = (0x01FF8000, 0x660, 0, 0x027E0000, 0x60, 0x20)
ARENA_HI_DEFAULT = 0x023E0000
LIT_MAIN_ARENA_HI = 0x020C9F24

SOULLOCKE_ORIGINS = {0x023DD240, 0x023DD4E0, 0x023DE7A0}

CLEAN_INTRO_CODES_FR = [
    300, 339, 338, 334, 339, 345, 342, 478, 427, 9660,
    315, 345, 329, 336, 336, 329, 478, 334, 339, 333, 329, 478,
    328, 329, 478, 344, 329, 478, 342, 329, 338, 327, 339, 338, 344, 342, 329, 342, 478, 427, 9660,
    300, 333, 329, 338, 346, 329, 338, 345, 329, 478,
    328, 325, 338, 343, 478, 336, 329, 478, 337, 339, 338, 328, 329, 57344,
    328, 329, 343, 478, 314, 339, 335, 392, 337, 339, 338, 478, 427, 9660,
    65535
]

CLEAN_INTRO_CODES_EN = [
    306, 329, 336, 336, 339, 478, 344, 332, 329, 342, 329, 427, 9660,
    307, 344, 435, 343, 478, 343, 339, 478, 346, 329, 342, 349, 478,
    338, 333, 327, 329, 478, 344, 339, 478, 337, 329, 329, 344, 478, 349, 339, 345, 427, 9660,
    321, 329, 336, 327, 339, 337, 329, 478, 344, 339, 478,
    344, 332, 329, 478, 347, 339, 342, 336, 328, 57344,
    339, 330, 478, 314, 339, 335, 392, 337, 339, 338, 427, 9660,
    65535
]

def _get_version_params(ov16_ram):
    """
    Detects version profile based on Overlay 16 load address.
    Returns: (ov16_ram, autoload_off, lit_arena_hi, vanilla_mod_params, app_heap_off, vanilla_bss_start, ver_str)
    """
    if ov16_ram == 0x0224A700:
        return (
            0x0224A700,
            0x109840,
            0x020C9B9C,
            (0x02109840, 0x02109858, 0x02109180, 0x02109180, 0x021E0280, 0x00000000),
            0xEC2D8,
            0x02109180,
            "045",
        )
    elif ov16_ram == 0x0224A920:
        return (
            0x0224A920,
            0x109A60,
            0x020C9DF0,
            (0x02109A60, 0x02109A78, 0x021093A0, 0x021093A0, 0x021E04A0, 0x00000000),
            0xEC52C,
            0x021093A0,
            "046",
        )
    return (
        OV16_RAM,
        AUTOLOAD_LIST_OFF,
        LIT_MAIN_ARENA_HI,
        VANILLA_MODULE_PARAMS,
        0xEC660,
        0x021094E0,
        "047",
    )

def _resolve_version_payload_path(payload_json_path, ver_str):
    """
    Ensures the payload JSON matches the detected target ROM version (045, 046, 047).
    Supports aliases between en and usa and automatic version switching.
    """
    pdir = os.path.dirname(payload_json_path)
    base = os.path.basename(payload_json_path)
    name, ext = os.path.splitext(base)

    if name.endswith(f"_{ver_str}") and os.path.isfile(payload_json_path):
        return payload_json_path

    base_stem = re.sub(r"_(04[567])$", "", name)
    stems = [base_stem]
    if "_usa" in base_stem or "_us" in base_stem:
        stems.append(base_stem.replace("_usa", "_en").replace("_us", "_en"))
    elif "_en" in base_stem:
        stems.append(base_stem.replace("_en", "_usa"))

    for stem in stems:
        candidate = os.path.join(pdir, f"{stem}_{ver_str}{ext}")
        if os.path.isfile(candidate):
            return candidate

    for stem in stems:
        candidate = os.path.join(pdir, f"{stem}{ext}")
        if os.path.isfile(candidate):
            return candidate

    return payload_json_path

def _extract_custom_entries(arm9, autoload_off):
    """
    Parses active custom autoload entries from arm9 MODULE_PARAMS (entries 3..N).
    Returns list of (dest, blob, bss).
    """
    old_start, old_end = struct.unpack_from("<2I", arm9, MODULE_PARAMS_OFF)
    start_off = old_start - ARM9_BASE
    end_off = old_end - ARM9_BASE
    custom_entries = []
    if 0 <= start_off <= len(arm9) and 0 <= end_off <= len(arm9) and end_off >= start_off + 24:
        data_cursor = autoload_off
        for entry_pos in range(start_off + 24, end_off, 12):
            if entry_pos + 12 <= len(arm9):
                dest, sz, bss = struct.unpack_from("<3I", arm9, entry_pos)
                if 0x023C0000 <= dest < 0x023E0000 and 0 < sz <= 0x10000 and data_cursor + sz <= start_off:
                    blob = bytes(arm9[data_cursor:data_cursor + sz])
                    data_cursor += sz
                    custom_entries.append((dest, blob, bss))
    return custom_entries

def _rebuild_autoload(arm9, autoload_off, lit_arena_hi, vanilla_mod_params, custom_entries, app_heap_off, vanilla_bss_start):
    """
    Non-Destructive Unified Autoload Manager:
    Rebuilds ARM9 autoload section, preserves sibling payloads,
    updates MODULE_PARAMS, LIT_MAIN_ARENA_HI, and adjusts HEAP_ID_APPLICATION.
    """
    new_arm9 = bytearray(arm9[:autoload_off])
    for _, blob, _ in custom_entries:
        new_arm9 += blob
    list_start = ARM9_BASE + len(new_arm9)
    new_arm9 += struct.pack("<6I", *VANILLA_AUTOLOAD_LIST)
    for dest, blob, bss in custom_entries:
        new_arm9 += struct.pack("<3I", dest, len(blob), bss)
    list_end = ARM9_BASE + len(new_arm9)

    # Update ModuleParams (list_start, list_end) and keep vanilla bss_start at 0x0BAC
    struct.pack_into("<2I", new_arm9, MODULE_PARAMS_OFF, list_start, list_end)
    struct.pack_into("<I", new_arm9, MODULE_PARAMS_OFF + 0x0C, vanilla_bss_start)

    # Calculate High Arena ceiling
    high_arena_dests = [d & ~0x1F for d, _, _ in custom_entries if 0x023C0000 <= d < 0x023E0000]
    arena_hi = min(high_arena_dests) if high_arena_dests else ARENA_HI_DEFAULT
    struct.pack_into("<I", new_arm9, lit_arena_hi - ARM9_BASE, arena_hi)

    # Adjust HEAP_ID_APPLICATION pool size (Hook H11):
    # When any custom payload is present: reduce by 14,336 bytes (0x3800) -> 0x00181000
    # When zero custom payloads remain: restore to vanilla 0x00501000
    if app_heap_off > 0 and app_heap_off + 4 <= len(new_arm9):
        cur_heap = new_arm9[app_heap_off:app_heap_off + 4]
        if high_arena_dests:
            if cur_heap in (b"\x00\x50\x10\x00", b"\x00\x40\x10\x00", b"\x00\x30\x10\x00", b"\x00\x20\x10\x00"):
                new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x18\x10\x00"
        else:
            if cur_heap in (b"\x00\x18\x10\x00", b"\x00\x20\x10\x00", b"\x00\x30\x10\x00", b"\x00\x40\x10\x00"):
                new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x50\x10\x00"

    return new_arm9

MSG_BANK = 368
MSG_INDEX = 1301
INTRO_BANK = 389
INTRO_INDEX = 0

def unpack_bank(data):
    if len(data) < 4:
        return 0, []
    num_entries, init_key = struct.unpack("<HH", data[:4])
    entries = []
    for i in range(num_entries):
        key = (init_key * (i + 1) * 0x2FD) & 0xFFFF
        key_32 = key | (key << 16)
        offset_enc, len_unk_enc = struct.unpack("<II", data[4 + i*8 : 4 + i*8 + 8])
        offset = offset_enc ^ key_32
        len_unk = len_unk_enc ^ key_32
        length = len_unk & 0xFFFF
        unk = len_unk >> 16
        entries.append((offset, length, unk))
    char_lists = []
    for i, (offset, length, unk) in enumerate(entries):
        key = (0x91BD3 * (i + 1)) & 0xFFFF
        chars = []
        for j in range(length):
            w = struct.unpack("<H", data[offset + j*2 : offset + (j+1)*2])[0] ^ key
            chars.append(w)
            key = (key + 0x493D) & 0xFFFF
        char_lists.append((chars, unk))
    return init_key, char_lists

def pack_bank(init_key, char_lists):
    num_entries = len(char_lists)
    header_size = 4 + num_entries * 8
    str_data = bytearray()
    toc = []
    for chars, unk in char_lists:
        offset = header_size + len(str_data)
        toc.append((offset, len(chars), unk))
        i = len(toc) - 1
        key = (0x91BD3 * (i + 1)) & 0xFFFF
        for c in chars:
            enc = c ^ key
            str_data.extend(struct.pack("<H", enc))
            key = (key + 0x493D) & 0xFFFF
    header_data = bytearray(struct.pack("<HH", num_entries, init_key))
    for i, (offset, length, unk) in enumerate(toc):
        key = (init_key * (i + 1) * 0x2FD) & 0xFFFF
        key_32 = key | (key << 16)
        offset_enc = offset ^ key_32
        len_unk_enc = (length | (unk << 16)) ^ key_32
        header_data.extend(struct.pack("<II", offset_enc, len_unk_enc))
    return bytes(header_data + str_data)

def apply_soullocke(input_path, output_path, payload_json_path, log_cb=None):
    """
    Directly injects SoulLocke / Nuzlocke C mod into the given ROM.
    Preserves sibling custom payloads (60 FPS Visual Engine, Move Type Effectiveness)
    and dynamically recalculates LIT_MAIN_ARENA_HI and HEAP_ID_APPLICATION.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    log(f"[Injector] Reading ROM: {os.path.basename(input_path)}")
    rom = ndspy.rom.NintendoDSRom.fromFile(input_path)
    arm9 = bytearray(rom.arm9)
    ovs = rom.loadArm9Overlays()
    if 16 not in ovs or ovs[16].ramAddress not in (OV16_RAM, 0x0224A920, 0x0224A700):
        raise ValueError("Overlay 16 not found or address mismatch.")
    ov16 = ovs[16]
    ov16_ram, autoload_off, lit_arena_hi, vanilla_mod_params, app_heap_off, vanilla_bss_start, ver_str = _get_version_params(ov16.ramAddress)
    ov16_data = bytearray(ov16.data)

    payload_json_path = _resolve_version_payload_path(payload_json_path, ver_str)
    log(f"[Injector] Using payload profile: {os.path.basename(payload_json_path)} (target ProjectPM {ver_str})")
    with open(payload_json_path, "r", encoding="utf-8") as f:
        mod_data = json.load(f)

    origin = mod_data["origin"]
    payload = bytes.fromhex(mod_data["payload_hex"])
    hooks = mod_data["hooks"]
    msg_codes = mod_data["msg_codes"]
    intro_codes = mod_data["intro_codes"]

    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (ov16_ram, ov16_data)}

    # Apply hooks
    log(f"[Injector] Applying {len(hooks)} binary hooks for ProjectPM {ver_str}...")
    for h in hooks:
        name = h["name"]
        reg = h["region"]
        addr = h["addr"]
        hook_hex = h["hook_hex"]
        
        base, buf = regions[reg]
        off = addr - base
        patch_bytes = bytes.fromhex(hook_hex)
        buf[off: off + len(patch_bytes)] = patch_bytes

    # Autoload table (preserve any existing sibling custom autoload entries)
    log(f"[Injector] Registering Autoload entry -> 0x{origin:08X} ({len(payload)} bytes)...")
    custom_entries = _extract_custom_entries(arm9, autoload_off)
    # Filter out existing SoulLocke / Nuzlocke entry if any
    custom_entries = [
        (d, b, s) for d, b, s in custom_entries
        if d not in (origin, 0x023DD240, 0x023DD4E0, 0x023DE7A0)
    ]
    custom_entries.append((origin, payload, 0))
    arm9 = _rebuild_autoload(
        arm9, autoload_off, lit_arena_hi, vanilla_mod_params,
        custom_entries, app_heap_off, vanilla_bss_start
    )

    # Message injection
    log("[Injector] Updating pl_msg.narc texts...")
    pl_msg = ndspy.narc.NARC(rom.getFileByName("msgdata/pl_msg.narc"))
    
    # Rejection msg in MSG_BANK (368)
    ik_msg, cl_msg = unpack_bank(pl_msg.files[MSG_BANK])
    cl_msg_new = list(cl_msg)
    while len(cl_msg_new) < MSG_INDEX:
        cl_msg_new.append(([0xFFFF], 0))
    if len(cl_msg_new) == MSG_INDEX:
        cl_msg_new.append((msg_codes, 0))
    else:
        cl_msg_new[MSG_INDEX] = (msg_codes, 0)
    pl_msg.files[MSG_BANK] = pack_bank(ik_msg, cl_msg_new)

    # Intro msg in INTRO_BANK (389)
    if intro_codes:
        ik_intro, cl_intro = unpack_bank(pl_msg.files[INTRO_BANK])
        cl_intro_new = list(cl_intro)
        cl_intro_new[INTRO_INDEX] = (intro_codes, cl_intro[INTRO_INDEX][1])
        pl_msg.files[INTRO_BANK] = pack_bank(ik_intro, cl_intro_new)

    rom.setFileByName("msgdata/pl_msg.narc", pl_msg.save())

    # Finalize ROM
    rom.name = b"POKEMON PL\x00\x00"
    rom.arm9 = bytes(arm9)
    ov16.data = bytes(ov16_data)
    ovs[16] = ov16
    rom.files[ov16.fileID] = ov16.data
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

    rom_bytes = bytearray(rom.save())
    if len(rom_bytes) < ROM_TARGET_SIZE:
        rom_bytes.extend(b"\xff" * (ROM_TARGET_SIZE - len(rom_bytes)))

    with open(output_path, "wb") as f:
        f.write(rom_bytes)

    log(f"[Injector] SUCCESS: Mod installed cleanly to {os.path.basename(output_path)}")
    return True

def restore_clean_projectpm(input_path, output_path, payload_json_path, log_cb=None):
    """
    Reverts SoulLocke/Nuzlocke hooks and restores a clean ProjectPM multiplayer ROM.
    Preserves sibling custom payloads (60 FPS Visual Engine, Move Type Effectiveness),
    recalculates LIT_MAIN_ARENA_HI, adjusts HEAP_ID_APPLICATION, and cleans pl_msg.narc Banks 368 and 389.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    log(f"[Restore] Reading ROM: {os.path.basename(input_path)}")
    rom = ndspy.rom.NintendoDSRom.fromFile(input_path)
    arm9 = bytearray(rom.arm9)
    ovs = rom.loadArm9Overlays()
    if 16 not in ovs or ovs[16].ramAddress not in (OV16_RAM, 0x0224A920, 0x0224A700):
        raise ValueError("Overlay 16 not found or address mismatch.")
    ov16 = ovs[16]
    ov16_ram, autoload_off, lit_arena_hi, vanilla_mod_params, app_heap_off, vanilla_bss_start, ver_str = _get_version_params(ov16.ramAddress)
    ov16_data = bytearray(ov16.data)

    payload_json_path = _resolve_version_payload_path(payload_json_path, ver_str)
    log(f"[Restore] Using payload profile: {os.path.basename(payload_json_path)} (target ProjectPM {ver_str})")
    with open(payload_json_path, "r", encoding="utf-8") as f:
        mod_data = json.load(f)

    hooks = mod_data["hooks"]
    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (ov16_ram, ov16_data)}

    # Revert hooks to orig_hex
    log(f"[Restore] Reverting {len(hooks)} hooks to stock ProjectPM {ver_str} bytes...")
    for h in hooks:
        reg = h["region"]
        addr = h["addr"]
        orig_hex = h["orig_hex"]
        
        base, buf = regions[reg]
        off = addr - base
        orig_bytes = bytes.fromhex(orig_hex)
        if 0 <= off and off + len(orig_bytes) <= len(buf):
            buf[off: off + len(orig_bytes)] = orig_bytes

    # Non-destructive Autoload restoration: preserve sibling custom payloads
    custom_entries = _extract_custom_entries(arm9, autoload_off)
    custom_entries = [
        (d, b, s) for d, b, s in custom_entries
        if d not in (0x023DD240, 0x023DD4E0, 0x023DE7A0)
    ]
    if custom_entries:
        sibling_names = []
        for d, _, _ in custom_entries:
            if d == 0x023DE000:
                sibling_names.append("Moteur Visuel 60 FPS (0x023DE000)")
            elif d == 0x023DF000:
                sibling_names.append("Efficacité des Types (0x023DF000)")
            else:
                sibling_names.append(f"Payload 0x{d:08X}")
        log(f"[Restore] Preserving active sibling payload(s): {', '.join(sibling_names)}")
    else:
        log("[Restore] Zero custom payloads remaining; resetting Autoload to stock vanilla.")

    arm9 = _rebuild_autoload(
        arm9, autoload_off, lit_arena_hi, vanilla_mod_params,
        custom_entries, app_heap_off, vanilla_bss_start
    )

    # Clean pl_msg.narc Banks 368 and 389
    log("[Restore] Cleaning pl_msg.narc text banks 368 and 389...")
    pl_msg = ndspy.narc.NARC(rom.getFileByName("msgdata/pl_msg.narc"))
    
    # Bank 368: truncate to 1301 entries if extra entries exist
    ik_368, cl_368 = unpack_bank(pl_msg.files[MSG_BANK])
    if len(cl_368) > 1301:
        log(f"[Restore] Truncating Bank 368 from {len(cl_368)} to 1301 entries.")
        cl_368 = cl_368[:1301]
        pl_msg.files[MSG_BANK] = pack_bank(ik_368, cl_368)

    # Bank 389: restore Rowan intro (index 0) to clean base dialogue
    is_en = "_en" in os.path.basename(payload_json_path).lower()
    clean_intro_codes = CLEAN_INTRO_CODES_EN if is_en else CLEAN_INTRO_CODES_FR
    ik_389, cl_389 = unpack_bank(pl_msg.files[INTRO_BANK])
    if cl_389:
        log("[Restore] Restoring Bank 389[0] Rowan intro to clean base dialogue.")
        cl_389[INTRO_INDEX] = (clean_intro_codes, cl_389[INTRO_INDEX][1])
        pl_msg.files[INTRO_BANK] = pack_bank(ik_389, cl_389)

    rom.setFileByName("msgdata/pl_msg.narc", pl_msg.save())

    # Finalize ROM
    rom.name = b"POKEMON PL\x00\x00"
    rom.arm9 = bytes(arm9)
    ov16.data = bytes(ov16_data)
    ovs[16] = ov16
    rom.files[ov16.fileID] = ov16.data
    rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

    rom_bytes = bytearray(rom.save())
    if len(rom_bytes) < ROM_TARGET_SIZE:
        rom_bytes.extend(b"\xff" * (ROM_TARGET_SIZE - len(rom_bytes)))

    with open(output_path, "wb") as f:
        f.write(rom_bytes)

    log(f"[Restore] SUCCESS: Restored clean ProjectPM to {os.path.basename(output_path)}")
    return True
