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
        section[data-testid="stSidebar"] {
            background-color: #171717 !important;
            min-width: 320px !important;
            max-width: 320px !important;
            border-right: 1px solid #2D2D2D;
        }
        
        /* 側邊欄裡面的內容容器 */
        section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
            padding: 2rem 1rem !important;
        }

        /* 側邊欄標題與文字加大 */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #ECECEC !important;
            font-weight: 700 !important;
        }
        
        section[data-testid="stSidebar"] h1 { font-size: 24px !important; margin-bottom: 24px !important; }
        section[data-testid="stSidebar"] .stMarkdown p { font-size: 16px !important; }

        /* 選單項目設計 (Radio group) */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            padding-top: 10px;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 14px 18px !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
            color: #A1A1AA !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            display: flex !important;
            align-items: center !important;
        }
        
        /* 選單 Hover */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #2A2B32 !important;
            color: #ECECEC !important;
        }
        
        /* 選單 Active (選中狀態) */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #343541 !important;
            color: #ECECEC !important;
            border-left: 5px solid #F87171 !important; /* 左側紅色亮條 */
            padding-left: 13px !important; /* 補償亮條寬度 */
        }
        
        /* 徹底隱藏 Radio 圈圈 (使用多種選擇器確保生效) */
        section[data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownArmchair"],
        section[data-testid="stSidebar"] div[role="radiogroup"] label div:first-child,
        section[data-testid="stSidebar"] div[role="radiogroup"] label span {
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

        /* 標題系統 */
        h1 {
            font-size: 32px !important;
            font-weight: 700 !important;
            margin-bottom: 24px !important;
            border-bottom: 1px solid #2D2D2D !important;
            padding-bottom: 12px !important;
            color: #ECECEC !important;
        }

        /* 4. 警示區改進 - Danger Zone */
        .danger-zone {
            background-color: rgba(127, 29, 29, 0.4) !important;
            border: 1px solid #EF4444 !important;
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

        .normal-zone {
            background-color: rgba(16, 185, 129, 0.1) !important;
            border: 1px solid #10B981 !important;
            border-radius: 16px !important;
            padding: 24px !important;
            color: #ECECEC !important;
        }

        /* 5. 修正側邊欄輸入框樣式 */
        section[data-testid="stSidebar"] .stTextInput input {
            background-color: #2A2B32 !important;
            border: 1px solid #3F3F46 !important;
            color: #ECECEC !important;
            border-radius: 8px !important;
        }
        
        section[data-testid="stSidebar"] .stButton button {
            width: 100% !important;
            background-color: #3F3F46 !important;
            border: none !important;
            color: #ECECEC !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)
