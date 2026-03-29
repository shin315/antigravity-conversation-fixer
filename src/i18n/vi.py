"""Vietnamese strings (default language)."""

STRINGS = {
    # ── App ──────────────────────────────────────────────────────────────
    "app_title": "Antigravity Fixer",
    "app_version": "v2.0",

    # ── Status ───────────────────────────────────────────────────────────
    "ag_not_running": "✅ Antigravity không chạy",
    "ag_running": "⚠️ Antigravity đang chạy!",
    "ag_running_detail": "Cần tắt Antigravity trước khi sửa.",
    "ag_kill_confirm": "Tắt Antigravity tự động?",
    "ag_kill_success": "✅ Đã tắt Antigravity",
    "ag_kill_fail": "❌ Không thể tắt Antigravity. Vui lòng tắt thủ công.",
    "ag_launch_success": "🚀 Đã mở Antigravity",
    "ag_launch_fail": "Không tìm thấy Antigravity. Vui lòng mở thủ công.",

    # ── Scanning ─────────────────────────────────────────────────────────
    "scanning": "Đang quét conversations...",
    "found_n": "Tìm thấy {n} conversations",
    "found_none": "Không tìm thấy conversations nào.",
    "existing_titles": "Tiêu đề đã lưu: {n}",
    "existing_blobs": "Metadata đã lưu: {n}",

    # ── Sources ──────────────────────────────────────────────────────────
    "source_brain": "brain",
    "source_preserved": "đã lưu",
    "source_fallback": "dự phòng",

    # ── Workspace ────────────────────────────────────────────────────────
    "ws_auto_assign": "Đang tự động gán workspace...",
    "ws_auto_result": "Đã tự động gán {n} workspace",
    "ws_none_detected": "Không thể tự động phát hiện workspace nào.",
    "ws_manual_prompt": "Nhập đường dẫn workspace (Enter = bỏ qua):",
    "ws_choose_title": "GÁN WORKSPACE",
    "ws_choose_desc": "{n} conversation(s) chưa có workspace.",
    "ws_option_auto": "Tự động gán workspace (khuyến nghị)",
    "ws_option_auto_manual": "Tự động + gán thủ công phần còn lại",
    "ws_all_assigned": "Tất cả đã được tự động gán — không cần gán thủ công.",
    "ws_batch_prompt": "Đường dẫn cho TẤT CẢ còn lại (Enter = huỷ):",
    "ws_skip": "Bỏ qua.",
    "ws_stop": "Dừng — các conversation còn lại không gán.",
    "ws_mapped": "→ {name}",
    "ws_path_not_found": "Không tìm thấy: {path}",
    "ws_prompt": "Đường dẫn workspace (Enter=bỏ qua, 'all'=gán hàng loạt, 'q'=dừng):",

    # ── Fix ──────────────────────────────────────────────────────────────
    "fixing": "Đang rebuild index...",
    "fix_backup": "Đã backup: {path}",
    "fix_success": "✅ Hoàn tất! Đã rebuild {n} conversations.",
    "fix_reopen": "Mở lại Antigravity để áp dụng thay đổi.",
    "fix_stats": "📗 {brain} brain  📘 {preserved} đã lưu  📙 {fallback} dự phòng",
    "fix_ws_stats": "📁 {ws} workspaces  ⏱️ {ts} timestamps đã thêm",

    # ── Errors ───────────────────────────────────────────────────────────
    "error_db_not_found": "Không tìm thấy database: {path}",
    "error_conv_not_found": "Không tìm thấy thư mục conversations: {path}",
    "error_generic": "Lỗi: {msg}",

    # ── Buttons (GUI) ────────────────────────────────────────────────────
    "btn_scan": "🔍 Quét",
    "btn_fix": "⚡ Sửa tất cả",
    "btn_close": "❌ Đóng",
    "btn_launch": "🚀 Mở Antigravity",
    "btn_assign_ws": "📁 Gán Workspace...",
    "btn_kill_ag": "Tắt Antigravity",
    "btn_yes": "Có",
    "btn_no": "Không",

    # ── Table Headers ────────────────────────────────────────────────────
    "col_num": "#",
    "col_title": "Tiêu đề",
    "col_source": "Nguồn",
    "col_workspace": "WS",

    # ── Language ─────────────────────────────────────────────────────────
    "lang_switch": "🌐 English",
    "lang_current": "Tiếng Việt",

    # ── TUI ──────────────────────────────────────────────────────────────
    "tui_your_choice": "Lựa chọn của bạn",
    "tui_press_enter": "Nhấn Enter để đóng...",
    "tui_legend": "Chú thích: 🟢 brain  🔵 đã lưu  🟡 dự phòng  ✓ workspace",
}
