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

class ModernScrollbar(tk.Canvas):
    """
    Sleek, dark-mode custom scrollbar for Tkinter Canvas.
    Replaces default OS scrollbars with a modern, smooth pill slider.
    """
    def __init__(
        self,
        parent,
        command=None,
        width=12,
        bg=BG_DARK,
        thumb_color=BORDER_COLOR,
        thumb_hover="#535C80",
        thumb_active=COLOR_PRIMARY,
        **kwargs
    ):
        super().__init__(
            parent,
            width=width,
            bg=bg,
            highlightthickness=0,
            bd=0,
            cursor="arrow",
            **kwargs
        )
        self.command = command
        self.width = width
        self.thumb_color = thumb_color
        self.thumb_hover = thumb_hover
        self.thumb_active = thumb_active

        self.first = 0.0
        self.last = 1.0
        self.is_hovered = False
        self.is_dragging = False

        self.drag_start_y = None
        self.drag_start_top = None
        self.min_thumb_h = 24

        self.bind("<Configure>", self._on_resize)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<MouseWheel>", self._on_mousewheel)

    def set(self, first, last):
        try:
            self.first = float(first)
            self.last = float(last)
        except (ValueError, TypeError):
            return
        self._redraw()

    def _get_thumb_coords(self, h):
        span = max(0.01, min(1.0, self.last - self.first))
        thumb_h = max(self.min_thumb_h, span * h)
        thumb_h = min(h, thumb_h)
        range_y = max(1.0, h - thumb_h)
        max_first = max(0.0001, 1.0 - span)
        top_y = min(range_y, max(0.0, (self.first / max_first) * range_y))
        return top_y, top_y + thumb_h

    def _redraw(self):
        self.delete("all")
        h = self.winfo_height()
        if h <= 2:
            return

        if self.first <= 0.0 and self.last >= 1.0:
            return

        top_y, bot_y = self._get_thumb_coords(h)

        if self.is_dragging:
            fill_color = self.thumb_active
        elif self.is_hovered:
            fill_color = self.thumb_hover
        else:
            fill_color = self.thumb_color

        x1 = 3
        x2 = self.width - 3
        r = min(3, (x2 - x1) // 2)
        self._draw_pill(x1, top_y, x2, bot_y, r=r, fill=fill_color)

    def _draw_pill(self, x1, y1, x2, y2, r=3, **kwargs):
        if y2 - y1 < 2 * r:
            self.create_rectangle(x1, y1, x2, y2, outline="", **kwargs)
            return

        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        self.create_polygon(points, smooth=True, outline="", **kwargs)

    def _on_resize(self, event):
        self._redraw()

    def _on_enter(self, event):
        self.is_hovered = True
        self._redraw()

    def _on_leave(self, event):
        self.is_hovered = False
        self._redraw()

    def _on_press(self, event):
        h = self.winfo_height()
        if h <= 2 or not self.command:
            return

        top_y, bot_y = self._get_thumb_coords(h)

        if top_y <= event.y <= bot_y:
            self.is_dragging = True
            self.drag_start_y = event.y
            self.drag_start_top = top_y
            self._redraw()
        elif event.y < top_y:
            self.command("scroll", -1, "pages")
        else:
            self.command("scroll", 1, "pages")

    def _on_drag(self, event):
        if not self.is_dragging or self.drag_start_y is None or not self.command:
            return

        h = self.winfo_height()
        if h <= 2:
            return

        span = max(0.01, min(1.0, self.last - self.first))
        thumb_h = max(self.min_thumb_h, span * h)
        thumb_h = min(h, thumb_h)
        range_y = max(1.0, h - thumb_h)
        max_first = max(0.0001, 1.0 - span)

        delta_y = event.y - self.drag_start_y
        new_top_y = min(range_y, max(0.0, self.drag_start_top + delta_y))
        new_first = (new_top_y / range_y) * max_first

        self.command("moveto", new_first)

    def _on_release(self, event):
        self.is_dragging = False
        self.drag_start_y = None
        self.drag_start_top = None
        self._redraw()

    def _on_mousewheel(self, event):
        if self.command:
            self.command("scroll", int(-1 * (event.delta / 120)), "units")

