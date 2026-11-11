@echo off
chcp 65001 > nul
echo ===================================================
echo  NutriAgent - 環境自動建置腳本 (Setup Environment)
echo ===================================================
echo.
echo [1/3] 正在檢查 Python 安裝...
python --version
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先至 https://www.python.org 安裝 Python 3.10 以上版本！
    pause
    exit /b 1
)

echo.
echo [2/3] 正在建立虛擬環境 (.venv)...
if not exist ".venv" (
    python -m venv .venv
    echo 虛擬環境建立成功！
) else (
    echo 虛擬環境 (.venv) 已存在，跳過建立。
)

echo.
echo [3/3] 正在安裝必要套件 (requirements.txt)...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ===================================================
echo  環境安裝完成！
echo  您可以執行：
echo    run_demo.bat  -> 執行單次推薦示範
echo    run_web.bat   -> 啟動網頁介面 (Web Cockpit)
echo    run_test.bat  -> 執行自動化測試
echo ===================================================
pause
