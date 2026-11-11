@echo off
chcp 65001 > nul
echo ===================================================
echo  NutriAgent - 啟動互動展示伺服器 (Web Cockpit)
echo ===================================================
echo.
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
echo 請於瀏覽器打開: http://127.0.0.1:5000
echo 按 Ctrl + C 可結束伺服器。
echo.
python app.py
pause
