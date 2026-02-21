import streamlit as st

def apply_global_theme():
    """
    極致極簡：石墨黑沈浸方案 (Immersive Graphite)
    解決問題：
    1. 背景白邊割裂 (全站強制石墨黑)
    2. 標題視覺層級 (雜誌級排版)
    3. 警告區質感 (磨砂玻璃透明紅)
    """
    st.markdown("""
        <style>
        /* 1. 全站背景強制覆蓋 (解決白邊問題) */
        .stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], [data-testid="stSidebar"], .block-container {
            background-color: #0D0D0D !important;
            background-image: none !important;
            color: #FFFFFF !important;
        }

        /* 頂部導航欄模糊化 */
        header[data-testid="stHeader"] {
            background-color: rgba(13, 13, 13, 0.7) !important;
            backdrop-filter: blur(10px) !important;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* 主內容區：置中排版優化 */
        .main .block-container {
            max-width: 1100px !important;
            padding: 4rem 1.5rem !important;
            margin: 0 auto !important;
        }

        /* 2. 標題與字體系統 (解決標題層級問題) */
        h1, h2, h3 {
            font-family: 'Inter', 'Segoe UI Semibold', sans-serif !important;
            color: #FFFFFF !important;
            letter-spacing: -0.04em !important;
            border: none !important;
        }
        
        h1 {
            font-size: 36px !important;
            font-weight: 900 !important;
            margin-bottom: 2rem !important;
            line-height: 1.1 !important;
        }
        
        h2 {
            font-size: 24px !important;
            font-weight: 800 !important;
            margin-top: 1.5rem !important;
        }

        /* 3. 側邊欄：導航體驗升級 */
        section[data-testid="stSidebar"] {
            width: 320px !important;
            border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
        }

        /* 選單標籤樣式 */
        section[data-testid="stSidebar"] .stMarkdown p, 
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            font-size: 19px !important;
            font-weight: 700 !important;
            color: #ECECEC !important;
            margin: 0 !important;
        }

        /* 選單 Radio 項目項目自訂 */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 18px 22px !important;
            border-radius: 14px !important;
            margin-bottom: 12px !important;
            transition: all 0.25s cubic-bezier(0.19, 1, 0.22, 1) !important;
            border: 1px solid transparent !important;
            background-color: transparent !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Active 狀態：紅條與深色底 */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #1A1A1A !important;
            box-shadow: inset 5px 0 0 0 #F87171 !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
            color: #FFFFFF !important;
            font-weight: 900 !important;
        }

        /* 隱藏原生 Radio 圓圈 */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* 4. 警告區：沈浸式磨砂紅 (解決警告區質感問題) */
        .danger-zone {
            background-color: rgba(239, 68, 68, 0.06) !important;
            border: 1px solid rgba(239, 68, 68, 0.4) !important;
            border-radius: 20px !important;
            padding: 30px !important;
            margin-bottom: 30px !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
        }
        
        .danger-zone h2 {
            color: #F87171 !important;
            font-size: 26px !important;
            margin-bottom: 10px !important;
        }
        
        .danger-zone b {
            font-family: 'JetBrains Mono', 'Monaco', monospace !important;
            font-size: 24px !important;
            color: #FFFFFF !important;
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 8px;
            border-radius: 6px;
        }

        .normal-zone {
            background-color: rgba(16, 185, 129, 0.04) !important;
            border: 1px solid rgba(16, 185, 129, 0.3) !important;
            border-radius: 20px !important;
            padding: 24px !important;
        }

        /* 5. 數據指標 (Metric) 優化 */
        [data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 18px !important;
            padding: 24px !important;
        }
        
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }

        /* 登入按鈕 */
        .stButton button {
            background-color: #F87171 !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            height: 50px !important;
            transition: all 0.2s ease;
        }
        
        .stButton button:hover {
            background-color: #EF4444 !important;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(248, 113, 113, 0.3);
        }
        </style>
    """, unsafe_allow_html=True)
