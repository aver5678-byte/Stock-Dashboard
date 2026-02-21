import streamlit as st

def apply_global_theme():
    """
    專業金融冷靜深色主題 (ChatGPT 風格)
    低飽和、低對比、灰階分層
    """
    st.markdown("""
        <style>
        /* 1. 整體背景與字體 - ChatGPT 深色風格 */
        .stApp {
            background-color: #212121 !important;
            color: #ECECEC;
            font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* 主內容容器：置中並限制寬度 (SaaS 質感) */
        .main .block-container {
            max-width: 1100px !important;
            padding-top: 3rem !important;
            padding-bottom: 5rem !important;
            margin: 0 auto !important;
        }

        /* 2. 側邊欄 (Sidebar) 改進 */
        [data-testid="stSidebar"] {
            background-color: #171717 !important;
            min-width: 300px !important;
            max-width: 300px !important;
            border-right: 1px solid #2D2D2D;
        }
        
        /* 側邊欄標題 */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
            font-size: 22px !important;
            font-weight: 700 !important;
            color: #ECECEC !important;
            margin-bottom: 20px !important;
            border: none !important;
        }

        /* 選單項目設計 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 12px 16px !important;
            border-radius: 12px !important;
            margin-bottom: 8px !important;
            color: #A1A1AA !important;
            font-size: 17px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
            background-color: transparent !important;
            border: 1px solid transparent !important;
        }
        
        /* 選單 Hover */
        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #2A2B32 !important;
            color: #ECECEC !important;
        }
        
        /* 選單 Active (選中狀態) */
        [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #343541 !important;
            color: #ECECEC !important;
            border-left: 4px solid #F87171 !important; /* 左側亮條 */
        }
        
        /* 隱藏 Radio 圈圈 */
        [data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownArmchair"] {
            display: none !important;
        }
        [data-testid="stSidebar"] div[role="radiogroup"] label div:first-child {
            display: none !important;
        }

        /* 3. 卡片與容器系統 (stMetric / DataFrame) */
        [data-testid="stMetric"], [data-testid="stDataFrame"], .stAlert {
            background-color: #2A2B32 !important;
            border: 1px solid #3F3F46 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
        }

        /* 標題加強 */
        h1, h2, h3 {
            font-family: 'Inter', sans-serif !important;
            letter-spacing: -0.02em !important;
        }
        
        h1 {
            font-size: 32px !important;
            font-weight: 700 !important;
            margin-bottom: 24px !important;
            border-bottom: 1px solid #2D2D2D !important;
            padding-bottom: 12px !important;
        }

        /* 4. 警示區改進 - Danger Zone (低對比專業感) */
        .danger-zone {
            background-color: rgba(127, 29, 29, 0.4) !important; /* 深紅半透明 */
            border: 1px solid #EF4444 !important; /* 紅色細框 */
            border-radius: 16px !important;
            padding: 30px !important;
            margin-bottom: 30px !important;
            color: #ECECEC !important;
        }
        
        .danger-zone h2 {
            color: #F87171 !important;
            font-size: 26px !important;
            margin-top: 0 !important;
            font-weight: 700 !important;
            border: none !important;
        }
        
        .danger-zone p {
            font-size: 18px !important;
            color: #D1D5DB !important;
        }

        .normal-zone {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border: 1px solid #10B981 !important;
            border-radius: 16px !important;
            padding: 24px !important;
        }

        /* 5. 其他元件優化 */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #2A2B32 !important;
            border-radius: 12px !important;
        }
        
        .stButton>button {
            border-radius: 12px !important;
            background-color: #3F3F46 !important;
            border: none !important;
            font-weight: 600 !important;
        }
        
        /* 避免 Plotly 容器溢出 */
        .js-plotly-plot {
            border-radius: 16px !important;
            overflow: hidden !important;
        }
        </style>
    """, unsafe_allow_html=True)
