import streamlit as st

def apply_global_theme():
    """
    全站共用的「彭博終端機黑科技模式」，只允許黑、白、紅三種色系。
    """
    st.markdown("""
        <style>
        /* 徹底黑化的背景與純白字體 */
        .stApp {
            background-color: #050505;
            color: #ffffff;
            font-family: 'Inter', 'Segoe UI', monospace;
        }
        
        /* 側邊欄：深灰黑 */
        [data-testid="stSidebar"] {
            background-color: #0a0a0a;
            border-right: 1px solid #1f1f1f;
        }
        
        /* 數字指標毛玻璃卡片（黑/灰/紅基調） */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 800;
            color: #ffffff !important;
        }
        [data-testid="stMetricDelta"] svg {
            color: #ff3333 !important; /* 強制所有箭頭都是紅色，或是看情境如果是正的也可以是白色 */
        }
        [data-testid="stMetric"] {
            background: rgba(20, 20, 20, 0.8);
            border: 1px solid #333333;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            border: 1px solid #ffffff;
            box-shadow: 0 6px 15px rgba(255,255,255,0.1);
        }
        
        /* 標題純白加粗 */
        h1, h2, h3, h4 {
            color: #ffffff !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #333333;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        
        /* 按鈕：極簡白框或是紅底 */
        .stButton>button {
            background: transparent;
            border: 2px solid #ffffff;
            color: #ffffff;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background: #ffffff;
            color: #000000;
        }
        .stButton>button:active {
            background: #ff0000;
            border-color: #ff0000;
            color: #ffffff;
        }

        /* 隱藏原生分隔線，改成極簡細線 */
        hr {
            border-top: 1px solid #333333;
        }
        
        /* 表格黑化 */
        [data-testid="stDataFrame"] {
            background-color: #0b0b0b;
        }
        </style>
    """, unsafe_allow_html=True)
