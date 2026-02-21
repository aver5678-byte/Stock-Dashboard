import streamlit as st

def apply_global_theme():
    """
    大師級極簡白方案 (Masterpiece Pure White)
    設計邏輯：
    - 精緻白(#FFFFFF)與冷淺灰(#F9F9FB)的層次堆疊
    - 垂直置中對齊系統
    - 大型標題排版 (Typography-first)
    """
    st.markdown("""
        <style>
        /* 1. 全站背景 (徹底白色化，消除白邊) */
        .stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], .block-container {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
        }

        /* 導航欄模糊化 */
        header[data-testid="stHeader"] {
            background-color: rgba(255, 255, 255, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            border-bottom: 1px solid #F0F0F0 !important;
        }

        /* 主內容容器：極簡置中佈局 */
        .main .block-container {
            max-width: 1100px !important;
            padding-top: 3rem !important;
            padding-bottom: 6rem !important;
            margin: 0 auto !important;
        }

        /* 2. 側邊欄 (Sidebar) 大師級設計 */
        section[data-testid="stSidebar"] {
            background-color: #F9F9FB !important; /* 冷淺灰 */
            width: 320px !important;
            border-right: 1px solid #E5E7EB !important;
        }
        
        section[data-testid="stSidebar"] .st-emotion-cache-16txtl3 {
            padding: 3rem 1.5rem !important;
        }

        /* 側欄標題與文字 */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] .stMarkdown p,
        section[data-testid="stSidebar"] .stWidgetLabel p {
            color: #1A1A1A !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }
        
        section[data-testid="stSidebar"] h1 { font-size: 26px !important; margin-bottom: 30px !important; border:none !important; }
        section[data-testid="stSidebar"] .stMarkdown p { font-size: 16px !important; opacity: 0.6; }

        /* 選單項目 (Radio Group) */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 16px 20px !important;
            border-radius: 14px !important;
            margin-bottom: 12px !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            cursor: pointer;
            background-color: transparent !important;
            border: 1px solid transparent !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #EDEDF0 !important;
        }
        
        /* 選單 Active 狀態：膠囊高亮 + 紅條 */
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] {
            background-color: #EDEDF0 !important;
            box-shadow: inset 4px 0 0 0 #F87171 !important;
            border: 1px solid #E5E7EB !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] label p {
            font-size: 18px !important;
            font-weight: 700 !important;
            color: #374151 !important;
        }
        
        section[data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"] p {
            color: #111827 !important;
            font-weight: 800 !important;
        }

        /* 隱藏 Radio 圈圈 */
        section[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child {
            display: none !important;
        }

        /* 3. 置中大型標題系統 */
        h1.centered-title {
            text-align: center !important;
            font-size: 42px !important;
            font-weight: 900 !important;
            letter-spacing: 0.05em !important;
            color: #1A1A1A !important;
            margin: 2rem 0 !important;
            line-height: 1.2 !important;
            border: none !important;
        }

        /* 4. 風險預警區：白色磨砂置中卡片 */
        .danger-zone {
            text-align: center !important;
            background-color: #FFF5F5 !important; /* 極淺粉紅 */
            border: 1px solid #FEE2E2 !important;
            border-left: 6px solid #EF4444 !important; /* 紅色質感提示 */
            border-radius: 20px !important;
            padding: 40px !important;
            margin: 30px auto !important;
            max-width: 850px !important;
            box-shadow: 0 10px 30px rgba(239, 68, 68, 0.05) !important;
        }
        
        .danger-zone h2 {
            color: #DC2626 !important;
            font-size: 32px !important;
            font-weight: 900 !important;
            margin-bottom: 20px !important;
            border: none !important;
        }
        
        .danger-zone .bias-value {
            font-size: 52px !important;
            font-weight: 900 !important;
            color: #1A1A1A !important;
            font-family: 'JetBrains Mono', 'Monaco', monospace !important;
            display: block;
            margin: 15px 0;
            letter-spacing: -2px;
        }

        .normal-zone {
            text-align: center !important;
            background-color: #F0FDF4 !important;
            border: 1px solid #DCFCE7 !important;
            border-radius: 20px !important;
            padding: 40px !important;
            margin: 30px auto !important;
            max-width: 850px !important;
        }

        /* 5. 數據指標與按鈕 */
        [data-testid="stMetric"] {
            background-color: #F9FAFB !important;
            border: 1px solid #F3F4F6 !important;
            border-radius: 18px !important;
            padding: 24px !important;
        }
        
        .stButton button {
            background-color: #F87171 !important;
            color: white !important;
            font-weight: 800 !important;
            border-radius: 12px !important;
            height: 50px !important;
            border: none !important;
            box-shadow: 0 4px 6px rgba(248, 113, 113, 0.2);
        }

        .stDataFrame {
            border: 1px solid #F3F4F6 !important;
            border-radius: 16px !important;
        }
        </style>
    """, unsafe_allow_html=True)
