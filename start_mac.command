#!/bin/bash
cd "$(dirname "$0")"

echo "============================================="
echo "   Antigravity Fixer - macOS Launcher"
echo "============================================="
echo ""
echo "[1/3] Kiem tra moi truong Python..."

# Kiem tra python3 co ton tai khong
if ! command -v python3 &> /dev/null; then
    echo "❌ LOI: Khong tim thay Python tren may cua ban!"
    echo "Vui long vao day de tai: https://www.python.org/downloads/mac-os/"
    echo "Bam ban phim bat ky de thoat..."
    read -n 1 -s
    exit 1
fi

# Tao môi trường ảo để không báo lỗi "externally managed environment" trên macOS mới
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Dang khoi tao moi truong Python rieng (.venv)..."
    python3 -m venv .venv
fi

# Kich hoat moi truong
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "[2/3] Dang cai dat thu vien (chay lan dau se hoi lau xiu nhe)..."
pip install -r requirements.txt --quiet

echo "[3/3] Dang khoi chay giao dien Antigravity Fixer..."
python gui_main.py
