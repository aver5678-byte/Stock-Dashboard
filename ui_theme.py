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
        
        /* 主內容容器：置中並限制寬度 */
        .main .block-container {
            max-width: 1100px !important;
            padding-top: 3rem !important;
            padding-bottom: 5rem !important;
            margin: 0 auto !important;
        }

        /* 2. 側邊欄 (Sidebar) 寬度與背景 */
        section[data-testid="stSidebar"] {
            background-color: #171717 !important;
            min-width: 320px !important;
            max-width: 320px !important;
            border-right: 1px solid #2D2D2D;
        }
        
        /* 側邊欄內容間距 */
        section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
            padding: 2.5rem 1.25rem !important;
        }

        /* 側邊欄所有標題 */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3 {
            color: #FFFFFF !important;
            font-size: 24px !important;
            font-weight: 800 !important;
            margin-bottom: 24px !important;
            border: none !important;
        }
        
        /* 側邊欄普通文字與 Label */
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stWidgetLabel p {
            color: #ECECEC !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }

        /* 選單項目設計 (Radio group) */
        section[data-testid="stSidebar"] div[role="radiogroup"] {
            display: flex;
            flex-direction: column;
            gap: 10px;
            padding-top: 15px;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 16px 20px !important;
            border-radius: 12px !important;
            color: #ECECEC !important;
            font-size: 19px !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
            cursor: pointer;
            background-color: transparent !important;
            border: 1px solid transparent !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
        }
        
        /* 選單文字強制白色 */
        section[data-testid="stSidebar"] div[role="radiogroup"] label div p {
            color: #ECECEC !important;
            font-size: 19px !important;
            margin: 0 !important;
        }

        /* 選單 Hover */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #2A2B32 !important;
            border: 1px solid #3F3F46 !important;
        }
        
        /* 選單 Active (選中狀態) */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #343541 !important;
            color: #FFFFFF !important;
            box-shadow: inset 4px 0 0 0 #F87171 !important; /* 內部紅條，更穩定 */
            border: 1px solid #4D4D4D !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
        }
        
        /* 隱藏 Radio 圈圈 (修正：只隱藏第一個 div) */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* 3. 主內容區卡片系統 */
        [data-testid="stMetric"] {
            background-color: #2A2B32 !important;
            border: 1px solid #3F3F46 !important;
            border-radius: 16px !important;
            padding: 24px !important;
        }

        h1 {
            font-size: 34px !important;
            font-weight: 800 !important;
            margin-bottom: 24px !important;
            color: #FFFFFF !important;
            border-bottom: 1px solid #2D2D2D !important;
        }

        /* 4. 警示與安全區 */
        .danger-zone {
            background-color: rgba(127, 29, 29, 0.45) !important;
            border: 1px solid #EF4444 !important;
            border-radius: 16px !important;
            padding: 35px !important;
            margin-bottom: 30px !important;
        }
        
        .danger-zone h2 {
            color: #F87171 !important;
            font-size: 28px !important;
            font-weight: 800 !important;
            border: none !important;
        }

        .normal-zone {
            background-color: rgba(16, 185, 129, 0.15) !important;
            border: 1px solid #10B981 !important;
            border-radius: 16px !important;
            padding: 28px !important;
        }

        /* 5. 組件樣式優化 */
        section[data-testid="stSidebar"] .stTextInput input {
            height: 45px !important;
            font-size: 16px !important;
            background-color: #2A2B32 !important;
            border: 1px solid #3F3F46 !important;
            color: #FFFFFF !important;
        }
        
        section[data-testid="stSidebar"] button {
            height: 45px !important;
            font-size: 17px !important;
            font-weight: 700 !important;
            background-color: #F87171 !important; /* 登入按鈕改用紅色點綴 */
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 10px !important;
        }
        </style>
    """, unsafe_allow_html=True)
