@echo off
chcp 65001 >nul 2>&1
title Antigravity Fixer — Terminal

:: Check Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo   [!] Python khong duoc tim thay.
    echo       Tai Python tai: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

:: Install dependencies (silent if already installed)
pip install -q -r "%~dp0requirements.txt" >nul 2>&1

:: Launch TUI
python "%~dp0tui_main.py"

:: Keep window open after finishing
echo.
pause
