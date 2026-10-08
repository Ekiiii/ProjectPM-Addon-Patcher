# -*- coding: utf-8 -*-
"""
theme.py
Design system & styling for ProjectPM Addon Patcher:
- Sleek 'Platine Moderne' dark theme
- Nintendo DS Pixel Art font loading via Windows GDI
- Custom color tokens & button styles
"""
import os
import ctypes

# Color Palette (Platine Moderne)
BG_DARK      = "#14161F"  # Deep dark navy background
BG_PANEL     = "#1D202D"  # Section background
BG_CARD      = "#25293A"  # Interactive element background
BG_HOVER     = "#2F344A"  # Hover state
BORDER_COLOR = "#3A405A"  # Subtle separator border

COLOR_PRIMARY = "#3D74B8" # Platinum Steel Blue
COLOR_GOLD    = "#E5A823" # Giratina Gold
COLOR_GREEN   = "#3EB665" # Success Emerald
COLOR_RED     = "#E04F4F" # Alert Crimson

TEXT_WHITE   = "#F2F4F8"
TEXT_MUTED   = "#8E97B0"
TEXT_GOLD    = "#F3C354"
TEXT_GREEN   = "#56D67F"

FONT_NAME = "Segoe UI"

def load_ds_font(assets_dir):
    """
    Dynamically registers PlatinumDS.ttf into current Windows session without permanent install.
    """
    global FONT_NAME
    font_path = os.path.join(assets_dir, "PlatinumDS.ttf")
    if os.path.isfile(font_path):
        try:
            # GDI AddFontResourceExW
            FR_PRIVATE = 0x10
            res = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, 0)
            if res > 0:
                FONT_NAME = "Platinum DS"
        except Exception:
            FONT_NAME = "Segoe UI"
    return FONT_NAME

def get_font(size=10, bold=False):
    weight = "bold" if bold else "normal"
    return (FONT_NAME, size, weight)
