"""
rom_validator.py
Post-patch ROM integrity checks (header, NARC counts, trainer structs, scripts, text banks, and autoload bounds).
"""
import os
import struct
from typing import Optional, Callable, Union, List, Tuple, Dict, Any

import ndspy.rom
import ndspy.narc

# Invariants
STRIDE_BY_MON_TYPE = {0: 16, 1: 24, 2: 20, 3: 28}
MAX_SPECIES_ID = 493
MAX_LEVEL = 100
MAX_BALL_SEAL = 128
MAX_NATURE = 25
MAX_ABILITY = 126

# Static encounter definitions in scr_seq.narc
STATIC_BATTLES = [
    {"name": "Uxie", "subfile": 361, "offset": 70, "species": 480, "level": 50, "opcode": 701},
    {"name": "Azelf", "subfile": 357, "offset": 142, "species": 482, "level": 50, "opcode": 701},
    {"name": "Dialga", "subfile": 239, "offset": 182, "species": 483, "level": 70, "opcode": 701},
    {"name": "Palkia", "subfile": 240, "offset": 182, "species": 484, "level": 70, "opcode": 701},
    {"name": "Giratina Turnback", "subfile": 291, "offset": 80, "species": 487, "level": 47, "opcode": 701},
    {"name": "Giratina Distortion", "subfile": 389, "offset": 219, "species": 487, "level": 47, "opcode": 793},
    {"name": "Heatran", "subfile": 286, "offset": 272, "species": 485, "level": 50, "opcode": 701},
    {"name": "Regirock", "subfile": 396, "offset": 187, "species": 377, "level": 30, "opcode": 701},
    {"name": "Regice", "subfile": 394, "offset": 187, "species": 378, "level": 30, "opcode": 701},
    {"name": "Registeel", "subfile": 392, "offset": 187, "species": 379, "level": 30, "opcode": 701},
    {"name": "Regigigas", "subfile": 317, "offset": 146, "species": 486, "level": 1, "opcode": 701},
    {"name": "Darkrai", "subfile": 363, "offset": 140, "species": 491, "level": 50, "opcode": 701},
    {"name": "Arceus", "subfile": 238, "offset": 135, "species": 493, "level": 80, "opcode": 701},
    {"name": "Rotom", "subfile": 337, "offset": 91, "species": 479, "level": 20, "opcode": 292},
    {"name": "Spiritomb", "subfile": 441, "offset": 350, "species": 442, "level": 25, "opcode": 292},
    {"name": "Drifloon", "subfile": 216, "offset": 472, "species": 425, "level": 15, "opcode": 701},
    {"name": "Shaymin", "subfile": 310, "offset": 148, "species": 492, "level": 30, "opcode": 792},
    {"name": "Pichu Event", "subfile": 219, "offset": 2692, "species": 172, "level": 30, "opcode": 859},
]


class ValidationError(Exception):
    """Raised when post-patch ROM integrity validation fails."""
    pass


def detect_rom_pm_version(rom_obj: ndspy.rom.NintendoDSRom) -> str:
    """Detects 045, 046, or 047 version string from ROM overlay 16 address and arm9 size."""
    try:
        ov16_entry = rom_obj.loadArm9Overlays().get(16)
        if ov16_entry:
            ram = ov16_entry.ramAddress
            if ram == 0x0224A700:
                return "045"
            elif ram == 0x0224A920:
                return "046"
            elif ram == 0x0224AAE0:
                return "047"
    except Exception:
        pass

    arm9_len = len(rom_obj.arm9)
    if arm9_len == 0x109858:
        return "045"
    elif arm9_len == 0x109A78:
        return "046"
    return "047"


def unpack_text_bank(data: bytes) -> Tuple[int, List[Tuple[List[int], int]]]:
    """
    Unpacks Gen 4 encrypted text bank data into (init_key, [(char_codes, unk), ...]).
    Each entry is a list of 16-bit character/control codes terminated by 0xFFFF.
    """
    if len(data) < 4:
        return 0, []
    num_entries, init_key = struct.unpack('<HH', data[:4])
    entries = []
    for i in range(num_entries):
        key = (init_key * (i + 1) * 0x2FD) & 0xFFFF
        key_32 = key | (key << 16)
        if 4 + i * 8 + 8 > len(data):
            break
        offset_enc, len_unk_enc = struct.unpack('<II', data[4 + i * 8 : 4 + i * 8 + 8])
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
            if offset + (j + 1) * 2 > len(data):
                break
            w = struct.unpack('<H', data[offset + j * 2 : offset + (j + 1) * 2])[0] ^ key
            chars.append(w)
            key = (key + 0x493D) & 0xFFFF
        char_lists.append((chars, unk))
    return init_key, char_lists


def validate_stage1_header(rom_obj: ndspy.rom.NintendoDSRom) -> None:
    """Stage 1: ROM Header & Metadata Integrity."""
    game_code = bytes(rom_obj.idCode[:4])
    if game_code not in (b"CPUE", b"CPUF"):
        raise ValidationError(f"Stage 1: Invalid game code: {game_code}")

    if len(rom_obj.arm9) < 0x20000:
        raise ValidationError("Stage 1: ARM9 binary truncated (< 128 KB)")

    entrypoint = getattr(rom_obj, "arm9EntryAddress", 0)
    if entrypoint and not (0x02000000 <= entrypoint < 0x02100000):
        raise ValidationError(f"Stage 1: Invalid ARM9 entrypoint: {hex(entrypoint)}")


def validate_stage2_narcs(rom_obj: ndspy.rom.NintendoDSRom) -> Tuple[ndspy.narc.NARC, ndspy.narc.NARC, ndspy.narc.NARC, ndspy.narc.NARC]:
    """Stage 2: NARC File Counts & Table Bounds."""
    trdata_raw = rom_obj.getFileByName("poketool/trainer/trdata.narc")
    if trdata_raw is None:
        raise ValidationError("Stage 2: trdata.narc missing from ROM")
    trdata = ndspy.narc.NARC(trdata_raw)
    if len(trdata.files) != 973:
        raise ValidationError(f"Stage 2: trdata.narc subfile count {len(trdata.files)} != 973")

    trpoke_raw = rom_obj.getFileByName("poketool/trainer/trpoke.narc")
    if trpoke_raw is None:
        raise ValidationError("Stage 2: trpoke.narc missing from ROM")
    trpoke = ndspy.narc.NARC(trpoke_raw)
    if len(trpoke.files) != 1945:
        raise ValidationError(f"Stage 2: trpoke.narc subfile count {len(trpoke.files)} != 1945")

    scr_raw = rom_obj.getFileByName("fielddata/script/scr_seq.narc")
    if scr_raw is None:
        raise ValidationError("Stage 2: scr_seq.narc missing from ROM")
    scr_narc = ndspy.narc.NARC(scr_raw)
    if len(scr_narc.files) < 442:
        raise ValidationError(f"Stage 2: scr_seq.narc subfile count {len(scr_narc.files)} < 442")

    msg_raw = rom_obj.getFileByName("msgdata/pl_msg.narc")
    if msg_raw is None:
        raise ValidationError("Stage 2: pl_msg.narc missing from ROM")
    msg_narc = ndspy.narc.NARC(msg_raw)

    return trdata, trpoke, scr_narc, msg_narc


def validate_stage3_trainers(trdata: ndspy.narc.NARC, trpoke: ndspy.narc.NARC) -> None:
    """Stage 3: Trainer Party Struct & Value Range Verification (Solo & Co-Op)."""
    for tid in range(1, len(trdata.files)):
        h = trdata.files[tid]
        if len(h) != 28:
            raise ValidationError(f"Stage 3: Trainer {tid} header length {len(h)} != 28")
        mtype = h[0]
        psize = h[3]
        if mtype not in STRIDE_BY_MON_TYPE:
            raise ValidationError(f"Stage 3: Trainer {tid} invalid mon_type: {mtype}")
        stride = STRIDE_BY_MON_TYPE[mtype]
        pdata = trpoke.files[tid]
        if len(pdata) != psize * stride:
            raise ValidationError(f"Stage 3: Trainer {tid} party size mismatch: {len(pdata)} != {psize * stride}")

        seal_off = 6 if mtype == 0 else (14 if mtype == 1 else (8 if mtype == 2 else 16))
        for m in range(psize):
            off = m * stride
            sp = struct.unpack_from('<H', pdata, off + 4)[0] & 0x3FF
            lvl = struct.unpack_from('<H', pdata, off + 2)[0]
            seal = struct.unpack_from('<H', pdata, off + seal_off)[0]
            if not (1 <= sp <= MAX_SPECIES_ID):
                raise ValidationError(f"Stage 3: Trainer {tid} mon {m} species {sp} out of bounds")
            if not (1 <= lvl <= MAX_LEVEL):
                raise ValidationError(f"Stage 3: Trainer {tid} mon {m} level {lvl} out of bounds")
            if not (0 <= seal <= MAX_BALL_SEAL):
                raise ValidationError(f"Stage 3: Trainer {tid} mon {m} ball_seal {seal} > 128 (CRITICAL)")

        # Co-Op Party Verification
        coop_idx, coop_size, coop_mtype = struct.unpack_from('<HBB', h, 24)
        if 973 <= coop_idx < len(trpoke.files) and coop_size > 0:
            if coop_mtype not in STRIDE_BY_MON_TYPE:
                raise ValidationError(f"Stage 3: Trainer {tid} invalid coop_mon_type: {coop_mtype}")
            coop_stride = STRIDE_BY_MON_TYPE[coop_mtype]
            cpdata = trpoke.files[coop_idx]
            if len(cpdata) != coop_size * coop_stride:
                raise ValidationError(f"Stage 3: Co-Op Trainer {coop_idx} party size mismatch: {len(cpdata)} != {coop_size * coop_stride}")
            c_seal_off = 6 if coop_mtype == 0 else (14 if coop_mtype == 1 else (8 if coop_mtype == 2 else 16))
            for cm in range(coop_size):
                coff = cm * coop_stride
                csp = struct.unpack_from('<H', cpdata, coff + 4)[0] & 0x3FF
                clvl = struct.unpack_from('<H', cpdata, coff + 2)[0]
                cseal = struct.unpack_from('<H', cpdata, coff + c_seal_off)[0]
                if not (1 <= csp <= MAX_SPECIES_ID):
                    raise ValidationError(f"Stage 3: Co-Op Trainer {coop_idx} mon {cm} species {csp} out of bounds")
                if not (1 <= clvl <= MAX_LEVEL):
                    raise ValidationError(f"Stage 3: Co-Op Trainer {coop_idx} mon {cm} level {clvl} out of bounds")
                if not (0 <= cseal <= MAX_BALL_SEAL):
                    raise ValidationError(f"Stage 3: Co-Op Trainer {coop_idx} mon {cm} ball_seal {cseal} > 128 (CRITICAL)")


def validate_stage4_scripts(scr_narc: ndspy.narc.NARC, pm_ver: str) -> None:
    """Stage 4: Script NARC Integrity & Invariant Encounters."""
    for entry in STATIC_BATTLES:
        sub = entry["subfile"]
        off = entry["offset"]
        if sub >= len(scr_narc.files):
            raise ValidationError(f"Stage 4: Script subfile {sub} missing")
        sdata = scr_narc.files[sub]
        if off + 4 > len(sdata):
            continue
        opcode = struct.unpack_from('<H', sdata, off)[0]
        valid_opcodes = [entry["opcode"]]
        if entry["name"] == "Giratina Distortion" or (sub == 389 and off == 219):
            valid_opcodes.append(701)
        if pm_ver == "047" and opcode not in valid_opcodes:
            raise ValidationError(f"Stage 4: Battle {entry['name']} opcode {hex(opcode)} != {hex(entry['opcode'])}")
        sp = struct.unpack_from('<H', sdata, off + 2)[0]
        if pm_ver == "047" and not (1 <= sp <= MAX_SPECIES_ID):
            raise ValidationError(f"Stage 4: Battle {entry['name']} species {sp} out of bounds")

    # Script header table validation
    for i, sf in enumerate(scr_narc.files):
        if len(sf) < 2:
            continue
        term_pos = sf.find(b'\x13\xfd')
        if term_pos != -1 and term_pos % 4 == 0:
            for j in range(0, term_pos, 4):
                rel = struct.unpack_from('<i', sf, j)[0]
                target = j + 4 + rel
                if not (0 <= target <= len(sf)):
                    raise ValidationError(f"Stage 4: Script subfile {i} header offset {j} target {target} out of file bounds ({len(sf)})")


def validate_stage5_texts(msg_narc: ndspy.narc.NARC) -> None:
    """Stage 5: Text Bank Terminator Validation."""
    for bank_id in (544, 147, 366, 417, 548):
        if bank_id < len(msg_narc.files):
            init_key, char_lists = unpack_text_bank(msg_narc.files[bank_id])
            for idx, (chars, unk) in enumerate(char_lists):
                if chars and chars[-1] != 0xFFFF:
                    raise ValidationError(f"Stage 5: Bank {bank_id} entry {idx} missing 0xFFFF terminator")


def validate_stage6_autoload_hooks(rom_obj: ndspy.rom.NintendoDSRom, pm_ver: str) -> None:
    """Stage 6: Autoload Memory Bounds & BL Hook Integrity."""
    arm9 = rom_obj.arm9
    base_vma = 0x02000000
    mod_params_off = 0xBA0
    list_start, list_end = struct.unpack_from('<II', arm9, mod_params_off)
    custom_modules: List[Tuple[int, int]] = []

    if 0x02000000 <= list_start <= 0x02000000 + len(arm9):
        table_off = list_start - 0x02000000
        table_len = list_end - list_start
        for i in range(table_len // 12):
            dest, size, bss = struct.unpack_from('<3I', arm9, table_off + i * 12)
            if 0x023C0000 <= dest < 0x023E0000:
                if dest + size > 0x023E0000:
                    raise ValidationError(f"Stage 6: Custom module at {hex(dest)} exceeds arena bounds (end: {hex(dest + size)} > 0x023E0000)")
                custom_modules.append((dest, size))

    # Verify no overlapping custom modules
    sorted_modules = sorted(custom_modules, key=lambda x: x[0])
    for k in range(len(sorted_modules) - 1):
        if sorted_modules[k][0] + sorted_modules[k][1] > sorted_modules[k + 1][0]:
            raise ValidationError(f"Stage 6: Overlapping custom modules: {hex(sorted_modules[k][0])} and {hex(sorted_modules[k + 1][0])}")

    # Verify all primary ARM9 hook sites (H1, H2, H7, H8, H9)
    ver = pm_ver
    h_sites_vma = [
        (0x0205624C if ver == "047" else (0x02056110 if ver == "046" else 0x02055FA8)),  # H1
        (0x0205670E if ver == "047" else (0x020565D2 if ver == "046" else 0x0205646A)),  # H2
        (0x02000DE0),  # H7
        (0x0203F192 if ver == "047" else (0x0203F0DA if ver == "046" else 0x0203F09A)),  # H8
        (0x0205462E if ver == "047" else (0x020544F2 if ver == "046" else 0x020543A6)),  # H9
    ]
    for h_vma in h_sites_vma:
        off = h_vma - base_vma
        if off + 4 <= len(arm9):
            hw1, hw2 = struct.unpack_from('<HH', arm9, off)
            if (hw1 & 0xF800) == 0xF000 and (hw2 & 0xE800) == 0xE800:
                offset = ((hw1 & 0x7FF) << 11) | (hw2 & 0x7FF)
                if offset & (1 << 21):
                    offset -= (1 << 22)
                target = (h_vma + 4) + (offset << 1)
                if 0x023D0000 <= target < 0x023E0000:
                    if not any(m_start <= target < m_start + m_size for m_start, m_size in custom_modules):
                        raise ValidationError(f"Stage 6: Dangling BL at {hex(h_vma)} jumping to unmapped {hex(target)}")


def validate_rom_comprehensive(rom_obj: ndspy.rom.NintendoDSRom) -> None:
    """
    Executes the authoritative 6-stage post-patch ROM validator.
    Raises ValidationError if any integrity check fails.
    """
    validate_stage1_header(rom_obj)
    trdata, trpoke, scr_narc, msg_narc = validate_stage2_narcs(rom_obj)
    validate_stage3_trainers(trdata, trpoke)
    pm_ver = detect_rom_pm_version(rom_obj)
    validate_stage4_scripts(scr_narc, pm_ver)
    validate_stage5_texts(msg_narc)
    validate_stage6_autoload_hooks(rom_obj, pm_ver)


def validate_rom(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    raise_on_error: bool = True,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Convenience validator entry point accepting either a file path or an ndspy ROM object.
    Returns True if valid, or raises ValidationError (or returns False if raise_on_error=False).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                raise ValidationError(f"ROM file not found: {rom_input}")
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        validate_rom_comprehensive(rom)
        log("[Validator] ROM integrity validation passed (6/6 stages successful).")
        return True
    except ValidationError as ve:
        log(f"[Validator ERROR] Integrity validation failed: {ve}")
        if raise_on_error:
            raise
        return False
    except Exception as e:
        log(f"[Validator ERROR] Unexpected exception during validation: {e}")
        if raise_on_error:
            raise ValidationError(f"Unexpected validation failure: {e}") from e
        return False
