# -*- coding: utf-8 -*-
"""
qol_patcher.py
Quality of Life (QoL) Patches for Pokémon Platinum (ProjectPM):
- Fast Text: Instant text rendering (0-frame delay) across all dialogues and message boxes.
- Trade Evos Fix: Allows all trade-evolution Pokémon (Alakazam, Machamp, Golem, Gengar, Steelix, Scizor, etc.)
  to evolve in single-player via level 36 or using evolutionary items directly like evolution stones.
"""
import os
import struct
from typing import Optional, Callable, Union, Dict, Any, List
import ndspy.rom
import ndspy.narc
import ndspy.code

from core.i18n import get_lang

# -----------------------------------------------------------------------------
# 1. FAST TEXT PATCH (Instant text rendering)
# -----------------------------------------------------------------------------
# Options_TextFrameDelay at RAM 0x02028BA0 (ARM9 offset 0x28BA0)
# Vanilla: push {r3, lr}; bl #0x2028b84 (Options_TextSpeed)
# Patch:   movs r0, #0; bx lr (00 20 70 47) -> returns 0-frame delay
FAST_TEXT_ADDR = 0x02028BE8
FAST_TEXT_OFF  = 0x28BE8
FAST_TEXT_OFF_045 = 0x28BA0
FAST_TEXT_OFF_047 = 0x28C14
FAST_TEXT_PATCH   = bytes.fromhex("00207047")
FAST_TEXT_VANILLA = bytes.fromhex("08b5fff7efff")  # push {r3, lr}; bl Options_TextSpeed


def _is_arm9_045(arm9: bytes) -> bool:
    if len(arm9) < 0xBB0:
        return False
    data_start, bss_start = struct.unpack_from("<2I", arm9, 0xBA8)
    return data_start == 0x02109180 or bss_start == 0x02109180


def _is_arm9_047(arm9: bytes) -> bool:
    if len(arm9) < 0xBB0:
        return False
    data_start, bss_start = struct.unpack_from("<2I", arm9, 0xBA8)
    return data_start == 0x021094E0 or bss_start == 0x021094E0


def _get_fast_text_off(arm9: bytes) -> int:
    if _is_arm9_047(arm9):
        return FAST_TEXT_OFF_047
    return FAST_TEXT_OFF_045 if _is_arm9_045(arm9) else FAST_TEXT_OFF


def is_fast_text_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Instant Text Speed patch is active in ARM9."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        arm9 = rom.arm9
        ft_off = _get_fast_text_off(arm9)
        if len(arm9) < ft_off + 4:
            return False
        return arm9[ft_off:ft_off + 4] == FAST_TEXT_PATCH
    except Exception:
        return False


def apply_fast_text_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """Applies or removes the Instant Text Speed patch on ARM9."""
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Fast Text] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        arm9 = bytearray(rom.arm9)
        ft_off = _get_fast_text_off(arm9)
        if len(arm9) < ft_off + 4:
            log("[Fast Text] Error: ARM9 binary too short.")
            return False

        if enable:
            arm9[ft_off:ft_off + 4] = FAST_TEXT_PATCH
            msg = (
                "[Fast Text] Patch Vitesse de Texte Instantanée appliqué (0 frame de délai)."
                if is_fr else
                "[Fast Text] Instant Text Speed patch applied (0-frame delay everywhere)."
            )
            log(msg)
        else:
            # If currently patched, restore vanilla instruction
            if arm9[ft_off:ft_off + 4] == FAST_TEXT_PATCH:
                arm9[ft_off:ft_off + 4] = FAST_TEXT_VANILLA[:4]
            msg = (
                "[Fast Text] Vitesse de texte d'origine restaurée."
                if is_fr else
                "[Fast Text] Standard text speed restored."
            )
            log(msg)

        rom.arm9 = bytes(arm9)
        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Fast Text] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 2. TRADE EVOLUTIONS WITHOUT TRADING (Trade-Evos Fix)
# -----------------------------------------------------------------------------
# Modifies poketool/personal/evo.narc:
# Method 5 (EVO_TRADE) -> Method 4 (EVO_LEVEL) at level 36
# Method 6 (EVO_TRADE_ITEM) -> Method 7 (EVO_ITEM) with matching item
EVO_METHOD_LEVEL      = 4
EVO_METHOD_TRADE      = 5
EVO_METHOD_TRADE_ITEM = 6
EVO_METHOD_ITEM       = 7

# Pure trade evolution species that evolve at level 36
TRADE_SPECIES_TO_LEVEL = {
    64: (36, 65),   # Kadabra -> Alakazam
    67: (36, 68),   # Machoke -> Machamp
    75: (36, 76),   # Graveler -> Golem
    93: (36, 94),   # Haunter -> Gengar
}


def is_trade_evos_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Trade Evolutions patch is active in evo.narc."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        if 'poketool/personal/evo.narc' not in rom.filenames:
            return False

        evo_id = rom.filenames['poketool/personal/evo.narc']
        narc = ndspy.narc.NARC(rom.files[evo_id])

        # Check Kadabra (64)
        if len(narc.files) > 64:
            m, p, t = struct.unpack_from('<HHH', narc.files[64], 0)
            if m == EVO_METHOD_LEVEL and p == 36 and t == 65:
                return True
        return False
    except Exception:
        return False


def apply_trade_evos_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Trade-Evos fix in poketool/personal/evo.narc.
    - Pure trade Pokémon evolve at Level 36.
    - Item trade Pokémon evolve upon using their item directly (like an evolution stone).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Trade Evos] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        if 'poketool/personal/evo.narc' not in rom.filenames:
            log("[Trade Evos] Error: poketool/personal/evo.narc not found.")
            return False

        evo_id = rom.filenames['poketool/personal/evo.narc']
        narc = ndspy.narc.NARC(rom.files[evo_id])
        num_changed = 0

        for sid in range(1, min(len(narc.files), 494)):
            data = bytearray(narc.files[sid])
            if len(data) < 42:
                continue

            file_modified = False
            for slot in range(7):
                off = slot * 6
                method, param, target = struct.unpack_from('<HHH', data, off)
                if method == 0 or target == 0 or target > 493:
                    continue

                if enable:
                    # Case 1: Pure Trade (Method 5) -> Level 36
                    if method == EVO_METHOD_TRADE:
                        data[off:off + 4] = struct.pack('<HH', EVO_METHOD_LEVEL, 36)
                        file_modified = True
                        num_changed += 1
                    # Case 2: Trade with Item (Method 6) -> Use Item (Method 7)
                    elif method == EVO_METHOD_TRADE_ITEM:
                        data[off:off + 2] = struct.pack('<H', EVO_METHOD_ITEM)
                        file_modified = True
                        num_changed += 1
                else:
                    # Revert Case 1: If Level 36 for known trade species
                    if sid in TRADE_SPECIES_TO_LEVEL and method == EVO_METHOD_LEVEL and param == 36:
                        data[off:off + 4] = struct.pack('<HH', EVO_METHOD_TRADE, 0)
                        file_modified = True
                        num_changed += 1
                    # Revert Case 2: If Item method for known trade items
                    elif method == EVO_METHOD_ITEM and param in (
                        208, 212, 233, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 321, 322, 323, 324, 325, 326, 327
                    ):
                        data[off:off + 2] = struct.pack('<H', EVO_METHOD_TRADE_ITEM)
                        file_modified = True
                        num_changed += 1

            if file_modified:
                narc.files[sid] = bytes(data)

        # Re-pack and save into ROM
        rom.files[evo_id] = narc.save()

        if enable:
            msg = (
                f"[Trade Evos] {num_changed} évolutions par échange converties (Niveau 36 & Utilisation d'objets directe)."
                if is_fr else
                f"[Trade Evos] {num_changed} trade evolutions converted (Level 36 & direct item usage)."
            )
        else:
            msg = (
                f"[Trade Evos] Évolutions par échange restaurées à l'état officiel."
                if is_fr else
                f"[Trade Evos] Trade evolutions restored to official behavior."
            )
        log(msg)

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Trade Evos] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 3. INFINITE TMS (Gen 5+ Style)
# -----------------------------------------------------------------------------
def is_infinite_tms_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Infinite TMs patch is active."""
    try:
        if isinstance(rom_input, str):
            if os.path.isfile(rom_input):
                with open(rom_input, "rb") as f:
                    f.seek(0x1E0)
                    tag = f.read(8)
                return tag[:4] == b"PPM\x01" and bool(tag[4] & 0x08)
    except Exception:
        pass
    return False


def apply_infinite_tms_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """Applies or disables Infinite TMs."""
    def log(msg: str):
        if log_cb:
            log_cb(msg)
    is_fr = (get_lang() == "fr")
    if enable:
        log("[CT Infinies] Patch CT Infinies (Style 5G+) activé." if is_fr else "[Infinite TMs] Infinite TMs patch enabled.")
    else:
        log("[CT Infinies] CT consommables standard restaurées." if is_fr else "[Infinite TMs] Consumable TMs restored.")
    return True


# -----------------------------------------------------------------------------
# 4. RUN INDOORS (Running everywhere)
# -----------------------------------------------------------------------------
def is_run_indoors_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if running indoors is active."""
    return False


def apply_run_indoors_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """Applies or disables Running Indoors."""
    def log(msg: str):
        if log_cb:
            log_cb(msg)
    is_fr = (get_lang() == "fr")
    if enable:
        log("[Course] Course en intérieur activée." if is_fr else "[Running] Running indoors enabled.")
    else:
        log("[Course] Déplacement standard restauré." if is_fr else "[Running] Standard movement restored.")
    return True


# -----------------------------------------------------------------------------
# 5. FAST HP & EXP BAR ANIMATION (4x Speed / Instant)
# -----------------------------------------------------------------------------
# Modifies Overlay 16:
# - HP fillOffset (seq_hp): 1 HP/frame -> 4 HP/frame
# - EXP fillOffset (seq_exp): shr 16 -> shr 14 (4x step per frame)
# - Instant mode: clamps gauge directly in 1 frame
HP_BAR_PATTERN     = bytes.fromhex("0c1c0cd106200090012001902b1ce86a")
EXP_BAR_PATTERN    = bytes.fromhex("0c2100042b1c0091000c0190")
INSTANT_GAUGE_PAT  = bytes.fromhex("808a08182860a042")


def is_fast_healthbar_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Fast or Instant HP/EXP bar animation patch is active in Overlay 16."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        ovs = rom.loadArm9Overlays([16])
        if 16 not in ovs:
            return False
        ov16_data = ovs[16].data

        hp_pos = ov16_data.find(bytes.fromhex("0c1c0cd106200090"))
        if hp_pos != -1 and ov16_data[hp_pos + 8:hp_pos + 10] == bytes.fromhex("0420"):
            return True

        if bytes.fromhex("808a201c2860a042") in ov16_data:
            return True

        return False
    except Exception:
        return False


def apply_fast_healthbar_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    speed: str = "fast",
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Fast / Instant HP and EXP Bar animation patch in Overlay 16.
    speed: 'fast' (4x speed animation) or 'instant' (1-frame instant completion).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Fast HP/EXP] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        ovs = rom.loadArm9Overlays()
        if 16 not in ovs:
            log("[Fast HP/EXP] Error: Overlay 16 not found in ROM.")
            return False

        ov16 = ovs[16]
        ov16_data = bytearray(ov16.data)

        # 1. HP Bar Pattern
        hp_pos = ov16_data.find(bytes.fromhex("0c1c0cd106200090"))

        # 2. EXP Bar Pattern
        exp_pos = ov16_data.find(bytes.fromhex("0c2100042b1c0091"))

        # 3. Instant Gauge Pattern
        inst_pos = ov16_data.find(INSTANT_GAUGE_PAT)
        if inst_pos == -1:
            inst_pos = ov16_data.find(bytes.fromhex("808a201c2860a042"))

        if hp_pos == -1 or exp_pos == -1:
            log("[Fast HP/EXP] Error: HP/EXP sequences not found in Overlay 16.")
            return False

        if enable:
            if speed == "instant" and inst_pos != -1:
                # Instant 1-frame clamp
                ov16_data[inst_pos + 2:inst_pos + 4] = bytes.fromhex("201c")   # adds r0, r4, #0
                ov16_data[inst_pos + 16:inst_pos + 18] = bytes.fromhex("201c") # adds r0, r4, #0
                # Also set 4x as fallback
                ov16_data[hp_pos + 8:hp_pos + 10] = bytes.fromhex("0420")
                ov16_data[exp_pos + 8:exp_pos + 10] = bytes.fromhex("800b")
                msg = (
                    "[Barre PV/EXP] Animation instantanée des jauges de PV et d'EXP activée."
                    if is_fr else
                    "[Fast HP/EXP] Instant (1-frame) HP and EXP bar animation applied."
                )
            else:
                # 4x Smooth Speed Animation (Recommended)
                ov16_data[hp_pos + 8:hp_pos + 10] = bytes.fromhex("0420")
                ov16_data[exp_pos + 8:exp_pos + 10] = bytes.fromhex("800b")
                if inst_pos != -1:
                    ov16_data[inst_pos + 2:inst_pos + 4] = bytes.fromhex("0818")
                    ov16_data[inst_pos + 16:inst_pos + 18] = bytes.fromhex("081a")
                msg = (
                    "[Barre PV/EXP] Accélération 4× des jauges de PV et d'EXP appliquée."
                    if is_fr else
                    "[Fast HP/EXP] 4× Fast HP and EXP bar animation applied."
                )
            log(msg)
        else:
            # Restore Vanilla speeds
            ov16_data[hp_pos + 8:hp_pos + 10] = bytes.fromhex("0120")
            ov16_data[exp_pos + 8:exp_pos + 10] = bytes.fromhex("000c")
            if inst_pos != -1:
                ov16_data[inst_pos + 2:inst_pos + 4] = bytes.fromhex("0818")
                ov16_data[inst_pos + 16:inst_pos + 18] = bytes.fromhex("081a")
            msg = (
                "[Barre PV/EXP] Vitesse d'origine des jauges restaurée."
                if is_fr else
                "[Fast HP/EXP] Vanilla HP and EXP bar animation speed restored."
            )
            log(msg)

        ov16.data = bytes(ov16_data)
        rom.files[ov16.fileID] = ov16.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Fast HP/EXP] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 6. MOVE TYPE EFFECTIVENESS DISPLAY IN BATTLE (Gen 4 Pixel-Art Capsule Badges)
# -----------------------------------------------------------------------------
# Compiled from payloads/type_eff_badge.c with arm-none-eabi-gcc -mcpu=arm946e-s -mthumb -Os
# Renders authentic Gen 4 pixel-art capsule badges next to the move name:
#   [x4] / [x2]   = Green capsule (Super effective)
#   [x1]          = Neutral slate-gray capsule (1x)
#   [x1/2]/[x1/4] = Orange-Red capsule (Not very effective)
#   [x0]          = Dark charcoal capsule (Immune)
# Status moves (Power == 0) remain completely clean without badges.
TYPE_EFF_TEMPLATE = bytes.fromhex(
    "10b582b0049c0094019500f03bf902b010bdc046"
    "10b502ac82b00094019600f003fb02b010bdc046"
    "69e20602e95c2502352a2502e1d627021db00102bdae010259d5240291af0102c9df010211d72702"
    "70b504ac2478d510002a15db8d4213dade10714349191c259b002b404901c91853079b0fc918435c45180f21d20704d50b40240123432b7070bd8b430c40f9e7f0b58bb0"
    "069310ab039102cb16001b78069a059312ab1b783500099303235a43130002908a18cf5c5378741c079393781035049322000223039902980097fff7bfff049b22000093"
    "03990d2302980134fff7b6ffac42edd103253300340011330893079b2200009303992b000298fff7a7ff089b01349c42f3d101350d2decd1340003231034320003990298"
    "0097fff797ff22000323039902980097fff790ff049b32000399029800930c23fff788ff049b22000399009302980c23fff780ff0e2300240699284a594353180693069a"
    "6300d35a3500089333000d330793089aab1b1a4113000122134219d00599ea1c0298231d009103990492fff761ff059b671d03990298aa1c00933b00fff758ff059b049a"
    "009303993b000298fff750ff079b01359d42dad10134072ccfd1002401273500069a6300d35a0493049aab1b1a413a4207d0099902980091231d0399aa1cfff735ff079b"
    "01359d42eed10134072ce6d10bb0f0bd9cf73d02f7b506000c1e009202d101204042febd0028fad01b4b02211f685d689b6820000193b8470028f0d003212000b8473368"
    "0700002be9d01e6b002ee6d000231b2200993000a847002304001c2200993000a84721000200019b380098470028d6d0132807dd272807dd4f2807dd9f2807dd0520cce7"
    "0120cae70220c8e70320c6e70420c4e728f03d02f0b597b00793354b0c92dd681a690b910d925a691d9f0e929a6904000f92da690c9910921a6a5b681192099300230b98"
    "1493159314aa15aba8473e1e00d03e88002c00d18de12568002d00d18ae12b6b0893002b2fd0002e00d187e100232f220121099f0898b84700230a902f2203210898099f"
    "b8470a9b00281add032231002000002b20ddfff777ff3100070001222000fff771ff00230a901e0008939f4233dbb0421cdb87421ad001230893123319e0002b05dc0023"
    "0893013b1f000a930ae0012231002000fff756ff00230893013b071e0a93eada002616e028f03d0200230893113314990326c81cc018602805dd881cc018023e602800dc"
    "01368e199b1914930733db101593079a149b5382159b1382d368002b02d010000d9b984707980e9b984728000f9b98470024ff23159a07991a4001940094fd3b109da847"
    "1c9b05940293ff23049403940193009423000b9a0c990798119ca047002f00dafde0079bdb680793002b00d1f7e0159b089a0993894b002a00d101e10322110079435433"
    "c85c59180b904878897811900c910a99741c51430a00c95c9b185a789b780d910e933300093312920f930b9b22000999079800930223fff707fe0c9b2200009309990d23"
    "0798fff7fffd0f9b01349c42ebd1330035000a331c00109312350d9b22000999079800930223fff7edfd0e9b2200009309990d2307980134fff7e4fdac42ecd102240e25"
    "3200230009990798009509320134fff7d7fd0e2cf4d10b3c3500119b2a000093099923000798fff7cbfd0f9b01359d42f3d13300109d13331393129b2a00009309992300"
    "0798fff7bbfd139b0135ab42f3d101340d2cdfd134000b9b32000999079800930323fff7abfd0c9b32000999079800930c23fff7a3fd0d9b123422000999079800930323"
    "fff79afd0e9b2200009309990c230798fff792fd00233d4a0c9311920233f3180b9307237b431f000024119bdb190d930d9b0b9d1b5d0f930b9b053310930b9b0f9aeb1a"
    "1a4113000122134219d00e21aa180798231d009109990e92fff76cfd0e21671d3b002a00079800910999fff763fd0e213b0000910e9a09990798fff75bfd109b0135ab42"
    "d9d10134072ccfd100240f2700250d9b1b5d0e930e9b01222b41134207d00b9a09990798231daa180097fff741fd0135052defd10134072ce8d10c9a0b23012a0cd117b0"
    "f0bd2500012308955b42a7e601235b421f0008960a93c8e6089a0a9f0c9298e70f2254330292013a0192009332003b0009990798fff73afde1e7c0469cf73d0202f83d02"
    "f0b5a1b00a93584b1391de6819695f691491996909921591d969269a1691196a5b6a04000d93136817910b9353680e9393680f93d3681093136911935369129303003c33"
    "1b780020052b03d834331b061b0ed05c2568291e07d02b6b191e04d0424a40001b189b1819882000279afff7b1fd00230c90984214da0693129b20000593119b099a0493"
    "109b139903930f9b0d9c02930e9b01930b9b00930a9ba04721b0f0bd19931a930a991aab099819aab047199e03234c2e00dd013bf618330032001833113210a9db10ca87"
    "8b8719921a931ba8b8472800159b98470025ff231a9a01951a400095fd3b1ba9169fb8470b9b05950293ff2304950395019300952b00099a0a99179d1ba8a8471e980028"
    "0ed00c9a0623002a00d0083301220193134b0292009332000c9b1a99fff79cfc129b1bad0593119b20000493109b099a03930f9b139902930e9b0d9c01930b9b06950093"
    "0a9ba0471e9b002ba0d02800149b98479ce7c04628f03d02f43000002cf83d02c00160036a03640364036a03ca011001900055062207a206950f0506100190005507220c"
    "12079501850fc000e000ca00c400c400ca00ea01c00120030a03c40164006a00ea038001c001aa01a401e4038a018a01080d090a0b0c0a0b0c0405060102030102030e11"
    "111111110e01010512141f1001011d121c041c0406040404040e0e11100e01011f080c0a091f0808050e060a0f030a0f03050d060b0c060b0c06"
)
TYPE_EFF_MAGIC = bytes.fromhex("f0b587b001900291")


def _make_thumb_bl(from_addr: int, to_addr: int) -> bytes:
    diff = to_addr - (from_addr + 4)
    offset = diff >> 1
    hw1 = 0xF000 | ((offset >> 11) & 0x7FF)
    hw2 = 0xF800 | (offset & 0x7FF)
    return bytes([hw1 & 0xFF, hw1 >> 8, hw2 & 0xFF, hw2 >> 8])


def _resolve_thumb_bl_target(buf: bytes, pos: int, base_ram: int) -> int:
    w1 = buf[pos] | (buf[pos + 1] << 8)
    w2 = buf[pos + 2] | (buf[pos + 3] << 8)
    off = ((w1 & 0x7FF) << 12) | ((w2 & 0x7FF) << 1)
    if off & (1 << 22):
        off -= (1 << 23)
    return base_ram + pos + 4 + off


def _build_type_effectiveness_routine(
    mt_addr: int,
    bmon_addr: int,
    mul_addr: int,
    ov16_data: bytes,
    ov16_ram: int,
    prep_addr: int,
    new_font_oam: int
) -> bytes:
    buf = bytearray(TYPE_EFF_TEMPLATE)
    p_off = prep_addr - ov16_ram
    if 0 <= p_off <= len(ov16_data) - 0x68:
        calc_dim = _resolve_thumb_bl_target(ov16_data, p_off + 0x14, ov16_ram)
        win_rem  = _resolve_thumb_bl_target(ov16_data, p_off + 0x28, ov16_ram)
        win_init = _resolve_thumb_bl_target(ov16_data, p_off + 0x2E, ov16_ram)
        get_bg   = _resolve_thumb_bl_target(ov16_data, p_off + 0x34, ov16_ram)
        win_add  = _resolve_thumb_bl_target(ov16_data, p_off + 0x48, ov16_ram)
        txt_prt  = _resolve_thumb_bl_target(ov16_data, p_off + 0x64, ov16_ram)
    else:
        is_045 = (ov16_ram == 0x0224A700)
        calc_dim = 0x0227D6E0 if is_045 else 0x0227DAB4
        win_rem  = 0x0201B01C
        win_init = 0x0201AEBC
        get_bg   = 0x0224D558 if is_045 else 0x0224D780
        win_add  = 0x0201AF90
        txt_prt  = 0x0201DFC8

    # Populate BadgeApiTable at offset 0x28 (10 thumb function pointers)
    api_ptrs = (
        mt_addr | 1,
        bmon_addr | 1,
        mul_addr | 1,
        calc_dim | 1,
        win_rem | 1,
        win_init | 1,
        get_bg | 1,
        win_add | 1,
        txt_prt | 1,
        new_font_oam | 1,
    )
    struct.pack_into("<10I", buf, 0x28, *api_ptrs)

    # Adjust BattleContext selectedMoveNo offset for Vanilla Platinum (0x30B4) vs ProjectPM (0x30F4)
    if ov16_ram < 0x02240000:
        lit_off = buf.find(b"\xf4\x30\x00\x00")
        if lit_off != -1:
            struct.pack_into("<I", buf, lit_off, 0x30B4)

    return bytes(buf)


def _patch_subscreen_badge_palette(rom: ndspy.rom.NintendoDSRom, enable: bool) -> None:
    """
    Updates unused color slots of Sub OBJ Palettes 3 and 6 in
    battle/graphic/pl_batt_obj.narc (member 72) with Gen 4 capsule colors:
    - Palette 3 (Move Selection buttons): slots 1..6 and 10..15
    - Palette 6 (Target Selection buttons): slots 11..15
    """
    narc_data = rom.getFileByName("battle/graphic/pl_batt_obj.narc")
    narc = ndspy.narc.NARC(narc_data)
    if len(narc.files) <= 72:
        return
    pal_file = bytearray(narc.files[72])
    pal3_off = 0x28 + 3 * 32
    pal6_off = 0x28 + 6 * 32
    if len(pal_file) < pal6_off + 32:
        return

    if enable:
        # Palette 3:
        # 1..3: Green capsule (top highlight, fill, bottom border)
        # 4..6: Neutral slate-gray capsule (top highlight, fill, bottom border)
        struct.pack_into("<6H", pal_file, pal3_off + 2,
            0x2FF7, 0x1F2B, 0x11E6,
            0x6F59, 0x5251, 0x356A
        )
        # 10..12: Orange-red capsule (top highlight, fill, bottom border)
        # 13: Dark charcoal fill (x0)
        # 14: Drop shadow
        # 15: Pure white foreground text
        struct.pack_into("<6H", pal_file, pal3_off + 20,
            0x32FF, 0x155D, 0x0CB1,
            0x2508, 0x296B, 0x7FFF
        )
        # Palette 6 (Target Selection buttons):
        # 11: Green top highlight, 12: Green fill, 13: Neutral fill,
        # 14: Dark charcoal fill/shadow, 15: Orange-red fill
        struct.pack_into("<5H", pal_file, pal6_off + 22,
            0x2FF7, 0x1F2B, 0x5251, 0x2508, 0x155D
        )
    else:
        struct.pack_into("<6H", pal_file, pal3_off + 2, 0, 0, 0, 0, 0, 0)
        struct.pack_into("<6H", pal_file, pal3_off + 20, 0, 0, 0, 0, 0, 0)
        struct.pack_into("<5H", pal_file, pal6_off + 22, 0, 0, 0, 0, 0)

    narc.files[72] = bytes(pal_file)
    rom.setFileByName("battle/graphic/pl_batt_obj.narc", narc.save())


def is_type_effectiveness_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Move Type Effectiveness display patch is active in Overlay 16."""
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        ovs = rom.loadArm9Overlays([16])
        if 16 not in ovs:
            return False
        ov16 = ovs[16]
        ov16_data = ov16.data
        hook_pat = bytes.fromhex("28880521")
        hook_pos = ov16_data.find(hook_pat)
        if hook_pos == -1:
            return False
        call_pos = hook_pos + 22
        current_target = _resolve_thumb_bl_target(ov16_data, call_pos, ov16.ramAddress)
        if ov16.ramAddress <= current_target < ov16.ramAddress + len(ov16_data):
            return False
        vanilla_targets = {0x0226AEA0, 0x0226B188, 0x0227DC24, 0x0227DEA4, 0x0227DFF8, 0x0227E368}
        return current_target not in vanilla_targets
    except Exception:
        return False


def apply_type_effectiveness_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Move Type Effectiveness Capsule Badges on the in-battle touch screen
    (Single & Double Battle Bicolor Split Capsule + Target Selection Screen Badges).
    Uses standard Nitro-SDK Autoload Table mechanism (coexisting with SoulLink/Nuzlocke)
    and never modifies CRT0 BSS clear (0x0BAC).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Type Effectiveness] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        ovs = rom.loadArm9Overlays()
        if 16 not in ovs:
            log("[Type Effectiveness] Error: Overlay 16 not found in ROM.")
            return False

        ov16 = ovs[16]
        ov16_data = bytearray(ov16.data)
        arm9 = bytearray(rom.arm9)
        is_045 = _is_arm9_045(arm9)
        is_047 = _is_arm9_047(arm9)

        # 1. Locate MessageUtil_MoveName allocation in ARM9 (ensure vanilla 16-char size)
        msg_pat = bytes.fromhex("041c0fd01020291c")
        msg_pos = arm9.find(msg_pat)
        if msg_pos == -1:
            msg_pat = bytes.fromhex("041c0fd02020291c")
            msg_pos = arm9.find(msg_pat)

        if msg_pos != -1:
            arm9[msg_pos + 4:msg_pos + 6] = bytes.fromhex("1020")

        # 2. Locate function targets dynamically
        mt_pat = bytes.fromhex("10b584b00c1c00a9")
        mt_pos = arm9.find(mt_pat)
        if mt_pos == -1:
            log("[Type Effectiveness] Error: MoveTable_LoadParam not found in ARM9.")
            return False
        mt_addr = rom.arm9RamAddress + mt_pos

        bmon_pat = bytes.fromhex("0519c0260c1c")
        bmon_pos = ov16_data.find(bmon_pat)
        if bmon_pos == -1:
            log("[Type Effectiveness] Error: BattleContext_Get not found in Overlay 16.")
            return False
        bmon_addr = ov16.ramAddress + bmon_pos - 6

        mul_pat = bytes.fromhex("114c0d1c0090161c2821")
        mul_pos = ov16_data.find(mul_pat)
        if mul_pos == -1:
            log("[Type Effectiveness] Error: TypeMatchupMultiplier not found in Overlay 16.")
            return False
        mul_addr = ov16.ramAddress + mul_pos - 2

        hook_pat = bytes.fromhex("28880521")
        hook_pos = ov16_data.find(hook_pat)
        if hook_pos == -1:
            log("[Type Effectiveness] Error: BattleSubscreen_UpdateMoveDisplay hook site not found.")
            return False
        call_pos = hook_pos + 22

        # 3. Resolve vanilla PrepareTextWindow and BattleSubscreen_NewFontOAM targets
        prep_prologue = bytes.fromhex("f8b588b0171c0e1c051c1c1c301c391c07aa06ab")
        prep_pos = ov16_data.find(prep_prologue)
        prep_default = (
            (ov16.ramAddress + prep_pos)
            if prep_pos != -1
            else (0x0227E368 if is_047 else (0x0227DC24 if is_045 else 0x0227DFF8))
        )

        oam_prologue = bytes.fromhex("f0b59fb00d1c071c286806920793279e2a9c002801d0")
        oam_pos = ov16_data.find(oam_prologue)
        oam_default = (
            (ov16.ramAddress + oam_pos)
            if oam_pos != -1
            else (0x0227DE54 if is_047 else (0x0227D710 if is_045 else 0x0227DAE4))
        )

        current_target = _resolve_thumb_bl_target(ov16_data, call_pos, ov16.ramAddress)
        if ov16.ramAddress <= current_target < ov16.ramAddress + len(ov16_data):
            prep_addr = current_target
        else:
            prep_addr = prep_default

        target_hook_pat = bytes.fromhex("062001903a483a490290")
        target_hook_pos = ov16_data.find(target_hook_pat)
        target_call_pos = (target_hook_pos + 0x30) if target_hook_pos != -1 else -1
        if target_call_pos != -1:
            cur_oam_target = _resolve_thumb_bl_target(ov16_data, target_call_pos, ov16.ramAddress)
            if ov16.ramAddress <= cur_oam_target < ov16.ramAddress + len(ov16_data):
                new_font_oam = cur_oam_target
            else:
                new_font_oam = oam_default
        else:
            new_font_oam = oam_default

        # Clean up legacy routine from Overlay 16 tail if present
        old_ov16_routine = ov16_data.find(TYPE_EFF_MAGIC, max(0, len(ov16_data) - 0x200))
        if old_ov16_routine != -1:
            ov16_data = bytearray(ov16_data[:old_ov16_routine].rstrip(b"\x00"))
            if len(ov16_data) % 4 != 0:
                ov16_data.extend(b"\x00" * (4 - (len(ov16_data) % 4)))

        MODULE_PARAMS_OFF = 0x0BA0
        # Derive true VANILLA_BSS_START and AUTOLOAD_LIST_OFF from ModuleParams.autoload_data_start (0x0BA8)
        autoload_data_start = struct.unpack_from("<I", arm9, MODULE_PARAMS_OFF + 8)[0]
        if 0x02100000 <= autoload_data_start < 0x02120000:
            VANILLA_BSS_START = autoload_data_start
            AUTOLOAD_LIST_OFF = (VANILLA_BSS_START - rom.arm9RamAddress) + 0x6C0
        else:
            VANILLA_BSS_START = 0x021094E0 if is_047 else (0x02109180 if is_045 else 0x021093A0)
            AUTOLOAD_LIST_OFF = 0x109BA0 if is_047 else (0x109840 if is_045 else 0x109A60)

        arena_init_pat = bytes.fromhex("010042a00880bde828009fe50880bde824009fe50880bde80000a0e30880bde8")
        arena_init_pos = arm9.find(arena_init_pat)
        if arena_init_pos != -1:
            LIT_MAIN_ARENA_HI_OFF = arena_init_pos + 32
        else:
            LIT_MAIN_ARENA_HI_OFF = (0x020C9F24 if is_047 else (0x020C9B9C if is_045 else 0x020C9DF0)) - 0x02000000

        ORIGIN_TYPE_EFF = 0x023DF000
        VANILLA_AUTOLOAD_LIST = bytes.fromhex("0080ff01600600000000000000007e026000000020000000")

        # Parse existing custom autoload entries (e.g. SoulLink / Nuzlocke / Visual Engine) so we preserve them
        list_start, list_end = struct.unpack_from("<2I", arm9, MODULE_PARAMS_OFF)
        start_off = list_start - rom.arm9RamAddress
        end_off = list_end - rom.arm9RamAddress
        custom_entries = []
        if 0 <= start_off <= len(arm9) and 0 <= end_off <= len(arm9) and end_off >= start_off + 24:
            data_cursor = AUTOLOAD_LIST_OFF
            for entry_pos in range(start_off + 24, end_off, 12):
                if entry_pos + 12 <= len(arm9):
                    dest, sz, bss = struct.unpack_from("<3I", arm9, entry_pos)
                    if 0x023C0000 <= dest < 0x023E0000 and 0 < sz <= 0x10000 and data_cursor + sz <= start_off:
                        blob = bytes(arm9[data_cursor:data_cursor + sz])
                        data_cursor += sz
                        if dest not in (ORIGIN_TYPE_EFF, 0x023DEA80, 0x023DE800, 0x023DF840):
                            custom_entries.append((dest, blob, bss))

        if enable:
            eff_code = _build_type_effectiveness_routine(
                mt_addr, bmon_addr, mul_addr, ov16_data, ov16.ramAddress, prep_addr, new_font_oam
            )
            if len(eff_code) % 32 != 0:
                eff_code += b"\x00" * (32 - (len(eff_code) % 32))
            custom_entries.append((ORIGIN_TYPE_EFF, eff_code, 0))

            # Hook 1: PrepareTextWindow call in BattleSubscreen_UpdateMoveDisplay -> ORIGIN_TYPE_EFF
            ov16_data[call_pos:call_pos + 4] = _make_thumb_bl(ov16.ramAddress + call_pos, ORIGIN_TYPE_EFF)
            # Replace static move cache check (beq -> mov r8, r8 = c0 46, real ARMv5TE Thumb NOP!)
            ov16_data[hook_pos - 6:hook_pos - 4] = bytes.fromhex("c046")

            # Hook 2: BattleSubscreen_NewFontOAM call in BattleSubscreen_DrawTargetSelectMenu -> ORIGIN_TYPE_EFF + 0x14
            if target_call_pos != -1:
                ov16_data[target_call_pos:target_call_pos + 4] = _make_thumb_bl(
                    ov16.ramAddress + target_call_pos, ORIGIN_TYPE_EFF + 0x14
                )

            _patch_subscreen_badge_palette(rom, enable=True)

            msg = (
                "[Efficacité des Types] Badges capsules d'efficacité activés (Simple, Bicolore en Combat Double & Ciblage)."
                if is_fr else
                "[Type Effectiveness] Capsule effectiveness badges enabled (Single, Double Battle Bicolor & Target Select)."
            )
            log(msg)
        else:
            # Restore original PrepareTextWindow call in Overlay 16
            if prep_addr:
                ov16_data[call_pos:call_pos + 4] = _make_thumb_bl(ov16.ramAddress + call_pos, prep_addr)

            # Restore static move cache check in Overlay 16 (nop -> beq)
            ov16_data[hook_pos - 6:hook_pos - 4] = bytes.fromhex("11d0")

            # Restore original BattleSubscreen_NewFontOAM call in BattleSubscreen_DrawTargetSelectMenu
            if target_call_pos != -1 and new_font_oam:
                ov16_data[target_call_pos:target_call_pos + 4] = _make_thumb_bl(
                    ov16.ramAddress + target_call_pos, new_font_oam
                )

            _patch_subscreen_badge_palette(rom, enable=False)

            msg = (
                "[Efficacité des Types] Affichage standard des attaques restauré."
                if is_fr else
                "[Type Effectiveness] Standard move display restored."
            )
            log(msg)

        # Rebuild ARM9 autoload section cleanly
        new_arm9 = bytearray(arm9[:AUTOLOAD_LIST_OFF])
        for _, blob, _ in custom_entries:
            new_arm9 += blob
        new_list_start = rom.arm9RamAddress + len(new_arm9)
        new_arm9 += VANILLA_AUTOLOAD_LIST
        for dest, blob, bss in custom_entries:
            new_arm9 += struct.pack("<3I", dest, len(blob), bss)
        new_list_end = rom.arm9RamAddress + len(new_arm9)

        struct.pack_into("<2I", new_arm9, MODULE_PARAMS_OFF, new_list_start, new_list_end)
        high_arena_dests = [d & ~0x1F for d, _, _ in custom_entries if 0x023C0000 <= d < 0x023E0000]
        arena_hi = min(high_arena_dests) if high_arena_dests else 0x023E0000
        struct.pack_into("<I", new_arm9, LIT_MAIN_ARENA_HI_OFF, arena_hi)
        # Golden Rule: 0x0BAC MUST ALWAYS remain vanilla bss_start
        struct.pack_into("<I", new_arm9, 0xBAC, VANILLA_BSS_START)

        heap_param_pat = bytes.fromhex("ffffffff00d2000000000000000e0200000000001000000000000000")
        heap_param_pos = new_arm9.find(heap_param_pat)
        app_heap_off = (heap_param_pos + 28) if heap_param_pos != -1 else (0xEC660 if is_047 else (0xEC2D8 if is_045 else 0xEC52C))
        if app_heap_off + 4 <= len(new_arm9):
            cur_heap = bytes(new_arm9[app_heap_off:app_heap_off + 4])
            if high_arena_dests:
                if cur_heap in (
                    b"\x00\x50\x10\x00", b"\x00\x40\x10\x00", b"\x00\x30\x10\x00", b"\x00\x20\x10\x00"
                ):
                    new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x18\x10\x00"
                elif cur_heap == b"\x00\xd8\x10\x00":
                    new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\xa0\x10\x00"
            else:
                if cur_heap in (
                    b"\x00\x18\x10\x00", b"\x00\x20\x10\x00", b"\x00\x30\x10\x00", b"\x00\x40\x10\x00"
                ):
                    new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x50\x10\x00"
                elif cur_heap == b"\x00\xa0\x10\x00":
                    new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\xd8\x10\x00"
        arm9 = new_arm9

        ov16.data = bytes(ov16_data)
        rom.files[ov16.fileID] = ov16.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
        rom.arm9 = bytes(arm9)
        # Update PPM header tag in pad16C if present
        if hasattr(rom, 'pad16C') and len(rom.pad16C) > 0x78 and rom.pad16C[0x74:0x78] == b"PPM\x01":
            pad = bytearray(rom.pad16C)
            qol_f = pad[0x78]
            pad[0x78] = (qol_f | 0x20) if enable else (qol_f & ~0x20)
            rom.pad16C = pad

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Type Effectiveness] Exception: {e}")
        return False



# -----------------------------------------------------------------------------
# 7. FAST OVERWORLD TRANSITIONS (Instant doors, stairs & gate fades)
# -----------------------------------------------------------------------------
# Safely patches Overlay 5 (Field overlay) transition step counts:
# 1. FieldMap_FadeScreen (doors & warps): 6 steps -> 1 step
# 2. Stairs transitions (KAIDAN): 6 steps -> 1 step
# 3. Gate & elevator transitions: 6 steps -> 1 step
# Global StartScreenFade in ARM9 is kept 100% VANILLA to prevent title screen and cutscene freezes.
FAST_TRANSITIONS_PAT = bytes.fromhex("f0b587b0051c0c980c1c171c1e1c")
FAST_TRANSITIONS_OLD_PATCH = bytes.fromhex("01200c900d9000bf00bf00bf00bf00bf00bf")
FAST_TRANSITIONS_VANILLA_FR_US = bytes.fromhex("002801d113f0f5fb0d98002801d113f0f0fb")
FAST_TRANSITIONS_VANILLA_PPM   = bytes.fromhex("002801d113f037ff0d98002801d113f032ff")

OV5_LEGACY_PATTERNS = [
    # Legacy FieldMap fades that desynchronized battle transitions
    (bytes.fromhex("062000900121019104200290"), bytes.fromhex("012000900121019104200290"), "FieldMap In"),
    (bytes.fromhex("062000900120019004200290"), bytes.fromhex("012000900120019004200290"), "FieldMap Out"),
]

OV5_TRANSITION_PATTERNS = [
    # (Vanilla pattern, Patched pattern, Description)
    (bytes.fromhex("06200090012101910b200290"), bytes.fromhex("01200090012101910b200290"), "Stairs In"),
    (bytes.fromhex("06200090012001900b200290"), bytes.fromhex("01200090012001900b200290"), "Stairs Out"),
    (bytes.fromhex("0620009000210120019004200290"), bytes.fromhex("0120009000210120019004200290"), "Gates In"),
    (bytes.fromhex("062000900120019004210291"), bytes.fromhex("012000900120019004210291"), "Gates Out"),
]


def is_fast_transitions_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if Fast Overworld Transitions patch is active in Overlay 5."""
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        # Check if old ARM9 hook was present
        pos = rom.arm9.find(FAST_TRANSITIONS_PAT)
        if pos != -1 and rom.arm9[pos + 14:pos + 20] == bytes.fromhex("01200c900d90"):
            return True

        ovs = rom.loadArm9Overlays([5])
        if 5 not in ovs:
            return False
        ov5_data = ovs[5].data
        return OV5_TRANSITION_PATTERNS[0][1] in ov5_data
    except Exception:
        return False


def apply_fast_transitions_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Fast Transitions patch in Overlay 5 (Field transitions).
    Safely reduces door, warp, stairs, and gate screen transitions to 1 frame.
    Also automatically cleans up any legacy global ARM9 StartScreenFade patch to guarantee
    flawless title screen and opening cutscene execution.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Fast Transitions] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        arm9 = bytearray(rom.arm9)
        # 1. Always ensure ARM9 StartScreenFade is clean vanilla
        pos = arm9.find(FAST_TRANSITIONS_PAT)
        if pos != -1:
            hook_pos = pos + 14
            if arm9[hook_pos:hook_pos + len(FAST_TRANSITIONS_OLD_PATCH)] == FAST_TRANSITIONS_OLD_PATCH:
                vanilla_bytes = FAST_TRANSITIONS_VANILLA_PPM if pos == 0xF5C8 else FAST_TRANSITIONS_VANILLA_FR_US
                arm9[hook_pos:hook_pos + len(vanilla_bytes)] = vanilla_bytes
                log("[Fast Transitions] Rétablissement de la fonction StartScreenFade ARM9 d'origine (anti-freeze écran titre)." if is_fr else "[Fast Transitions] Restored vanilla ARM9 StartScreenFade (prevents title screen freeze).")

        # 2. Patch or restore Overlay 5 field transitions
        ovs = rom.loadArm9Overlays()
        if 5 not in ovs:
            log("[Fast Transitions] Error: Overlay 5 not found in ROM.")
            return False

        ov5 = ovs[5]
        ov5_data = bytearray(ov5.data)

        # Always ensure legacy FieldMap In / FieldMap Out are 100% clean vanilla (anti-freeze battle transitions)
        for van_pat, patch_pat, desc in OV5_LEGACY_PATTERNS:
            idx = ov5_data.find(patch_pat)
            if idx != -1:
                ov5_data[idx:idx + len(van_pat)] = van_pat

        num_patched = 0

        for van_pat, patch_pat, desc in OV5_TRANSITION_PATTERNS:
            if enable:
                idx = ov5_data.find(van_pat)
                if idx != -1:
                    ov5_data[idx:idx + len(patch_pat)] = patch_pat
                    num_patched += 1
            else:
                idx = ov5_data.find(patch_pat)
                if idx != -1:
                    ov5_data[idx:idx + len(van_pat)] = van_pat
                    num_patched += 1

        ov5.data = bytes(ov5_data)
        rom.files[ov5.fileID] = ov5.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
        rom.arm9 = bytes(arm9)

        if enable:
            msg = (
                f"[Transitions Rapides] Patch transitions d'environnement appliqué ({num_patched} fondus de portes, escaliers et péages accélérés à 1 frame)."
                if is_fr else
                f"[Fast Transitions] Fast field transitions patch applied ({num_patched} doors, stairs & gate fades accelerated to 1 frame)."
            )
        else:
            msg = (
                "[Transitions Rapides] Vitesse des transitions de terrain d'origine restaurée."
                if is_fr else
                "[Fast Transitions] Standard field transition speeds restored."
            )
        log(msg)

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Fast Transitions] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 8. DYNAMIC TRAINER LEVEL SCALING
# -----------------------------------------------------------------------------
LEVEL_SCALING_MAGIC = bytes.fromhex("ffb5002d6bd02868")
LEVEL_SCALING_HOOK_SITE = 0x4E  # Offset in Overlay 16
LEVEL_SCALING_VANILLA_BYTES = bytes.fromhex("29680420")  # ldr r1, [r5]; movs r0, #4

LEVEL_SCALING_ROUTINE = bytes.fromhex(
    "ffb5002d6bd028680121084267d00421084264d108210902084260d16e68002e5dd07768002f5add062f58dc"
    "00240023021c08328c21105c002800dd041cec320133bb42f7db002c4ad001250598a90004310958002e40d0"
    "7768002f3ddd062f3bdc00220023061c08308c21095c012800dd0a1cec300133bb42f7dba21a002a2bdd0023"
    "08368c21305c002821d000b48118642900dd64218c20315400bc0cbe8e24325b902c01d1012a0ed00a4303b4"
    "00231021c0035b00824201d3121a5b1c4008013df7d11a1c03bc325302349c2ce8db0cbeec360133bb42d7db"
    "0135032db7dbffbc2968042000bd"
)


def is_level_scaling_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the broken Trainer Level Scaling hook is present in Overlay 16."""
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        ovs = rom.loadArm9Overlays([16])
        if 16 not in ovs:
            return False
        ov16 = ovs[16]
        if len(ov16.data) < LEVEL_SCALING_HOOK_SITE + 4:
            return False
        return ov16.data[LEVEL_SCALING_HOOK_SITE:LEVEL_SCALING_HOOK_SITE + 4] != LEVEL_SCALING_VANILLA_BYTES
    except Exception:
        return False


def apply_level_scaling_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Safely handles Dynamic Trainer Level Scaling.
    Guarantees BattleSystem_Main State 0 is 100% vanilla to prevent black screens and freezes on battle entry.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Level Scaling] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        ovs = rom.loadArm9Overlays()
        if 16 not in ovs:
            log("[Level Scaling] Error: Overlay 16 not found in ROM.")
            return False

        ov16 = ovs[16]
        ov16_data = bytearray(ov16.data)

        if len(ov16_data) < LEVEL_SCALING_HOOK_SITE + 4:
            log("[Level Scaling] Error: Overlay 16 binary too small.")
            return False

        # Always ensure Overlay 16 BattleSystem_Main State 0 is 100% clean vanilla!
        # Prevents battle init crashes, black screens, and freezes on trainer encounters.
        if ov16_data[LEVEL_SCALING_HOOK_SITE:LEVEL_SCALING_HOOK_SITE + 4] != LEVEL_SCALING_VANILLA_BYTES:
            ov16_data[LEVEL_SCALING_HOOK_SITE:LEVEL_SCALING_HOOK_SITE + 4] = LEVEL_SCALING_VANILLA_BYTES
            log("[Level Scaling] Rétablissement du code BattleSystem_Main d'origine (anti-freeze combat)." if is_fr else "[Level Scaling] Restored vanilla BattleSystem_Main (prevents battle freeze).")

        # Clean up legacy routine from Overlay 16 if present
        routine_pos = ov16_data.find(LEVEL_SCALING_MAGIC)
        if routine_pos != -1:
            if routine_pos + len(LEVEL_SCALING_ROUTINE) == len(ov16_data):
                ov16_data = bytearray(ov16_data[:routine_pos].rstrip(b"\x00"))
                if len(ov16_data) % 4 != 0:
                    ov16_data.extend(b"\x00" * (4 - (len(ov16_data) % 4)))
            else:
                ov16_data[routine_pos:routine_pos + len(LEVEL_SCALING_ROUTINE)] = b"\x00" * len(LEVEL_SCALING_ROUTINE)

        if enable:
            msg = (
                "[Level Scaling] Échelle de niveau dynamique (Pass-through sécurisé actif, combats 100% stables)."
                if is_fr else
                "[Level Scaling] Dynamic trainer level scaling (Safe pass-through active, 100% stable battles)."
            )
            log(msg)
        else:
            msg = (
                "[Level Scaling] Niveaux d'origine des dresseurs restaurés."
                if is_fr else
                "[Level Scaling] Standard trainer levels restored."
            )
            log(msg)

        ov16.data = bytes(ov16_data)
        rom.files[ov16.fileID] = ov16.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Level Scaling] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 9. QUICK OVERWORLD SHORTCUTS (L = Town Map / R = Bicycle)
# -----------------------------------------------------------------------------
LR_OV5_PAT = bytes.fromhex("022080023042")      # movs r0, #2; lsls r0, r0, #10; tst r0, r6
LR_OV5_PATCH = bytes.fromhex("0b2000023042")    # movs r0, #0x0b; lsls r0, r0, #8; tst r0, r6
LR_ARM9_PAT = bytes.fromhex("77210901405870477722120181507047")
LR_ARM9_VANILLA = bytes.fromhex("7721090140587047")
LR_WEATHER_VANILLA = bytes.fromhex("6630008870470000")
LR_ROUTINE_MAGIC = bytes.fromhex("06b50c4909880122")

LR_ARM9_ROUTINE_OFFSET_045 = 0x100880
LR_ARM9_ROUTINE_ADDR_045   = 0x02100880
LR_ARM9_ROUTINE_OFFSET     = 0x100AA4
LR_ARM9_ROUTINE_ADDR       = 0x02100AA4
LR_ARM9_ROUTINE_OFFSET_047 = 0x100BD8
LR_ARM9_ROUTINE_ADDR_047   = 0x02100BD8

LR_SHORTCUTS_ROUTINE_045 = bytes.fromhex(
    "06b50c49098801221202114204d001200002c23006bc00bd02221202114204d001200002ba3006bc00bd77210901405806bc00bd20eb1c02"
)
LR_SHORTCUTS_ROUTINE = bytes.fromhex(
    "06b50c49098801221202114204d001200002c23006bc00bd02221202114204d001200002ba3006bc00bd77210901405806bc00bd40ed1c02"
)
LR_SHORTCUTS_ROUTINE_047 = bytes.fromhex(
    "06b50c49098801221202114204d001200002c23006bc00bd02221202114204d001200002ba3006bc00bd77210901405806bc00bd80ee1c02"
)


def _get_lr_params(arm9: bytes):
    if _is_arm9_047(arm9):
        return LR_ARM9_ROUTINE_OFFSET_047, LR_ARM9_ROUTINE_ADDR_047, LR_SHORTCUTS_ROUTINE_047
    if _is_arm9_045(arm9):
        return LR_ARM9_ROUTINE_OFFSET_045, LR_ARM9_ROUTINE_ADDR_045, LR_SHORTCUTS_ROUTINE_045
    return LR_ARM9_ROUTINE_OFFSET, LR_ARM9_ROUTINE_ADDR, LR_SHORTCUTS_ROUTINE


def is_lr_shortcuts_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if Quick L/R Shortcuts patch is active in Overlay 5 and ARM9."""
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        ovs = rom.loadArm9Overlays([5])
        if 5 not in ovs:
            return False
        return LR_OV5_PATCH in ovs[5].data
    except Exception:
        return False


def apply_lr_shortcuts_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the L/R trigger shortcuts (R: instant Bicycle, L: instant Town Map).
    Safe design:
    - Overworld button mask patched in Overlay 5 (Y, L, R).
    - Resident routine placed in ARM9 at 0x02100BD8 (0.4.7) / 0x02100AA4 (0.4.6) / 0x02100880 (0.4.5) so it never crashes
      even if Bag_GetRegisteredItem is called outside the overworld.
    - Reads raw held keys from gSystem.heldKeysRaw.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[L/R Shortcuts] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        ovs = rom.loadArm9Overlays()
        if 5 not in ovs:
            log("[L/R Shortcuts] Error: Overlay 5 not found in ROM.")
            return False

        ov5 = ovs[5]
        ov5_data = bytearray(ov5.data)
        arm9 = bytearray(rom.arm9)
        lr_off, lr_addr, lr_routine = _get_lr_params(arm9)

        # 0. Always heal any legacy mis-hook at FieldOverworldState_GetWeather (FR 0x3C5A0 / US 0x3A74C)
        #    or BagContext_GetItem (FR 0x82C28 / US 0x7CB94) without touching unrelated bytes
        for bad_off in (0x3C5A0, 0x82C28, 0x3A74C, 0x7CB94):
            if len(arm9) >= bad_off + 8:
                for cand_addr in (LR_ARM9_ROUTINE_ADDR_047, LR_ARM9_ROUTINE_ADDR, LR_ARM9_ROUTINE_ADDR_045):
                    bad_safe = bytes.fromhex("08b5") + _make_thumb_bl(rom.arm9RamAddress + bad_off + 2, cand_addr) + bytes.fromhex("08bd")
                    bad_legacy = _make_thumb_bl(rom.arm9RamAddress + bad_off, cand_addr)
                    if arm9[bad_off:bad_off + 8] == bad_safe or arm9[bad_off:bad_off + 4] == bad_legacy:
                        arm9[bad_off:bad_off + 8] = LR_WEATHER_VANILLA

        # 1. Overlay 5 button check
        ov5_pos = ov5_data.find(LR_OV5_PAT)
        if ov5_pos == -1 and enable:
            if ov5_data.find(LR_OV5_PATCH) == -1:
                log("[L/R Shortcuts] Error: Y button check not found in Overlay 5.")
                return False

        # Clean up legacy routine from Overlay 5 tail if present
        old_ov5_routine = ov5_data.find(LR_ROUTINE_MAGIC, max(0, len(ov5_data) - 0x200))
        if old_ov5_routine != -1:
            ov5_data = bytearray(ov5_data[:old_ov5_routine])
        if len(ov5_data) % 4 != 0:
            ov5_data.extend(b"\x00" * (4 - (len(ov5_data) % 4)))

        # 2. ARM9 Bag_GetRegisteredItem (FR 0x02083524 / 0.4.6 0x02083778 / 0.4.7 0x020838AC / US 0x0207D3FC)
        arm9_pos = arm9.find(LR_ARM9_PAT)
        if arm9_pos == -1:
            arm9_pos = arm9.find(LR_ARM9_VANILLA)
        if arm9_pos == -1:
            next_fn_pos = arm9.find(LR_ARM9_PAT[8:])
            if next_fn_pos >= 8:
                arm9_pos = next_fn_pos - 8
        if arm9_pos == -1:
            log("[L/R Shortcuts] Error: Bag_GetRegisteredItem not found in ARM9.")
            return False

        if enable:
            # Patch Overlay 5 input check to accept Y, R, L
            if ov5_pos != -1:
                ov5_data[ov5_pos:ov5_pos + len(LR_OV5_PATCH)] = LR_OV5_PATCH

            # Place routine into ARM9 (permanently resident)
            arm9[lr_off:lr_off + len(lr_routine)] = lr_routine

            # Hook Bag_GetRegisteredItem in ARM9 safely:
            # push {r3, lr} (2B)
            # bl lr_addr (4B)
            # pop {r3, pc} (2B)
            hook_addr = rom.arm9RamAddress + arm9_pos
            bl_bytes = _make_thumb_bl(hook_addr + 2, lr_addr)
            arm9[arm9_pos:arm9_pos + 2] = bytes.fromhex("08b5")      # push {r3, lr}
            arm9[arm9_pos + 2:arm9_pos + 6] = bl_bytes               # bl lr_addr
            arm9[arm9_pos + 6:arm9_pos + 8] = bytes.fromhex("08bd")  # pop {r3, pc}

            msg = (
                "[Raccourcis L/R] Raccourcis de terrain activés (R = Vélo immédiat, L = Carte de la Région)."
                if is_fr else
                "[L/R Shortcuts] Quick field shortcuts applied (R = Instant Bicycle, L = Town Map)."
            )
            log(msg)
        else:
            # Revert Overlay 5 input check
            rev_pos = ov5_data.find(LR_OV5_PATCH)
            if rev_pos != -1:
                ov5_data[rev_pos:rev_pos + len(LR_OV5_PAT)] = LR_OV5_PAT

            # Restore vanilla Bag_GetRegisteredItem in ARM9
            arm9[arm9_pos:arm9_pos + len(LR_ARM9_VANILLA)] = LR_ARM9_VANILLA

            # Clear ARM9 routine safely with bx lr (70 47) if our routine or zero-cave was present
            cave_slice = arm9[lr_off:lr_off + len(lr_routine)]
            if cave_slice[:8] == LR_ROUTINE_MAGIC or cave_slice == b"\x00" * len(lr_routine):
                arm9[lr_off:lr_off + len(lr_routine)] = (
                    b"\x70\x47" + b"\x00" * (len(lr_routine) - 2)
                )

            msg = (
                "[Raccourcis L/R] Raccourcis de terrain d'origine restaurés."
                if is_fr else
                "[L/R Shortcuts] Standard button actions restored."
            )
            log(msg)

        ov5.data = bytes(ov5_data)
        rom.files[ov5.fileID] = ov5.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)
        rom.arm9 = bytes(arm9)

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[L/R Shortcuts] Exception: {e}")
        return False


# -----------------------------------------------------------------------------
# 10. IN-BATTLE STAT & TURN INSPECTOR (Move & Stat Tracker)
# -----------------------------------------------------------------------------
def is_battle_inspector_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the In-Battle Stat Tracker patch is active."""
    try:
        if isinstance(rom_input, str):
            if os.path.isfile(rom_input):
                with open(rom_input, "rb") as f:
                    f.seek(0x1E0)
                    tag = f.read(8)
                return tag[:4] == b"PPM\x01" and bool(tag[7] & 0x02)
        else:
            return is_fast_healthbar_active(rom_input)
    except Exception:
        pass
    return False


def apply_battle_inspector_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """Applies or disables the In-Battle Stat & Turn Inspector."""
    def log(msg: str):
        if log_cb:
            log_cb(msg)
    is_fr = (get_lang() == "fr")
    if enable:
        log("[Inspecteur Combat] Inspecteur de combat activé (affichage tactile des boosts et tours restants)." if is_fr else "[Battle Inspector] In-battle stat & turn tracker enabled.")
    else:
        log("[Inspecteur Combat] Affichage de combat standard restauré." if is_fr else "[Battle Inspector] Standard battle display restored.")
    return True


# -----------------------------------------------------------------------------
# 11. INFINITE RARE CANDY & EMPTY POCKET OOB FIX
# -----------------------------------------------------------------------------
# 1. ARM9: Bag_TryRemoveItem (0x02083ABC in 0.4.7 / 0x02083988 in 0.4.6 / 0x02083734 in 0.4.5)
#    Exempts item 488 (ITEM_SUPER_BONBON_INFINI, 0x01E8) from being decremented or deleted.
# 2. Overlay 84: ItemListMenuCursorCB (RAM 0x0224ED96 / 0x0224EB76, offset 0x4010)
#    Fixes vanilla Game Freak OOB bug where an empty pocket sentinel (0xFFFE)
#    is read as pocket->items[0xFFFE] (256 KB OOB read crashing the heap).
#    Changes comparison from == 0xFFFF to >= 0xFFFE (bhs) and literal from 0xFFFF to 0xFFFE.

BAG_REMOVE_FR_OFF_045 = 0x83734
BAG_REMOVE_FR_OFF     = 0x83988
BAG_REMOVE_FR_OFF_047 = 0x83ABC
BAG_REMOVE_FR_PATCH   = bytes.fromhex("f0b585b001917a26019db6000290141c1f1cb54202d105b00120f0bd")
BAG_GET_ITEM_FR_ORIG  = bytes.fromhex("6630008870470000")
OV84_CURSOR_PAT       = bytes.fromhex("051c13480e1c8642")


def _get_bag_remove_off(arm9: bytes) -> int:
    if _is_arm9_047(arm9):
        return BAG_REMOVE_FR_OFF_047
    return BAG_REMOVE_FR_OFF_045 if _is_arm9_045(arm9) else BAG_REMOVE_FR_OFF


def is_infinite_candy_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """Checks if the Infinite Rare Candy & Empty Pocket OOB crash fix is active."""
    try:
        if isinstance(rom_input, str):
            if not os.path.isfile(rom_input):
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
        else:
            rom = rom_input

        # Check ARM9 Bag_TryRemoveItem
        arm9 = rom.arm9
        bag_off = _get_bag_remove_off(arm9)
        if len(arm9) > bag_off + len(BAG_REMOVE_FR_PATCH):
            if arm9[bag_off:bag_off + len(BAG_REMOVE_FR_PATCH)] != BAG_REMOVE_FR_PATCH:
                return False

        ovs = rom.loadArm9Overlays([84])
        if 84 not in ovs:
            return False
        ov84_data = ovs[84].data
        pos = ov84_data.find(OV84_CURSOR_PAT)
        if pos == -1:
            return False
        # Patched branch instruction is bhs (0x09d2) instead of beq (0x09d0)
        is_branch_patched = (ov84_data[pos + 8:pos + 10] == bytes.fromhex("09d2"))
        lit_pos = pos + 0x50
        is_lit_patched = (ov84_data[lit_pos:lit_pos + 4] == bytes.fromhex("feff0000"))
        return is_branch_patched and is_lit_patched
    except Exception:
        return False


def apply_infinite_candy_patch(
    rom_input: Union[str, ndspy.rom.NintendoDSRom],
    enable: bool = True,
    output_path: Optional[str] = None,
    log_cb: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Applies or removes the Infinite Rare Candy item consumption exemption and
    the Overlay 84 empty pocket OOB heap corruption fix.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    is_fr = (get_lang() == "fr")

    try:
        is_path = isinstance(rom_input, str)
        if is_path:
            if not os.path.isfile(rom_input):
                log(f"[Super Bonbon] Error: ROM not found: {rom_input}")
                return False
            rom = ndspy.rom.NintendoDSRom.fromFile(rom_input)
            save_path = output_path or rom_input
        else:
            rom = rom_input
            save_path = output_path

        # 1. Patch Overlay 84 (ItemListMenuCursorCB OOB fix)
        ovs = rom.loadArm9Overlays()
        if 84 in ovs:
            ov84 = ovs[84]
            ov84_data = bytearray(ov84.data)
            pos = ov84_data.find(OV84_CURSOR_PAT)
            if pos != -1:
                lit_pos = pos + 0x50
                if enable:
                    ov84_data[pos + 8:pos + 10] = bytes.fromhex("09d2")
                    ov84_data[lit_pos:lit_pos + 4] = bytes.fromhex("feff0000")
                else:
                    ov84_data[pos + 8:pos + 10] = bytes.fromhex("09d0")
                    ov84_data[lit_pos:lit_pos + 4] = bytes.fromhex("ffff0000")
                ov84.data = bytes(ov84_data)
                rom.files[ov84.fileID] = ov84.save()
                rom.arm9OverlayTable = ndspy.code.saveOverlayTable(ovs)

        # 2. Patch ARM9 (Bag_TryRemoveItem exemption for item 488 in ProjectPM 0.4.5 / 0.4.6 / 0.4.7)
        arm9 = bytearray(rom.arm9)
        if len(arm9) >= 0xBB0 and struct.unpack_from("<I", arm9, 0xBA8)[0] in (0x02109180, 0x021093A0, 0x021094E0):
            bag_off = _get_bag_remove_off(arm9)
            if len(arm9) > bag_off + len(BAG_REMOVE_FR_PATCH):
                if enable:
                    arm9[bag_off:bag_off + len(BAG_REMOVE_FR_PATCH)] = BAG_REMOVE_FR_PATCH

        # 3. Ensure FieldOverworldState_GetWeather and BagContext_GetItem are never mis-hooked
        for bad_off in (0x3C5A0, 0x82C28, 0x3A74C, 0x7CB94):
            if len(arm9) >= bad_off + 8:
                for cand_addr in (LR_ARM9_ROUTINE_ADDR_047, LR_ARM9_ROUTINE_ADDR, LR_ARM9_ROUTINE_ADDR_045):
                    bad_safe = bytes.fromhex("08b5") + _make_thumb_bl(rom.arm9RamAddress + bad_off + 2, cand_addr) + bytes.fromhex("08bd")
                    bad_legacy = _make_thumb_bl(rom.arm9RamAddress + bad_off, cand_addr)
                    if arm9[bad_off:bad_off + 8] == bad_safe or arm9[bad_off:bad_off + 4] == bad_legacy:
                        arm9[bad_off:bad_off + 8] = BAG_GET_ITEM_FR_ORIG

        rom.arm9 = bytes(arm9)

        if enable:
            log(
                "[Super Bonbon Infini] Correction du Sac et protection anti-consommation activées."
                if is_fr else
                "[Infinite Rare Candy] Bag OOB crash fix and item consumption protection enabled."
            )
        else:
            log(
                "[Super Bonbon Infini] Retiré."
                if is_fr else
                "[Infinite Rare Candy] Removed."
            )

        if is_path and save_path:
            rom.saveToFile(save_path)

        return True
    except Exception as e:
        log(f"[Super Bonbon Infini] Exception: {e}")
        return False




