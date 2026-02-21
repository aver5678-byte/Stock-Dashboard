import streamlit as st

def apply_global_theme():
    """
    頂尖 1% 前端工程師作品：ChatGPT 5.0 輕量白沈浸主題
    融合重點：
    - 分組導航系統 (Section Headers)
    - 底部個人中心 (User Profile Section)
    - 膠囊型高亮選取 (Pill Hover/Active)
    - 全站亮色圖表優化
    """
    st.markdown("""
        <style>
        /* 1. 全站基礎 - 沈浸式亮白 */
        .stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], .block-container {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
        }

        /* 導航頭部毛玻璃 */
        header[data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(15px) !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.03) !important;
        }

        /* 2. 側邊欄 (Sidebar) - GPT 精密重構 */
        section[data-testid="stSidebar"] {
            background-color: #F9F9FB !important;
            min-width: 320px !important;
            max-width: 320px !important;
            border-right: 1px solid #EDEDF0 !important;
        }
        
        /* 側邊欄內邊距 */
        section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
            padding: 2rem 1rem !important;
            display: flex;
            flex-direction: column;
        }

        /* --- 選單分組標題 (Section Headers) --- */
        .sidebar-section-header {
            font-size: 13px !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #9CA3AF !important;
            margin: 24px 0 12px 12px !important;
        }

        /* --- 選單項目 (The Pill Design) --- */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 12px 14px !important;
            border-radius: 12px !important;
            margin: 0 4px 6px 4px !important;
            transition: all 0.2s cubic-bezier(0.19, 1, 0.22, 1) !important;
            background-color: transparent !important;
            border: none !important;
        }

        /* Hover & Active 效果 */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #ECECEC !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #E2E2E6 !important;
        }
        
        /* 隱藏 Radio 圈圈，只留文字 */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            font-size: 17px !important;
            font-weight: 600 !important;
            color: #374151 !important;
            margin: 0 !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
            color: #111827 !important;
            font-weight: 700 !important;
        }

        /* 3. 底部個人中心 (Profile Section) */
        .user-profile-card {
            margin-top: auto; /* 強制置底 */
            padding: 16px;
            border-top: 1px solid #EDEDF0;
            display: flex;
            align-items: center;
            gap: 12px;
            cursor: pointer;
            transition: background 0.2s;
            border-radius: 12px;
        }
        .user-profile-card:hover {
            background-color: #EDEDF0;
        }
        .user-avatar {
            width: 36px;
            height: 36px;
            background-color: #F87171;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 15px;
        }
        .user-info-text {
            flex-grow: 1;
        }
        .user-name {
            font-size: 15px;
            font-weight: 700;
            color: #1A1A1A;
        }
        .user-role {
            font-size: 12px;
            color: #9CA3AF;
        }

        /* 4. 主內容置中與警告卡片 */
        h1.centered-title {
            text-align: center !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            letter-spacing: -0.04em !important;
            color: #111827 !important;
            margin-top: 1rem !important;
            margin-bottom: 2.5rem !important;
        }

        .danger-zone {
            text-align: center !important;
            background-color: #FFF5F5 !important;
            border: 1px solid #FEE2E2 !important;
            border-left: 6px solid #EF4444 !important;
            border-radius: 20px !important;
            padding: 40px !important;
            margin: 0 auto 40px auto !important;
            max-width: 850px !important;
            box-shadow: 0 4px 20px rgba(239, 68, 68, 0.04) !important;
        }
        
        .danger-zone h2 {
            color: #B91C1C !important;
            font-size: 32px !important;
            font-weight: 850 !important;
        }
        
        .bias-value {
            font-size: 58px !important;
            font-weight: 900 !important;
            color: #111827 !important;
            letter-spacing: -3px;
        }

        /* 5. 組件樣式優化 */
        section[data-testid="stSidebar"] div.stButton > button {
            background-color: white !important;
            border: 1px solid #E5E7EB !important;
            color: #374151 !important;
            font-size: 14px !important;
            border-radius: 10px !important;
            box-shadow: none !important;
            height: 38px !important;
            width: fit-content !important;
            padding: 0 16px !important;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #F9FAFB !important;
            border-color: #D1D5DB !important;
        }

        .stTextInput input {
            background-color: white !important;
            border: 1px solid #E5E7EB !important;
            height: 40px !important;
            font-size: 14px !important;
        }
        </style>
    """, unsafe_allow_html=True)
