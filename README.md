# Antigravity Fixer

Sửa lỗi mất conversation history, sai thứ tự, và mất workspace trong Antigravity IDE.

## ⚡ Quick Start (Windows)

### Cách 1: Double-click (đơn giản nhất)

1. Tắt Antigravity hoàn toàn
2. Double-click **`start_gui.bat`** → mở giao diện desktop
3. Bấm **🔍 Quét** → xem danh sách conversations
4. (Tuỳ chọn) Gán workspace cho conversations chưa có
5. Bấm **⚡ Sửa tất cả** → chờ hoàn tất
6. Mở lại Antigravity

> Thích dùng terminal? Double-click **`start_tui.bat`** thay vì `start_gui.bat`.

### Cách 2: Chạy file .exe

1. Tắt Antigravity hoàn toàn
2. Chạy **`AntigravityFixer.exe`** (GUI) hoặc **`AntigravityFixer-CLI.exe`** (Terminal)
3. Làm theo hướng dẫn trên màn hình

> File `.bat` tự động kiểm tra Python và cài dependencies. Không cần cài đặt gì trước.
> 
> Yêu cầu: Python 3.7+ (tải tại [python.org](https://www.python.org/downloads/))

## Tính năng

| Vấn đề | Đã sửa? |
|---|---|
| Conversations biến mất khỏi sidebar | ✅ |
| Conversations sai thứ tự | ✅ Sắp xếp mới nhất trước |
| Tiêu đề bị placeholder | ✅ Khôi phục từ brain artifacts |
| Mất workspace assignments | ✅ Tự động khôi phục |
| Thiếu timestamps | ✅ Tự động thêm từ file dates |

## Cách hoạt động

Antigravity lưu dữ liệu ở 2 nơi:

- **Conversation files** (`*.pb`) — trong thư mục user profile
- **Sidebar index** — database SQLite trong app data

| OS | Conversations | Database |
|---|---|---|
| Windows | `%USERPROFILE%\.gemini\antigravity\conversations\` | `%APPDATA%\antigravity\...\state.vscdb` |
| macOS | `~/.gemini/antigravity/conversations/` | `~/Library/Application Support/antigravity/.../state.vscdb` |
| Linux | `~/.gemini/antigravity/conversations/` | `~/.config/Antigravity/.../state.vscdb` |

Khi index bị hỏng, conversations vẫn tồn tại trên đĩa nhưng không hiện trong sidebar. Tool này quét lại tất cả conversation files, sắp xếp theo ngày, khôi phục tiêu đề và workspace, rồi ghi lại index mới.

## Kiến trúc

```
src/
├── core/           # Logic chính (không phụ thuộc UI)
│   ├── paths.py        # Phát hiện OS, đường dẫn
│   ├── protobuf.py     # Encode/decode protobuf
│   ├── database.py     # Đọc/ghi SQLite
│   ├── scanner.py      # Quét conversations, khôi phục tiêu đề
│   ├── fixer.py        # Orchestrator: scan() + fix()
│   └── process.py      # Kiểm tra/tắt Antigravity process
├── i18n/           # Đa ngôn ngữ (Việt mặc định + Anh)
├── tui/            # Terminal UI (Rich)
└── gui/            # Desktop UI (CustomTkinter)
```

## Ngôn ngữ

- 🇻🇳 **Tiếng Việt** (mặc định)
- 🇺🇸 **English**

GUI: Bấm nút 🌐 ở góc phải để chuyển ngôn ngữ.
TUI: Dùng `--lang en` hoặc `--lang vi`.

## An toàn

- **Tự động backup** — index hiện tại được lưu trước khi thay đổi
- **Không phá huỷ** — file conversation (`*.pb`) không bao giờ bị sửa
- **Bảo toàn metadata** — workspace, timestamps, và state đều được giữ lại
- **Chạy nhiều lần** — an toàn khi chạy lặp lại

## Build từ source

```bash
# Cài dependencies
pip install -r requirements.txt

# Chạy GUI
python gui_main.py

# Chạy TUI
python tui_main.py

# Build exe (GUI)
pyinstaller --onefile --windowed --name "AntigravityFixer" gui_main.py

# Build exe (TUI)
pyinstaller --onefile --console --name "AntigravityFixer-CLI" tui_main.py
```

## License

MIT
