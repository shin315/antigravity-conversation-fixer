"""English strings."""

STRINGS = {
    # ── App ──────────────────────────────────────────────────────────────
    "app_title": "Antigravity Fixer",
    "app_version": "v2.0",

    # ── Status ───────────────────────────────────────────────────────────
    "ag_not_running": "✅ Antigravity is not running",
    "ag_not_running_short": "Antigravity not running",
    "ag_running": "⚠️ Antigravity is running!",
    "ag_running_short": "Antigravity is running",
    "ag_running_detail": "Antigravity must be closed before fixing.",
    "ag_kill_confirm": "Kill Antigravity automatically?",
    "ag_kill_success": "✅ Antigravity has been closed",
    "ag_kill_success_short": "Antigravity closed",
    "ag_kill_fail": "❌ Could not close Antigravity. Please close it manually.",
    "ag_kill_fail_short": "Could not close. Please close manually.",
    "ag_launch_success": "🚀 Antigravity launched",
    "ag_launch_fail": "Could not find Antigravity. Please open it manually.",

    # ── Scanning ─────────────────────────────────────────────────────────
    "scanning": "Scanning conversations...",
    "found_n": "Found {n} conversations",
    "found_none": "No conversations found on disk.",
    "existing_titles": "Existing titles: {n}",
    "existing_blobs": "Existing metadata: {n}",

    # ── Sources ──────────────────────────────────────────────────────────
    "source_brain": "brain",
    "source_preserved": "preserved",
    "source_fallback": "fallback",

    # ── Workspace ────────────────────────────────────────────────────────
    "ws_auto_assign": "Auto-assigning workspaces...",
    "ws_auto_result": "Auto-assigned {n} workspace(s)",
    "ws_none_detected": "No workspaces could be auto-detected.",
    "ws_manual_prompt": "Enter workspace path (Enter = skip):",
    "ws_choose_title": "WORKSPACE ASSIGNMENT",
    "ws_choose_desc": "{n} conversation(s) have no workspace.",
    "ws_option_auto": "Auto-assign workspaces (recommended)",
    "ws_option_auto_manual": "Auto-assign + manually assign the rest",
    "ws_all_assigned": "All conversations were auto-assigned — nothing left to assign manually.",
    "ws_batch_prompt": "Path for ALL remaining (Enter = cancel):",
    "ws_skip": "Skipped.",
    "ws_stop": "Stopped — remaining conversations left unmapped.",
    "ws_mapped": "→ {name}",
    "ws_path_not_found": "Path not found: {path}",
    "ws_prompt": "Workspace path (Enter=skip, 'all'=batch, 'q'=stop):",

    # ── Fix ──────────────────────────────────────────────────────────────
    "fixing": "Rebuilding index...",
    "fix_backup": "Backup saved: {path}",
    "fix_success": "✅ Done! Rebuilt {n} conversations.",
    "fix_reopen": "Reopen Antigravity to apply changes.",
    "fix_stats": "📗 {brain} brain  📘 {preserved} preserved  📙 {fallback} fallback",
    "fix_ws_stats": "📁 {ws} workspaces  ⏱️ {ts} timestamps injected",

    # ── Errors ───────────────────────────────────────────────────────────
    "error_db_not_found": "Database not found: {path}",
    "error_conv_not_found": "Conversations directory not found: {path}",
    "error_generic": "Error: {msg}",

    # ── Buttons (GUI) ────────────────────────────────────────────────────
    "btn_scan": "Scan",
    "btn_fix": "Fix All",
    "btn_close": "Close",
    "btn_launch": "Open Antigravity",
    "btn_assign_ws": "Assign Workspace",
    "btn_kill_ag": "Kill Antigravity",
    "btn_yes": "Yes",
    "btn_no": "No",

    # ── GUI Layout ───────────────────────────────────────────────────────
    "empty_state": "Press Scan on the left to start searching for conversations...",

    # ── Table Headers ────────────────────────────────────────────────────
    "col_num": "#",
    "col_title": "Title",
    "col_source": "Source",
    "col_workspace": "WS",

    # ── Language ─────────────────────────────────────────────────────────
    "lang_switch": "🌐 Tiếng Việt",
    "lang_current": "English",

    # ── TUI ──────────────────────────────────────────────────────────────
    "tui_your_choice": "Your choice",
    "tui_press_enter": "Press Enter to close...",
    "tui_legend": "Legend: 🟢 brain  🔵 preserved  🟡 fallback  ✓ workspace",
}
