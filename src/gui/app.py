"""CustomTkinter Desktop GUI for Antigravity Fixer — Fluent Design v2.1."""

import threading
import customtkinter as ctk
from tkinter import filedialog

from src.core import fixer, process
from src.core.fixer import Callbacks
from src.i18n import t, set_lang, get_lang


# ─── Theme ────────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ─── Design Tokens (Fluent / Win11) ──────────────────────────────────────────

SIDEBAR_BG = "#252525"
MAIN_BG = "#2b2b2b"
ROW_HOVER = "#333333"
ROW_SELECTED = "#383838"
ACCENT = "#0078D4"
ACCENT_HOVER = "#005FB8"
TEXT_PRIMARY = "#e4e4e4"
TEXT_SECONDARY = "#999999"
TEXT_MUTED = "#666666"
SUCCESS = "#10b981"
WARNING = "#f59e0b"
DANGER = "#ef4444"
CORNER_RADIUS = 6
FONT_FAMILY = "Segoe UI Variable"  # Win11 native; CTk falls back to Segoe UI
DISABLED_TEXT = "#444444"           # Clearly dimmed text for disabled buttons
DISABLED_FG = "#2a2a2a"            # Dimmed background for disabled primary button

# Badge config: text label + tint color
SOURCE_BADGES = {
    "brain":     {"vi": "BRAIN",     "en": "BRAIN",     "color": "#10b981"},
    "preserved": {"vi": "ĐÃ LƯU",   "en": "SAVED",     "color": "#3b82f6"},
    "fallback":  {"vi": "DỰ PHÒNG",  "en": "FALLBACK",  "color": "#f59e0b"},
}


# ─── Main App ─────────────────────────────────────────────────────────────────

class AntigravityFixerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{t('app_title')} {t('app_version')}")
        self.geometry("820x560")
        self.minsize(700, 480)

        self.conversations = []
        self.ws_assignments = {}
        self.selected_conv_id = None
        self.conv_rows = []

        self._build_ui()
        self._check_antigravity()

    # ═══════════════════════════════════════════════════════════════════════
    #  UI Construction — 2-Column Layout
    # ═══════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        """Build the 2-column Fluent-style layout."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0, minsize=220)    # Sidebar
        self.grid_columnconfigure(1, weight=1)                  # Main

        self._build_sidebar()
        self._build_main_area()

    # ── Sidebar (Left Column) ────────────────────────────────────────────

    def _build_sidebar(self):
        """Left column: App info, status, scan button, language toggle."""
        self.sidebar = ctk.CTkFrame(
            self,
            fg_color=SIDEBAR_BG,
            corner_radius=0,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)  # spacer row pushes footer down
        self.sidebar.grid_columnconfigure(0, weight=1)

        # ── App Title ────────────────────────────────────────────────────
        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text=t("app_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(24, 0))

        self.version_label = ctk.CTkLabel(
            self.sidebar,
            text=t("app_version"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.version_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 16))

        # ── Divider ─────────────────────────────────────────────────────
        divider1 = ctk.CTkFrame(self.sidebar, height=1, fg_color="#3a3a3a")
        divider1.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

        # ── Status Indicator ─────────────────────────────────────────────
        status_container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        status_container.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 4))
        status_container.grid_columnconfigure(1, weight=1)

        self.status_dot = ctk.CTkLabel(
            status_container,
            text="●",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=TEXT_MUTED,
            width=16,
        )
        self.status_dot.grid(row=0, column=0, sticky="w")

        self.status_label = ctk.CTkLabel(
            status_container,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.status_label.grid(row=0, column=1, sticky="w", padx=(4, 0))

        # ── Count Label ──────────────────────────────────────────────────
        self.count_label = ctk.CTkLabel(
            self.sidebar,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.count_label.grid(row=4, column=0, sticky="w", padx=20, pady=(0, 16))

        # ── Scan Button ──────────────────────────────────────────────────
        self.scan_btn = ctk.CTkButton(
            self.sidebar,
            text=t("btn_scan"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            height=36,
            corner_radius=CORNER_RADIUS,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color="#3a3a3a",
            text_color=TEXT_PRIMARY,
            text_color_disabled=DISABLED_TEXT,
            command=self._on_scan,
        )
        self.scan_btn.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))

        # ── Spacer (row 6 — weight=1) ───────────────────────────────────

        # ── Sidebar Footer: Language toggle ─────────────────────────────
        self.lang_btn = ctk.CTkButton(
            self.sidebar,
            text=t("lang_switch"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            height=28,
            corner_radius=CORNER_RADIUS,
            fg_color="transparent",
            hover_color="#3a3a3a",
            text_color=TEXT_MUTED,
            command=self._toggle_language,
        )
        self.lang_btn.grid(row=7, column=0, sticky="ew", padx=16, pady=(0, 16))

    # ── Main Area (Right Column) ─────────────────────────────────────────

    def _build_main_area(self):
        """Right column: conversation list, progress, action buttons."""
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=MAIN_BG,
            corner_radius=0,
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)  # list area expands
        self.main_frame.grid_columnconfigure(0, weight=1)

        self._build_main_header()
        self._build_conversation_list()
        self._build_bottom_bar()

    def _build_main_header(self):
        """Header row in main area: summary text + workspace assign button."""
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        header.grid_columnconfigure(0, weight=1)

        self.main_title = ctk.CTkLabel(
            header,
            text=t("col_title"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            text_color=TEXT_PRIMARY,
            anchor="w",
        )
        self.main_title.grid(row=0, column=0, sticky="w")

        self.selected_info = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_MUTED,
            anchor="e",
        )
        self.selected_info.grid(row=0, column=1, sticky="e", padx=(0, 8))

        self.ws_btn = ctk.CTkButton(
            header,
            text=t("btn_assign_ws"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            width=140,
            height=28,
            corner_radius=CORNER_RADIUS,
            fg_color="transparent",
            border_width=1,
            border_color="#3a3a3a",
            hover_color="#3a3a3a",
            text_color=TEXT_SECONDARY,
            text_color_disabled=DISABLED_TEXT,
            state="disabled",
            command=self._on_assign_workspace,
        )
        self.ws_btn.grid(row=0, column=2, sticky="e")

    def _build_conversation_list(self):
        """Scrollable conversation list with column headers."""
        list_container = ctk.CTkFrame(
            self.main_frame,
            fg_color="#303030",
            corner_radius=CORNER_RADIUS,
        )
        list_container.grid(row=1, column=0, sticky="nsew", padx=16, pady=(4, 8))
        list_container.grid_rowconfigure(1, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # ── Column Headers ───────────────────────────────────────────────
        header_frame = ctk.CTkFrame(list_container, fg_color="transparent", height=28)
        header_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        header_frame.grid_columnconfigure(1, weight=1)

        hdr_font = ctk.CTkFont(family=FONT_FAMILY, size=11)
        hdr_color = TEXT_MUTED

        self.hdr_num = ctk.CTkLabel(header_frame, text=t("col_num"), width=32, font=hdr_font, text_color=hdr_color, anchor="e")
        self.hdr_num.grid(row=0, column=0, padx=(4, 8))
        self.hdr_title = ctk.CTkLabel(header_frame, text=t("col_title"), font=hdr_font, text_color=hdr_color, anchor="w")
        self.hdr_title.grid(row=0, column=1, sticky="w")
        self.hdr_source = ctk.CTkLabel(header_frame, text=t("col_source"), width=80, font=hdr_font, text_color=hdr_color)
        self.hdr_source.grid(row=0, column=2, padx=4)
        self.hdr_ws = ctk.CTkLabel(header_frame, text=t("col_workspace"), width=32, font=hdr_font, text_color=hdr_color)
        self.hdr_ws.grid(row=0, column=3, padx=(4, 8))

        # ── Scrollable List ──────────────────────────────────────────────
        self.conv_scroll = ctk.CTkScrollableFrame(
            list_container,
            fg_color="transparent",
        )
        self.conv_scroll.grid(row=1, column=0, sticky="nsew", padx=4, pady=(2, 6))
        self.conv_scroll.grid_columnconfigure(1, weight=1)

        # ── Empty State ──────────────────────────────────────────────────
        self.empty_label = ctk.CTkLabel(
            self.conv_scroll,
            text=t("empty_state"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
            wraplength=320,
        )
        self.empty_label.grid(row=0, column=0, columnspan=4, pady=60)

    def _build_bottom_bar(self):
        """Progress bar + action buttons at the bottom of main area."""
        bottom = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        bottom.grid_columnconfigure(0, weight=1)

        # ── Progress ─────────────────────────────────────────────────────
        self.progress_bar = ctk.CTkProgressBar(
            bottom,
            height=3,
            corner_radius=2,
            progress_color=ACCENT,
        )
        self.progress_bar.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 6))
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            bottom,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        self.progress_label.grid(row=1, column=0, sticky="w")

        # ── Action Buttons ───────────────────────────────────────────────
        btn_container = ctk.CTkFrame(bottom, fg_color="transparent")
        btn_container.grid(row=1, column=1, columnspan=3, sticky="e")

        self.fix_btn = ctk.CTkButton(
            btn_container,
            text=t("btn_fix"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            width=120,
            height=32,
            corner_radius=CORNER_RADIUS,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            text_color_disabled=DISABLED_TEXT,
            state="disabled",
            command=self._on_fix,
        )
        self.fix_btn.pack(side="left", padx=(0, 6))

        self.launch_btn = ctk.CTkButton(
            btn_container,
            text=t("btn_launch"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            width=140,
            height=32,
            corner_radius=CORNER_RADIUS,
            fg_color="transparent",
            border_width=1,
            border_color="#3a3a3a",
            hover_color="#3a3a3a",
            text_color=TEXT_SECONDARY,
            text_color_disabled=DISABLED_TEXT,
            state="disabled",
            command=self._on_launch,
        )
        self.launch_btn.pack(side="left", padx=(0, 6))

        self.close_btn = ctk.CTkButton(
            btn_container,
            text=t("btn_close"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            width=80,
            height=32,
            corner_radius=CORNER_RADIUS,
            fg_color="transparent",
            hover_color="#3a3a3a",
            text_color=TEXT_MUTED,
            command=self.destroy,
        )
        self.close_btn.pack(side="left")

    # ═══════════════════════════════════════════════════════════════════════
    #  Antigravity Process Check
    # ═══════════════════════════════════════════════════════════════════════

    def _check_antigravity(self):
        """Check if Antigravity is running and update sidebar status."""
        if process.is_antigravity_running():
            self.status_dot.configure(text_color=WARNING)
            self.status_label.configure(
                text=t("ag_running_short"),
                text_color=WARNING,
            )
            self.scan_btn.configure(state="disabled")
            self._show_infobar()
        else:
            self._hide_infobar()
            self.status_dot.configure(text_color=SUCCESS)
            self.status_label.configure(
                text=t("ag_not_running_short"),
                text_color=SUCCESS,
            )

    def _show_infobar(self):
        """Show an inline InfoBar in the sidebar warning that Antigravity is running."""
        # Remove existing infobar if any
        self._hide_infobar()

        self.infobar = ctk.CTkFrame(
            self.sidebar,
            fg_color="#3d2e00",
            corner_radius=CORNER_RADIUS,
        )
        # Insert after the scan button (row 5) — use row 5 and shift scan to after
        # Actually, insert between divider and status: put it after count_label area
        self.infobar.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))
        # Shift scan button down
        self.scan_btn.grid(row=8, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.infobar.grid_columnconfigure(0, weight=1)

        infobar_text = ctk.CTkLabel(
            self.infobar,
            text=t("ag_running_detail"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color="#fbbf24",
            anchor="w",
            wraplength=170,
        )
        infobar_text.grid(row=0, column=0, sticky="w", padx=10, pady=(8, 4))

        kill_btn = ctk.CTkButton(
            self.infobar,
            text=t("btn_kill_ag"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            height=28,
            corner_radius=4,
            fg_color="#b45309",
            hover_color="#92400e",
            text_color="#fff",
            command=self._on_kill_antigravity,
        )
        kill_btn.grid(row=1, column=0, sticky="ew", padx=10, pady=(2, 8))

    def _hide_infobar(self):
        """Remove inline InfoBar if it exists."""
        if hasattr(self, "infobar") and self.infobar is not None:
            self.infobar.destroy()
            self.infobar = None
            # Restore scan button position
            self.scan_btn.grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 8))

    def _on_kill_antigravity(self):
        """Handle kill button click from InfoBar."""
        if process.kill_antigravity():
            self.status_dot.configure(text_color=SUCCESS)
            self.status_label.configure(
                text=t("ag_kill_success_short"),
                text_color=SUCCESS,
            )
            self.scan_btn.configure(state="normal")
            self._hide_infobar()
        else:
            self.status_dot.configure(text_color=DANGER)
            self.status_label.configure(
                text=t("ag_kill_fail_short"),
                text_color=DANGER,
            )

    # ═══════════════════════════════════════════════════════════════════════
    #  Button State Helpers
    # ═══════════════════════════════════════════════════════════════════════

    def _set_fix_enabled(self):
        """Enable the Fix button with full accent color."""
        self.fix_btn.configure(state="normal", fg_color=ACCENT)

    def _set_fix_disabled(self):
        """Disable the Fix button with dimmed appearance."""
        self.fix_btn.configure(state="disabled", fg_color=DISABLED_FG)

    def _set_launch_enabled(self):
        """Enable Launch button with visible border."""
        self.launch_btn.configure(state="normal", border_color="#555555")

    def _set_launch_disabled(self):
        """Disable Launch button with dimmed border."""
        self.launch_btn.configure(state="disabled", border_color="#3a3a3a")

    def _set_ws_enabled(self):
        """Enable Workspace button with visible border."""
        self.ws_btn.configure(state="normal", border_color="#555555")

    def _set_ws_disabled(self):
        """Disable Workspace button with dimmed border."""
        self.ws_btn.configure(state="disabled", border_color="#3a3a3a")

    # ═══════════════════════════════════════════════════════════════════════
    #  Scan
    # ═══════════════════════════════════════════════════════════════════════

    def _on_scan(self):
        """Start scanning in a background thread."""
        self.scan_btn.configure(state="disabled")
        self._set_fix_disabled()
        self.progress_bar.set(0)
        self.progress_label.configure(text=t("scanning"))

        thread = threading.Thread(target=self._scan_worker, daemon=True)
        thread.start()

    def _scan_worker(self):
        """Background scan worker."""
        def on_progress(msg, pct):
            self.after(0, lambda: self.progress_bar.set(pct))
            self.after(0, lambda: self.progress_label.configure(
                text=f"{t('scanning')} {int(pct * 100)}%"
            ))

        def on_error(msg):
            self.after(0, lambda: self.progress_label.configure(
                text=msg, text_color=DANGER,
            ))

        callbacks = Callbacks(on_progress=on_progress, on_error=on_error)

        try:
            self.conversations = fixer.scan(callbacks)
        except RuntimeError:
            self.after(0, lambda: self.scan_btn.configure(state="normal"))
            return

        # Auto-assign workspaces
        self.ws_assignments = fixer.auto_assign_workspaces(self.conversations)

        self.after(0, self._scan_complete)

    def _scan_complete(self):
        """Update UI after scan completes."""
        n = len(self.conversations)
        self.count_label.configure(text=t("found_n", n=n))
        self.progress_bar.set(1.0)
        self.progress_label.configure(text="")
        self.scan_btn.configure(state="normal")

        if self.conversations:
            self._set_fix_enabled()
            self._populate_conversation_list()

    # ═══════════════════════════════════════════════════════════════════════
    #  Conversation List
    # ═══════════════════════════════════════════════════════════════════════

    def _populate_conversation_list(self):
        """Fill the scrollable list with conversation rows."""
        for widget in self.conv_scroll.winfo_children():
            widget.destroy()
        self.conv_rows = []
        self.selected_conv_id = None
        self._set_ws_disabled()
        self.selected_info.configure(text="")

        if not self.conversations:
            # Re-show empty state
            self.empty_label = ctk.CTkLabel(
                self.conv_scroll,
                text=t("empty_state"),
                font=ctk.CTkFont(family=FONT_FAMILY, size=12),
                text_color=TEXT_MUTED,
                wraplength=320,
            )
            self.empty_label.grid(row=0, column=0, columnspan=4, pady=60)
            return

        for i, conv in enumerate(self.conversations):
            row = self._create_conv_row(i, conv)
            self.conv_rows.append(row)

    def _create_conv_row(self, index, conv):
        """Create a single conversation row with text badges."""
        has_ws = conv.has_workspace or conv.id in self.ws_assignments

        row_frame = ctk.CTkFrame(
            self.conv_scroll,
            fg_color="transparent",
            corner_radius=4,
            cursor="hand2",
            height=32,
        )
        row_frame.grid(row=index, column=0, sticky="ew", pady=1, padx=2)
        self.conv_scroll.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        # ── Number ───────────────────────────────────────────────────────
        num_label = ctk.CTkLabel(
            row_frame,
            text=str(index + 1),
            width=32,
            anchor="e",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_MUTED,
        )
        num_label.grid(row=0, column=0, padx=(4, 8))

        # ── Title ────────────────────────────────────────────────────────
        title_text = conv.title[:55] if len(conv.title) > 55 else conv.title
        title_label = ctk.CTkLabel(
            row_frame,
            text=title_text,
            anchor="w",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=TEXT_PRIMARY,
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(0, 8))

        # ── Source Badge ─────────────────────────────────────────────────
        lang = get_lang()
        badge_info = SOURCE_BADGES.get(conv.source, {"vi": "?", "en": "?", "color": TEXT_MUTED})
        badge_text = badge_info.get(lang, badge_info["en"])

        source_label = ctk.CTkLabel(
            row_frame,
            text=badge_text,
            width=80,
            font=ctk.CTkFont(family=FONT_FAMILY, size=9, weight="bold"),
            text_color=badge_info["color"],
            fg_color="#3a3a3a",
            corner_radius=3,
            padx=6,
            pady=1,
        )
        source_label.grid(row=0, column=2, padx=4)

        # ── Workspace Checkmark ──────────────────────────────────────────
        ws_text = "✓" if has_ws else "✕"
        ws_color = SUCCESS if has_ws else TEXT_MUTED
        ws_label = ctk.CTkLabel(
            row_frame,
            text=ws_text,
            width=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=ws_color,
        )
        ws_label.grid(row=0, column=3, padx=(4, 8))

        # ── Click & Hover ────────────────────────────────────────────────
        def on_click(event, cid=conv.id, title=conv.title):
            self._select_conversation(cid, title)

        def on_enter(event, frame=row_frame):
            if self.selected_conv_id != conv.id:
                frame.configure(fg_color=ROW_HOVER)

        def on_leave(event, frame=row_frame):
            if self.selected_conv_id != conv.id:
                frame.configure(fg_color="transparent")

        for widget in [row_frame, num_label, title_label, source_label, ws_label]:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)

        return row_frame

    def _select_conversation(self, conv_id, title):
        """Handle conversation row selection."""
        self.selected_conv_id = conv_id
        short_title = title[:35] if len(title) > 35 else title
        self.selected_info.configure(text=f"#{conv_id[:8]}… — {short_title}")
        self._set_ws_enabled()

        # Highlight selected row, clear others
        for i, row in enumerate(self.conv_rows):
            if self.conversations[i].id == conv_id:
                row.configure(fg_color=ROW_SELECTED)
            else:
                row.configure(fg_color="transparent")

    # ═══════════════════════════════════════════════════════════════════════
    #  Workspace Assignment
    # ═══════════════════════════════════════════════════════════════════════

    def _on_assign_workspace(self):
        """Open folder dialog and assign workspace."""
        if not self.selected_conv_id:
            return

        folder = filedialog.askdirectory(title=t("btn_assign_ws"))
        if folder:
            self.ws_assignments[self.selected_conv_id] = folder
            self._populate_conversation_list()

    # ═══════════════════════════════════════════════════════════════════════
    #  Fix
    # ═══════════════════════════════════════════════════════════════════════

    def _on_fix(self):
        """Start fixing in a background thread."""
        self._set_fix_disabled()
        self.scan_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_label.configure(text=t("fixing"))

        thread = threading.Thread(target=self._fix_worker, daemon=True)
        thread.start()

    def _fix_worker(self):
        """Background fix worker."""
        def on_progress(msg, pct):
            self.after(0, lambda: self.progress_bar.set(pct))
            self.after(0, lambda: self.progress_label.configure(
                text=f"{t('fixing')} {int(pct * 100)}%"
            ))

        def on_log(msg):
            pass

        callbacks = Callbacks(on_progress=on_progress, on_log=on_log)
        result = fixer.fix(self.conversations, self.ws_assignments, callbacks)

        self.after(0, lambda: self._fix_complete(result))

    def _fix_complete(self, result):
        """Update UI after fix completes."""
        self.progress_bar.set(1.0)
        stats = result.by_source

        summary_short = t("fix_success", n=result.total)

        self.progress_label.configure(text=summary_short, text_color=SUCCESS)
        self._set_launch_enabled()
        self.scan_btn.configure(state="normal")

        # Show result summary as an inline banner in main area
        self._show_result_banner(result)

    def _show_result_banner(self, result):
        """Show an inline success banner in the main area after fix completes."""
        # Remove previous banner if any
        self._hide_result_banner()

        stats = result.by_source
        brain = stats.get("brain", 0)
        preserved = stats.get("preserved", 0)
        fallback = stats.get("fallback", 0)

        self.result_banner = ctk.CTkFrame(
            self.main_frame,
            fg_color="#0c3b2e",
            corner_radius=CORNER_RADIUS,
        )
        # Insert at top of main area (before the list)
        self.result_banner.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 4))
        # Shift main header down
        self.main_frame.winfo_children()[1].grid(row=1, column=0, sticky="ew", padx=16, pady=(4, 4))

        self.result_banner.grid_columnconfigure(0, weight=1)

        title_line = ctk.CTkLabel(
            self.result_banner,
            text=t("fix_success", n=result.total),
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=SUCCESS,
            anchor="w",
        )
        title_line.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 2))

        detail_text = (
            f"● {brain} brain   ● {preserved} "
            f"{t('source_preserved')}   ● {fallback} "
            f"{t('source_fallback')}   |   "
            f"{result.workspaces_mapped} ws   {result.timestamps_injected} ts"
        )
        detail_line = ctk.CTkLabel(
            self.result_banner,
            text=detail_text,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color="#6ee7b7",
            anchor="w",
        )
        detail_line.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 2))

        reopen_line = ctk.CTkLabel(
            self.result_banner,
            text=t("fix_reopen"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=TEXT_MUTED,
            anchor="w",
        )
        reopen_line.grid(row=2, column=0, sticky="w", padx=12, pady=(0, 10))

        # Dismiss button
        dismiss_btn = ctk.CTkButton(
            self.result_banner,
            text="✕",
            width=24,
            height=24,
            corner_radius=4,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            hover_color="#1a5c45",
            text_color=TEXT_MUTED,
            command=self._hide_result_banner,
        )
        dismiss_btn.grid(row=0, column=1, sticky="ne", padx=(0, 6), pady=(6, 0))

    def _hide_result_banner(self):
        """Remove inline result banner if it exists."""
        if hasattr(self, "result_banner") and self.result_banner is not None:
            self.result_banner.destroy()
            self.result_banner = None

    # ═══════════════════════════════════════════════════════════════════════
    #  Launch
    # ═══════════════════════════════════════════════════════════════════════

    def _on_launch(self):
        """Launch Antigravity."""
        if process.launch_antigravity():
            self.progress_label.configure(text=t("ag_launch_success"), text_color=SUCCESS)
        else:
            self.progress_label.configure(text=t("ag_launch_fail"), text_color=DANGER)

    # ═══════════════════════════════════════════════════════════════════════
    #  Language Toggle
    # ═══════════════════════════════════════════════════════════════════════

    def _toggle_language(self):
        """Toggle between Vietnamese and English."""
        new_lang = "en" if get_lang() == "vi" else "vi"
        set_lang(new_lang)
        self._refresh_ui()

    def _refresh_ui(self):
        """Refresh all UI text after language change."""
        self.title(f"{t('app_title')} {t('app_version')}")

        # Sidebar
        self.title_label.configure(text=t("app_title"))
        self.version_label.configure(text=t("app_version"))
        self.lang_btn.configure(text=t("lang_switch"))
        self.scan_btn.configure(text=t("btn_scan"))

        # Status
        if process.is_antigravity_running():
            self.status_label.configure(text=t("ag_running_short"))
            # Rebuild infobar with new language
            if hasattr(self, "infobar") and self.infobar is not None:
                self._show_infobar()
        else:
            self.status_label.configure(text=t("ag_not_running_short"))

        # Column headers
        self.hdr_num.configure(text=t("col_num"))
        self.hdr_title.configure(text=t("col_title"))
        self.hdr_source.configure(text=t("col_source"))
        self.hdr_ws.configure(text=t("col_workspace"))

        # Main area
        self.main_title.configure(text=t("col_title"))
        self.ws_btn.configure(text=t("btn_assign_ws"))
        self.fix_btn.configure(text=t("btn_fix"))
        self.launch_btn.configure(text=t("btn_launch"))
        self.close_btn.configure(text=t("btn_close"))

        # Empty state (if visible)
        if hasattr(self, "empty_label") and self.empty_label is not None:
            try:
                self.empty_label.configure(text=t("empty_state"))
            except Exception:
                pass

        # Count
        if self.conversations:
            self.count_label.configure(text=t("found_n", n=len(self.conversations)))
            self._populate_conversation_list()
