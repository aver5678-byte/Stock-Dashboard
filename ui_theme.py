import streamlit as st

def apply_global_theme():
    """
    專業金融冷靜深色主題 (ChatGPT 風格)
    低飽和、低對比、灰階分層
    """
    st.markdown("""
        <style>
        /* 1. 整體背景與字體 (色票系統) */
        .stApp {
            background-color: #212121; /* 主背景 */
            color: #ECECEC;           /* 第一層級文字 (Primary) */
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        
        /* 2. 側邊欄 (左側選單) */
        [data-testid="stSidebar"] {
            background-color: #171717; /* 側邊欄背景 */
            border-right: 1px solid #262626;
        }
        
        /* 隱藏預設 Radio button 的圈圈，改造成選單樣式 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label > div:first-of-type {
            display: none;
        }
        
        /* 左側選單設計規格：一般狀態 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label {
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 4px;
            color: #A1A1AA; /* 預設為次要灰色 */
            transition: all 0.2s ease;
            cursor: pointer;
            background-color: transparent;
            display: flex;
            align-items: center;
        }
        
        /* 左側選單設計規格：Hover 狀態 */
        [data-testid="stSidebar"] div[role="radiogroup"] > label:hover {
            background-color: #2A2B32; /* 懸停底色 */
            color: #ECECEC; /* 懸停字體亮起 */
        }
        
        /* 左側選單設計規格：Active 狀態 */
        /* Streamlit checked state is nested but applies aria-checked */
        [data-testid="stSidebar"] div[role="radiogroup"] > label[data-checked="true"],
        [data-testid="stSidebar"] div[role="radiogroup"] > label[aria-checked="true"] {
            background-color: #343541 !important; /* 選中狀態，如 ChatGPT */
            color: #ECECEC !important;
            font-weight: 500;
        }
        
        /* 3. 主畫面卡片系統 (stMetric) */
        [data-testid="stMetric"] {
            background-color: #1E1E1E;
            border: 1px solid #262626; /* 框線 */
            border-radius: 12px;       /* 圓角 12px */
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06); /* 柔和陰影 */
            transition: all 0.2s ease;
        }
        [data-testid="stMetric"]:hover {
            border-color: #3F3F46;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1);
        }
        
        /* 卡片標題：次要資訊 (Low Contrast) */
        [data-testid="stMetricLabel"] {
            color: #A1A1AA !important;
            font-size: 14px;
            font-weight: 500;
        }
        
        /* 卡片數值：主要資訊 */
        [data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 32px !important;
            font-weight: 600;
            padding-top: 8px;
        }
        
        /* 卡片小指標 (綠/紅) 自動由框架控制，我們不強制寫死，保留柔和感 */
        
        /* 4. 字級階層系統 */
        h1 {
            font-size: 24px !important;
            font-weight: 600 !important;
            color: #ECECEC !important;
            padding-bottom: 16px;
            border-bottom: 1px solid #262626;
            margin-bottom: 24px;
        }
        h2 {
            font-size: 18px !important;
            font-weight: 600 !important;
            color: #ECECEC !important;
            margin-top: 32px;
            margin-bottom: 16px;
        }
        h3 {
            font-size: 16px !important;
            font-weight: 500 !important;
            color: #D4D4D8 !important;
        }
        p, li {
            font-size: 14px !important;
            font-weight: 400 !important;
            color: #D4D4D8 !important;
            line-height:建设 1.6;
        }
        
        /* 5. 分隔線與間距規範 */
        hr {
            border-top: 1px solid #262626;
            margin: 32px 0; /* 區塊間距至少 32px */
        }
        
        /* 表格與 DataFrame (卡片化) */
        [data-testid="stDataFrame"] {
            background-color: #1E1E1E;
            border-radius: 12px;
            border: 1px solid #262626;
            overflow: hidden;
        }
        
        /* 按鈕設計 */
        .stButton>button {
            background-color: #262626;
            border: 1px solid #3F3F46;
            color: #ECECEC;
            border-radius: 8px;
            font-weight: 500;
            padding: 8px 16px;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #3F3F46;
            border-color: #52525B;
            color: #FFFFFF;
        }
        
        /* --- 6. 警示狀態設計規格 --- */
        
        /* 極端警示 (極少用，低明度暗紅底 + 警示紅文字，非刺眼的純紅) */
        .danger-zone {
            background-color: #2C1111; /* 低飽和暗紅 */
            border: 1px solid #7F1D1D; /* 強調紅框 */
            border-radius: 12px;
            padding: 20px;
            color: #FCA5A5; /* 安全感警示文字 */
            margin-bottom: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        /* 一般安全 / 中立區塊 */
        .normal-zone {
            background-color: #1E1E1E;
            border: 1px solid #262626;
            border-radius: 12px;
            padding: 20px;
            color: #D4D4D8;
            margin-bottom: 24px;
        }
        
        /* 時空背景提示框 (黃底暖色，非極端警示) */
        .warning-box {
            background-color: #221A0F; /* 低飽和暗橘黃 */
            border-left: 4px solid #D97706; /* 框線提示 */
            border-radius: 4px 12px 12px 4px; /* 單邊直角，其餘圓角 */
            padding: 16px;
            margin: 16px 0;
            color: #FDE68A; /* 暖黃文字 */
        }
        </style>
    """, unsafe_allow_html=True)
