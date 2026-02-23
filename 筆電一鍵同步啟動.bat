@echo off
chcp 65001 > nul
echo ==========================================
echo    Stock Dashboard 筆電快速同步工具
echo ==========================================
echo.
echo [1/3] 正在檢查並更新代碼...
git pull
echo.
echo [2/3] 正在檢查必要套件...
python -m pip install -r requirements.txt
echo.
echo [3/3] 準備就緒！正在啟動戰情室...
python -m streamlit run tse_dashboard.py
pause

