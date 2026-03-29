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
    echo "Dang tu dong mo trang tai Python (Mac OS)..."
    open "https://www.python.org/downloads/mac-os/"
    echo "Vui long tai va cai dat ban Python 3.x moi nhat."
    echo "Bam ban phim bat ky de thoat..."
    read -n 1 -s
    exit 1
fi

# Kiem tra thu vien tkinter (dieu kien bat buoc cho giao dien CustomTkinter)
if ! python3 -c "import tkinter" &> /dev/null; then
    echo "⚠️ Khong tim thay thu vien 'tkinter' dac thu tren macOS!"
    if command -v brew &> /dev/null; then
        PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        echo "Dang tu dong cai dat python-tk@$PY_VER qua Homebrew..."
        brew install "python-tk@$PY_VER"
        
        # Kiem tra lai
        if ! python3 -c "import tkinter" &> /dev/null; then
            echo "❌ LOI: Tu dong cai dat that bai. Vui long chay lenh: brew install python-tk@$PY_VER"
            echo "Bam ban phim bat ky de thoat..."
            read -n 1 -s
            exit 1
        fi
    else
        echo "❌ LOI: May cua ban khong co Homebrew, va Python hien tai thieu Tkinter."
        echo "Dang tu dong mo trang tai Python chinh thuc (bao gom san Tkinter)..."
        open "https://www.python.org/downloads/mac-os/"
        echo "Vui long tai va cai tai lai Python bang bo cai dat (installer) tren web nhe."
        echo "Bam ban phim bat ky de thoat..."
        read -n 1 -s
        exit 1
    fi
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
