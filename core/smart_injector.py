# -*- coding: utf-8 -*-
"""
smart_injector.py
Core C Mod Injection Engine:
- Injects SoulLocke C mod payload via Nitro-SDK Autoload Table into high main arena
- Installs ARM9 and Overlay 16 hooks
- Injects in-game rejection & intro messages into msgdata/pl_msg.narc
- Fully reversible ("Restore Clean ProjectPM")
"""
import os
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

def _get_version_params(ov16_ram):
    if ov16_ram == 0x0224A700:
        return (
            0x0224A700,
            0x109840,
            0x020C9B9C,
            (0x02109840, 0x02109858, 0x02109180, 0x02109180, 0x021E0280, 0x00000000),
        )
    elif ov16_ram == 0x0224A920:
        return (
            0x0224A920,
            0x109A60,
            0x020C9DF0,
            (0x02109A60, 0x02109A78, 0x021093A0, 0x021093A0, 0x021E04A0, 0x00000000),
        )
    return (
        OV16_RAM,
        AUTOLOAD_LIST_OFF,
        LIT_MAIN_ARENA_HI,
        VANILLA_MODULE_PARAMS,
    )

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
    Directly injects SoulLocke C mod into the given ROM.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    with open(payload_json_path, "r", encoding="utf-8") as f:
        mod_data = json.load(f)

    origin = mod_data["origin"]
    payload = bytes.fromhex(mod_data["payload_hex"])
    hooks = mod_data["hooks"]
    msg_codes = mod_data["msg_codes"]
    intro_codes = mod_data["intro_codes"]

    log(f"[Injector] Reading ROM: {os.path.basename(input_path)}")
    rom = ndspy.rom.NintendoDSRom.fromFile(input_path)
    arm9 = bytearray(rom.arm9)
    ovs = rom.loadArm9Overlays()
    if 16 not in ovs or ovs[16].ramAddress not in (OV16_RAM, 0x0224A920, 0x0224A700):
        raise ValueError("Overlay 16 not found or address mismatch.")
    ov16 = ovs[16]
    ov16_ram, autoload_off, lit_arena_hi, _ = _get_version_params(ov16.ramAddress)
    ov16_data = bytearray(ov16.data)

    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (ov16_ram, ov16_data)}

    # Apply hooks
    log("[Injector] Applying hooks...")
    for h in hooks:
        name = h["name"]
        reg = h["region"]
        addr = h["addr"]
        hook_hex = h["hook_hex"]
        
        base, buf = regions[reg]
        off = addr - base
        patch_bytes = bytes.fromhex(hook_hex)
        buf[off: off + len(patch_bytes)] = patch_bytes

    # Autoload table (preserve any existing non-SoulLocke custom autoload entries)
    log(f"[Injector] Setting Autoload entry 3 -> 0x{origin:08X} ({len(payload)} bytes)...")
    old_start, old_end = struct.unpack_from("<2I", arm9, MODULE_PARAMS_OFF)
    start_off = old_start - ARM9_BASE
    end_off = old_end - ARM9_BASE
    custom_entries = [(origin, payload, 0)]
    if 0 <= start_off <= len(arm9) and 0 <= end_off <= len(arm9) and end_off >= start_off + 24:
        data_cursor = autoload_off
        for entry_pos in range(start_off + 24, end_off, 12):
            if entry_pos + 12 <= len(arm9):
                dest, sz, bss = struct.unpack_from("<3I", arm9, entry_pos)
                if 0x023C0000 <= dest < 0x023E0000 and 0 < sz <= 0x10000 and data_cursor + sz <= start_off:
                    blob = bytes(arm9[data_cursor:data_cursor + sz])
                    data_cursor += sz
                    if dest not in (origin, 0x023DD240, 0x023DD4E0, 0x023DE240, 0x023DE4E0, 0x023DF240, 0x023DF280, 0x023DF4E0):
                        custom_entries.append((dest, blob, bss))

    new_arm9 = bytearray(arm9[:autoload_off])
    for _, blob, _ in custom_entries:
        new_arm9 += blob
    list_start = ARM9_BASE + len(new_arm9)
    new_arm9 += struct.pack("<6I", *VANILLA_AUTOLOAD_LIST)
    for dest, blob, bss in custom_entries:
        new_arm9 += struct.pack("<3I", dest, len(blob), bss)
    struct.pack_into("<2I", new_arm9, MODULE_PARAMS_OFF, list_start, ARM9_BASE + len(new_arm9))
    high_arena_dests = [d & ~0x1F for d, _, _ in custom_entries if 0x023C0000 <= d < 0x023E0000]
    arena_hi = min(high_arena_dests) if high_arena_dests else ARENA_HI_DEFAULT
    struct.pack_into("<I", new_arm9, lit_arena_hi - ARM9_BASE, arena_hi)
    arm9 = new_arm9

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

    log(f"[Injector] SUCCESS: SoulLocke installed to {os.path.basename(output_path)}")
    return True

def restore_clean_projectpm(input_path, output_path, payload_json_path, log_cb=None):
    """
    Reverts SoulLocke hooks and restores a clean ProjectPM multiplayer ROM.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    with open(payload_json_path, "r", encoding="utf-8") as f:
        mod_data = json.load(f)

    hooks = mod_data["hooks"]

    log(f"[Restore] Reading ROM: {os.path.basename(input_path)}")
    rom = ndspy.rom.NintendoDSRom.fromFile(input_path)
    arm9 = bytearray(rom.arm9)
    ovs = rom.loadArm9Overlays()
    ov16 = ovs[16]
    ov16_ram, autoload_off, lit_arena_hi, vanilla_mod_params = _get_version_params(ov16.ramAddress)
    ov16_data = bytearray(ov16.data)

    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (ov16_ram, ov16_data)}

    # Revert hooks to orig_hex
    log("[Restore] Reverting hooks to stock ProjectPM bytes...")
    for h in hooks:
        reg = h["region"]
        addr = h["addr"]
        orig_hex = h["orig_hex"]
        
        base, buf = regions[reg]
        off = addr - base
        orig_bytes = bytes.fromhex(orig_hex)
        if 0 <= off and off + len(orig_bytes) <= len(buf):
            buf[off: off + len(orig_bytes)] = orig_bytes

    # Restore Autoload table and arena hi
    log("[Restore] Restoring Arena Hi to 0x023E0000...")
    struct.pack_into("<I", arm9, lit_arena_hi - ARM9_BASE, ARENA_HI_DEFAULT)
    
    # Restore Nitro-SDK Module Parameters at 0xBA0
    log("[Restore] Restoring Nitro-SDK Module Parameters at 0xBA0...")
    struct.pack_into("<6I", arm9, MODULE_PARAMS_OFF, *vanilla_mod_params)

    # Truncate ARM9 to autoload_off to strip the injected C payload
    arm9 = bytearray(arm9[:autoload_off])

    # Append clean 24-byte Autoload List (2 entries: ITCM 0x01FF8000 and DTCM 0x027E0000)
    clean_autoload = struct.pack("<6I", 0x01FF8000, 0x660, 0, 0x027E0000, 0x60, 0x20)
    arm9.extend(clean_autoload)
    log(f"[Restore] Truncated ARM9 and restored clean Autoload List ({len(arm9)} bytes)...")

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
