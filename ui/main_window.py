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
        self.var_mp_base = tk.StringVar(value="none")     # "installed", "fr", "en", "none"
        self.var_sl_mode = tk.StringVar(value="none")     # "soullocke_fr", "soullocke_en", "restore", "none"
        self.var_bg = tk.StringVar(value="keep")          # "builtin", "off", "keep"
        self.var_cam = tk.StringVar(value="keep")         # "builtin", "off", "keep"
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

        # Radio options frame
        self.frame_mp_opts = tk.Frame(self.card_mp, bg=BG_CARD)
        self.frame_mp_opts.pack(fill="x")

        # Option: Keep Vanilla
        row0 = tk.Frame(self.frame_mp_opts, bg=BG_CARD)
        row0.pack(fill="x", pady=2)
        self.rb_mp_vanilla = tk.Radiobutton(
            row0,
            text=t("mp_opt_keep_vanilla"),
            variable=self.var_mp_base,
            value="none",
            command=self._on_mp_base_changed,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_PRIMARY,
            selectcolor=BG_PANEL,
            font=get_font(10)
        )
        self.rb_mp_vanilla.pack(side="left")

        # Option: FR Multiplayer
        row1 = tk.Frame(self.frame_mp_opts, bg=BG_CARD)
        row1.pack(fill="x", pady=2)
        self.rb_mp_fr = tk.Radiobutton(
            row1,
            text=t("mp_opt_fr"),
            variable=self.var_mp_base,
            value="fr",
            command=self._on_mp_base_changed,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_PRIMARY,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_mp_fr.pack(side="left")

        self.badge_mp_fr_status = StatusBadge(row1, text="", badge_type="success")

        # Option: EN Multiplayer
        row2 = tk.Frame(self.frame_mp_opts, bg=BG_CARD)
        row2.pack(fill="x", pady=2)
        self.rb_mp_en = tk.Radiobutton(
            row2,
            text=t("mp_opt_en"),
            variable=self.var_mp_base,
            value="en",
            command=self._on_mp_base_changed,
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_PRIMARY,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_mp_en.pack(side="left")

        self.badge_mp_en_status = StatusBadge(row2, text="", badge_type="success")

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

        self.lbl_soullocke_desc = tk.Label(
            self.card_addons,
            text=t("addon_soullocke_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            wraplength=820,
            justify="left"
        )
        self.lbl_soullocke_desc.pack(anchor="w", pady=(0, 6))

        # Radio 1: SoulLocke Français
        row_fr = tk.Frame(self.card_addons, bg=BG_CARD)
        row_fr.pack(fill="x", pady=3)

        self.rb_sl_fr = tk.Radiobutton(
            row_fr,
            text=t("addon_soullocke_fr"),
            variable=self.var_sl_mode,
            value="soullocke_fr",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_GOLD,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_sl_fr.pack(side="left")

        self.badge_sl_fr_lock = StatusBadge(row_fr, text="", badge_type="danger")

        # Radio 2: SoulLocke English
        row_en = tk.Frame(self.card_addons, bg=BG_CARD)
        row_en.pack(fill="x", pady=3)

        self.rb_sl_en = tk.Radiobutton(
            row_en,
            text=t("addon_soullocke_en"),
            variable=self.var_sl_mode,
            value="soullocke_en",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_GOLD,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_sl_en.pack(side="left")

        self.badge_sl_en_lock = StatusBadge(row_en, text="", badge_type="danger")

        # Radio 3: None / Do not add
        row_none = tk.Frame(self.card_addons, bg=BG_CARD)
        row_none.pack(fill="x", pady=3)

        self.rb_sl_none = tk.Radiobutton(
            row_none,
            text=t("addon_none"),
            variable=self.var_sl_mode,
            value="none",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=TEXT_WHITE,
            selectcolor=BG_PANEL,
            font=get_font(10)
        )
        self.rb_sl_none.pack(side="left")

        # Radio 4: Restore Clean ProjectPM
        row_res = tk.Frame(self.card_addons, bg=BG_CARD)
        row_res.pack(fill="x", pady=3)

        self.rb_sl_restore = tk.Radiobutton(
            row_res,
            text=t("addon_restore"),
            variable=self.var_sl_mode,
            value="restore",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_RED,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_sl_restore.pack(side="left")

        self.lbl_restore_desc = tk.Label(
            self.card_addons,
            text=t("addon_restore_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            wraplength=820,
            justify="left"
        )
        self.lbl_restore_desc.pack(anchor="w", padx=(25, 0))

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
        self.rb_mp_vanilla.config(text=t("mp_opt_keep_vanilla"))
        self.rb_mp_fr.config(text=t("mp_opt_fr"))
        self.rb_mp_en.config(text=t("mp_opt_en"))
        self.sec_addons_title.config(text=t("section_addons"))
        self.lbl_soullocke_desc.config(text=t("addon_soullocke_desc"))
        self.rb_sl_fr.config(text=t("addon_soullocke_fr"))
        self.rb_sl_en.config(text=t("addon_soullocke_en"))
        self.rb_sl_none.config(text=t("addon_none"))
        self.rb_sl_restore.config(text=t("addon_restore"))
        self.lbl_restore_desc.config(text=t("addon_restore_desc"))
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
        self.sec_save_title.config(text=t("section_save"))
        self.cb_save.config(text=t("save_preserve_checkbox"))
        self.btn_apply.config(text=t("btn_apply"))
        self.lbl_footer.config(text=t("disclaimer"))

        if self.current_rom_info:
            self._update_rom_display(self.current_rom_info)
        else:
            self.badge_rom_status.set_badge(t("rom_placeholder"), badge_type="info")
            self.lbl_status.config(text=t("status_ready"))

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
        sl_mode = self.var_sl_mode.get()

        if info and info.has_multiplayer:
            effective_mp = info.mp_lang
        else:
            effective_mp = self.var_mp_base.get()

        target_lang = "fr" if (sl_mode == "soullocke_fr" or effective_mp == "fr") else "en"

        if sl_mode in ("soullocke_fr", "soullocke_en"):
            out_name = "ProjectPM_FR_SoulLocke.nds" if target_lang == "fr" else "ProjectPM_USA_SoulLocke.nds"
        elif sl_mode == "restore":
            out_name = f"{base_name}_Clean.nds"
        elif info and not info.has_multiplayer and effective_mp in ("fr", "en"):
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

        if info.has_visual_cam:
            self.badge_feat_vcam.set_badge(t("badge_vcam_yes"), badge_type="success")
            self.var_cam.set("builtin")
        else:
            self.badge_feat_vcam.set_badge("Visual+ Cam: Off", badge_type="info")

        # Save status
        if info.companion_save:
            save_name = os.path.basename(info.companion_save)
            msg = t("save_detected", save_name)
            if info.has_rand_sidecar:
                msg += " | " + t("rand_detected")
            self.lbl_save_status.config(text=msg, fg=TEXT_GREEN)
        else:
            self.lbl_save_status.config(text=t("save_none"), fg=TEXT_MUTED)

        # Update Multiplayer Base section
        if info.has_multiplayer:
            self.lbl_mp_desc.config(text=t("mp_installed_desc"), fg=COLOR_GOLD)
            # Select detected multiplayer language
            self.var_mp_base.set(info.mp_lang)
            # Gray out / disable radio buttons since it's already installed
            self.rb_mp_vanilla.config(state="disabled")
            self.rb_mp_fr.config(state="disabled")
            self.rb_mp_en.config(state="disabled")
            
            # Show "Already Installed" badge on the active option
            if info.mp_lang == "fr":
                self.badge_mp_fr_status.set_badge(f"[{t('badge_already_installed')}]", badge_type="success")
                self.badge_mp_fr_status.pack(side="left", padx=8)
                self.badge_mp_en_status.pack_forget()
            else:
                self.badge_mp_en_status.set_badge(f"[{t('badge_already_installed')}]", badge_type="success")
                self.badge_mp_en_status.pack(side="left", padx=8)
                self.badge_mp_fr_status.pack_forget()
        else:
            self.lbl_mp_desc.config(text=t("mp_vanilla_desc"), fg=TEXT_MUTED)
            self.rb_mp_vanilla.config(state="normal")
            self.rb_mp_fr.config(state="normal")
            self.rb_mp_en.config(state="normal")
            self.badge_mp_fr_status.pack_forget()
            self.badge_mp_en_status.pack_forget()
            # Default to French if Vanilla FR, or English if Vanilla US
            self.var_mp_base.set(info.lang if info.lang in ("fr", "en") else "fr")

        # Update Addon dependencies
        self._update_addon_dependencies()

        self.lbl_status.config(text=t("status_ready"), fg=TEXT_WHITE)

    def _on_mp_base_changed(self):
        self._update_addon_dependencies()

    def _update_addon_dependencies(self):
        info = self.current_rom_info
        if not info:
            return

        # Determine effective multiplayer status and language
        if info.has_multiplayer:
            effective_mp = info.mp_lang
        else:
            effective_mp = self.var_mp_base.get()

        # Update SoulLocke options based on effective multiplayer
        if effective_mp == "none":
            # ROM is Vanilla and no Multiplayer selected -> SoulLocke completely disabled!
            self.rb_sl_fr.config(state="disabled")
            self.rb_sl_en.config(state="disabled")
            self.badge_sl_fr_lock.set_badge(f"[{t('badge_incompatible_req_mp')}]", badge_type="danger")
            self.badge_sl_fr_lock.pack(side="left", padx=8)
            self.badge_sl_en_lock.pack_forget()
            if self.var_sl_mode.get() in ("soullocke_fr", "soullocke_en"):
                self.var_sl_mode.set("none")
        elif effective_mp == "fr":
            # French Multiplayer -> French SoulLocke enabled, English disabled
            self.rb_sl_fr.config(state="normal")
            self.badge_sl_fr_lock.pack_forget()

            self.rb_sl_en.config(state="disabled")
            self.badge_sl_en_lock.set_badge(f"[{t('badge_incompatible_lang')}]", badge_type="danger")
            self.badge_sl_en_lock.pack(side="left", padx=8)

            if self.var_sl_mode.get() == "soullocke_en":
                self.var_sl_mode.set("soullocke_fr")
            elif self.var_sl_mode.get() == "none" and not info.is_soullocke:
                self.var_sl_mode.set("soullocke_fr")
        elif effective_mp == "en":
            # English Multiplayer -> English SoulLocke enabled, French disabled
            self.rb_sl_en.config(state="normal")
            self.badge_sl_en_lock.pack_forget()

            self.rb_sl_fr.config(state="disabled")
            self.badge_sl_fr_lock.set_badge(f"[{t('badge_incompatible_lang')}]", badge_type="danger")
            self.badge_sl_fr_lock.pack(side="left", padx=8)

            if self.var_sl_mode.get() == "soullocke_fr":
                self.var_sl_mode.set("soullocke_en")
            elif self.var_sl_mode.get() == "none" and not info.is_soullocke:
                self.var_sl_mode.set("soullocke_en")

        # Restore Clean ProjectPM option: enabled if SoulLocke is active
        if info.is_soullocke:
            self.rb_sl_restore.config(state="normal")
        else:
            self.rb_sl_restore.config(state="disabled")

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

        self.btn_apply.config(state="disabled")
        self._log_msg(t("status_patching"))

        t_thread = threading.Thread(target=self._run_patch_pipeline, daemon=True)
        t_thread.start()

    def _run_patch_pipeline(self):
        try:
            rom_path = self.selected_rom_path
            info = self.current_rom_info or detect_rom(rom_path)
            sl_mode = self.var_sl_mode.get()
            bg_opt = self.var_bg.get()
            cam_opt = self.var_cam.get()
            
            # Determine effective multiplayer and target language
            if info.has_multiplayer:
                effective_mp = info.mp_lang
            else:
                effective_mp = self.var_mp_base.get()

            target_lang = "fr" if (sl_mode == "soullocke_fr" or effective_mp == "fr") else "en"

            # Destination ROM name
            user_output = self.entry_output.get().strip()
            if user_output:
                output_rom = user_output
                if not output_rom.lower().endswith(".nds"):
                    output_rom += ".nds"
            else:
                parent_dir = os.path.dirname(rom_path)
                base_name = os.path.splitext(os.path.basename(rom_path))[0]
                if sl_mode in ("soullocke_fr", "soullocke_en"):
                    out_name = "ProjectPM_FR_SoulLocke.nds" if target_lang == "fr" else "ProjectPM_USA_SoulLocke.nds"
                elif sl_mode == "restore":
                    out_name = f"{base_name}_Clean.nds"
                elif not info.has_multiplayer and effective_mp in ("fr", "en"):
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

            # 1. Base ROM check: If Vanilla and user wants Multiplayer, apply base xDelta patch!
            working_rom = rom_path
            if not info.has_multiplayer and effective_mp in ("fr", "en"):
                self._log_msg("[Pipeline] Converting Vanilla ROM to ProjectPM Multiplayer...")
                temp_base = os.path.join(parent_dir, "temp_projectpm_base.nds")
                patch_file = None
                
                # Check source ROM language for proper patch selection
                if effective_mp == "fr":
                    if info.lang == "fr":
                        patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5_FR.xdelta")
                    else:
                        patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5_FR-From-USA.xdelta")
                else: # English
                    patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5.xdelta")

                xd_exe = os.path.join(self.assets_dir, "xdelta3.exe")
                ok = apply_xdelta(rom_path, patch_file, temp_base, xd_exe, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to apply base ProjectPM patch to Vanilla ROM.")
                working_rom = temp_base

            # 2. Backup Save & ROM if enabled
            if self.var_backup_save.get():
                backup_and_sync_save(rom_path, output_rom, self._log_msg)

            # 3. Apply Mod (SoulLocke or Restore)
            if sl_mode in ("soullocke_fr", "soullocke_en"):
                payload_json = os.path.join(self.payloads_dir, f"soullocke_{target_lang}.json")
                self._log_msg(f"[Pipeline] Injecting SoulLocke ({target_lang.upper()}) C mod payload...")
                ok = apply_soullocke(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to inject SoulLocke payload.")
            elif sl_mode == "restore":
                payload_json = os.path.join(self.payloads_dir, f"soullocke_{info.lang}.json")
                self._log_msg("[Pipeline] Restoring clean ProjectPM...")
                ok = restore_clean_projectpm(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to restore clean ProjectPM.")
            else:
                # Direct copy if no addon mode
                import shutil
                shutil.copy2(working_rom, output_rom)

            # Clean up temp base if created
            if working_rom != rom_path and os.path.isfile(working_rom):
                try:
                    os.remove(working_rom)
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

            self._log_msg(t("status_success"))
            messagebox.showinfo("Success", f"{t('status_success')}\n\nOutput: {os.path.basename(output_rom)}")

        except Exception as e:
            self._log_msg(f"{t('status_error')} ({e})")
            messagebox.showerror("Error", f"{t('status_error')}\n\nDetails: {e}")
        finally:
            self.btn_apply.config(state="normal")
