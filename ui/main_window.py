# -*- coding: utf-8 -*-
"""
main_window.py
Main graphical interface for ProjectPM Addon Patcher:
- Platine Moderne pixel-art theme
- Bilingual support with real-time toggle
- Visual+ options with image previews
- Drag & Drop / File selector with automatic ROM analysis
- Save & Randomizer protection
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
        self.geometry("900x780")
        self.minsize(860, 720)
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
        self.var_mode = tk.StringVar(value="soullocke")   # "soullocke", "restore", "none"
        self.var_bg = tk.StringVar(value="keep")          # "builtin", "off", "keep"
        self.var_cam = tk.StringVar(value="keep")         # "builtin", "off", "keep"
        self.var_backup_save = tk.BooleanVar(value=True)

        # Image cache
        self.img_cache = {}

        # Build UI
        self._build_header()
        self._build_rom_section()
        self._build_addons_section()
        self._build_visual_section()
        self._build_save_section()
        self._build_action_section()
        self._build_footer()

        # Check for updates in background
        check_for_updates_async(self._on_update_found)

    def _build_header(self):
        header_frame = tk.Frame(self, bg=BG_DARK)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        # Title + Subtitle
        left_box = tk.Frame(header_frame, bg=BG_DARK)
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
        right_box = tk.Frame(header_frame, bg=BG_DARK)
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

    def _build_rom_section(self):
        self.card_rom = ModernCard(self)
        self.card_rom.pack(fill="x", padx=20, pady=6)

        self.sec_rom_title = tk.Label(
            self.card_rom,
            text=t("section_rom"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_rom_title.pack(anchor="w")

        row = tk.Frame(self.card_rom, bg=BG_CARD)
        row.pack(fill="x", pady=(6, 4))

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

        # Info line
        info_row = tk.Frame(self.card_rom, bg=BG_CARD)
        info_row.pack(fill="x", pady=(4, 0))

        self.badge_rom_status = StatusBadge(info_row, text=t("rom_placeholder"), badge_type="info")
        self.badge_rom_status.pack(side="left")

        self.lbl_rom_sha1 = tk.Label(info_row, text="", bg=BG_CARD, fg=TEXT_MUTED, font=get_font(9))
        self.lbl_rom_sha1.pack(side="right")

    def _build_addons_section(self):
        self.card_addons = ModernCard(self)
        self.card_addons.pack(fill="x", padx=20, pady=6)

        self.sec_addons_title = tk.Label(
            self.card_addons,
            text=t("section_addons"),
            bg=BG_CARD,
            fg=COLOR_PRIMARY,
            font=get_font(11, bold=True)
        )
        self.sec_addons_title.pack(anchor="w", pady=(0, 6))

        # Radio 1: SoulLocke
        row1 = tk.Frame(self.card_addons, bg=BG_CARD)
        row1.pack(fill="x", pady=3)

        self.rb_soullocke = tk.Radiobutton(
            row1,
            text=t("addon_soullocke"),
            variable=self.var_mode,
            value="soullocke",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_GOLD,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_soullocke.pack(side="left")

        self.badge_sl_tag = StatusBadge(row1, text="Soul Link Co-op", badge_type="gold")
        self.badge_sl_tag.pack(side="left", padx=8)

        self.lbl_soullocke_desc = tk.Label(
            self.card_addons,
            text=t("addon_soullocke_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            wraplength=800,
            justify="left"
        )
        self.lbl_soullocke_desc.pack(anchor="w", padx=(25, 0), pady=(0, 8))

        # Radio 2: Restore Clean
        row2 = tk.Frame(self.card_addons, bg=BG_CARD)
        row2.pack(fill="x", pady=3)

        self.rb_restore = tk.Radiobutton(
            row2,
            text=t("addon_restore"),
            variable=self.var_mode,
            value="restore",
            bg=BG_CARD,
            fg=TEXT_WHITE,
            activebackground=BG_CARD,
            activeforeground=COLOR_RED,
            selectcolor=BG_PANEL,
            font=get_font(10, bold=True)
        )
        self.rb_restore.pack(side="left")

        self.lbl_restore_desc = tk.Label(
            self.card_addons,
            text=t("addon_restore_desc"),
            bg=BG_CARD,
            fg=TEXT_MUTED,
            font=get_font(9),
            wraplength=800,
            justify="left"
        )
        self.lbl_restore_desc.pack(anchor="w", padx=(25, 0))

    def _build_visual_section(self):
        self.card_visual = ModernCard(self)
        self.card_visual.pack(fill="x", padx=20, pady=6)

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

        self.lbl_vbg_desc = tk.Label(left_b1, text=t("visual_battle_bg_desc"), bg=BG_PANEL, fg=TEXT_MUTED, font=get_font(9), wraplength=260, justify="left")
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

        self.lbl_vcam_desc = tk.Label(left_b2, text=t("visual_camera_desc"), bg=BG_PANEL, fg=TEXT_MUTED, font=get_font(9), wraplength=260, justify="left")
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
        self.card_save = ModernCard(self)
        self.card_save.pack(fill="x", padx=20, pady=6)

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
        action_frame = tk.Frame(self, bg=BG_DARK)
        action_frame.pack(fill="x", padx=20, pady=10)

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
        footer_frame.pack(side="bottom", fill="x", padx=20, pady=(0, 8))

        self.lbl_footer = tk.Label(
            footer_frame,
            text=t("disclaimer"),
            bg=BG_DARK,
            fg="#555C75",
            font=get_font(8)
        )
        self.lbl_footer.pack()

    # --- Handlers & Actions ---

    def _toggle_language(self):
        new_lang = "fr" if get_lang() == "en" else "en"
        set_lang(new_lang)
        self._refresh_ui_texts()

    def _refresh_ui_texts(self):
        self.btn_lang.config(text="Language: EN" if get_lang() == "en" else "Langue: FR")
        self.lbl_title.config(text=t("app_title"))
        self.lbl_sub.config(text=t("app_subtitle"))
        self.sec_rom_title.config(text=t("section_rom"))
        self.btn_browse.config(text=t("rom_browse"))
        self.sec_addons_title.config(text=t("section_addons"))
        self.rb_soullocke.config(text=t("addon_soullocke"))
        self.lbl_soullocke_desc.config(text=t("addon_soullocke_desc"))
        self.rb_restore.config(text=t("addon_restore"))
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
        self._update_rom_display(info)

    def _update_rom_display(self, info):
        if not info.exists:
            self.badge_rom_status.set_badge(t("rom_unknown"), badge_type="danger")
            return

        # Badge type & text
        b_type = "success" if info.category == "projectpm" else "gold"
        self.badge_rom_status.set_badge(f"{info.display_name} ({info.size // (1024*1024)} MB)", badge_type=b_type)
        self.lbl_rom_sha1.config(text=f"SHA1: {info.sha1[:10]}...")

        # Save status
        if info.companion_save:
            save_name = os.path.basename(info.companion_save)
            msg = t("save_detected", save_name)
            if info.has_rand_sidecar:
                msg += " | " + t("rand_detected")
            self.lbl_save_status.config(text=msg, fg=TEXT_GREEN)
        else:
            self.lbl_save_status.config(text=t("save_none"), fg=TEXT_MUTED)

        # Preselect Visual options
        if info.has_visual_bg:
            self.var_bg.set("builtin")
        if info.has_visual_cam:
            self.var_cam.set("builtin")

        self.lbl_status.config(text=t("status_ready"), fg=TEXT_WHITE)

    def _on_update_found(self, tag, url):
        self.update_info = (tag, url)
        self.lbl_update_text.config(text=t("update_available", tag))
        self.banner_update.pack(fill="x", padx=20, pady=(0, 6), before=self.card_rom)

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
            mode = self.var_mode.get()
            bg_opt = self.var_bg.get()
            cam_opt = self.var_cam.get()
            lang = info.lang

            # Destination ROM name
            parent_dir = os.path.dirname(rom_path)
            base_name = os.path.splitext(os.path.basename(rom_path))[0]
            
            if mode == "soullocke":
                out_name = "ProjectPM_FR_SoulLocke.nds" if lang == "fr" else "ProjectPM_USA_SoulLocke.nds"
            else:
                out_name = f"{base_name}_patched.nds"
            
            output_rom = os.path.join(parent_dir, out_name)

            # 1. Base ROM check: If Vanilla, run xDelta base patch first!
            working_rom = rom_path
            if info.category == "vanilla":
                self._log_msg("[Pipeline] Converting Vanilla ROM to ProjectPM...")
                temp_base = os.path.join(parent_dir, "temp_projectpm_base.nds")
                patch_file = None
                if info.lang == "fr":
                    patch_file = os.path.join(self.assets_dir, "base_patches", "PlatinumMultiplayerV0.4.5_FR.xdelta")
                else:
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
            payload_json = os.path.join(self.payloads_dir, f"soullocke_{lang}.json")
            if mode == "soullocke":
                self._log_msg("[Pipeline] Injecting SoulLocke C mod payload...")
                ok = apply_soullocke(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to inject SoulLocke payload.")
            elif mode == "restore":
                self._log_msg("[Pipeline] Restoring clean ProjectPM...")
                ok = restore_clean_projectpm(working_rom, output_rom, payload_json, self._log_msg)
                if not ok:
                    raise RuntimeError("Failed to restore clean ProjectPM.")
            else:
                # Direct copy if no mode
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
