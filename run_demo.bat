@echo off
chcp 65001 > nul
echo ===================================================
echo  NutriAgent - 執行即時外食推薦示範 (CLI Demo)
echo ===================================================
echo.
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python demo_run.py
echo.
pause
