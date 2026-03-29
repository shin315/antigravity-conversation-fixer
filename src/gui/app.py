"""CustomTkinter Desktop GUI for Antigravity Fixer."""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from src.core import fixer, process
from src.core.fixer import Callbacks
from src.i18n import t, set_lang, get_lang


# ─── Theme ────────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ─── Source Icons ─────────────────────────────────────────────────────────────

SOURCE_COLORS = {
    "brain": "#22c55e",      # green
    "preserved": "#3b82f6",  # blue
    "fallback": "#eab308",   # yellow
}

SOURCE_ICONS = {
    "brain": "📗",
    "preserved": "📘",
    "fallback": "📙",
}


# ─── Main App ─────────────────────────────────────────────────────────────────

class AntigravityFixerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{t('app_title')} {t('app_version')}")
        self.geometry("720x580")
        self.minsize(620, 480)

        self.conversations = []
        self.ws_assignments = {}
        self.selected_conv_id = None
        self.conv_rows = []

        self._build_ui()
        self._check_antigravity()

    # ── UI Construction ──────────────────────────────────────────────────

    def _build_ui(self):
        """Build all UI components."""
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_header()
        self._build_status_frame()
        self._build_conversation_list()
        self._build_progress_frame()
        self._build_action_buttons()

    def _build_header(self):
        """Header with title and language toggle."""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        header.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            header,
            text=f"🔧 {t('app_title')}",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title_label.grid(row=0, column=0, sticky="w")

        version_label = ctk.CTkLabel(
            header,
            text=t("app_version"),
            font=ctk.CTkFont(size=14),
            text_color="gray",
        )
        version_label.grid(row=0, column=1, sticky="w", padx=(10, 0))

        self.lang_btn = ctk.CTkButton(
            header,
            text=t("lang_switch"),
            width=120,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self._toggle_language,
        )
        self.lang_btn.grid(row=0, column=2, sticky="e")

    def _build_status_frame(self):
        """Status indicators and scan button."""
        status_frame = ctk.CTkFrame(self)
        status_frame.grid(row=1, column=0, sticky="ew", padx=15, pady=5)
        status_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.grid(row=0, column=0, sticky="w", padx=15, pady=(10, 2))

        self.count_label = ctk.CTkLabel(
            status_frame,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.count_label.grid(row=1, column=0, sticky="w", padx=15, pady=(2, 10))

        self.scan_btn = ctk.CTkButton(
            status_frame,
            text=t("btn_scan"),
            width=120,
            command=self._on_scan,
        )
        self.scan_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=15, pady=10)

    def _build_conversation_list(self):
        """Scrollable conversation list."""
        list_container = ctk.CTkFrame(self)
        list_container.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        list_container.grid_rowconfigure(1, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        # Column headers
        header_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        header_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header_frame, text=t("col_num"), width=40, font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(header_frame, text=t("col_title"), font=ctk.CTkFont(weight="bold"), anchor="w").grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(header_frame, text=t("col_source"), width=80, font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5)
        ctk.CTkLabel(header_frame, text=t("col_workspace"), width=40, font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5)

        # Scrollable list
        self.conv_scroll = ctk.CTkScrollableFrame(list_container)
        self.conv_scroll.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.conv_scroll.grid_columnconfigure(1, weight=1)

        # Workspace assign button (below list)
        ws_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        ws_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(0, 5))

        self.selected_info = ctk.CTkLabel(
            ws_frame, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.selected_info.grid(row=0, column=0, sticky="w", padx=5)

        self.ws_btn = ctk.CTkButton(
            ws_frame,
            text=t("btn_assign_ws"),
            width=160,
            state="disabled",
            command=self._on_assign_workspace,
        )
        self.ws_btn.grid(row=0, column=1, sticky="e", padx=5)
        ws_frame.grid_columnconfigure(0, weight=1)

    def _build_progress_frame(self):
        """Progress bar and status text."""
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=5)
        prog_frame.grid_columnconfigure(0, weight=1)

        self.progress_bar = ctk.CTkProgressBar(prog_frame)
        self.progress_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        self.progress_bar.set(0)

        self.progress_label = ctk.CTkLabel(
            prog_frame, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.progress_label.grid(row=1, column=0, sticky="w", padx=5)

    def _build_action_buttons(self):
        """Fix, Launch, and Close buttons."""
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=15, pady=(5, 15))

        self.fix_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_fix"),
            width=140,
            state="disabled",
            fg_color="#22c55e",
            hover_color="#16a34a",
            command=self._on_fix,
        )
        self.fix_btn.pack(side="left", padx=5)

        self.launch_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_launch"),
            width=160,
            state="disabled",
            command=self._on_launch,
        )
        self.launch_btn.pack(side="left", padx=5)

        close_btn = ctk.CTkButton(
            btn_frame,
            text=t("btn_close"),
            width=100,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self.destroy,
        )
        close_btn.pack(side="right", padx=5)

    # ── Antigravity Check ────────────────────────────────────────────────

    def _check_antigravity(self):
        """Check if Antigravity is running."""
        if process.is_antigravity_running():
            self.status_label.configure(text=t("ag_running"), text_color="#ef4444")
            result = messagebox.askyesno(
                t("app_title"),
                f"{t('ag_running')}\n\n{t('ag_kill_confirm')}",
            )
            if result:
                if process.kill_antigravity():
                    self.status_label.configure(text=t("ag_kill_success"), text_color="#22c55e")
                else:
                    self.status_label.configure(text=t("ag_kill_fail"), text_color="#ef4444")
                    self.scan_btn.configure(state="disabled")
                    return
            else:
                self.scan_btn.configure(state="disabled")
                return
        else:
            self.status_label.configure(text=t("ag_not_running"), text_color="#22c55e")

    # ── Scan ─────────────────────────────────────────────────────────────

    def _on_scan(self):
        """Start scanning in a background thread."""
        self.scan_btn.configure(state="disabled")
        self.fix_btn.configure(state="disabled")
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
            self.after(0, lambda: messagebox.showerror(t("app_title"), msg))

        callbacks = Callbacks(on_progress=on_progress, on_error=on_error)

        try:
            self.conversations = fixer.scan(callbacks)
        except RuntimeError as e:
            self.after(0, lambda: self.scan_btn.configure(state="normal"))
            return

        # Auto-assign workspaces
        self.ws_assignments = fixer.auto_assign_workspaces(self.conversations)

        self.after(0, self._scan_complete)

    def _scan_complete(self):
        """Update UI after scan completes."""
        self.count_label.configure(text=t("found_n", n=len(self.conversations)))
        self.progress_bar.set(1.0)
        self.progress_label.configure(text="")
        self.scan_btn.configure(state="normal")

        if self.conversations:
            self.fix_btn.configure(state="normal")
            self._populate_conversation_list()

    def _populate_conversation_list(self):
        """Fill the scrollable list with conversation rows."""
        # Clear existing
        for widget in self.conv_scroll.winfo_children():
            widget.destroy()
        self.conv_rows = []
        self.selected_conv_id = None
        self.ws_btn.configure(state="disabled")
        self.selected_info.configure(text="")

        for i, conv in enumerate(self.conversations):
            row = self._create_conv_row(i, conv)
            self.conv_rows.append(row)

    def _create_conv_row(self, index, conv):
        """Create a single conversation row in the list."""
        has_ws = conv.has_workspace or conv.id in self.ws_assignments
        row_frame = ctk.CTkFrame(
            self.conv_scroll,
            fg_color="transparent",
            cursor="hand2",
        )
        row_frame.grid(row=index, column=0, sticky="ew", pady=1)
        self.conv_scroll.grid_columnconfigure(0, weight=1)
        row_frame.grid_columnconfigure(1, weight=1)

        # Number
        num_label = ctk.CTkLabel(row_frame, text=str(index + 1), width=40, anchor="e")
        num_label.grid(row=0, column=0, padx=5)

        # Title
        title_label = ctk.CTkLabel(
            row_frame,
            text=conv.title[:50],
            anchor="w",
            font=ctk.CTkFont(size=13),
        )
        title_label.grid(row=0, column=1, sticky="w", padx=5)

        # Source
        src_icon = SOURCE_ICONS.get(conv.source, "⚪")
        source_label = ctk.CTkLabel(
            row_frame,
            text=src_icon,
            width=80,
            text_color=SOURCE_COLORS.get(conv.source, "gray"),
        )
        source_label.grid(row=0, column=2, padx=5)

        # Workspace
        ws_text = "✅" if has_ws else "❌"
        ws_label = ctk.CTkLabel(row_frame, text=ws_text, width=40)
        ws_label.grid(row=0, column=3, padx=5)

        # Click handler
        def on_click(event, cid=conv.id, title=conv.title):
            self._select_conversation(cid, title)

        for widget in [row_frame, num_label, title_label, source_label, ws_label]:
            widget.bind("<Button-1>", on_click)

        return row_frame

    def _select_conversation(self, conv_id, title):
        """Handle conversation row selection."""
        self.selected_conv_id = conv_id
        self.selected_info.configure(text=f"#{conv_id[:8]}... — {title[:40]}")
        self.ws_btn.configure(state="normal")

        # Highlight selected row
        for i, row in enumerate(self.conv_rows):
            if self.conversations[i].id == conv_id:
                row.configure(fg_color=("gray80", "gray25"))
            else:
                row.configure(fg_color="transparent")

    # ── Workspace Assignment ─────────────────────────────────────────────

    def _on_assign_workspace(self):
        """Open folder dialog and assign workspace."""
        if not self.selected_conv_id:
            return

        folder = filedialog.askdirectory(title=t("btn_assign_ws"))
        if folder:
            self.ws_assignments[self.selected_conv_id] = folder
            # Refresh the list to show updated workspace status
            self._populate_conversation_list()

    # ── Fix ──────────────────────────────────────────────────────────────

    def _on_fix(self):
        """Start fixing in a background thread."""
        self.fix_btn.configure(state="disabled")
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

        summary = (
            f"{t('fix_success', n=result.total)}\n\n"
            f"{t('fix_stats', brain=stats.get('brain', 0), preserved=stats.get('preserved', 0), fallback=stats.get('fallback', 0))}\n"
            f"{t('fix_ws_stats', ws=result.workspaces_mapped, ts=result.timestamps_injected)}\n\n"
            f"{t('fix_reopen')}"
        )

        self.progress_label.configure(text=t("fix_success", n=result.total))
        self.launch_btn.configure(state="normal")
        self.scan_btn.configure(state="normal")

        messagebox.showinfo(t("app_title"), summary)

    # ── Launch ───────────────────────────────────────────────────────────

    def _on_launch(self):
        """Launch Antigravity."""
        if process.launch_antigravity():
            self.progress_label.configure(text=t("ag_launch_success"))
        else:
            messagebox.showwarning(t("app_title"), t("ag_launch_fail"))

    # ── Language Toggle ──────────────────────────────────────────────────

    def _toggle_language(self):
        """Toggle between Vietnamese and English."""
        new_lang = "en" if get_lang() == "vi" else "vi"
        set_lang(new_lang)
        self._refresh_ui()

    def _refresh_ui(self):
        """Refresh all UI text after language change."""
        self.title(f"{t('app_title')} {t('app_version')}")
        self.lang_btn.configure(text=t("lang_switch"))
        self.scan_btn.configure(text=t("btn_scan"))
        self.fix_btn.configure(text=t("btn_fix"))
        self.launch_btn.configure(text=t("btn_launch"))
        self.ws_btn.configure(text=t("btn_assign_ws"))

        # Re-check status text
        if process.is_antigravity_running():
            self.status_label.configure(text=t("ag_running"))
        else:
            self.status_label.configure(text=t("ag_not_running"))

        if self.conversations:
            self.count_label.configure(text=t("found_n", n=len(self.conversations)))
            self._populate_conversation_list()
