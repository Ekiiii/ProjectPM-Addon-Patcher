# -*- coding: utf-8 -*-
"""
widgets.py
Custom reusable Tkinter widgets:
- Pixel art styled cards & frames
- Interactive buttons with hover transitions
- Status badges & preview card containers
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from ui.theme import *

class ModernCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=BG_CARD,
            highlightbackground=BORDER_COLOR,
            highlightthickness=1,
            padx=12,
            pady=10,
            **kwargs
        )

class PixelButton(tk.Button):
    def __init__(self, parent, text, command=None, bg_color=COLOR_PRIMARY, fg_color=TEXT_WHITE, font_size=11, bold=True, padx=16, pady=8, **kwargs):
        self.normal_bg = bg_color
        self.hover_bg = BG_HOVER
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=self.normal_bg,
            fg=fg_color,
            activebackground=BG_HOVER,
            activeforeground=fg_color,
            font=get_font(font_size, bold=bold),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=padx,
            pady=pady,
            **kwargs
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        self.config(bg=self.hover_bg)

    def _on_leave(self, e):
        self.config(bg=self.normal_bg)

class StatusBadge(tk.Label):
    def __init__(self, parent, text="", badge_type="info", **kwargs):
        bg = BG_PANEL
        fg = TEXT_WHITE
        if badge_type == "success":
            bg = "#1B3B2B"
            fg = TEXT_GREEN
        elif badge_type == "gold":
            bg = "#3D3215"
            fg = TEXT_GOLD
        elif badge_type == "danger":
            bg = "#3D1C1C"
            fg = COLOR_RED
        elif badge_type == "purple":
            bg = "#331D42"
            fg = "#C678DD"
            
        super().__init__(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=get_font(9, bold=True),
            padx=8,
            pady=3,
            relief="flat",
            **kwargs
        )

    def set_badge(self, text, badge_type="info"):
        bg = BG_PANEL
        fg = TEXT_WHITE
        if badge_type == "success":
            bg = "#1B3B2B"
            fg = TEXT_GREEN
        elif badge_type == "gold":
            bg = "#3D3215"
            fg = TEXT_GOLD
        elif badge_type == "danger":
            bg = "#3D1C1C"
            fg = COLOR_RED
        elif badge_type == "purple":
            bg = "#331D42"
            fg = "#C678DD"
        self.config(text=text, bg=bg, fg=fg)
