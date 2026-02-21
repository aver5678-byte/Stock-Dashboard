import streamlit as st

def apply_global_theme():
    """
    頂尖 1% 前端工程師作品：ChatGPT 5.0 旗艦白美學 (Masterpiece v2)
    更新：導入置中數據卡片、精簡化專業表格與高級陰影系統
    """
    st.markdown("""
        <style>
        /* 1. 全站沈浸式白底 */
        .stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], [data-testid="stSidebar"], .block-container {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
        }

        header[data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.7) !important;
            backdrop-filter: blur(15px) !important;
            border-bottom: 1px solid rgba(0, 0, 0, 0.03) !important;
        }

        .main .block-container {
            max-width: 1100px !important;
            padding: 3rem 1.5rem !important;
            margin: 0 auto !important;
        }

        /* 2. 側邊欄：GPT 導航進化 */
        section[data-testid="stSidebar"] {
            background-color: #F9F9FB !important;
            min-width: 320px !important;
            border-right: 1px solid #EDEDF0 !important;
        }
        
        /* 分組標題設計 */
        .sidebar-section-header {
            font-size: 13px !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #9CA3AF !important;
            margin: 28px 0 10px 12px !important;
        }

        /* 選項膠囊 */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 12px 14px !important;
            border-radius: 14px !important;
            margin: 2px 4px !important;
            transition: all 0.2s ease !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #ECECEC !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #E2E2E6 !important;
            box-shadow: inset 4px 0 0 0 #F87171 !important;
        }

        /* 3. 置中大標題與卡片系統 */
        h1.centered-title {
            text-align: center !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            letter-spacing: -0.05em !important;
            margin: 2rem 0 !important;
        }

        .summary-card {
            background-color: #FFFFFF !important;
            border: 1px solid #E5E7EB !important;
            border-radius: 24px !important;
            padding: 35px !important;
            text-align: center !important;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.04) !important;
            transition: transform 0.3s ease !important;
        }
        
        .summary-card:hover {
            transform: translateY(-5px) !important;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.06) !important;
        }

        .summary-value {
            font-size: 48px !important;
            font-weight: 900 !important;
            color: #111827 !important;
            letter-spacing: -2px !important;
            margin: 10px 0 !important;
        }
        
        .summary-label {
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #6B7280 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        /* 4. 專業化歷史回測表格樣式 */
        .stDataFrame {
            border: none !important;
            border-radius: 20px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03) !important;
        }

        /* 5. 底部個人中心 (Profile Section) */
        .user-profile-card {
            margin-top: auto;
            padding: 20px 16px;
            border-top: 1px solid #EDEDF0;
            display: flex;
            align-items: center;
            gap: 12px;
            border-radius: 12px;
        }
        
        .user-avatar {
            width: 38px;
            height: 38px;
            background-color: #F87171;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 900;
        }

        /* 6. 其他 UI 元件微調 */
        .stButton button {
            border-radius: 14px !important;
            font-weight: 800 !important;
            transition: all 0.2s !important;
        }
        
        .stSelectbox div[data-baseweb="select"] {
            border-radius: 14px !important;
            background-color: #F9FAFB !important;
        }
        </style>
    """, unsafe_allow_html=True)
