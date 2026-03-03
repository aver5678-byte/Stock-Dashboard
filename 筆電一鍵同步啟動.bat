@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul

echo ========================================================
echo    🚀 Stock Dashboard 戰情室快速啟動及同步系統 (v9.6)
echo ========================================================
echo.

echo [啟動選項]
echo A. 🚀 快速啟動 (跳過更新，直接運行)
echo B. 🔄 同步更新 (Git Pull + 套件檢查，更新本地版)
echo C. 📤 上傳雲端 (本地代碼推送至 Cloud Streamlit)
echo D. 🛑 強制重新啟動 (清理背景佔用的 Streamlit 進程)
echo.
set /p CHOICE="請選擇操作並按回車 (預設 A 直接啟動): "

if /i "%CHOICE%"=="B" (
    echo.
    echo 正在同步雲端最新代碼 (Git Pull)...
    git pull
    echo.
    echo 正在檢查必要套件 (Pip Install)...
    python -m pip install -r requirements.txt
    echo.
)

if /i "%CHOICE%"=="C" (
    echo.
    set /p MSG="請輸入本次更新說明 (預設「Fix UI fixes」): "
    if "!MSG!"=="" set MSG=Fix UI fixes
    echo 正在上傳代碼至 GitHub / Streamlit Cloud...
    git add .
    git commit -m "!MSG!"
    git push
    echo.
    echo 上傳完成！雲端版本將在數分鐘後自動反映。
    pause
    goto :EOF
)

if /i "%CHOICE%"=="D" (
    echo.
    echo 正在強制關閉舊的進程...
    taskkill /f /im python.exe /t
    echo 本地連接已清理，請重新運行此腳本。
    pause
    goto :EOF
)

echo.
echo ------------------------------------------
echo 準備啟動戰情室...
echo.
echo 💡 小提示：若瀏覽器未連動，請手動輸入：http://localhost:8501
echo.

:: 在啟動前先嘗試背景打開瀏覽器，避免 streamlit 延遲
start "" http://localhost:8501
python -m streamlit run tse_dashboard.py --server.port 8501

echo.
echo 程式已結束。
pause
