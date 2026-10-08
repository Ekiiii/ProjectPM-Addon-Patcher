# -*- coding: utf-8 -*-
"""
main_window.py
Main graphical interface for ProjectPM Addon Patcher:
- Platine Moderne pixel-art theme
- Bilingual support with real-time toggle
- Full window scrolling (Canvas + Scrollbar + MouseWheel)
- In-depth ROM state detection & live badges (Multiplayer, SoulLocke, Randomizer, Visual+)
- Selectable Multiplayer Base with auto-detection & lock when already present
- Dynamic interlocking dependencies between Multiplayer and SoulLocke addons
- Visual+ options with image previews
- Save file (.dsv) & Randomizer (.rand.txt) preservation
- GitHub Auto-Updater integration
"""
import os
import sys
import webbrowser
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

from core.i18n import t, set_lang, get_lang
from core.rom_detector import detect_rom
from core.smart_injector import apply_soullocke, restore_clean_projectpm
from core.visual_patcher import apply_battle_bg_patch, apply_camera_patch
from core.xdelta_engine import apply_xdelta
from core.save_manager import backup_and_sync_save
from core.updater import check_for_updates_async, CURRENT_VERSION
from core.rand_manager import extract_randomizer_data, clean_vanilla_for_xdelta, restore_randomizer_data
from core.addon_registry import (
    MULTIPLAYER_VERSIONS,
    ADDONS_REGISTRY,
    get_mp_version,
    is_mp_version_supported,
    get_addon_definition,
    is_addon_variant_supported,
)

from ui.theme import *
from ui.widgets import ModernCard, PixelButton, StatusBadge

class MainWindow(tk.Tk):
    def __init__(self, root_dir):
        super().__init__()
        self.root_dir = root_dir
        self.assets_dir = os.path.join(root_dir, "assets")
        self.payloads_dir = os.path.join(root_dir, "payloads")

        # Load fonts
        load_ds_font(self.assets_dir)

        # Window settings
        self.title("ProjectPM Addon Patcher")
        self.geometry("920x820")
        self.minsize(880, 700)
        self.configure(bg=BG_DARK)

        # App Icon
        icon_path = os.path.join(self.assets_dir, "PM.ico")
        if os.path.isfile(icon_path):
            try:
                self.iconbitmap(icon_path)
            except Exception:
                pass

        # State
        self.selected_rom_path = ""
        self.current_rom_info = None
        self.update_info = None

        # Mode Variables
        self.var_mp_enabled = tk.BooleanVar(value=True)
        self.var_mp_version = tk.StringVar(value="")     # No default language pre-selected
        self.addon_enabled_vars = {}
        self.addon_variant_vars = {}
        self.addon_mode_vars = {}

        for addon in ADDONS_REGISTRY:
            a_id = addon["id"]
            self.addon_enabled_vars[a_id] = tk.BooleanVar(value=True)
            self.addon_variant_vars[a_id] = tk.StringVar(value="")  # No default language pre-selected
            self.addon_mode_vars[a_id] = tk.StringVar(value="apply")
        self.var_bg = tk.StringVar(value="keep")          # "builtin", "off", "keep"
        self.var_cam = tk.StringVar(value="keep")         # "builtin", "off", "keep"
        self.var_custom_patch_enabled = tk.BooleanVar(value=False)
        self.var_backup_save = tk.BooleanVar(value=True)
        self.output_manually_edited = False

        # Image cache
        self.img_cache = {}

        # Top fixed header
        self._build_header()

        # Center scrollable container
        self._build_scrollable_container()

        # Sections inside scrollable container
        self._build_rom_section()
        self._build_multiplayer_section()
        self._build_addons_section()
        self._build_visual_section()
        self._build_custom_patch_section()
        self._build_save_section()
        self._build_action_section()

        # Bottom fixed footer
        self._build_footer()

        # Ensure scroll is at the top on start
        self.after(50, lambda: self.canvas.yview_moveto(0))

        # Check for updates in background
        check_for_updates_async(self._on_update_found)

    def _build_header(self):
        self.header_frame = tk.Frame(self, bg=BG_DARK)
        self.header_frame.pack(fill="x", padx=20, pady=(12, 6))

        # Title + Subtitle
        left_box = tk.Frame(self.header_frame, bg=BG_DARK)
        left_box.pack(side="left")

        self.lbl_title = tk.Label(
            left_box,
            text=t("app_title"),
            bg=BG_DARK,
            fg=COLOR_GOLD,
            font=get_font(18, bold=True)
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_sub = tk.Label(
            left_box,
            text=t("app_subtitle"),
            bg=BG_DARK,
            fg=TEXT_MUTED,
            font=get_font(10)
        )
        self.lbl_sub.pack(anchor="w")

        # Right box: Lang switch & Version
        right_box = tk.Frame(self.header_frame, bg=BG_DARK)
        right_box.pack(side="right", anchor="e")

        self.btn_lang = PixelButton(
            right_box,
            text="Language: EN" if get_lang() == "en" else "Langue: FR",
            command=self._toggle_language,
            bg_color=BG_CARD,
            font_size=9,
            padx=10,
            pady=4
        )
        self.btn_lang.pack(side="right", padx=(10, 0))

        self.badge_ver = StatusBadge(right_box, text=CURRENT_VERSION, badge_type="gold")
        self.badge_ver.pack(side="right")

        # Update Banner (hidden by default)
        self.banner_update = tk.Frame(self, bg="#332B10", highlightbackground=COLOR_GOLD, highlightthickness=1)
        self.lbl_update_text = tk.Label(self.banner_update, text="", bg="#332B10", fg=COLOR_GOLD, font=get_font(10, bold=True))
        self.lbl_update_text.pack(side="left", padx=15, pady=6)
        self.btn_update_action = PixelButton(
            self.banner_update,
            text="Update",
            command=self._open_update_link,
            bg_color=COLOR_GOLD,
            fg_color="#101010",
            font_size=9,
            padx=8,
            pady=3
        )
        self.btn_update_action.pack(side="right", padx=15, pady=6)

    def _build_scrollable_container(self):
        container = tk.Frame(self, bg=BG_DARK)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG_DARK, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_content = tk.Frame(self.canvas, bg=BG_DARK)

        self.scroll_content.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_content, anchor="nw")

        def _on_canvas_configure(event):
            self.canvas.itemconfig(self.canvas_win, width=event.width)

        self.canvas.bind("<Configure>", _on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.scrollbar.pack(side="right", fill="y")

        # MouseWheel for Windows
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        self.bind_all("<MouseWheel>", _on_mousewheel)

    def _build_rom_section(self):
        self.card_rom = ModernCard(self.scroll_content)
        self.card_rom.pack(fill="x", padx=10, pady=5)

        self.sec_rom_title = tk.Label(
            self.card_rom,
            text=t("section_rom"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_rom_title.pack(anchor="w")

        # Source ROM sub-label
        self.lbl_in_title = tk.Label(
            self.card_rom,
            text=t("rom_input_label"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9, bold=True)
        )
        self.lbl_in_title.pack(anchor="w", pady=(6, 2))

        row = tk.Frame(self.card_rom, bg=BG_CARD)
        row.pack(fill="x", pady=(0, 4))

        self.entry_rom = tk.Entry(
            row,
            bg=BG_PANEL,
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            highlightbackground=BORDER_COLOR,
            highlightcolor=COLOR_PRIMARY,
            highlightthickness=1,
            relief="flat",
            font=get_font(10)
        )
        self.entry_rom.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)

        self.btn_browse = PixelButton(
            row,
            text=t("rom_browse"),
            command=self._on_browse_rom,
            bg_color=COLOR_PRIMARY,
            font_size=10,
            padx=14,
            pady=4
        )
        self.btn_browse.pack(side="right")

        # Status & SHA1 line
        info_row = tk.Frame(self.card_rom, bg=BG_CARD)
        info_row.pack(fill="x", pady=(2, 6))

        self.badge_rom_status = StatusBadge(info_row, text=t("rom_placeholder"), badge_type="info")
        self.badge_rom_status.pack(side="left")

        self.lbl_rom_sha1 = tk.Label(info_row, text="", bg=BG_CARD, fg=TEXT_MUTED, font=get_font(9))
        self.lbl_rom_sha1.pack(side="right")

        # Multi-badge features row
        self.badges_row = tk.Frame(self.card_rom, bg=BG_CARD)
        self.badges_row.pack(fill="x", pady=(2, 8))

        self.badge_feat_mp = StatusBadge(self.badges_row, text=t("badge_mp_none"), badge_type="info")
        self.badge_feat_mp.pack(side="left", padx=(0, 6))

        self.badge_feat_sl = StatusBadge(self.badges_row, text=t("badge_sl_none"), badge_type="info")
        self.badge_feat_sl.pack(side="left", padx=(0, 6))

        self.badge_feat_rand = StatusBadge(self.badges_row, text=t("badge_rand_no"), badge_type="info")
        self.badge_feat_rand.pack(side="left", padx=(0, 6))

        self.badge_feat_vbg = StatusBadge(self.badges_row, text="Visual+ BG: Off", badge_type="info")
        self.badge_feat_vbg.pack(side="left", padx=(0, 6))

        self.badge_feat_vcam = StatusBadge(self.badges_row, text="Visual+ Cam: Off", badge_type="info")
        self.badge_feat_vcam.pack(side="left")

        # Destination ROM (Where to save) line
        out_box = tk.Frame(self.card_rom, bg=BG_CARD)
        out_box.pack(fill="x", pady=(8, 2))

        self.lbl_out_title = tk.Label(
            out_box,
            text=t("rom_output_label"),
            bg=BG_CARD,
            fg=COLOR_GOLD,
            font=get_font(9, bold=True)
        )
        self.lbl_out_title.pack(anchor="w", pady=(0, 3))

        out_row = tk.Frame(out_box, bg=BG_CARD)
        out_row.pack(fill="x")

        self.entry_output = tk.Entry(
            out_row,
            bg=BG_PANEL,
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            highlightbackground=BORDER_COLOR,
            highlightcolor=COLOR_GOLD,
            highlightthickness=1,
            relief="flat",
            font=get_font(10)
        )
        self.entry_output.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=5)
        self.entry_output.bind("<Key>", lambda e: self._on_output_manual_edit())

        self.btn_browse_output = PixelButton(
            out_row,
            text=t("rom_output_browse"),
            command=self._on_browse_output,
            bg_color=COLOR_GOLD,
            fg_color="#101010",
            font_size=10,
            padx=14,
            pady=4
        )
        self.btn_browse_output.pack(side="right")

    def _build_multiplayer_section(self):
        self.card_mp = ModernCard(self.scroll_content)
        self.card_mp.pack(fill="x", padx=10, pady=5)

        self.sec_mp_title = tk.Label(
            self.card_mp,
            text=t("section_multiplayer"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_mp_title.pack(anchor="w")

        self.lbl_mp_desc = tk.Label(
            self.card_mp,
            text=t("mp_vanilla_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            justify="left"
        )
        self.lbl_mp_desc.pack(anchor="w", pady=(2, 6))

        # Checkbox + Version selection row
        row = tk.Frame(self.card_mp, bg=BG_CARD)
        row.pack(fill="x", pady=4)

        self.cb_mp_enable = tk.Checkbutton(
            row,
            text=t("mp_enable_checkbox"),
            variable=self.var_mp_enabled,
            command=self._on_mp_toggle_changed,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_PRIMARY,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.cb_mp_enable.pack(side="left")

        # Version button (opens modal dialog to pick language / version)
        self.btn_mp_version = PixelButton(
            row,
            text=t("btn_select_lang"),
            command=self._open_mp_version_dialog,
            bg_color=BG_PANEL,
            fg_color=COLOR_GOLD,
            font_size=9,
            bold=True,
            padx=12,
            pady=3
        )
        self.btn_mp_version.pack(side="left", padx=12)

        self.badge_mp_status = StatusBadge(row, text="", badge_type="success")

    def _build_addons_section(self):
        self.card_addons = ModernCard(self.scroll_content)
        self.card_addons.pack(fill="x", padx=10, pady=5)

        self.sec_addons_title = tk.Label(
            self.card_addons,
            text=t("section_addons"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_addons_title.pack(anchor="w", pady=(0, 4))

        # Extensible container for all registered addons
        self.frame_addons_list = tk.Frame(self.card_addons, bg=BG_CARD)
        self.frame_addons_list.pack(fill="x")

        self.addon_widgets = {}

        for addon in ADDONS_REGISTRY:
            a_id = addon["id"]
            row_card = tk.Frame(self.frame_addons_list, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=10, pady=8)
            row_card.pack(fill="x", pady=4)

            top_line = tk.Frame(row_card, bg=BG_PANEL)
            top_line.pack(fill="x")

            cb = tk.Checkbutton(
                top_line,
                text=t(addon["name_key"]),
                variable=self.addon_enabled_vars[a_id],
                command=lambda id=a_id: self._on_addon_toggle_changed(id),
                bg=BG_PANEL,
                fg=TEXT_WHITE,
                activebackground=BG_PANEL,
                activeforeground=COLOR_GOLD,
                selectcolor=BG_DARK,
                font=get_font(10, bold=True)
            )
            cb.pack(side="left")

            btn_ver = PixelButton(
                top_line,
                text=t("btn_select_lang"),
                command=lambda id=a_id: self._open_addon_config_dialog(id),
                bg_color=BG_DARK,
                fg_color=COLOR_GOLD,
                font_size=9,
                bold=True,
                padx=10,
                pady=2
            )
            btn_ver.pack(side="left", padx=10)

            badge = StatusBadge(top_line, text="", badge_type="info")
            badge.pack(side="left", padx=6)

            btn_un = PixelButton(
                top_line,
                text=t("btn_uninstall_addon"),
                command=lambda id=a_id: self._on_addon_uninstall_clicked(id),
                bg_color="#3D1C1C",
                fg_color=COLOR_RED,
                font_size=9,
                padx=8,
                pady=2
            )

            desc = tk.Label(
                row_card,
                text=t(addon["desc_key"]),
                bg=BG_PANEL,
                fg=TEXT_MUTED,
                font=get_font(9),
                wraplength=800,
                justify="left"
            )
            desc.pack(anchor="w", padx=(24, 0), pady=(4, 0))

            self.addon_widgets[a_id] = {
                "container": row_card,
                "cb": cb,
                "btn_ver": btn_ver,
                "badge": badge,
                "btn_uninstall": btn_un,
                "desc": desc,
            }

    # --- Small Windows / Modal Dialogs for Selection ---

    def _open_mp_version_dialog(self):
        info = self.current_rom_info
        if info and info.has_multiplayer:
            return

        dlg = tk.Toplevel(self)
        dlg.title(t("dialog_mp_title"))
        dlg.geometry("520x330")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        icon_path = os.path.join(self.assets_dir, "PM.ico")
        if os.path.isfile(icon_path):
            try:
                dlg.iconbitmap(icon_path)
            except Exception:
                pass

        x = self.winfo_x() + (self.winfo_width() // 2) - 260
        y = self.winfo_y() + (self.winfo_height() // 2) - 165
        dlg.geometry(f"+{x}+{y}")

        lbl_title = tk.Label(dlg, text=t("dialog_mp_title"), bg=BG_DARK, fg=COLOR_GOLD, font=get_font(12, bold=True))
        lbl_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_desc = tk.Label(dlg, text=t("dialog_mp_desc"), bg=BG_DARK, fg=TEXT_MUTED, font=get_font(9), wraplength=480, justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))

        card = ModernCard(dlg)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        selected_var = tk.StringVar(value=self.var_mp_version.get())

        for v in MULTIPLAYER_VERSIONS:
            v_id = v["id"]
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", pady=6)

            is_supported, err_key = is_mp_version_supported(v_id, info)

            rb = tk.Radiobutton(
                row,
                text=v["name"],
                variable=selected_var,
                value=v_id,
                tristatevalue="--UNSET--",
                bg=BG_CARD,
                fg=TEXT_WHITE if is_supported else TEXT_MUTED,
                activebackground=BG_CARD,
                activeforeground=COLOR_PRIMARY,
                selectcolor=BG_PANEL,
                state="normal" if is_supported else "disabled",
                font=get_font(10, bold=True)
            )
            rb.pack(side="left")

            if not is_supported and err_key:
                b = StatusBadge(row, text=f"[{t(err_key)}]", badge_type="danger")
                b.pack(side="left", padx=8)

        btn_box = tk.Frame(dlg, bg=BG_DARK)
        btn_box.pack(fill="x", padx=20, pady=(0, 15))

        def _on_confirm():
            choice = selected_var.get()
            if not choice:
                messagebox.showwarning("Notice", t("dialog_select_prompt"), parent=dlg)
                return
            self.var_mp_version.set(choice)
            for a in ADDONS_REGISTRY:
                a_id = a["id"]
                if a.get("requires_multiplayer"):
                    self.addon_variant_vars[a_id].set(choice)
            self._update_multiplayer_ui_state()
            self._update_suggested_output_path()
            dlg.destroy()

        btn_cancel = PixelButton(btn_box, text=t("dialog_cancel"), command=dlg.destroy, bg_color=BG_PANEL, fg_color=TEXT_WHITE, font_size=10, padx=14, pady=6)
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_ok = PixelButton(btn_box, text=t("dialog_confirm"), command=_on_confirm, bg_color=COLOR_GOLD, fg_color="#101010", font_size=10, bold=True, padx=18, pady=6)
        btn_ok.pack(side="right")

    def _open_addon_config_dialog(self, addon_id):
        addon = get_addon_definition(addon_id)
        if not addon:
            return

        info = self.current_rom_info
        if info and info.has_multiplayer:
            effective_mp_lang = info.mp_lang
        elif self.var_mp_enabled.get():
            effective_mp_lang = self.var_mp_version.get()
        else:
            effective_mp_lang = None

        dlg = tk.Toplevel(self)
        dlg.title(t("dialog_addon_title", addon["name"]))
        dlg.geometry("520x330")
        dlg.configure(bg=BG_DARK)
        dlg.transient(self)
        dlg.grab_set()
        dlg.resizable(False, False)

        icon_path = os.path.join(self.assets_dir, "PM.ico")
        if os.path.isfile(icon_path):
            try:
                dlg.iconbitmap(icon_path)
            except Exception:
                pass

        x = self.winfo_x() + (self.winfo_width() // 2) - 260
        y = self.winfo_y() + (self.winfo_height() // 2) - 165
        dlg.geometry(f"+{x}+{y}")

        lbl_title = tk.Label(dlg, text=t("dialog_addon_title", addon["name"]), bg=BG_DARK, fg=COLOR_GOLD, font=get_font(12, bold=True))
        lbl_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_desc = tk.Label(dlg, text=t("dialog_addon_desc"), bg=BG_DARK, fg=TEXT_MUTED, font=get_font(9), wraplength=480, justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))

        card = ModernCard(dlg)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        selected_var = tk.StringVar(value=self.addon_variant_vars[addon_id].get())

        for v in addon["variants"]:
            v_id = v["id"]
            row = tk.Frame(card, bg=BG_CARD)
            row.pack(fill="x", pady=6)

            is_supported, err_key = is_addon_variant_supported(addon_id, v_id, effective_mp_lang)

            rb = tk.Radiobutton(
                row,
                text=v["name"],
                variable=selected_var,
                value=v_id,
                tristatevalue="--UNSET--",
                bg=BG_CARD,
                fg=TEXT_WHITE if is_supported else TEXT_MUTED,
                activebackground=BG_CARD,
                activeforeground=COLOR_PRIMARY,
                selectcolor=BG_PANEL,
                state="normal" if is_supported else "disabled",
                font=get_font(10, bold=True)
            )
            rb.pack(side="left")

            if not is_supported and err_key:
                b = StatusBadge(row, text=f"[{t(err_key)}]", badge_type="danger")
                b.pack(side="left", padx=8)

        # Revert / Uninstall option if installed on ROM
        if addon_id == "soullocke" and info and info.is_soullocke:
            sep = tk.Frame(card, bg=BORDER_COLOR, height=1)
            sep.pack(fill="x", pady=10)

            def _on_uninstall():
                self.addon_mode_vars[addon_id].set("restore")
                self.addon_enabled_vars[addon_id].set(False)
                self._update_addon_ui_state()
                self._update_suggested_output_path()
                dlg.destroy()

            btn_un = PixelButton(card, text=t("btn_uninstall_addon"), command=_on_uninstall, bg_color="#5A1E1E", fg_color=COLOR_RED, font_size=9, padx=10, pady=4)
            btn_un.pack(anchor="w", pady=(0, 4))

        btn_box = tk.Frame(dlg, bg=BG_DARK)
        btn_box.pack(fill="x", padx=20, pady=(0, 15))

        def _on_confirm():
            choice = selected_var.get()
            if not choice:
                messagebox.showwarning("Notice", t("dialog_select_prompt"), parent=dlg)
                return
            self.addon_variant_vars[addon_id].set(choice)
            if self.addon_mode_vars[addon_id].get() == "restore":
                self.addon_mode_vars[addon_id].set("apply")
            self._update_addon_ui_state()
            self._update_suggested_output_path()
            dlg.destroy()

        btn_cancel = PixelButton(btn_box, text=t("dialog_cancel"), command=dlg.destroy, bg_color=BG_PANEL, fg_color=TEXT_WHITE, font_size=10, padx=14, pady=6)
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_ok = PixelButton(btn_box, text=t("dialog_confirm"), command=_on_confirm, bg_color=COLOR_GOLD, fg_color="#101010", font_size=10, bold=True, padx=18, pady=6)
        btn_ok.pack(side="right")

    def _on_mp_toggle_changed(self):
        if self.var_mp_enabled.get() and not self.var_mp_version.get():
            self._open_mp_version_dialog()
        self._update_multiplayer_ui_state()
        self._update_suggested_output_path()

    def _on_addon_toggle_changed(self, addon_id):
        if self.addon_enabled_vars[addon_id].get():
            self.addon_mode_vars[addon_id].set("apply")
            if not self.addon_variant_vars[addon_id].get():
                if self.var_mp_version.get():
                    self.addon_variant_vars[addon_id].set(self.var_mp_version.get())
                else:
                    self._open_addon_config_dialog(addon_id)
        self._update_addon_ui_state()
        self._update_suggested_output_path()

    def _on_addon_uninstall_clicked(self, addon_id):
        self.addon_mode_vars[addon_id].set("restore")
        self.addon_enabled_vars[addon_id].set(False)
        self._update_addon_ui_state()
        self._update_suggested_output_path()

    def _build_visual_section(self):
        self.card_visual = ModernCard(self.scroll_content)
        self.card_visual.pack(fill="x", padx=10, pady=5)

        self.sec_visual_title = tk.Label(
            self.card_visual,
            text=t("section_visual"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_visual_title.pack(anchor="w", pady=(0, 6))

        grid = tk.Frame(self.card_visual, bg=BG_CARD)
        grid.pack(fill="x")

        # Box 1: Battle Backgrounds
        box_bg = tk.Frame(grid, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=10, pady=8)
        box_bg.pack(side="left", fill="both", expand=True, padx=(0, 6))

        left_b1 = tk.Frame(box_bg, bg=BG_PANEL)
        left_b1.pack(side="left", fill="both", expand=True)

        self.lbl_vbg_title = tk.Label(left_b1, text=t("visual_battle_bg"), bg=BG_PANEL, fg=TEXT_WHITE, font=get_font(10, bold=True))
        self.lbl_vbg_title.pack(anchor="w")

        self.lbl_vbg_desc = tk.Label(left_b1, text=t("visual_battle_bg_desc"), bg=BG_PANEL, fg=TEXT_MUTED, font=get_font(9), wraplength=250, justify="left")
        self.lbl_vbg_desc.pack(anchor="w", pady=(2, 6))

        rb_row1 = tk.Frame(left_b1, bg=BG_PANEL)
        rb_row1.pack(anchor="w")
        self.rb_bg_builtin = tk.Radiobutton(rb_row1, text=t("opt_builtin"), variable=self.var_bg, value="builtin", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_bg_builtin.pack(side="left", padx=(0, 8))
        self.rb_bg_off = tk.Radiobutton(rb_row1, text=t("opt_off"), variable=self.var_bg, value="off", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_bg_off.pack(side="left", padx=(0, 8))
        self.rb_bg_keep = tk.Radiobutton(rb_row1, text=t("opt_keep"), variable=self.var_bg, value="keep", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_bg_keep.pack(side="left")

        # Thumbnail BG
        thumb_bg_path = os.path.join(self.assets_dir, "preview_visualplus_bg.png")
        if os.path.isfile(thumb_bg_path):
            img1 = Image.open(thumb_bg_path).resize((130, 68), Image.Resampling.LANCZOS)
            self.img_cache["bg"] = ImageTk.PhotoImage(img1)
            lbl_img1 = tk.Label(box_bg, image=self.img_cache["bg"], bg=BG_PANEL, relief="solid", bd=1)
            lbl_img1.pack(side="right", padx=(8, 0))

        # Box 2: 3D Camera
        box_cam = tk.Frame(grid, bg=BG_PANEL, highlightbackground=BORDER_COLOR, highlightthickness=1, padx=10, pady=8)
        box_cam.pack(side="right", fill="both", expand=True, padx=(6, 0))

        left_b2 = tk.Frame(box_cam, bg=BG_PANEL)
        left_b2.pack(side="left", fill="both", expand=True)

        self.lbl_vcam_title = tk.Label(left_b2, text=t("visual_camera"), bg=BG_PANEL, fg=TEXT_WHITE, font=get_font(10, bold=True))
        self.lbl_vcam_title.pack(anchor="w")

        self.lbl_vcam_desc = tk.Label(left_b2, text=t("visual_camera_desc"), bg=BG_PANEL, fg=TEXT_MUTED, font=get_font(9), wraplength=250, justify="left")
        self.lbl_vcam_desc.pack(anchor="w", pady=(2, 6))

        rb_row2 = tk.Frame(left_b2, bg=BG_PANEL)
        rb_row2.pack(anchor="w")
        self.rb_cam_builtin = tk.Radiobutton(rb_row2, text=t("opt_builtin"), variable=self.var_cam, value="builtin", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_cam_builtin.pack(side="left", padx=(0, 8))
        self.rb_cam_off = tk.Radiobutton(rb_row2, text=t("opt_off"), variable=self.var_cam, value="off", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_cam_off.pack(side="left", padx=(0, 8))
        self.rb_cam_keep = tk.Radiobutton(rb_row2, text=t("opt_keep"), variable=self.var_cam, value="keep", bg=BG_PANEL, fg=TEXT_WHITE, selectcolor=BG_DARK, font=get_font(9))
        self.rb_cam_keep.pack(side="left")

        # Thumbnail Cam
        thumb_cam_path = os.path.join(self.assets_dir, "preview_visualplus_cam_town.png")
        if os.path.isfile(thumb_cam_path):
            img2 = Image.open(thumb_cam_path).resize((130, 68), Image.Resampling.LANCZOS)
            self.img_cache["cam"] = ImageTk.PhotoImage(img2)
            lbl_img2 = tk.Label(box_cam, image=self.img_cache["cam"], bg=BG_PANEL, relief="solid", bd=1)
            lbl_img2.pack(side="right", padx=(8, 0))

    def _build_custom_patch_section(self):
        self.card_custom = ModernCard(self.scroll_content)
        self.card_custom.pack(fill="x", padx=10, pady=5)

        self.sec_custom_title = tk.Label(
            self.card_custom,
            text=t("section_custom_patch"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_custom_title.pack(anchor="w")

        self.lbl_custom_desc = tk.Label(
            self.card_custom,
            text=t("custom_patch_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            justify="left"
        )
        self.lbl_custom_desc.pack(anchor="w", pady=(2, 6))

        # Checkbox to enable
        self.cb_custom_patch = tk.Checkbutton(
            self.card_custom,
            text=t("custom_patch_checkbox"),
            variable=self.var_custom_patch_enabled,
            command=self._on_custom_patch_toggle_changed,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_PRIMARY,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.cb_custom_patch.pack(anchor="w", pady=(0, 4))

        # Row with Entry + Browse + Clear
        row = tk.Frame(self.card_custom, bg=BG_CARD)
        row.pack(fill="x", pady=2)

        self.entry_custom_patch = tk.Entry(
            row,
            bg=BG_PANEL,
            fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE,
            highlightbackground=BORDER_COLOR,
            highlightcolor=COLOR_PRIMARY,
            highlightthickness=1,
            relief="flat",
            font=get_font(10)
        )
        self.entry_custom_patch.pack(side="left", fill="x", expand=True, padx=(0, 8), ipady=5)
        self.entry_custom_patch.bind("<Key>", lambda e: self.var_custom_patch_enabled.set(True))

        self.btn_browse_custom = PixelButton(
            row,
            text=t("custom_patch_browse"),
            command=self._on_browse_custom_patch,
            bg_color=COLOR_PRIMARY,
            font_size=10,
            padx=14,
            pady=4
        )
        self.btn_browse_custom.pack(side="left", padx=(0, 6))

        self.btn_clear_custom = PixelButton(
            row,
            text=t("custom_patch_clear"),
            command=self._on_clear_custom_patch,
            bg_color=BG_PANEL,
            fg_color=COLOR_RED,
            font_size=10,
            padx=10,
            pady=4
        )
        self.btn_clear_custom.pack(side="left")

        # Bottom info label
        self.lbl_custom_info = tk.Label(
            self.card_custom,
            text=t("custom_patch_info"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(8),
            justify="left"
        )
        self.lbl_custom_info.pack(anchor="w", pady=(4, 0))

    def _on_custom_patch_toggle_changed(self):
        if self.var_custom_patch_enabled.get():
            if not self.entry_custom_patch.get().strip():
                self._on_browse_custom_patch()
        self._update_custom_patch_ui_state()

    def _on_browse_custom_patch(self):
        initial_dir = os.path.dirname(self.selected_rom_path) if self.selected_rom_path else os.getcwd()
        f = filedialog.askopenfilename(
            title="Select Custom XDelta Patch",
            initialdir=initial_dir,
            filetypes=[("xDelta Patches", "*.xdelta;*.patch;*.xd"), ("All files", "*.*")]
        )
        if f:
            self.entry_custom_patch.delete(0, tk.END)
            self.entry_custom_patch.insert(0, f)
            self.var_custom_patch_enabled.set(True)
            self._update_custom_patch_ui_state()

    def _on_clear_custom_patch(self):
        self.entry_custom_patch.delete(0, tk.END)
        self.var_custom_patch_enabled.set(False)
        self._update_custom_patch_ui_state()

    def _update_custom_patch_ui_state(self):
        is_en = self.var_custom_patch_enabled.get()
        if is_en:
            self.entry_custom_patch.config(bg=BG_PANEL, fg=TEXT_WHITE)
            self.lbl_custom_info.config(fg=COLOR_GOLD)
        else:
            self.entry_custom_patch.config(bg=BG_DARK, fg=TEXT_MUTED)
            self.lbl_custom_info.config(fg=TEXT_MUTED)

    def _build_save_section(self):
        self.card_save = ModernCard(self.scroll_content)
        self.card_save.pack(fill="x", padx=10, pady=5)

        self.sec_save_title = tk.Label(
            self.card_save,
            text=t("section_save"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_save_title.pack(anchor="w", pady=(0, 4))

        self.cb_save = tk.Checkbutton(
            self.card_save,
            text=t("save_preserve_checkbox"),
            variable=self.var_backup_save,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            selectcolor=BG_PANEL,
            activebackground=BG_CARD,
            activeforeground=TEXT_WHITE,
            font=get_font(9, bold=True)
        )
        self.cb_save.pack(anchor="w")

        self.lbl_save_status = tk.Label(
            self.card_save,
            text=t("save_none"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9)
        )
        self.lbl_save_status.pack(anchor="w", padx=(24, 0))

    def _build_action_section(self):
        action_frame = tk.Frame(self.scroll_content, bg=BG_DARK)
        action_frame.pack(fill="x", padx=10, pady=(10, 15))

        self.btn_apply = PixelButton(
            action_frame,
            text=t("btn_apply"),
            command=self._on_apply_clicked,
            bg_color=COLOR_GOLD,
            fg_color="#101010",
            font_size=13,
            bold=True,
            pady=12
        )
        self.btn_apply.pack(fill="x")

        # Status text below button
        self.lbl_status = tk.Label(
            action_frame,
            text=t("status_ready"),
            bg=BG_DARK,
            fg=TEXT_MUTED,
            font=get_font(10)
        )
        self.lbl_status.pack(pady=(6, 0))

    def _build_footer(self):
        footer_frame = tk.Frame(self, bg=BG_DARK)
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=(4, 8))

        self.lbl_footer = tk.Label(
            footer_frame,
            text=t("disclaimer"),
            bg=BG_DARK,
            fg="#555C75",
            font=get_font(8)
        )
        self.lbl_footer.pack()

    # --- Dynamic Interlocking & Handlers ---

    def _toggle_language(self):
        new_lang = "fr" if get_lang() == "en" else "en"
        set_lang(new_lang)
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        self.btn_lang.config(text="Language: EN" if get_lang() == "en" else "Langue: FR")
        self.lbl_title.config(text=t("app_title"))
        self.lbl_sub.config(text=t("app_subtitle"))
        self.sec_rom_title.config(text=t("section_rom"))
        self.lbl_in_title.config(text=t("rom_input_label"))
        self.lbl_out_title.config(text=t("rom_output_label"))
        self.btn_browse.config(text=t("rom_browse"))
        self.btn_browse_output.config(text=t("rom_output_browse"))
        self.sec_mp_title.config(text=t("section_multiplayer"))
        self.cb_mp_enable.config(text=t("mp_enable_checkbox"))
        self.sec_addons_title.config(text=t("section_addons"))

        for addon in ADDONS_REGISTRY:
            a_id = addon["id"]
            if a_id in self.addon_widgets:
                w = self.addon_widgets[a_id]
                w["cb"].config(text=t(addon["name_key"]))
                w["desc"].config(text=t(addon["desc_key"]))
                w["btn_uninstall"].config(text=t("btn_uninstall_addon"))

        self.sec_visual_title.config(text=t("section_visual"))
        self.lbl_vbg_title.config(text=t("visual_battle_bg"))
        self.lbl_vbg_desc.config(text=t("visual_battle_bg_desc"))
        self.lbl_vcam_title.config(text=t("visual_camera"))
        self.lbl_vcam_desc.config(text=t("visual_camera_desc"))
        self.rb_bg_builtin.config(text=t("opt_builtin"))
        self.rb_bg_off.config(text=t("opt_off"))
        self.rb_bg_keep.config(text=t("opt_keep"))
        self.rb_cam_builtin.config(text=t("opt_builtin"))
        self.rb_cam_off.config(text=t("opt_off"))
        self.rb_cam_keep.config(text=t("opt_keep"))
        self.sec_custom_title.config(text=t("section_custom_patch"))
        self.lbl_custom_desc.config(text=t("custom_patch_desc"))
        self.cb_custom_patch.config(text=t("custom_patch_checkbox"))
        self.btn_browse_custom.config(text=t("custom_patch_browse"))
        self.btn_clear_custom.config(text=t("custom_patch_clear"))
        self.lbl_custom_info.config(text=t("custom_patch_info"))
        self.sec_save_title.config(text=t("section_save"))
        self.cb_save.config(text=t("save_preserve_checkbox"))
        self.btn_apply.config(text=t("btn_apply"))
        self.lbl_footer.config(text=t("disclaimer"))

        if self.current_rom_info:
            self._update_rom_display(self.current_rom_info)
        else:
            self.badge_rom_status.set_badge(t("rom_placeholder"), badge_type="info")
            self.lbl_status.config(text=t("status_ready"))
            self._update_multiplayer_ui_state()

    def _on_output_manual_edit(self):
        self.output_manually_edited = True

    def _on_browse_output(self):
        current_val = self.entry_output.get().strip()
        if current_val:
            initial_dir = os.path.dirname(current_val)
            initial_file = os.path.basename(current_val)
        elif self.selected_rom_path:
            initial_dir = os.path.dirname(self.selected_rom_path)
            initial_file = "ProjectPM_Patched.nds"
        else:
            initial_dir = os.getcwd()
            initial_file = "ProjectPM_Patched.nds"

        f = filedialog.asksaveasfilename(
            title="Select Destination ROM",
            initialdir=initial_dir,
            initialfile=initial_file,
            defaultextension=".nds",
            filetypes=[("Nintendo DS ROMs", "*.nds"), ("All files", "*.*")]
        )
        if f:
            self.entry_output.delete(0, tk.END)
            self.entry_output.insert(0, f)
            self.output_manually_edited = True

    def _update_suggested_output_path(self):
        if self.output_manually_edited:
            return
        if not self.selected_rom_path:
            return

        parent_dir = os.path.dirname(self.selected_rom_path)
        base_name = os.path.splitext(os.path.basename(self.selected_rom_path))[0]
        info = self.current_rom_info

        if info and info.has_multiplayer:
            effective_mp = info.mp_lang
        elif self.var_mp_enabled.get():
            effective_mp = self.var_mp_version.get()
        else:
            effective_mp = None

        sl_enabled = self.addon_enabled_vars.get("soullocke", tk.BooleanVar(value=False)).get()
        sl_mode = self.addon_mode_vars.get("soullocke", tk.StringVar(value="apply")).get()
        sl_variant = self.addon_variant_vars.get("soullocke", tk.StringVar(value="")).get()

        target_lang = sl_variant if sl_enabled else (effective_mp or "")

        if sl_mode == "restore":
            out_name = f"{base_name}_Clean.nds"
        elif sl_enabled and effective_mp:
            out_name = "ProjectPM_FR_SoulLocke.nds" if target_lang == "fr" else ("ProjectPM_USA_SoulLocke.nds" if target_lang == "en" else f"{base_name}_SoulLocke.nds")
        elif info and not info.has_multiplayer and effective_mp:
            out_name = f"ProjectPM_{'FR' if effective_mp == 'fr' else 'USA'}.nds"
        else:
            out_name = f"{base_name}_modded.nds"

        suggested = os.path.join(parent_dir, out_name)
        if os.path.abspath(suggested).lower() == os.path.abspath(self.selected_rom_path).lower():
            suggested = os.path.join(parent_dir, f"{base_name}_patched.nds")

        self.entry_output.delete(0, tk.END)
        self.entry_output.insert(0, suggested)

    def _on_browse_rom(self):
        f = filedialog.askopenfilename(
            title="Select Pokémon Platinum / ProjectPM ROM",
            filetypes=[("Nintendo DS ROMs", "*.nds"), ("All files", "*.*")]
        )
        if f:
            self._load_rom(f)

    def _load_rom(self, rom_path):
        self.selected_rom_path = rom_path
        self.entry_rom.delete(0, tk.END)
        self.entry_rom.insert(0, rom_path)

        self.lbl_status.config(text=t("rom_detecting"), fg=COLOR_GOLD)
        self.update()

        info = detect_rom(rom_path)
        self.current_rom_info = info
        self.output_manually_edited = False
        self._update_rom_display(info)
        self._update_suggested_output_path()

    def _update_rom_display(self, info):
        if not info.exists:
            self.badge_rom_status.set_badge(t("rom_unknown"), badge_type="danger")
            return

        # Main ROM badge
        b_type = "success" if info.has_multiplayer else "gold"
        self.badge_rom_status.set_badge(f"{info.display_name} ({info.size // (1024*1024)} MB)", badge_type=b_type)
        self.lbl_rom_sha1.config(text=f"SHA1: {info.sha1[:10]}...")

        # Feature badges
        if info.has_multiplayer:
            self.badge_feat_mp.set_badge(t("badge_mp_active_fr") if info.mp_lang == "fr" else t("badge_mp_active_en"), badge_type="success")
        else:
            self.badge_feat_mp.set_badge(t("badge_mp_none"), badge_type="info")

        if info.is_soullocke:
            self.badge_feat_sl.set_badge(t("badge_sl_active"), badge_type="gold")
        else:
            self.badge_feat_sl.set_badge(t("badge_sl_none"), badge_type="info")

        if info.is_randomized:
            self.badge_feat_rand.set_badge(t("badge_rand_yes"), badge_type="purple")
        else:
            self.badge_feat_rand.set_badge(t("badge_rand_no"), badge_type="info")

        if info.has_visual_bg:
            self.badge_feat_vbg.set_badge(t("badge_vbg_yes"), badge_type="success")
            self.var_bg.set("builtin")
        else:
            self.badge_feat_vbg.set_badge("Visual+ BG: Off", badge_type="info")
            self.var_bg.set("off")

        if info.has_visual_cam:
            self.badge_feat_vcam.set_badge(t("badge_vcam_yes"), badge_type="success")
            self.var_cam.set("builtin")
        else:
            self.badge_feat_vcam.set_badge("Visual+ Cam: Off", badge_type="info")
            self.var_cam.set("off")

        # Save status
        if info.companion_save:
            saves = getattr(info, "all_companion_saves", [info.companion_save])
            save_names = ", ".join([os.path.basename(s) for s in saves])
            msg = t("save_detected", save_names)
            if info.has_rand_sidecar:
                msg += " | " + t("rand_detected")
            self.lbl_save_status.config(text=msg, fg=TEXT_GREEN)
        else:
            self.lbl_save_status.config(text=t("save_none"), fg=TEXT_MUTED)

        # Update Multiplayer Base section
        if info.has_multiplayer:
            self.lbl_mp_desc.config(text=t("mp_installed_desc"), fg=COLOR_GOLD)
            self.var_mp_enabled.set(True)
            self.var_mp_version.set(info.mp_lang)
            self.cb_mp_enable.config(state="disabled")
            self.btn_mp_version.config(state="disabled")
            self.badge_mp_status.set_badge(f"[{t('badge_already_installed')}]", badge_type="success")
            self.badge_mp_status.pack(side="left", padx=8)
        else:
            self.lbl_mp_desc.config(text=t("mp_vanilla_desc"), fg=TEXT_MUTED)
            self.cb_mp_enable.config(state="normal")
            self.badge_mp_status.pack_forget()

        self._update_multiplayer_ui_state()
        self.lbl_status.config(text=t("status_ready"), fg=TEXT_WHITE)

    def _update_multiplayer_ui_state(self):
        info = self.current_rom_info
        v = get_mp_version(self.var_mp_version.get())
        if v:
            self.btn_mp_version.config(text=t("mp_version_btn", v["short_name"]))
        else:
            self.btn_mp_version.config(text=t("btn_select_lang"))

        if info and info.has_multiplayer:
            self.btn_mp_version.config(state="disabled")
            self.cb_mp_enable.config(state="disabled")
        else:
            if self.var_mp_enabled.get():
                self.btn_mp_version.config(state="normal")
            else:
                self.btn_mp_version.config(state="disabled")

        self._update_addon_ui_state()

    def _update_addon_ui_state(self):
        info = self.current_rom_info
        if info and info.has_multiplayer:
            effective_mp = info.mp_lang
        elif self.var_mp_enabled.get():
            effective_mp = self.var_mp_version.get()
        else:
            effective_mp = None

        for addon in ADDONS_REGISTRY:
            a_id = addon["id"]
            if a_id not in self.addon_widgets:
                continue

            w = self.addon_widgets[a_id]
            is_req_mp = addon.get("requires_multiplayer", False)

            if is_req_mp and not effective_mp:
                # Addon requires multiplayer, but none active
                w["cb"].config(state="disabled")
                w["btn_ver"].config(state="disabled")
                w["badge"].set_badge(f"[{t('badge_incompatible_req_mp')}]", badge_type="danger")
                w["badge"].pack(side="left", padx=6)
                w["btn_uninstall"].pack_forget()
                self.addon_enabled_vars[a_id].set(False)
            else:
                w["cb"].config(state="normal")
                w["btn_ver"].config(state="normal")

                # Align variant with effective multiplayer
                current_var = self.addon_variant_vars[a_id].get()
                if effective_mp and current_var != effective_mp:
                    self.addon_variant_vars[a_id].set(effective_mp)

                if self.addon_variant_vars[a_id].get():
                    variant_name = "Français" if self.addon_variant_vars[a_id].get() == "fr" else "English"
                    w["btn_ver"].config(text=t("addon_version_btn", variant_name))
                else:
                    w["btn_ver"].config(text=t("btn_select_lang"))

                # If installed on ROM
                if a_id == "soullocke" and info and info.is_soullocke:
                    w["badge"].set_badge(f"[{t('addon_installed_badge')}]", badge_type="gold")
                    w["badge"].pack(side="left", padx=6)
                    if self.addon_mode_vars[a_id].get() == "restore":
                        w["btn_uninstall"].config(text="[ ✓ Revert Requested ]", bg_color=COLOR_RED, fg_color=TEXT_WHITE)
                    else:
                        w["btn_uninstall"].config(text=t("btn_uninstall_addon"), bg_color="#3D1C1C", fg_color=COLOR_RED)
                    w["btn_uninstall"].pack(side="left", padx=8)
                else:
                    w["badge"].pack_forget()
                    w["btn_uninstall"].pack_forget()

    def _on_update_found(self, tag, url):
        self.update_info = (tag, url)
        self.lbl_update_text.config(text=t("update_available", tag))
        self.banner_update.pack(fill="x", padx=20, pady=(0, 6), before=self.header_frame)

    def _open_update_link(self):
        if self.update_info:
            webbrowser.open(self.update_info[1])

    def _log_msg(self, msg):
        self.lbl_status.config(text=msg)
        self.update()

    def _on_apply_clicked(self):
        if not self.selected_rom_path or not os.path.isfile(self.selected_rom_path):
            messagebox.showwarning("Notice", "Please select a valid .nds ROM file first.")
            return

        info = self.current_rom_info or detect_rom(self.selected_rom_path)

        # Check if Multiplayer is enabled on Vanilla but no language chosen
        if not info.has_multiplayer and self.var_mp_enabled.get():
            if not self.var_mp_version.get():
                messagebox.showwarning("Notice", t("err_need_select_mp_lang"))
                self._open_mp_version_dialog()
                return

        # Check if any addon is enabled without a variant chosen
        for addon in ADDONS_REGISTRY:
            a_id = addon["id"]
            if self.addon_enabled_vars[a_id].get() and self.addon_mode_vars[a_id].get() == "apply":
                if not self.addon_variant_vars[a_id].get():
                    messagebox.showwarning("Notice", t("err_need_select_addon_lang", addon["name"]))
                    self._open_addon_config_dialog(a_id)
                    return

        self.btn_apply.config(state="disabled")
        self._log_msg(t("status_patching"))

        t_thread = threading.Thread(target=self._run_patch_pipeline, daemon=True)
        t_thread.start()

    def _run_patch_pipeline(self):
        try:
            rom_path = self.selected_rom_path
            info = self.current_rom_info or detect_rom(rom_path)
            bg_opt = self.var_bg.get()
            cam_opt = self.var_cam.get()

            # Determine effective multiplayer
            if info.has_multiplayer:
                effective_mp = info.mp_lang
            elif self.var_mp_enabled.get():
                effective_mp = self.var_mp_version.get()
            else:
                effective_mp = None

            # Addons state
            sl_enabled = self.addon_enabled_vars.get("soullocke", tk.BooleanVar(value=False)).get()
            sl_mode = self.addon_mode_vars.get("soullocke", tk.StringVar(value="apply")).get()
            sl_variant = self.addon_variant_vars.get("soullocke", tk.StringVar(value="fr")).get()

            # Destination ROM name
            user_output = self.entry_output.get().strip()
            if user_output:
                output_rom = user_output
                if not output_rom.lower().endswith(".nds"):
                    output_rom += ".nds"
            else:
                parent_dir = os.path.dirname(rom_path)
                base_name = os.path.splitext(os.path.basename(rom_path))[0]
                if sl_mode == "restore":
                    out_name = f"{base_name}_Clean.nds"
                elif sl_enabled and effective_mp:
                    out_name = "ProjectPM_FR_SoulLocke.nds" if sl_variant == "fr" else "ProjectPM_USA_SoulLocke.nds"
                elif info and not info.has_multiplayer and effective_mp:
                    out_name = f"ProjectPM_{'FR' if effective_mp == 'fr' else 'USA'}.nds"
                else:
                    out_name = f"{base_name}_modded.nds"
                output_rom = os.path.join(parent_dir, out_name)

            # Prevent accidental silent overwriting of input ROM
            if os.path.abspath(output_rom).lower() == os.path.abspath(rom_path).lower():
                ans = messagebox.askyesno(
                    "Confirm Overwrite",
                    "The destination file is identical to the source ROM.\nPatching in place will modify your original file directly.\n\nDo you want to proceed?"
                )
                if not ans:
                    self._log_msg("Patching cancelled by user.")
                    return

            # Ensure parent folder exists
            os.makedirs(os.path.dirname(os.path.abspath(output_rom)), exist_ok=True)

            # 0. Snapshot randomizer tables if input ROM is randomized
            rand_data = extract_randomizer_data(rom_path, log_cb=self._log_msg)
            if rand_data["is_randomized"]:
                self._log_msg(f"[Pipeline] Preserving {len(rand_data['files'])} randomized tables from source ROM...")

            # 1. Base ROM check: If Vanilla and user wants Multiplayer, apply base xDelta patch!
            working_rom = rom_path
            temp_clean = None
            temp_base = None
            if not info.has_multiplayer and effective_mp in ("fr", "en"):
                self._log_msg(f"[Pipeline] Converting Vanilla ROM to ProjectPM Multiplayer ({effective_mp.upper()})...")
                temp_base = os.path.join(parent_dir, "temp_projectpm_base.nds")
                patch_file = None

                # Check source ROM language for proper patch selection
                if effective_mp == "fr":
                    if info.lang == "fr":
                        patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5_FR.xdelta")
                    else:
                        patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5_FR-From-USA.xdelta")
                else:  # English
                    patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5.xdelta")

                clean_src = rom_path
                if rand_data["is_randomized"]:
                    temp_clean = os.path.join(parent_dir, "temp_vanilla_clean.nds")
                    clean_src = clean_vanilla_for_xdelta(rom_path, temp_clean, lang=info.lang, assets_dir=self.assets_dir, log_cb=self._log_msg)

                xd_exe = os.path.join(self.assets_dir, "xdelta3.exe")
                ok = apply_xdelta(clean_src, patch_file, temp_base, xd_exe, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to apply base ProjectPM patch to Vanilla ROM.")
                working_rom = temp_base

            # 2. Backup Save & ROM if enabled
            if self.var_backup_save.get():
                backup_and_sync_save(rom_path, output_rom, self._log_msg)

            # 3. Apply Mod (SoulLocke or Restore)
            if sl_mode == "restore":
                payload_json = os.path.join(self.payloads_dir, f"soullocke_{info.lang}.json")
                self._log_msg("[Pipeline] Restoring clean ProjectPM...")
                ok = restore_clean_projectpm(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to restore clean ProjectPM.")
            elif sl_enabled and effective_mp:
                target_payload_lang = sl_variant
                payload_json = os.path.join(self.payloads_dir, f"soullocke_{target_payload_lang}.json")
                self._log_msg(f"[Pipeline] Injecting SoulLocke ({target_payload_lang.upper()}) C mod payload...")
                ok = apply_soullocke(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to inject SoulLocke payload.")
            else:
                # Direct copy if no addon applied
                import shutil
                shutil.copy2(working_rom, output_rom)

            # Clean up temporary base & clean files if created
            for temp_f in (temp_clean, temp_base):
                if temp_f and os.path.isfile(temp_f):
                    try:
                        os.remove(temp_f)
                    except Exception:
                        pass

            # 4. Apply Visual+ Options
            if bg_opt == "builtin":
                self._log_msg("[Pipeline] Applying Visual+ Battle Backgrounds...")
                apply_battle_bg_patch(output_rom, self.assets_dir, enable=True, log_cb=self._log_msg)
            elif bg_opt == "off":
                self._log_msg("[Pipeline] Disabling Visual+ Battle Backgrounds...")
                apply_battle_bg_patch(output_rom, self.assets_dir, enable=False, log_cb=self._log_msg)

            if cam_opt == "builtin":
                self._log_msg("[Pipeline] Applying Visual+ 3D Camera...")
                apply_camera_patch(output_rom, enable=True, log_cb=self._log_msg)
            elif cam_opt == "off":
                self._log_msg("[Pipeline] Reverting Visual+ 3D Camera...")
                apply_camera_patch(output_rom, enable=False, log_cb=self._log_msg)

            # 5. Restore Randomizer tables if input was randomized
            if rand_data["is_randomized"]:
                self._log_msg("[Pipeline] Re-applying randomized tables onto destination ROM...")
                restore_randomizer_data(output_rom, rand_data, log_cb=self._log_msg)

            # 6. Apply Custom XDelta Patch if requested
            if self.var_custom_patch_enabled.get():
                custom_patch_file = self.entry_custom_patch.get().strip()
                if custom_patch_file:
                    if not os.path.isfile(custom_patch_file):
                        raise FileNotFoundError(f"Custom XDelta patch file not found: {custom_patch_file}")

                    self._log_msg(f"[Pipeline] Applying custom XDelta patch: {os.path.basename(custom_patch_file)}...")
                    temp_pre_custom = output_rom + ".pre_custom.tmp"
                    import shutil
                    shutil.copy2(output_rom, temp_pre_custom)
                    xd_exe = os.path.join(self.assets_dir, "xdelta3.exe")

                    ok = apply_xdelta(temp_pre_custom, custom_patch_file, output_rom, xd_exe, self._log_msg)
                    if not ok:
                        # Revert on error
                        if os.path.isfile(temp_pre_custom):
                            shutil.copy2(temp_pre_custom, output_rom)
                            os.remove(temp_pre_custom)
                        raise RuntimeError(f"Failed to apply custom XDelta patch ({os.path.basename(custom_patch_file)}). Check that the patch matches this base ROM.")

                    if os.path.isfile(temp_pre_custom):
                        try:
                            os.remove(temp_pre_custom)
                        except Exception:
                            pass
                    self._log_msg("[Pipeline] Custom XDelta patch successfully applied!")

            self._log_msg(t("status_success"))
            messagebox.showinfo("Success", f"{t('status_success')}\n\nOutput: {os.path.basename(output_rom)}")

        except Exception as e:
            self._log_msg(f"{t('status_error')} ({e})")
            messagebox.showerror("Error", f"{t('status_error')}\n\nDetails: {e}")
        finally:
            self.btn_apply.config(state="normal")
