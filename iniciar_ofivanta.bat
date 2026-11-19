@echo off
cd /d "%~dp0"
python -m src.app.main
if errorlevel 1 (
    echo.
    echo No se pudo abrir Ofivanta. Revisa que Python este instalado con tkinter.
    pause
)
