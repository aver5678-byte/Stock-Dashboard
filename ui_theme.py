import streamlit as st

def apply_global_theme():
    """
    指揮官專屬：SaaS 級量化交易終端美學 v5.0
    核心技術：全站黑化同步、導航卡片化、100% 高對比文字、發光指示條
    """
    st.markdown("""
        <style>
        /* 1. 核心字體與全站背景 */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;800&family=Inter:wght@400;700;900&display=swap');
        
        .stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], [data-testid="stSidebar"], .block-container {
            background-color: #020617 !important;
            color: #F8FAFC !important;
            font-family: 'Inter', -apple-system, sans-serif !important;
        }

        /* 2. 側邊欄 (Sidebar) 面板化重塑 */
        section[data-testid="stSidebar"] {
            background-color: #020617 !important;
            width: 380px !important;
            border-right: 1px solid rgba(56, 189, 248, 0.2) !important;
        }

        section[data-testid="stSidebar"] > div {
            background-color: #020617 !important;
            padding-top: 20px !important;
        }

        /* 解除 Streamlit 預設的大量左右留白，允許卡片擴張 */
        div[data-testid="stSidebarUserContent"] {
            padding-left: 20px !important;
            padding-right: 5px !important;
            padding-top: 0px !important;
        }

        /* 隱藏原生圓點與 Navigation 標籤 */
        div[data-testid="stSidebarUserContent"] .stRadio div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        div[data-testid="stSidebarUserContent"] .stRadio label[data-testid="stWidgetLabel"] {
            display: none !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
        }

        /* 側邊欄分類標題 (SaaS 標章) */
        .sidebar-section-header {
            font-size: 14px !important;
            text-transform: uppercase !important;
            letter-spacing: 3px !important;
            color: #38BDF8 !important;
            margin: 40px 0 20px 15px !important;
            font-weight: 900 !important;
            display: flex;
            align-items: center;
        }
        .sidebar-section-header::after {
            content: "";
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, #38BDF8, transparent);
            margin-left: 15px;
            opacity: 0.3;
        }

        /* 3. 導覽項目：強制撐滿側邊欄容器 */
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] > div[role="radiogroup"] {
            gap: 15px !important;
            width: 100% !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: stretch !important;
        }

        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] > div[role="radiogroup"] > label {
            width: 100% !important;
            max-width: 100% !important;
            box-sizing: border-box !important;
            background: rgba(30, 41, 59, 0.4) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
            border-radius: 12px !important;
            padding: 22px 20px !important;
            margin-bottom: 0px !important;
            transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 19px !important;
            font-family: 'JetBrains Mono', monospace !important;
            opacity: 1 !important;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6) !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            cursor: pointer !important;
        }

        /* 暴力強制所有狀態文字純白高亮與左對齊 */
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label p,
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label span,
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"] {
            color: #FFFFFF !important;
            opacity: 1 !important;
            font-size: 19px !important;
            font-weight: 800 !important;
            font-family: 'JetBrains Mono', monospace !important;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5) !important;
            width: 100% !important;
            text-align: left !important;
            display: block !important;
            margin: 0 !important;
        }

        /* Hover 時微浮起與發光 */
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label:hover {
            transform: translateY(-5px) scale(1.02) !important;
            background: #1E293B !important;
            border-color: #38BDF8 !important;
            box-shadow: 0 10px 30px rgba(56, 189, 248, 0.2) !important;
        }
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label:hover p {
            color: #38BDF8 !important;
        }

        /* Active 選中項：霓虹指示燈效果 */
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label[data-checked="true"],
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.3) 0%, rgba(56, 189, 248, 0.05) 100%) !important;
            border: 1px solid #38BDF8 !important;
            border-left: 8px solid #38BDF8 !important;
            box-shadow: 0 0 30px rgba(56, 189, 248, 0.3) !important;
            transform: scale(1.02) !important;
        }
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label[data-checked="true"] p,
        div[data-testid="stSidebarUserContent"] div[data-testid="stRadio"] label:has(input:checked) p {
            color: #FFFFFF !important;
            font-weight: 950 !important;
            text-shadow: 0 0 15px rgba(255, 255, 255, 0.5) !important;
        }

        /* 4. 側邊面板光束邊緣 */
        section[data-testid="stSidebar"]::after {
            content: "";
            position: absolute;
            right: 0;
            top: 10%;
            width: 2px;
            height: 80%;
            background: linear-gradient(180deg, transparent, #38BDF8, transparent);
            box-shadow: 0 0 20px #38BDF8;
        }

        /* 5. 強化右側主標題設計 */
        .centered-title {
            text-align: center !important;
            font-size: 56px !important;
            font-weight: 950 !important;
            letter-spacing: -2px !important;
            background: linear-gradient(135deg, #FFFFFF 0%, #94A3B8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 60px 0 40px 0 !important;
        }

        /* 6. 對齊右側卡片 (技術感) */
        .tech-card {
            position: relative;
            background: #0F172A !important;
            border: 1px solid #1E293B !important;
            border-radius: 20px !important;
            padding: 30px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5) !important;
        }
        .tech-card::before {
            content: "";
            position: absolute;
            top: -1px; left: -1px; width: 25px; height: 25px;
            border-top: 3px solid #38BDF8; border-left: 3px solid #38BDF8;
            border-top-left-radius: 20px;
        }

        /* 數據摘要卡片 */
        .summary-card {
            text-align: center;
            background: #1E293B !important;
            padding: 25px !important;
            border-radius: 20px !important;
            border: 1px solid #334155 !important;
            box-shadow: 0 10px 20px rgba(0,0,0,0.2) !important;
        }
        .summary-label {
            font-size: 13px !important; color: #94A3B8 !important;
            font-weight: 800 !important; letter-spacing: 1px !important;
            text-transform: uppercase; margin-bottom: 10px !important;
        }
        .summary-value {
            font-family: 'JetBrains Mono' !important; font-size: 42px !important;
            font-weight: 900 !important; color: #FFFFFF !important;
        }

        /* 修正按鈕樣貌 */
        .stButton button {
            background-color: #1E293B !important;
            color: #FFFFFF !important;
            border: 1px solid #38BDF8 !important;
            border-radius: 12px !important;
            width: 100% !important;
            padding: 10px !important;
            font-weight: 800 !important;
            transition: all 0.2s ease !important;
        }
        .stButton button:hover {
            background-color: #38BDF8 !important;
            color: #020617 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
        }

        /* ---------------------------------------------------
           下拉選單 (Selectbox) 暗黑玻璃化重塑
           --------------------------------------------------- */
        
        /* 1. 標題文字 (Label) 亮度拯救 */
        div[data-testid="stSelectbox"] label p {
            color: #FFFFFF !important;
            font-weight: 800 !important;
            font-size: 15px !important;
            letter-spacing: 1px !important;
        }

        /* 2. 選單本體 (Dropdown box) 玻璃化與外框 */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: rgba(15, 23, 42, 0.9) !important;
            border: 2px solid #334155 !important;
            border-radius: 8px !important;
            color: #F1F5F9 !important;
            transition: all 0.3s ease;
        }

        /* 3. 選單互動態 (Hover / Focus) 霓虹發光 */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div:focus-within {
            border-color: #38BDF8 !important;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
        }

        /* 4. 選單內文字與下拉箭頭 */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] span {
            color: #F1F5F9 !important;
            font-weight: 700 !important;
        }
        svg[data-baseweb="icon"] {
            color: #38BDF8 !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
