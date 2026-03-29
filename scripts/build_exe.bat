@echo off
REM Antigravity Fixer Build Script
REM Hỗ trợ tự động thiết lập môi trường và build file .exe bằng PyInstaller

echo [1/3] Kiem tra moi truong Python...
cd /d "%~dp0.."

if not exist ".venv" if not exist "venv" (
    echo Khong tim thay thu muc venv hoac .venv. Dang tao .venv moi...
    python -m venv .venv
)

if exist ".venv" (
    call .venv\Scripts\activate.bat
) else (
    call venv\Scripts\activate.bat
)

echo.
echo [2/3] Cai dat dependencies (requirements.txt & pyinstaller)...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo [3/3] Dang dong goi bang PyInstaller, vui long cho...
REM --onefile: 1 file duy nhat
REM --windowed: ẩn console terminal cho GUI
REM --clean: Xoa cache cu de tranh loi load package
pyinstaller --onefile --windowed --name "AntigravityFixer" --clean gui_main.py

echo.
echo ==============================================
echo Build hoan tat!
echo File thuc thi: dist\AntigravityFixer.exe
echo ==============================================
pause
