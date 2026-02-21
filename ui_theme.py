import streamlit as st

def apply_global_theme():
    """
    頂尖 1% 前端工程師作品：GPT-Command-Center 極簡白旗艦美學
    核心技術：半圓儀表盤、數位流水日誌、能量條可視化、科技角卡片
    """
    st.markdown("""
        <style>
        /* 1. 核心字體與背景 */
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;800&family=Inter:wght@400;700;900&display=swap');
    /* 1. 全站背景 (徹底白色化，消除白邊) */
.stApp, .stAppViewContainer, .stMain, [data-testid="stHeader"], [data-testid="stSidebar"], .block-container {
    background-color: #FFFFFF !important;
    color: #1A1A1A !important;
}

/* 側邊欄 (Sidebar) 大師級設計 */
section[data-testid="stSidebar"] {
    background-color: #F9F9FB !important; /* 冷淺灰 */
    width: 320px !important;
    border-right: 1px solid #E5E7EB !important;
}

/* 隱藏預設導覽標籤 */
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* 側邊欄分組標題 */
.sidebar-section-header {
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    color: #9CA3AF !important;
    margin: 20px 0 10px 10px !important;
    font-weight: 700 !important;
}

/* 導覽按鈕 (Radio 模擬) */
div[data-testid="stSidebarUserContent"] .stRadio > div {
    gap: 4px !important;
}

div[data-testid="stSidebarUserContent"] .stRadio label {
    background-color: transparent !important;
    border-radius: 12px !important;
    padding: 10px 15px !important;
    transition: all 0.2s ease !important;
    border: none !important;
    color: #4B5563 !important;
    font-weight: 500 !important;
}

div[data-testid="stSidebarUserContent"] .stRadio label:hover {
    background-color: #F3F4F6 !important;
    color: #111827 !important;
}

div[data-testid="stSidebarUserContent"] .stRadio label[data-selected="true"] {
    background-color: #F3F4F6 !important;
    color: #EF4444 !important;
    font-weight: 700 !important;
    box-shadow: inset 4px 0 0 #EF4444 !important;
}

/* 2. 主標題文字 (ChatGPT 大標風格) */
.centered-title {
    text-align: center !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 52px !important;
    font-weight: 900 !important;
    letter-spacing: -1.5px !important;
    background: linear-gradient(135deg, #1A1A1A 0%, #4B5563 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 60px 0 40px 0 !important;
}

/* 3. 數位指揮中心卡片 (Digital Command Card) */
.tech-card {
    position: relative;
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 20px !important;
    padding: 30px !important;
    box-shadow: 0 10px 40px rgba(0,0,0,0.03) !important;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.tech-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 20px 50px rgba(0,0,0,0.06) !important;
}

/* 科技尖角效果 */
.tech-card::before {
    content: "";
    position: absolute;
    top: -1px;
    left: -1px;
    width: 20px;
    height: 20px;
    border-top: 3px solid #EF4444;
    border-left: 3px solid #EF4444;
    border-top-left-radius: 20px;
}

/* 數據摘要卡片 (Summary Card) */
.summary-card {
    text-align: center;
    background: #F9FAFB !important;
    padding: 25px !important;
    border-radius: 16px !important;
    border: 1px solid #EDEDF0 !important;
}

.summary-label {
    font-size: 13px !important;
    color: #6B7280 !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    margin-bottom: 8px !important;
    text-transform: uppercase;
}

.summary-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 38px !important;
    font-weight: 800 !important;
    color: #111827 !important;
    line-height: 1 !important;
}

/* 4. 風險預警區 (Danger/Normal Zone) */
.danger-zone, .normal-zone {
    text-align: center !important;
    border-radius: 24px !important;
    padding: 40px !important;
    margin: 30px auto !important;
    max-width: 900px !important;
    border: 1px solid rgba(0,0,0,0.05) !important;
}

.danger-zone {
    background: linear-gradient(135deg, #FFF5F5 0%, #FFFFFF 100%) !important;
    border-left: 8px solid #EF4444 !important;
    box-shadow: 0 15px 45px rgba(239, 68, 68, 0.08) !important;
}

.normal-zone {
    background: linear-gradient(135deg, #F0FDF4 0%, #FFFFFF 100%) !important;
    border-left: 8px solid #10B981 !important;
    box-shadow: 0 15px 45px rgba(16, 185, 129, 0.08) !important;
}

.bias-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 64px !important;
    font-weight: 900 !important;
    color: #111827 !important;
    display: block;
    margin: 15px 0;
}

/* 5. 數位流水日誌 (Timeline Log) */
.log-item {
    display: flex;
    align-items: center;
    gap: 20px;
    background: #FFFFFF !important;
    border: 1px solid #F3F4F6 !important;
    padding: 20px 25px !important;
    border-radius: 16px !important;
    margin-bottom: 12px !important;
    transition: all 0.2s ease !important;
}

.log-item:hover {
    border-color: #E5E7EB !important;
    background: #F9FAFB !important;
    transform: scale(1.005);
}

.log-date {
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 800 !important;
    color: #374151 !important;
    min-width: 130px;
}

.log-type-tag {
    font-size: 11px !important;
    font-weight: 800 !important;
    padding: 4px 10px !important;
    border-radius: 20px !important;
    text-transform: uppercase;
}

/* 6. 能量條 (Energy Bar) */
.energy-bar-container {
    width: 100%;
    height: 6px;
    background: #F3F4F6;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 8px;
}

.energy-bar-fill-up {
    height: 100%;
    background: linear-gradient(90deg, #34D399, #10B981);
    border-radius: 10px;
}

.energy-bar-fill-down {
    height: 100%;
    background: linear-gradient(90deg, #F87171, #EF4444);
    border-radius: 10px;
}

/* 個人中心 (User Profile) */
.user-profile-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 16px;
    margin-top: 10px;
}

.user-avatar {
    width: 40px;
    height: 40px;
    background: #EF4444;
    color: white;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 18px;
}

.user-info-text {
    flex: 1;
}

.user-name {
    font-size: 14px;
    font-weight: 700;
    color: #1F2937;
}

.user-role {
    font-size: 11px;
    color: #6B7280;
}
        </style>
    """, unsafe_allow_html=True)
