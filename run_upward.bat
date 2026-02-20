@echo off
cd /d "%~dp0"
echo 正在啟動股市波段 【上漲】 分析儀表板...
"C:\Users\user\AppData\Local\Programs\Python\Python312\python.exe" -m streamlit run app_upward.py
