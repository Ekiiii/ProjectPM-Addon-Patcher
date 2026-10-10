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
OV16_RAM  = 0x0224A700
ROM_TARGET_SIZE = 134217728  # 128 MB

VANILLA_ARM9_LEN = 0x109858
MODULE_PARAMS_OFF = 0x0BA0
VANILLA_MODULE_PARAMS = (0x02109840, 0x02109858, 0x02109180, 0x02109180, 0x021E0280, 0x00000000)
AUTOLOAD_LIST_OFF = 0x109840
VANILLA_AUTOLOAD_LIST = (0x01FF8000, 0x660, 0, 0x027E0000, 0x60, 0x20)
ARENA_HI_DEFAULT = 0x023E0000
LIT_MAIN_ARENA_HI = 0x020C9B9C

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
    if 16 not in ovs or ovs[16].ramAddress != OV16_RAM:
        raise ValueError("Overlay 16 not found or address mismatch.")
    ov16 = ovs[16]
    ov16_data = bytearray(ov16.data)

    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (OV16_RAM, ov16_data)}

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

    # Autoload table
    log(f"[Injector] Setting Autoload entry 3 -> 0x{origin:08X} ({len(payload)} bytes)...")
    old_list = bytes(arm9[AUTOLOAD_LIST_OFF: AUTOLOAD_LIST_OFF + 24])
    new_arm9 = bytearray(arm9[:AUTOLOAD_LIST_OFF])
    new_arm9 += payload
    list_start = ARM9_BASE + len(new_arm9)
    new_arm9 += old_list
    new_arm9 += struct.pack("<3I", origin, len(payload), 0)
    struct.pack_into("<2I", new_arm9, MODULE_PARAMS_OFF, list_start, ARM9_BASE + len(new_arm9))
    struct.pack_into("<I", new_arm9, LIT_MAIN_ARENA_HI - ARM9_BASE, origin)
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
    ov16_data = bytearray(ov16.data)

    regions = {"arm9": (ARM9_BASE, arm9), "ov16": (OV16_RAM, ov16_data)}

    # Revert hooks to orig_hex
    log("[Restore] Reverting hooks to stock ProjectPM bytes...")
    for h in hooks:
        reg = h["region"]
        addr = h["addr"]
        orig_hex = h["orig_hex"]
        
        base, buf = regions[reg]
        off = addr - base
        orig_bytes = bytes.fromhex(orig_hex)
        buf[off: off + len(orig_bytes)] = orig_bytes

    # Restore Autoload table and arena hi
    log("[Restore] Restoring Arena Hi to 0x023E0000...")
    struct.pack_into("<I", arm9, LIT_MAIN_ARENA_HI - ARM9_BASE, ARENA_HI_DEFAULT)
    
    # Restore Nitro-SDK Module Parameters at 0xBA0
    log("[Restore] Restoring Nitro-SDK Module Parameters at 0xBA0...")
    struct.pack_into("<6I", arm9, MODULE_PARAMS_OFF, *VANILLA_MODULE_PARAMS)

    # Truncate ARM9 to AUTOLOAD_LIST_OFF (0x109840) to strip the injected C payload
    arm9 = bytearray(arm9[:AUTOLOAD_LIST_OFF])

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
