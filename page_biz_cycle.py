import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

from datetime import datetime

def page_biz_cycle():
    st.markdown('<h1 class="centered-title">🌡️ 景氣對策信號監控 (Business Cycle Monitor)</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#9CA3AF; margin-top:-30px; margin-bottom:50px;'>系統更新時間：2026-02-22 | 數據版本：Auto-Sync Terminal v4.2</p>", unsafe_allow_html=True)
    
    # --- 動態時間計算 ---
    # 起始日 2025-09-01，今日 2026-02-22
    now = datetime.now()
    research_start = datetime(2025, 9, 1)
    # 計算相差月數
    months_ongoing = (now.year - research_start.year) * 12 + (now.month - research_start.month)
    if months_ongoing < 1: months_ongoing = 1 # 確保最小為 1
    
    # --- 1. 頂部狀態：景氣壓力計 ---
    col_t1, col_t2 = st.columns([1.2, 1])
    
    current_score = 34.0  # 最新公布分數 (由研究模組提供)
    
    with col_t1:
        fig_score = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_score,
            title = {'text': "最新景氣對策信號分數", 'font': {'size': 20, 'color': '#6B7280'}},
            gauge = {
                'axis': {'range': [9, 45], 'tickcolor': "#E5E7EB"},
                'bar': {'color': "#EF4444" if current_score >= 32 else "#10B981"},
                'steps': [
                    {'range': [9, 17], 'color': '#DBEAFE'}, # 藍燈
                    {'range': [17, 23], 'color': '#F0FDF4'}, # 黃藍燈
                    {'range': [23, 31], 'color': '#FEF9C3'}, # 綠燈
                    {'range': [31, 37], 'color': '#FFEDD5'}, # 黃紅燈
                    {'range': [37, 45], 'color': '#FEE2E2'}  # 紅燈
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 32
                }
            },
            number = {'font': {'family': 'JetBrains Mono', 'size': 50}}
        ))
        fig_score.update_layout(height=350, margin=dict(l=30, r=40, t=50, b=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_score, use_container_width=True)

    with col_t2:
        # 計算進度條 (相對於中位數 10 個月)
        progress = min(100.0, float(months_ongoing / 10.0 * 100.0))
        st.markdown(f'''
            <div class="tech-card" style="margin-top:50px; text-align:center;">
                <div class="summary-label">本次黃紅燈已持續</div>
                <div class="summary-value" style="color:#EF4444;">{int(months_ongoing)} <span style="font-size:18px;">個月</span></div>
                <div style="margin-top:20px; font-size:14px; color:#6B7280;">
                    歷史中位數: 10 個月 | 歷史平均: 8.4 個月
                </div>
                <div class="energy-bar-container" style="height:10px; margin-top:15px;">
                    <div class="energy-bar-fill-up" style="width:{progress}%; background:#EF4444;"></div>
                </div>
                <p style="font-size:12px; color:#9CA3AF; margin-top:10px;">目前循環：高機率進入「長延續型」擴張週期</p>
            </div>
        ''', unsafe_allow_html=True)

    # --- 2. 核心結論區 ---
    st.markdown('<div style="margin-top:50px;"></div>', unsafe_allow_html=True)
    st.markdown(f'''
        <div class="normal-zone" style="max-width:100%; border-left:8px solid #3B82F6; background:linear-gradient(135deg, #F0F9FF 0%, #FFFFFF 100%);">
            <h3 style="color:#1E3A8A; margin-bottom:15px;">📊 歷史研究結論 (1995-2025)</h3>
            <p style="font-size:17px; color:#334155; line-height:1.7; text-align:left;">
                自 1995 年以來，景氣對策信號首次進入黃紅區共 <b>8 次</b>。約有 <b>57%</b> 機率進入長期過熱階段（持續 10 個月以上），
                另一半則快速回落（2 個月內）。歷史中長延續型的過熱週期多維持 <b>10–16 個月</b>，中位數約 10 個月。
            </p>
        </div>
    ''', unsafe_allow_html=True)

    # --- 3. 雙型態對決卡片 ---
    st.markdown('<h2 style="text-align:center; margin-top:80px;">🧬 歷史循環兩大明確型態</h2>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown('''
            <div class="tech-card" style="border-left:8px solid #FBBF24;">
                <h3 style="color:#B45309; margin:0;">🟡 短促型 (1-2個月)</h3>
                <p style="color:#6B7280; font-size:14px; margin:10px 0;">快速跌破 32，多為短期過熱或假突破。</p>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <span class="log-type-tag" style="background:#FEF3C7; color:#B45309;">1995</span>
                    <span class="log-type-tag" style="background:#FEF3C7; color:#B45309;">2000</span>
                    <span class="log-type-tag" style="background:#FEF3C7; color:#B45309;">2007</span>
                </div>
                <div style="margin-top:20px; font-size:12px; color:#9CA3AF;">發生率: 43% | 影響: 短暫洗盤</div>
            </div>
        ''', unsafe_allow_html=True)
        
    with c2:
        st.markdown('''
            <div class="tech-card" style="border-left:8px solid #EF4444;">
                <h3 style="color:#B91C1C; margin:0;">🔴 長延續型 (10-16個月)</h3>
                <p style="color:#6B7280; font-size:14px; margin:10px 0;">真正的景氣擴張循環，過熱持續時間較長。</p>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <span class="log-type-tag" style="background:#FEE2E2; color:#B91C1C;">2003</span>
                    <span class="log-type-tag" style="background:#FEE2E2; color:#B91C1C;">2009</span>
                    <span class="log-type-tag" style="background:#FEE2E2; color:#B91C1C;">2020</span>
                    <span class="log-type-tag" style="background:#FEE2E2; color:#B91C1C;">2025 (預估)</span>
                </div>
                <div style="margin-top:20px; font-size:12px; color:#9CA3AF;">發生率: 57% | 影響: 長期牛市</div>
            </div>
        ''', unsafe_allow_html=True)

    # --- 4. 歷史週期流水日誌 ---
    st.markdown('<h2 style="text-align:center; margin-top:80px;">📜 景氣黃紅區歷史全紀錄</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#9CA3AF; margin-bottom:40px;">能量條代表該循環持續月數 (Scale: 0-16 個月)</p>', unsafe_allow_html=True)

    history_data = [
        {"period": f"2025.09 - 進行中 ({now.strftime('%Y.%m')})", "months": float(months_ongoing), "type": "長延續型 (預估)", "color": "#EF4444", "bg": "#FEE2E2"},
        {"period": "2020.12 - 2022.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "#FEE2E2"},
        {"period": "2009.12 - 2011.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "#FEE2E2"},
        {"period": "2003.11 - 2004.09", "months": 11.0, "type": "長延續型", "color": "#EF4444", "bg": "#FEE2E2"},
        {"period": "2007.08 - 2007.09", "months": 2.0, "type": "短促型", "color": "#FBBF24", "bg": "#FEF3C7"},
        {"period": "2000.04 - 2000.05", "months": 2.0, "type": "短促型", "color": "#FBBF24", "bg": "#FEF3C7"},
        {"period": "1995.02 - 1995.02", "months": 1.0, "type": "短促型", "color": "#FBBF24", "bg": "#FEF3C7"},
    ]

    for item in history_data:
        w = (item['months'] / 16) * 100
        st.markdown(f'''
            <div class="log-item">
                <div class="log-date" style="min-width:180px;">📅 {item['period']}</div>
                <div style="flex: 1;">
                    <span class="log-type-tag" style="color:{item['color']}; background:{item['bg']};">{item['type']}</span>
                    <div style="display:flex; align-items:center; gap:15px; margin-top:10px;">
                        <div class="energy-bar-container" style="flex:1;"><div class="energy-bar-fill-up" style="width:{w}%; background:{item['color']};"></div></div>
                        <div style="font-family:'JetBrains Mono'; font-weight:800; font-size:14px; color:#4B5563;">{item['months']}M</div>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#9CA3AF; font-size:12px; margin-top:80px;'>系統由 aver5678 量化模組驅動 | 景氣研究模型: Cycle-Analyzer v1.0</p>", unsafe_allow_html=True)
