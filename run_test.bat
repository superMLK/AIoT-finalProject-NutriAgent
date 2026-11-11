@echo off
chcp 65001 > nul
echo ===================================================
echo  NutriAgent - 執行自動化臨床安全與演算法測試
echo ===================================================
echo.
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python -m unittest tests/test_agent.py
echo.
pause
