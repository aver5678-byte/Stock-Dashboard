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
        
        .stApp, .block-container {
            background-color: #FFFFFF !important;
            color: #1A1A1A !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* 2. 科技感卡片系統 (Tech corners) */
        .tech-card {
            background: #FFFFFF;
            border: 1px solid #EDEDF0;
            border-radius: 20px;
            padding: 24px;
            position: relative;
            box-shadow: 0 10px 30px rgba(0,0,0,0.02);
            transition: transform 0.2s ease;
            margin-bottom: 20px;
        }
        
        .tech-card::before, .tech-card::after {
            content: "";
            position: absolute;
            width: 15px;
            height: 15px;
            border: 2px solid #F87171;
            opacity: 0.3;
        }
        .tech-card::before { top: 10px; left: 10px; border-right: 0; border-bottom: 0; }
        .tech-card::after { bottom: 10px; right: 10px; border-left: 0; border-top: 0; }

        /* 3. 能量條 (Energy Bars for Logs) */
        .energy-bar-container {
            width: 100%;
            height: 8px;
            background: #F3F4F6;
            border-radius: 4px;
            margin: 8px 0;
            overflow: hidden;
        }
        .energy-bar-fill-up { height: 100%; background: #10B981; border-radius: 4px; } /* 綠色漲幅 */
        .energy-bar-fill-down { height: 100%; background: #EF4444; border-radius: 4px; } /* 紅色跌幅 */

        /* 4. 數位流水日誌卡片 (Timeline Log Card) */
        .log-item {
            display: flex;
            align-items: center;
            padding: 18px 25px;
            border-bottom: 1px solid #F3F4F6;
            gap: 20px;
            transition: background 0.2s;
        }
        .log-item:hover { background: #F9FAFB; }
        
        .log-date {
            min-width: 110px;
            font-family: 'JetBrains Mono', monospace;
            font-weight: 800;
            font-size: 15px;
            color: #374151;
        }
        .log-type-tag {
            padding: 4px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
        }

        /* 5. 側邊欄：GPT 導航 */
        section[data-testid="stSidebar"] {
            background-color: #F9F9FB !important;
            border-right: 1px solid #EDEDF0 !important;
        }
        
        .sidebar-section-header {
            font-size: 11px !important;
            font-weight: 800 !important;
            color: #9CA3AF !important;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin: 24px 0 8px 12px !important;
        }

        /* 6. 置中標題 */
        h1.centered-title {
            text-align: center !important;
            font-size: 40px !important;
            font-weight: 900 !important;
            letter-spacing: -0.06em !important;
            margin: 1rem 0 3rem 0 !important;
            color: #111827 !important;
        }

        /* 7. 修復原本毀損的警告區 (改造成半圓中心數據) */
        .gauge-center-data {
            text-align: center;
            margin-top: -60px; /* 向上移動至儀表板圓心 */
            z-index: 10;
        }
        .gauge-value-main {
            font-size: 56px;
            font-weight: 900;
            font-family: 'JetBrains Mono', monospace;
            color: #111827;
            letter-spacing: -3px;
        }
        </style>
    """, unsafe_allow_html=True)
