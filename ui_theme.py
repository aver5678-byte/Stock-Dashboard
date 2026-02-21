import streamlit as st

def apply_global_theme():
    """
    全站共用的「彭博終端機黑科技模式」，只允許黑、白、紅三種色系。
    """
    st.markdown("""
        <style>
        /* 徹底白化的背景與純黑字體 */
        .stApp {
            background-color: #ffffff;
            color: #000000;
            font-family: 'Inter', 'Segoe UI', monospace;
        }
        
        /* 側邊欄：純白 */
        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #eeeeee;
        }
        
        /* 數字指標毛玻璃卡片（白/灰/紅基調） */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 800;
            color: #000000 !important;
        }
        [data-testid="stMetricDelta"] svg {
            color: #ff0000 !important; /* 強制所有箭頭都是紅色 */
        }
        [data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid #dddddd;
            border-radius: 6px;
            padding: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            border: 1px solid #000000;
            box-shadow: 0 6px 15px rgba(0,0,0,0.1);
        }
        
        /* 標題純黑加粗 */
        h1, h2, h3, h4 {
            color: #000000 !important;
            font-weight: 800 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 2px solid #eeeeee;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        
        /* 按鈕：極簡黑框或是紅底 */
        .stButton>button {
            background: transparent;
            border: 2px solid #000000;
            color: #000000;
            border-radius: 4px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background: #000000;
            color: #ffffff;
        }
        .stButton>button:active {
            background: #ff0000;
            border-color: #ff0000;
            color: #ffffff;
        }

        /* 隱藏原生分隔線，改成極簡細線 */
        hr {
            border-top: 1px solid #eeeeee;
        }
        
        /* 表格白化 */
        [data-testid="stDataFrame"] {
            background-color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
