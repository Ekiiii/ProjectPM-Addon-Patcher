# -*- coding: utf-8 -*-
r"""
visual_patcher.py
Next-Gen 60 FPS Dynamic Visual Engine (Compiled in C via arm-none-eabi-gcc)
& Visual+ Battle Backgrounds for Pokémon Platinum / ProjectPM 0.4.5:

1. 3D Orbital Camera with Ease-In / Ease-Out & Left/Right Yaw Rotation:
   - Sub-pixel Q8 spring-damper with acceleration limiting (`SmoothEaseStep` in C)
     for true parabolic Ease-In and exponential Ease-Out.
   - Smooth Left/Right orbital yaw (`±6°`, `cam->angle.y` + incremental 3D eye orbit
     on `cam->position`), tall grass pitch (`-48.87° -> -53.27°`), and running/cycling
     zoom-out (`0x1D8000 -> +0x22000`).
   - Full 3x3 3D rotation matrix $R_y(\text{yaw}) \cdot R_x(\Delta \text{pitch})$ on 2D
     billboards (`Hook5_BillboardMtx`) so sprites face the orbiting camera cleanly.

2. Zero-Flicker Continuous Solar/Lunar Lighting & Moving Cloud Shadows:
   - Dirty-flag state caching (`lastActiveIdx`, `lastSolarTq8`, `lastInGrass`,
     `lastWeatherMode`, `lightDirty`) so 5-bit BGR555 `ModelAttributes` are only updated
     when lighting state actually changes — 100% zero quantization flicker.
   - Per-prop (`Hook4`) and per-billboard (`Hook6`) material color oscillations removed.
   - Breeze leaf/petal particles (`Hook8`) completely removed (`ov5_draw3d_off` restored).
   - Smooth 7-bit hardware depth fog & drifting cloud shadows (`REG_G3X_FOG_TABLE`).

3. Hardware Specular Bloom & 5 Advanced Weather Shaders in C:
   - 128-byte quadratic specular bloom LUT loaded into `REG_G3_SHININESS` (`0x040004C0`)
     with `enableSpecularReflectShininessTable = TRUE` and `prmMatColor1` bit 15 enabled.
   - 5 C shader modes (`SHADER_CLEAR_CLOUDS`, `SHADER_DAWN_MIST`, `SHADER_GOLDEN_GLOW`,
     `SHADER_NIGHT_AURORA`, `SHADER_WET_STORM`, plus `SHADER_NATIVE_WEATHER` passthrough).

4. Real-Time 60 FPS VRAM Water Palette Shimmer (`Hook7_WaterShimmer`):
   - Smooth time-of-day and weather-reactive water palette shimmer with `DC_FlushRange`.
"""
import os
import shutil
import struct
import subprocess
import tempfile
from typing import Optional, Callable, Union, Dict, Tuple, List
import ndspy.rom
import ndspy.narc
import ndspy.code

ORIGIN_VISUAL = 0x023DE000
LEGACY_ORIGIN_VISUAL = 0x023DF840
LEGACY_ORIGINS_VISUAL = (0x023DE000, 0x023DE800, 0x023DEA80, 0x023DF840)
VISUAL_MAGIC = 0x354E4547  # "GEN5"

# Precompiled C symbol table (identical layout for FR/PPM 0.4.6, 0.4.5 and US profiles)
DEFAULT_C_LABELS: Dict[str, int] = {
    "gVisualState":        0x023DE000,
    "Hook3_AreaLightFree": 0x023DE0A0,
    "Hook7_WaterShimmer":  0x023DE0A8,
    "Hook1_FieldUpdate":   0x023DE0BC,
    "Hook2_AreaLightApply": 0x023DE6B0,
    "Hook5_BillboardMtx":  0x023DE844,
}

# Preset forced weather byte at gVisualState + 0x16
PRESET_WEATHER_BYTE: Dict[str, int] = {
    "dynamic": 0x00,
    "day":     0x80 | 0,  # SHADER_CLEAR_CLOUDS
    "dawn":    0x80 | 1,  # SHADER_DAWN_MIST
    "sunset":  0x80 | 2,  # SHADER_GOLDEN_GLOW
    "night":   0x80 | 3,  # SHADER_NIGHT_AURORA
    "rain":    0x80 | 4,  # SHADER_WET_STORM
}

# 17 entries of CameraParam (24 bytes each: dist, rx, ry, rz, pad, proj, fovY, near, far)
VANILLA_CAMERA_ENTRIES = [
    (0x29AEC1, -0x29FE, 0, 0, 0, 0, 0x05C1, 0x096000, 0x384000),  # 0: Default outdoor
    (0x29AEC1, -0x309E, 0, 0, 0, 0, 0x05C1, 0x096000, 0x384000),  # 1: Special
    (0x20374C, -0x26DE, 0, 0, 0, 0, 0x0770, 0x096000, 0x384000),  # 2: Outdoor variant
    (0x29AEC1, -0x29FE, 0, 0, 0, 0, 0x05C1, 0x096000, 0x384000),  # 3: Outdoor normal
    (0x61B89B, -0x239E, 0, 0, 0, 1, 0x0281, 0x096000, 0x6C7000),  # 4: Interior Orthographic
    (0x13C805, -0x29FD, 0, 0, 0, 0, 0x0C01, 0x00A000, 0x3F0000),  # 5: Close-up
    (0x3628DF, -0x33FD, 0, 0, 0, 0, 0x0481, 0x073000, 0x4C5000),  # 6: Wide
    (0x29AEC1, -0x29FD, 0, 0, 0, 0, 0x05C1, 0x099000, 0x407000),  # 7: Outdoor extended
    (0x296EC1, -0x321D, 0, 0, 0, 0, 0x0701, 0x096000, 0x40A000),  # 8: Gym / special
    (0x1659AC, -0x1CDD, 0, 0, 0, 0, 0x0AB0, 0x096000, 0x384000),  # 9: Low-angle cutscene
    (0x4B25B1, -0x2B3D, 0, 0, 0, 0, 0x0341, 0x096000, 0x6D2000),  # 10: Far view
    (0x2A3D55, -0x291D, 0, 0, 0, 0, 0x05C1, 0x0E6000, 0x467000),  # 11: Outdoor lake/route
    (0x23E93F, -0x2CFD, 0, 0, 0, 0, 0x06C1, 0x096000, 0x384000),  # 12: Special
    (0x20374C, -0x21FD, 0, 0, 0, 0, 0x0770, 0x096000, 0x384000),  # 13: Outdoor coastal
    (0x0A9765, -0x37BC, 0, 0, 0, 0, 0x1501, 0x00A000, 0x3F0000),  # 14: Steep overhead
    (0x28DEDF, -0x26DE, 0, 0, 0, 0, 0x05F0, 0x096000, 0x384000),  # 15: Outdoor town/route
    (0x14AEC0, -0x29FE, 0, 0, 0, 0, 0x0B01, 0x096000, 0x384000),  # 16: Special indoor/cutscene
]

OUTDOOR_CAMERA_INDICES = {0, 2, 3, 7, 11, 13, 15}
BALANCED_OUTDOOR_ENTRY = (0x1D8000, -0x22C0, 0, 0, 0, 0, 0x0830, 0x096000, 0x384000)


def _pack_camera_entries(entries: List[Tuple[int, ...]]) -> bytes:
    buf = bytearray()
    for e in entries:
        buf.extend(struct.pack("<IhhhhHHII", *e))
    return bytes(buf)


CAM_VANILLA_FULL = _pack_camera_entries(VANILLA_CAMERA_ENTRIES)
CAM_DYNAMIC_FULL = _pack_camera_entries([
    BALANCED_OUTDOOR_ENTRY if i in OUTDOOR_CAMERA_INDICES else e
    for i, e in enumerate(VANILLA_CAMERA_ENTRIES)
])
CAM_LEGACY_VISUAL_ENTRY = struct.pack(
    "<IhhhhHHII", 0x1659AC, -0x1CDD, 0, 0, 0, 0, 0x0AB0, 0x096000, 0x384000
)
# Exported for backward compatibility with rom_detector
CAM_VANILLA_BYTES = CAM_VANILLA_FULL[:376]
CAM_VISUAL_BYTES = CAM_DYNAMIC_FULL[:376]


def build_arealight_file0(preset: str = "dynamic") -> bytes:
    """
    Builds the 15 time-of-day brackets for File 0 (Outdoors) of data/arealight.narc.
    Includes Light 0 (Sun/Moon), Light 1 (Environmental Bounce/Fill), Light 2 (Building Windows),
    Light 3 (Sprite Highlight), and balanced Diffuse / Ambient / Specular / Emission registers.
    """
    entries = [
        # 0: 00:00 (Deep Midnight)
        (0,
         (1, 13, 15, 22,  1850, -3400, -1300),
         (1,  7,  5,  2,     0, -3200, -2400),
         (1, 28, 18,  2,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 13, 15), (10, 10, 12), (15, 16, 19), (8, 8, 11)),
        # 1: 00:00 - 04:00 (Late Night)
        (7200,
         (1, 13, 15, 22,  1850, -3400, -1300),
         (1,  6,  4,  2,     0, -3200, -2400),
         (1, 22, 14,  2,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 13, 15), (10, 10, 12), (15, 16, 19), (8, 8, 11)),
        # 2: 04:00 - 04:30 (Pre-Dawn Indigo)
        (8100,
         (1, 15, 15, 22,   700, -3500, -1200),
         (1,  5,  5,  6,     0, -3300, -2200),
         (1, 14, 10,  6,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 14), (11, 11, 12), (14, 14, 17), (9, 9, 12)),
        # 3: 04:30 - 05:00 (Early Dawn Rose-Violet)
        (9000,
         (1, 19, 16, 22,  -600, -3500, -1200),
         (1,  6,  5,  6,     0, -3400, -2000),
         (1,  0,  2, 10,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 13), (10, 10, 11), (14, 14, 16), (11, 11, 13)),
        # 4: 05:00 - 08:00 (Sunrise Rose-Gold)
        (14400,
         (1, 23, 20, 21, -1700, -3450, -1250),
         (1,  6,  6,  5,     0, -3400, -2000),
         (1,  0,  0, 10,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (10, 10, 11), (15, 15, 16), (11, 11, 13)),
        # 5: 08:00 - 11:30 (Crisp Morning Sunlight)
        (20700,
         (1, 23, 23, 22, -1800, -3420, -1250),
         (1,  5,  6,  6,     0, -3500, -1800),
         (1,  1,  1, 11,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (10, 11, 11), (15, 15, 16), (11, 11, 12)),
        # 6: 11:30 - 12:00 (High Morning)
        (21600,
         (1, 24, 24, 22, -1850, -3400, -1300),
         (1,  5,  6,  6,     0, -3500, -1800),
         (1,  2,  2, 12,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (11, 11, 12), (16, 16, 16), (11, 11, 11)),
        # 7: 12:00 - 15:00 (Radiant Midday Zenith)
        (27000,
         (1, 25, 25, 22, -1850, -3400, -1300),
         (1,  5,  6,  5,     0, -3500, -1800),
         (1,  2,  2, 13,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (11, 12, 12), (16, 16, 15), (11, 11, 11)),
        # 8: 15:00 - 15:30 (Early Afternoon)
        (27900,
         (1, 24, 23, 20, -1100, -3480, -1250),
         (1,  6,  6,  5,     0, -3500, -1800),
         (1,  4,  4, 10,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (11, 12, 12), (16, 16, 15), (11, 11, 11)),
        # 9: 15:30 - 17:00 (Warm Late Afternoon)
        (30600,
         (1, 24, 21, 18,  -700, -3500, -1200),
         (1,  7,  6,  4,     0, -3400, -2000),
         (1,  3,  4, 10,     0,     0,  4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (12, 12, 12), (11, 11, 12), (16, 15, 14), (11, 10, 10)),
        # 10: 17:00 - 18:00 (Early Golden Hour)
        (32400,
         (1, 25, 19, 14,   750, -3480, -1250),
         (1,  9,  6,  2,     0, -3300, -2200),
         (1, 20, 13,  3,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 12, 12), (11, 11, 11), (17, 15, 12), (10,  9,  9)),
        # 11: 18:00 - 18:30 (Deep Golden Hour Sunset)
        (33300,
         (1, 26, 17, 11,  1850, -3400, -1300),
         (1, 10,  6,  2,     0, -3200, -2400),
         (1, 27, 17,  3,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 12, 11), (11, 10, 11), (18, 14, 11), (10,  8,  8)),
        # 12: 18:30 - 19:00 (Crimson-Amber Dusk)
        (34200,
         (1, 23, 15, 13,  1850, -3400, -1300),
         (1,  9,  6,  2,     0, -3200, -2400),
         (1, 27, 17,  3,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 12, 12), (11, 10, 11), (16, 13, 13), ( 9,  8,  8)),
        # 13: 19:00 - 20:00 (Violet-Blue Twilight)
        (36000,
         (1, 15, 15, 20,  1850, -3400, -1300),
         (1,  8,  5,  2,     0, -3200, -2400),
         (1, 28, 18,  2,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 13, 14), (10, 10, 12), (15, 15, 18), ( 8,  8, 10)),
        # 14: 20:00 - 24:00 (Starlit Night)
        (43200,
         (1, 13, 15, 22,  1850, -3400, -1300),
         (1,  7,  5,  2,     0, -3200, -2400),
         (1, 28, 18,  2,     0,     0, -4096),
         (1, 31, 31, 31,     0,     0,  4096),
         (13, 13, 15), (10, 10, 12), (15, 16, 19), ( 8,  8, 11)),
    ]

    if preset == "sunset":
        forced = entries[11][1:]
        entries = [(e[0], *forced) for e in entries]
    elif preset == "dawn":
        forced = entries[4][1:]
        entries = [(e[0], *forced) for e in entries]
    elif preset == "night":
        forced = entries[14][1:]
        entries = [(e[0], *forced) for e in entries]
    elif preset == "day":
        forced = entries[7][1:]
        entries = [(e[0], *forced) for e in entries]
    elif preset == "rain":
        rain_tpl = (
            (1, 16, 18, 23, -1500, -3450, -1250),
            (1,  5,  7,  9,     0, -3400, -2000),
            (1, 24, 16,  4,     0,     0, -4096),
            (1, 29, 30, 31,     0,     0,  4096),
            (11, 12, 14), (10, 11, 13), (18, 19, 22), (9, 10, 12),
        )
        entries = [(e[0], *rain_tpl) for e in entries]

    lines = []
    for end_t, l0, l1, l2, l3, diff, amb, spec, emi in entries:
        lines.append(f"{end_t},")
        for l in (l0, l1, l2, l3):
            lines.append(f"{l[0]},{l[1]},{l[2]},{l[3]},{l[4]},{l[5]},{l[6]},")
        for c in (diff, amb, spec, emi):
            lines.append(f"{c[0]},{c[1]},{c[2]},")
        lines.append("")
    lines.append("EOF")
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


VANILLA_AREALIGHT_ENTRIES = [
    (0,     (1,11,11,16,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,22,18, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,14,16), (10,10,10), (14,14,16), ( 8, 8,11)),
    (7200,  (1,11,11,16,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,12, 9, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,14,16), (10,10,10), (14,14,16), ( 8, 8,11)),
    (8100,  (1,14,13,18, 999,-3972,  82),  (0,0,0,0,0,0,0), (1, 0, 0,10,0,0,4096), (1,31,31,31,0,0,4096), (11,11,15), (12,12,12), (11,11,15), ( 9, 9,15)),
    (9000,  (1,18,14,20,-999,-3972,  82),  (0,0,0,0,0,0,0), (1, 0, 0,10,0,0,4096), (1,31,31,31,0,0,4096), (11,11,15), ( 9, 9, 9), (11,11,15), (11,11,15)),
    (14400, (1,22,19,20,-2043,-3548,110),  (0,0,0,0,0,0,0), (1, 0, 0,10,0,0,4096), (1,31,31,31,0,0,4096), (11,11,15), ( 9, 9, 9), (11,11,15), (11,11,15)),
    (20700, (1,22,22,22,-2043,-3548,110),  (0,0,0,0,0,0,0), (1, 0, 0,10,0,0,4096), (1,31,31,31,0,0,4096), (11,11,13), ( 9,10,10), (13,13,13), (12,12,13)),
    (21600, (1,23,23,23,-2043,-3548,110),  (0,0,0,0,0,0,0), (1, 2, 2,12,0,0,4096), (1,31,31,31,0,0,4096), (11,11,12), (10,11,11), (14,14,14), (12,12,12)),
    (27000, (1,24,24,22,-2043,-3548,110),  (0,0,0,0,0,0,0), (1, 2, 2,12,0,0,4096), (1,31,31,31,0,0,4096), (12,12,12), (10,12,12), (14,14,14), (12,12,12)),
    (27900, (1,23,23,20,-999,-3972,  82),  (0,0,0,0,0,0,0), (1, 4, 4,10,0,0,4096), (1,31,31,31,0,0,4096), (12,12,12), (10,12,12), (14,14,14), (12,12,12)),
    (30600, (1,23,21,17,-999,-3972,  82),  (0,0,0,0,0,0,0), (1, 3, 4,10,0,0,4096), (1,31,31,31,0,0,4096), (12,12,12), (10,12,12), (14,14,14), (12,12,12)),
    (32400, (1,24,18,12, 999,-3972,  82),  (0,0,0,0,0,0,0), (1,12, 8, 2,0,0,4096), (1,31,31,31,0,0,4096), (13,12,12), (11,10,10), (14,14,14), (11, 9, 9)),
    (33300, (1,25,16, 9,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,22,18, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,12,12), (12,10,10), (14,14,14), (11, 6, 6)),
    (34200, (1,22,14,11,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,22,18, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,13,13), (11,10,10), (14,14,14), (10, 6, 6)),
    (36000, (1,14,14,18,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,22,18, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,14,15), (10,10,10), (14,14,15), ( 9, 7, 9)),
    (43200, (1,11,11,16,1897,-3600,-466),  (0,0,0,0,0,0,0), (1,22,18, 0,0,0,4096), (1,31,31,31,0,0,4096), (14,14,16), (10,10,10), (14,14,16), ( 8, 8,11)),
]


def build_vanilla_arealight_file0() -> bytes:
    lines = []
    for end_t, l0, l1, l2, l3, diff, amb, spec, emi in VANILLA_AREALIGHT_ENTRIES:
        lines.append(f"{end_t},")
        for l in (l0, l1, l2, l3):
            lines.append(f"{l[0]},{l[1]},{l[2]},{l[3]},{l[4]},{l[5]},{l[6]},")
        for c in (diff, amb, spec, emi):
            lines.append(f"{c[0]},{c[1]},{c[2]},")
        lines.append("")
    lines.append("EOF")
    return ("\r\n".join(lines) + "\r\n").encode("ascii")


def _make_thumb_bl(from_addr: int, to_addr: int, is_blx: bool = False) -> bytes:
    base_pc = ((from_addr + 4) & ~3) if is_blx else (from_addr + 4)
    diff = to_addr - base_pc
    offset = diff >> 1
    hw1 = 0xF000 | ((offset >> 11) & 0x7FF)
    hw2 = (0xE800 if is_blx else 0xF800) | (offset & 0x7FF)
    return struct.pack("<HH", hw1, hw2)


def _get_rom_profile(ov5_ram: int) -> Dict[str, int]:
    """
    Returns the exact ARM9 and Overlay 5 address profile based on Overlay 5 RAM base.
    - 0x021E0600: ProjectPM 0.4.7 (both FR and US)
    - 0x021E04A0: ProjectPM 0.4.6 (both FR and US)
    - 0x021E0280: ProjectPM 0.4.5 (both FR and US) & Vanilla Platinum France
    - 0x021D0D80: Vanilla Platinum USA (Rev 1)
    """
    if ov5_ram == 0x021E0600:
        return {
            "profile_id": 47,
            "is_ppm_or_fr": 1,
            "ov5_base": 0x021E0600,
            "autoload_list_off": 0x109BA0,
            "module_params_off": 0x0BA0,
            "bss_start": 0x021094E0,
            "lit_arena_hi_off": 0x0C9F24,
            "get_sec_midnight": 0x02013DF4,
            "vram_transfer_req": 0x0201E4D0,
            "cam_calc_pos": 0x020208FC,
            "mtx_identity33": 0x020C247C,
            "g3d_renderer_draw": 0x0201D270,
            "mdl_set_amb_all": 0x020BA534,
            "mdl_set_emi_all": 0x020BA5B4,
            "g3x_set_fog": 0x020C6C28,
            "g3x_set_fog_table": 0x020C6CF8,
            "dc_flush_range": 0x020C9C0C,
            "glb_mat_col0": 0x021D53A0,
            "glb_mat_col1": 0x021D53A4,
            # ARM9 Hook offsets
            "bb_mtx_hook_off": 0x21692,
            "bb_draw_hook1_off": 0x21706,
            "bb_draw_hook2_off": 0x21732,
            # Overlay 5 targets & Hook offsets
            "arealight_update": 0x021E69CC,
            "arealight_apply_tpl": 0x021E6A28,
            "draw3d_part_fn": 0x021E152C,
            "prop_get_mat_shp": 0x021E6EC4,
            "set_base_trans": 0x020B5EC8,
            "ov5_field_update_off": 0x0073E,
            "ov5_draw3d_off": 0x00AC4,
            "ov5_al_free_assert_off": 0x063B0,
            "ov5_al_free_assert_bytes": b"\x01\xd1\x3c\xf6\x61\xfd\x20\x68",
            "ov5_al_free_tail_off": 0x063C8,
            "ov5_al_apply_off": 0x064CC,
            "ov5_al_apply_bl_off": 0x064D8,
            "ov5_texanim_off": 0x06FEA,
            "ov5_legacy_prop_off": 0x134D0,
            "ov5_prop_off": 0x134DA,
            "ov5_edgemark_off": 0x24D20,
            "ov5_aa_mask_off": 0x24D8C,
            "ov5_cam_table_off": 0x2E4CC,
        }
    elif ov5_ram == 0x021E04A0:
        return {
            "profile_id": 46,
            "is_ppm_or_fr": 1,
            "ov5_base": 0x021E04A0,
            "autoload_list_off": 0x109A60,
            "module_params_off": 0x0BA0,
            "bss_start": 0x021093A0,
            "lit_arena_hi_off": 0x0C9DF0,
            "get_sec_midnight": 0x02013DD4,
            "vram_transfer_req": 0x0201E4B0,
            "cam_calc_pos": 0x020208D0,
            "mtx_identity33": 0x020C2348,
            "g3d_renderer_draw": 0x0201D250,
            "mdl_set_amb_all": 0x020BA400,
            "mdl_set_emi_all": 0x020BA480,
            "g3x_set_fog": 0x020C6AF4,
            "g3x_set_fog_table": 0x020C6BC4,
            "dc_flush_range": 0x020C9AD8,
            "glb_mat_col0": 0x021D5240,
            "glb_mat_col1": 0x021D5244,
            # ARM9 Hook offsets
            "bb_mtx_hook_off": 0x21666,
            "bb_draw_hook1_off": 0x216DA,
            "bb_draw_hook2_off": 0x21706,
            # Overlay 5 targets & Hook offsets
            "arealight_update": 0x021E686C,
            "arealight_apply_tpl": 0x021E68C8,
            "draw3d_part_fn": 0x021E13CC,
            "prop_get_mat_shp": 0x021E6D64,
            "set_base_trans": 0x020B5D94,
            "ov5_field_update_off": 0x0073E,
            "ov5_draw3d_off": 0x00AC4,
            "ov5_al_free_assert_off": 0x063B0,
            "ov5_al_free_assert_bytes": b"\x01\xd1\x3c\xf6\xfb\xfd\x20\x68",
            "ov5_al_free_tail_off": 0x063C8,
            "ov5_al_apply_off": 0x064CC,
            "ov5_al_apply_bl_off": 0x064D8,
            "ov5_texanim_off": 0x06FEA,
            "ov5_legacy_prop_off": 0x134D0,
            "ov5_prop_off": 0x134DA,
            "ov5_edgemark_off": 0x24D20,
            "ov5_aa_mask_off": 0x24D8C,
            "ov5_cam_table_off": 0x2E4CC,
        }
    elif ov5_ram == 0x021E0280:
        return {
            "profile_id": 45,
            "is_ppm_or_fr": 1,
            "ov5_base": 0x021E0280,
            "autoload_list_off": 0x109840,
            "module_params_off": 0x0BA0,
            "bss_start": 0x02109180,
            "lit_arena_hi_off": 0x0C9B9C,
            "get_sec_midnight": 0x02013DD4,
            "vram_transfer_req": 0x0201E4B0,
            "cam_calc_pos": 0x020208D0,
            "mtx_identity33": 0x020C20F4,
            "g3d_renderer_draw": 0x0201D250,
            "mdl_set_amb_all": 0x020BA1AC,
            "mdl_set_emi_all": 0x020BA22C,
            "g3x_set_fog": 0x020C68A0,
            "g3x_set_fog_table": 0x020C6970,
            "dc_flush_range": 0x020C9884,
            "glb_mat_col0": 0x021D5020,
            "glb_mat_col1": 0x021D5024,
            # ARM9 Hook offsets
            "bb_mtx_hook_off": 0x21666,
            "bb_draw_hook1_off": 0x216DA,
            "bb_draw_hook2_off": 0x21706,
            # Overlay 5 targets & Hook offsets
            "arealight_update": 0x021E664C,
            "arealight_apply_tpl": 0x021E66A8,
            "draw3d_part_fn": 0x021E11AC,
            "prop_get_mat_shp": 0x021E6B44,
            "set_base_trans": 0x020B5B40,
            "ov5_field_update_off": 0x0073E,
            "ov5_draw3d_off": 0x00AC4,
            "ov5_al_free_assert_off": 0x063B0,
            "ov5_al_free_assert_bytes": b"\x01\xd1\x3c\xf6\x0b\xff\x20\x68",
            "ov5_al_free_tail_off": 0x063C8,
            "ov5_al_apply_off": 0x064CC,
            "ov5_al_apply_bl_off": 0x064D8,
            "ov5_texanim_off": 0x06FEA,
            "ov5_legacy_prop_off": 0x134D0,
            "ov5_prop_off": 0x134DA,
            "ov5_edgemark_off": 0x24D44,
            "ov5_aa_mask_off": 0x24DB0,
            "ov5_cam_table_off": 0x2E4F0,
        }
    else:
        return {
            "profile_id": 0,
            "is_ppm_or_fr": 0,
            "ov5_base": 0x021D0D80,
            "autoload_list_off": 0x1023E0,
            "module_params_off": 0x0BA0,
            "bss_start": 0x02101D20,
            "lit_arena_hi_off": 0x0C2F70,
            "get_sec_midnight": 0x020138C8,
            "vram_transfer_req": 0x0201DC68,
            "cam_calc_pos": 0x02020020,
            "mtx_identity33": 0x020BB4C8,
            "g3d_renderer_draw": 0x0201CA74,
            "mdl_set_amb_all": 0x020B35A4,
            "mdl_set_emi_all": 0x020B3624,
            "g3x_set_fog": 0x020BFC74,
            "g3x_set_fog_table": 0x020BFD44,
            "dc_flush_range": 0x020C2C58,
            "glb_mat_col0": 0x021C5B20,
            "glb_mat_col1": 0x021C5B24,
            # ARM9 Hook offsets
            "bb_mtx_hook_off": 0x20DB6,
            "bb_draw_hook1_off": -1,
            "bb_draw_hook2_off": 0x20E12,
            # Overlay 5 targets & Hook offsets
            "arealight_update": 0x021D5298,
            "arealight_apply_tpl": 0x021D52F4,
            "draw3d_part_fn": 0x021D1B18,
            "prop_get_mat_shp": 0x021D5790,
            "set_base_trans": 0x020AEF38,
            "ov5_field_update_off": 0x005E2,
            "ov5_draw3d_off": 0x00954,
            "ov5_al_free_assert_off": 0x044FC,
            "ov5_al_free_assert_bytes": b"\x01\xd1\x4d\xf6\x79\xfb\x20\x68",
            "ov5_al_free_tail_off": 0x04514,
            "ov5_al_apply_off": 0x04618,
            "ov5_al_apply_bl_off": 0x04624,
            "ov5_texanim_off": 0x050C6,
            "ov5_legacy_prop_off": 0x10AC0,
            "ov5_prop_off": 0x10ACA,
            "ov5_edgemark_off": 0x1EBEC,
            "ov5_aa_mask_off": 0x1EC58,
            "ov5_cam_table_off": 0x27D64,
        }


def _find_arm_toolchain() -> Optional[str]:
    """Locates the directory containing arm-none-eabi-gcc, objcopy, and nm."""
    default_dir = r"C:\Program Files (x86)\Arm GNU Toolchain arm-none-eabi\12.2 mpacbti-rel1\bin"
    if os.path.exists(os.path.join(default_dir, "arm-none-eabi-gcc.exe")):
        return default_dir
    gcc_in_path = shutil.which("arm-none-eabi-gcc")
    if gcc_in_path:
        return os.path.dirname(gcc_in_path)
    return None


def _build_visual_engine_payload(p: Dict[str, int], preset: str = "dynamic") -> Tuple[bytes, Dict[str, int]]:
    """
    Builds or loads the C-compiled `0x023DE000` visual engine payload (`visual_engine.c`)
    and patches `presetForcedWeather` at `+0x16`.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    c_dir = os.path.join(here, "c_visual")
    c_src = os.path.join(c_dir, "visual_engine.c")
    ld_src = os.path.join(c_dir, "visual_linker.ld")
    prof_id = p.get("profile_id", 47)
    if prof_id == 47:
        bin_name = "visual_047.bin"
        flags = ["-DPROFILE_047"]
    elif prof_id == 46:
        bin_name = "visual_fr.bin"
        flags = []
    elif prof_id == 45:
        bin_name = "visual_045.bin"
        flags = ["-DPROFILE_045"]
    else:
        bin_name = "visual_us.bin"
        flags = ["-DPROFILE_US"]
    precompiled_bin = os.path.join(c_dir, bin_name)

    payload_bytes: Optional[bytes] = None
    labels: Dict[str, int] = dict(DEFAULT_C_LABELS)

    toolchain_dir = _find_arm_toolchain()
    if toolchain_dir and os.path.exists(c_src) and os.path.exists(ld_src):
        try:
            ext = ".exe" if os.name == "nt" else ""
            gcc = os.path.join(toolchain_dir, f"arm-none-eabi-gcc{ext}")
            objcopy = os.path.join(toolchain_dir, f"arm-none-eabi-objcopy{ext}")
            nm = os.path.join(toolchain_dir, f"arm-none-eabi-nm{ext}")
            with tempfile.TemporaryDirectory() as tmpdir:
                elf_path = os.path.join(tmpdir, "visual.elf")
                out_bin = os.path.join(tmpdir, "visual.bin")
                cmd = [
                    gcc,
                    "-mcpu=arm946e-s",
                    "-mthumb",
                    "-Os",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-nostdlib",
                    *flags,
                    "-I", c_dir,
                    "-T", ld_src,
                    c_src,
                    "-o", elf_path,
                ]
                subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                subprocess.run([objcopy, "-O", "binary", elf_path, out_bin], check=True)
                nm_out = subprocess.check_output([nm, "-n", elf_path], text=True)
                parsed_labels: Dict[str, int] = {}
                for line in nm_out.splitlines():
                    parts = line.strip().split()
                    if len(parts) == 3:
                        parsed_labels[parts[2]] = int(parts[0], 16)
                with open(out_bin, "rb") as f:
                    payload_bytes = f.read()
                labels.update(parsed_labels)
        except Exception:
            payload_bytes = None

    if payload_bytes is None:
        if os.path.exists(precompiled_bin):
            with open(precompiled_bin, "rb") as f:
                payload_bytes = f.read()
        else:
            raise FileNotFoundError(f"Precompiled visual binary not found: {precompiled_bin}")

    buf = bytearray(payload_bytes)
    buf[0x16] = PRESET_WEATHER_BYTE.get(preset, 0x00)
    while len(buf) % 4 != 0:
        buf.append(0)
    assert len(buf) <= 0x1000, f"Payload size {len(buf)} exceeds 0x1000 arena slice (0x023DE000..0x023DF000)"
    return bytes(buf), labels


def _patch_diagonal_movement(
    arm9_buf: bytearray,
    is_ppm_or_fr: int,
    enable: bool = False,
    labels: Optional[Dict[str, int]] = None,
) -> None:
    """
    Ensures `PlayerAvatar_UpdateMoveState`, `PlayerAvatar_CalcFaceDirectionInternal`,
    `StepMovement_Init`, and `StepMovement_Tick` in ARM9 are 100% restored to original
    vanilla Pokémon Platinum behavior.
    """
    (void_enable := enable, void_labels := labels)
    ums_sig = bytes.fromhex("70b50c1c0021c943051c8c4204d10021")
    face_sig = bytes.fromhex(
        "2021014201d0022070471021084201d0032100e01139081c70470000"
        "4021014201d0002070478021084201d0012100e08139081c70470000"
    )
    step_body_sig = bytes.fromhex("02a9098a0180478044608660281c211c")

    ums_off = arm9_buf.find(ums_sig)
    face_off = arm9_buf.find(face_sig)
    step_body_off = arm9_buf.find(step_body_sig)
    if ums_off == -1 or face_off == -1 or step_body_off < 16:
        return

    calc_off = face_off + 56
    patch_off = calc_off + 0x26
    step_init_off = step_body_off - 16
    step_tick_off = step_init_off + 0x48

    if is_ppm_or_fr:
        vanilla_60 = bytes.fromhex(
            "301cfdf700fb071c301cfdf7c8fb0090301cfdf7c8fb0021c9438f420cd00099"
            "8c4203d1854201d1381cf8bd854201d0281cf8bd201cf8bd281cf8bd"
        )
        vanilla_step_tick_8 = bytes.fromhex("38b5051cfdf72cf8")
    else:
        vanilla_60 = bytes.fromhex(
            "301cfdf790fb071c301cfdf732fc0090301cfdf732fc0021c9438f420cd00099"
            "8c4203d1854201d1381cf8bd854201d0281cf8bd201cf8bd281cf8bd"
        )
        vanilla_step_tick_8 = bytes.fromhex("38b5051cfdf77cf8")

    vanilla_calc_8 = bytes.fromhex("f8b5151c061c281c")
    vanilla_step_init_12 = bytes.fromhex("f8b50c1c0c21051c161c1f1c")

    # Always restore 100% vanilla movement in ARM9
    arm9_buf[ums_off + 0x3A:ums_off + 0x3C] = b"\x0a\xd0"
    arm9_buf[calc_off:calc_off + 8] = vanilla_calc_8
    arm9_buf[patch_off:patch_off + 60] = vanilla_60
    arm9_buf[step_init_off:step_init_off + 12] = vanilla_step_init_12
    arm9_buf[step_tick_off:step_tick_off + 8] = vanilla_step_tick_8


def _patch_fldtanime_narc(rom: ndspy.rom.NintendoDSRom, enable: bool) -> int:
    """
    Adjusts or restores outdoor water/flower texture animation cadence in `data/fldtanime.narc`.
    Returns the number of modified files.
    """
    if "data/fldtanime.narc" not in rom.filenames:
        return 0
    fid = rom.filenames.idOf("data/fldtanime.narc")
    narc = ndspy.narc.NARC(rom.files[fid])
    modified = 0
    for idx, fdata in enumerate(narc.files):
        if len(fdata) != 208:
            continue
        b = bytearray(fdata)
        changed = False
        for entry in range(4):
            base = entry * 52
            if b[base] == 0:
                continue
            for f in range(16):
                off = base + 18 + f * 2
                delay = struct.unpack_from("<H", b, off)[0]
                if enable:
                    if delay == 9:
                        struct.pack_into("<H", b, off, 7)
                        changed = True
                    elif delay == 16:
                        struct.pack_into("<H", b, off, 12)
                        changed = True
                else:
                    if delay == 7:
                        struct.pack_into("<H", b, off, 9)
                        changed = True
                    elif delay == 12:
                        struct.pack_into("<H", b, off, 16)
                        changed = True
        if changed:
            narc.files[idx] = bytes(b)
            modified += 1
    if modified > 0:
        rom.files[fid] = narc.save()
    return modified


VANILLA_AUTOLOAD_LIST = struct.pack("<6I", 0x01FF8000, 0x660, 0, 0x027E0000, 0x60, 0x20)


def is_camera_patch_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """
    Returns True if the Visual+ 3D Camera patch is active in Overlay 5.
    """
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        ov5 = rom.loadArm9Overlays([5]).get(5)
        if ov5 is None:
            return False
        p = _get_rom_profile(ov5.ramAddress)
        cam_off = p["ov5_cam_table_off"]
        if cam_off + 24 <= len(ov5.data):
            entry0 = bytes(ov5.data[cam_off:cam_off + 24])
            if entry0 == CAM_DYNAMIC_FULL[:24] or entry0 == CAM_LEGACY_VISUAL_ENTRY:
                return True
        return False
    except Exception:
        return False


def is_visual_engine_active(rom_input: Union[str, ndspy.rom.NintendoDSRom]) -> bool:
    """
    Returns True if our custom C 60 FPS Dynamic Visual Engine (Clouds, Lighting & Water Shimmer)
    is active in the ARM9 autoload table.
    """
    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_input) if isinstance(rom_input, str) else rom_input
        arm9 = rom.arm9
        for mp_off in (0x0BA0, 0x0B7C):
            if len(arm9) >= mp_off + 8:
                list_start, list_end = struct.unpack_from("<2I", arm9, mp_off)
                start_off = list_start - rom.arm9RamAddress
                end_off = list_end - rom.arm9RamAddress
                if 0 <= start_off <= len(arm9) and 0 <= end_off <= len(arm9) and end_off >= start_off + 24:
                    for entry_pos in range(start_off + 24, end_off, 12):
                        if entry_pos + 12 <= len(arm9):
                            dest_addr = struct.unpack_from("<I", arm9, entry_pos)[0]
                            if dest_addr in LEGACY_ORIGINS_VISUAL:
                                return True
        return False
    except Exception:
        return False


def apply_camera_patch(
    rom_path: str,
    enable: bool = True,
    log_cb: Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Installs (`enable=True`) or reverts (`enable=False`) the Visual+ 3D Camera angle table
    in Overlay 5 ONLY (without touching the C 60 FPS Visual Engine / Clouds / Lighting).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
        overlays = rom.loadArm9Overlays()
        if 5 not in overlays:
            log("Overlay 5 introuvable dans la ROM.")
            return False

        ov5 = overlays[5]
        p = _get_rom_profile(ov5.ramAddress)
        ov5_buf = bytearray(ov5.data)
        cam_off = p["ov5_cam_table_off"]

        if enable:
            ov5_buf[cam_off:cam_off + len(CAM_DYNAMIC_FULL)] = CAM_DYNAMIC_FULL
            log("Caméra 3D Visual+ activée avec succès.")
        else:
            ov5_buf[cam_off:cam_off + len(CAM_VANILLA_FULL)] = CAM_VANILLA_FULL
            log("Caméra 3D Visual+ désactivée (angle d'origine restauré).")

        if hasattr(rom, "pad16C") and len(rom.pad16C) > 0x79 and rom.pad16C[0x74:0x78] == b"PPM\x01":
            pad = bytearray(rom.pad16C)
            pad[0x79] = (pad[0x79] | 0x08) if enable else (pad[0x79] & ~0x08)
            rom.pad16C = bytes(pad)

        ov5.data = bytes(ov5_buf)
        rom.files[ov5.fileID] = ov5.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
        rom.saveToFile(rom_path)
        return True
    except Exception as e:
        log(f"Erreur lors du patch Caméra 3D Visual+ : {e}")
        return False


def apply_visual_engine_patch(
    rom_path: str,
    enable: bool = True,
    log_cb: Optional[Callable[[str], None]] = None,
    preset: str = "dynamic",
) -> bool:
    """
    Installs (`enable=True`) or completely reverts (`enable=False`) our custom C-compiled
    Next-Gen 60 FPS Dynamic Visual Engine (`visual_engine.c` at `0x023DE000`):
    - Zero-Flicker Solar/Lunar Interpolation + Hardware Specular Bloom + 5 Weather Shaders
      + Drifting 7-Bit Cloud Shadows (`Hook1_FieldUpdate`, `Hook2_AreaLightApply`, `Hook3_AreaLightFree`).
    - Real-time 60 FPS VRAM Water Shimmer (`Hook7_WaterShimmer`) + `fldtanime.narc`.
    - 3D Billboard Pitch & Yaw Alignment (`Hook5_BillboardMtx`).
    - Leaves the Overlay 5 camera table (`ov5_cam_table_off`) untouched so Visual+ 3D Camera
      remains completely independent.
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
        overlays = rom.loadArm9Overlays()
        if 5 not in overlays:
            log("Overlay 5 introuvable dans la ROM.")
            return False

        ov5 = overlays[5]
        p = _get_rom_profile(ov5.ramAddress)
        ov5_base = p["ov5_base"]
        ov5_buf = bytearray(ov5.data)
        arm9_buf = bytearray(rom.arm9)

        # 1. Parse existing custom autoload entries (e.g. SoulLink/Nuzlocke, Type Effectiveness)
        list_off = p["autoload_list_off"]
        mp_off = p["module_params_off"]
        list_start, list_end = struct.unpack_from("<2I", arm9_buf, mp_off)
        start_off = list_start - rom.arm9RamAddress
        end_off = list_end - rom.arm9RamAddress
        custom_entries: List[Tuple[int, bytes, int]] = []
        if 0 <= start_off <= len(arm9_buf) and 0 <= end_off <= len(arm9_buf) and end_off >= start_off + 24:
            data_cursor = list_off
            for entry_pos in range(start_off + 24, end_off, 12):
                if entry_pos + 12 <= len(arm9_buf):
                    dest, sz, bss = struct.unpack_from("<3I", arm9_buf, entry_pos)
                    if 0x023C0000 <= dest < 0x023E0000 and 0 < sz <= 0x10000 and data_cursor + sz <= start_off:
                        blob = bytes(arm9_buf[data_cursor:data_cursor + sz])
                        data_cursor += sz
                        if dest not in LEGACY_ORIGINS_VISUAL:
                            custom_entries.append((dest, blob, bss))

        # 2. Heal any legacy hook artifacts in ARM9 and Overlay 5 before applying/restoring
        d1_off = p["bb_draw_hook1_off"]
        if p["is_ppm_or_fr"] and d1_off > 0 and arm9_buf[d1_off + 4:d1_off + 6] == b"\x20\x1c":
            if arm9_buf[d1_off + 10:d1_off + 14] == b"\x01\x28\x01\xd1":
                arm9_buf[d1_off + 6:d1_off + 10] = b"\xb5\x30\x00\x78"
        if len(arm9_buf) >= 0x100938 and arm9_buf[0x1008C0:0x1008C6] == b"\x38\xb5\x04\x1c\x15\x1c":
            arm9_buf[0x1008C0:0x100938] = b"\x00" * 0x78

        ov5_buf[p["ov5_al_free_assert_off"]:p["ov5_al_free_assert_off"] + 8] = p["ov5_al_free_assert_bytes"]
        if p["is_ppm_or_fr"]:
            ov5_buf[p["ov5_legacy_prop_off"]:p["ov5_legacy_prop_off"] + 4] = b"\xf3\xf7\xf4\xfa"
        else:
            ov5_buf[p["ov5_legacy_prop_off"]:p["ov5_legacy_prop_off"] + 4] = b"\xf4\xf7\x82\xf8"
        ov5_buf[p["ov5_al_free_tail_off"] - 2:p["ov5_al_free_tail_off"]] = b"\x00\x20"
        # Restore AreaLightManager_ApplyActiveTemplateToAreaModelAttrs first 12 bytes and AreaLightTemplate_Init prologue
        ov5_buf[p["ov5_al_apply_off"] - 12:p["ov5_al_apply_off"]] = (
            b"\x03\x1c\x99\x68\x30\x20\x48\x43\x5a\x68\xd9\x68"
        )
        ov5_buf[p["ov5_al_apply_bl_off"]:p["ov5_al_apply_bl_off"] + 8] = (
            b"\x10\xb5\x04\x1c\x00\x21\x40\x22"
        )

        # Locate all G3dRenderer_Draw call sites inside BillboardList_Draw dynamically
        bb_draw_sites: List[int] = []
        scan_start = p["bb_mtx_hook_off"]
        scan_end = min(len(arm9_buf) - 16, scan_start + 0xB8)
        idx = scan_start
        while idx < scan_end:
            pos = arm9_buf.find(b"\x30\x30\x21\x1c", idx, scan_end)
            if pos == -1:
                break
            pos_330c = arm9_buf.find(b"\x0c\x33", pos + 4, pos + 10)
            if pos_330c != -1:
                bb_draw_sites.append(pos_330c + 2)
            idx = pos + 4

        # Always restore Hook4 (prop), Hook6 (billboard draw), and Hook8 (breeze leaf particles) to vanilla
        for site_off in bb_draw_sites:
            arm9_buf[site_off:site_off + 4] = _make_thumb_bl(
                0x02000000 + site_off, p["g3d_renderer_draw"], is_blx=False
            )
        ov5_buf[p["ov5_prop_off"]:p["ov5_prop_off"] + 4] = _make_thumb_bl(
            ov5_base + p["ov5_prop_off"], p["prop_get_mat_shp"], is_blx=False
        )
        ov5_buf[p["ov5_draw3d_off"]:p["ov5_draw3d_off"] + 4] = _make_thumb_bl(
            ov5_base + p["ov5_draw3d_off"], p["draw3d_part_fn"], is_blx=False
        )

        if enable:
            payload, labels = _build_visual_engine_payload(p, preset=preset)
            if len(payload) % 32 != 0:
                payload += b"\x00" * (32 - (len(payload) % 32))
            custom_entries.append((ORIGIN_VISUAL, payload, 0))

            # Install ARM9 hook (Hook5_BillboardMtx: 3D Pitch + Orbital Yaw billboard alignment)
            arm9_buf[p["bb_mtx_hook_off"]:p["bb_mtx_hook_off"] + 4] = _make_thumb_bl(
                0x02000000 + p["bb_mtx_hook_off"], labels["Hook5_BillboardMtx"], is_blx=False
            )

            # Install Overlay 5 C hooks (Hook1, Hook2, Hook3, Hook7)
            ov5_buf[p["ov5_field_update_off"]:p["ov5_field_update_off"] + 4] = _make_thumb_bl(
                ov5_base + p["ov5_field_update_off"], labels["Hook1_FieldUpdate"], is_blx=False
            )
            ov5_buf[p["ov5_al_apply_off"]:p["ov5_al_apply_off"] + 12] = (
                b"\x10\x18\x1a\x68\x00\x4b\x18\x47"
                + struct.pack("<I", labels["Hook2_AreaLightApply"] | 1)
            )
            ov5_buf[p["ov5_al_free_tail_off"]:p["ov5_al_free_tail_off"] + 4] = _make_thumb_bl(
                ov5_base + p["ov5_al_free_tail_off"], labels["Hook3_AreaLightFree"], is_blx=False
            )
            ov5_buf[p["ov5_texanim_off"]:p["ov5_texanim_off"] + 4] = _make_thumb_bl(
                ov5_base + p["ov5_texanim_off"], labels["Hook7_WaterShimmer"], is_blx=False
            )

            # Enable hardware Anti-Aliasing & Edge Marking in Overlay 5 (0x10 AAE | 0x20 EME)
            ov5_buf[p["ov5_edgemark_off"]:p["ov5_edgemark_off"] + 2] = b"\x30\x20"  # movs r0, #0x30
            ov5_buf[p["ov5_aa_mask_off"]:p["ov5_aa_mask_off"] + 4] = b"\xff\xcf\xff\xff"

            # Update data/arealight.narc File 0
            if "data/arealight.narc" in rom.filenames:
                al_id = rom.filenames.idOf("data/arealight.narc")
                al_narc = ndspy.narc.NARC(rom.files[al_id])
                al_narc.files[0] = build_arealight_file0(preset=preset)
                rom.files[al_id] = al_narc.save()

            # Update data/fldtanime.narc water/flower cadence
            _patch_fldtanime_narc(rom, enable=True)

            # Restore vanilla movement in ARM9
            _patch_diagonal_movement(arm9_buf, p["is_ppm_or_fr"], enable=True, labels=labels)

            log(
                f"Moteur Visuel 60 FPS (Éclairage & Nuages) installé ({len(payload)} octets à 0x023DE000, preset={preset})."
            )
        else:
            # Restore ARM9 instructions
            arm9_buf[p["bb_mtx_hook_off"]:p["bb_mtx_hook_off"] + 4] = _make_thumb_bl(
                0x02000000 + p["bb_mtx_hook_off"], p["mtx_identity33"], is_blx=True
            )

            # Restore Overlay 5 instructions
            ov5_buf[p["ov5_field_update_off"]:p["ov5_field_update_off"] + 4] = _make_thumb_bl(
                ov5_base + p["ov5_field_update_off"], p["arealight_update"], is_blx=False
            )
            ov5_buf[p["ov5_al_apply_off"]:p["ov5_al_apply_off"] + 12] = (
                b"\x01\x4b\x10\x18\x18\x47\xc0\x46"
                + struct.pack("<I", p["arealight_apply_tpl"] | 1)
            )
            ov5_buf[p["ov5_al_free_tail_off"]:p["ov5_al_free_tail_off"] + 4] = b"\x20\x60\x10\xbd"
            ov5_buf[p["ov5_texanim_off"]:p["ov5_texanim_off"] + 4] = _make_thumb_bl(
                ov5_base + p["ov5_texanim_off"], p["vram_transfer_req"], is_blx=False
            )

            # Restore vanilla Edge Marking & Anti-Aliasing mask
            ov5_buf[p["ov5_edgemark_off"]:p["ov5_edgemark_off"] + 2] = b"\x20\x20"  # movs r0, #0x20
            ov5_buf[p["ov5_aa_mask_off"]:p["ov5_aa_mask_off"] + 4] = b"\xff\xcf\xff\xff"

            # Restore vanilla data/arealight.narc File 0
            if "data/arealight.narc" in rom.filenames:
                al_id = rom.filenames.idOf("data/arealight.narc")
                al_narc = ndspy.narc.NARC(rom.files[al_id])
                al_narc.files[0] = build_vanilla_arealight_file0()
                rom.files[al_id] = al_narc.save()

            # Restore vanilla data/fldtanime.narc delays
            _patch_fldtanime_narc(rom, enable=False)

            # Restore vanilla diagonal movement in ARM9
            _patch_diagonal_movement(arm9_buf, p["is_ppm_or_fr"], enable=False)

            log("Moteur Visuel 60 FPS (Éclairage & Nuages) désactivé (éclairage et animations d'origine restaurés).")

        # Rebuild ARM9 autoload section cleanly (coexisting with SoulLink/Nuzlocke & Type Effectiveness)
        new_arm9 = bytearray(arm9_buf[:list_off])
        for _, blob, _ in custom_entries:
            new_arm9 += blob
        new_list_start = rom.arm9RamAddress + len(new_arm9)
        new_arm9 += VANILLA_AUTOLOAD_LIST
        for dest, blob, bss in custom_entries:
            new_arm9 += struct.pack("<3I", dest, len(blob), bss)
        new_list_end = rom.arm9RamAddress + len(new_arm9)

        struct.pack_into("<2I", new_arm9, mp_off, new_list_start, new_list_end)
        high_arena_dests = [d & ~0x1F for d, _, _ in custom_entries if 0x023C0000 <= d < 0x023E0000]
        arena_hi = min(high_arena_dests) if high_arena_dests else 0x023E0000
        struct.pack_into("<I", new_arm9, p["lit_arena_hi_off"], arena_hi)
        struct.pack_into("<I", new_arm9, mp_off + 0x0C, p["bss_start"])

        # Adjust HEAP_ID_APPLICATION pool size in ProjectPM 0.4.7 / 0.4.6 / 0.4.5 so MainArena has plenty of headroom
        app_heap_off = (
            0xEC660 if p["profile_id"] == 47 else (
                0xEC52C if p["profile_id"] == 46 else (
                    0xEC2D8 if p["profile_id"] == 45 else -1
                )
            )
        )
        if app_heap_off > 0 and app_heap_off + 4 <= len(new_arm9):
            cur_heap = new_arm9[app_heap_off:app_heap_off + 4]
            if high_arena_dests and cur_heap in (
                b"\x00\x50\x10\x00", b"\x00\x40\x10\x00", b"\x00\x30\x10\x00", b"\x00\x20\x10\x00"
            ):
                new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x18\x10\x00"
            elif not high_arena_dests and cur_heap in (
                b"\x00\x18\x10\x00", b"\x00\x20\x10\x00", b"\x00\x30\x10\x00", b"\x00\x40\x10\x00"
            ):
                new_arm9[app_heap_off:app_heap_off + 4] = b"\x00\x50\x10\x00"

        if hasattr(rom, "pad16C") and len(rom.pad16C) > 0x79 and rom.pad16C[0x74:0x78] == b"PPM\x01":
            pad = bytearray(rom.pad16C)
            pad[0x79] = (pad[0x79] | 0x10) if enable else (pad[0x79] & ~0x10)
            rom.pad16C = bytes(pad)

        rom.arm9 = bytes(new_arm9)
        ov5.data = bytes(ov5_buf)
        rom.files[ov5.fileID] = ov5.save()
        rom.arm9OverlayTable = ndspy.code.saveOverlayTable(overlays)
        rom.saveToFile(rom_path)
        return True
    except Exception as e:
        log(f"Erreur lors du patch Moteur Visuel 60 FPS : {e}")
        return False


def apply_battle_bg_patch(
    rom_path: str,
    assets_dir: str,
    enable: bool = True,
    log_cb: Optional[Callable[[str], None]] = None,
) -> bool:
    """
    Injects (`enable=True`) or removes (`enable=False`) Visual+ HD Battle Backgrounds NARC
    into `battle/graphic/pl_batt_bg.narc` (file 159).
    """
    def log(msg: str):
        if log_cb:
            log_cb(msg)

    narc_name = "visualplus_battlebg.narc" if enable else "standard_battlebg.narc"
    narc_path = os.path.join(assets_dir, narc_name)
    if not os.path.isfile(narc_path):
        log(f"[Visual+] Error: {narc_name} not found in {assets_dir}.")
        return False

    try:
        rom = ndspy.rom.NintendoDSRom.fromFile(rom_path)
        target_id = 159
        try:
            found_id = rom.filenames.idOf("battle/graphic/pl_batt_bg.narc")
            if found_id is not None:
                target_id = found_id
        except Exception:
            pass

        if len(rom.files) <= target_id:
            log("[Visual+] Error: Invalid ROM file table (missing battle bg).")
            return False

        with open(narc_path, "rb") as f:
            new_narc = f.read()

        rom.files[target_id] = new_narc
        try:
            rom.setFileByName("battle/graphic/pl_batt_bg.narc", new_narc)
        except Exception:
            pass

        if hasattr(rom, "pad16C") and len(rom.pad16C) > 0x79 and rom.pad16C[0x74:0x78] == b"PPM\x01":
            pad = bytearray(rom.pad16C)
            pad[0x79] = (pad[0x79] | 0x04) if enable else (pad[0x79] & ~0x04)
            rom.pad16C = bytes(pad)

        rom.saveToFile(rom_path)
        mode_str = "activés" if enable else "restaurés (Vanilla)"
        log(f"Fonds de combat Visual+ {mode_str} avec succès.")
        return True
    except Exception as e:
        log(f"Erreur lors de l'application des fonds de combat : {e}")
        return False

