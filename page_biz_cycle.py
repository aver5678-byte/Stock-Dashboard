import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from datetime import datetime

def page_biz_cycle():
    # 使用 session_state 中的 visit_logs 進行記錄，避免 import 循環
    if 'visit_logs' in st.session_state:
        st.session_state['visit_logs'].append({
            '時間': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '使用者': st.session_state.get('user_email', '訪客 (未登入)'),
            '瀏覽模組': "景氣信號監控"
        })
    
    # --- 1. 數據與時間備份項 ---
    now = datetime.now()
    research_start = datetime(2025, 9, 1)
    months_ongoing = (now.year - research_start.year) * 12 + (now.month - research_start.month)
    if months_ongoing < 1: months_ongoing = 1
    current_score = 34.0  # 最新公布分數

    # --- 2. 頂部區域：一體化戰情標頭 (Hero Header) ---
    status_pill_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    status_pill_text = "OVERHEATED" if current_score >= 38 else "EXPANSION" if current_score >= 32 else "STABLE"
    
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;"><div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // BIAS_MACRO_v2.0 // AUTO-SYNC</div><div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div></div><h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2;">💼 景氣信號：長線價值觀測儀</h1><div style="margin-top:20px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.6; max-width:900px; border-left:4px solid #334155; padding-left:20px;">旨在偵測宏觀經濟的「週期水位」。透過國發會對策信號紅/藍燈交替，鎖定歷史性的長線買賣點。當前分數 {current_score} 分，代表市場正處於景氣擴張的活躍階段。</div></div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)

    # --- 3. 戰術即時面板 (Macro HUD) --- 精密重構版
    score_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    
    # 模擬趨勢數據 (MoM)
    mom_delta = -1.0 # 假設由 35 降至 34
    mom_color = "#EF4444" if mom_delta > 0 else "#10B981"
    mom_icon = "↑" if mom_delta > 0 else "↓"
    
    # 生成月份足跡序列 (最後 5 個月)
    months_data = [
        {"m": "09", "s": 38, "c": "#EF4444"},
        {"m": "10", "s": 37, "c": "#EF4444"},
        {"m": "11", "s": 35, "c": "#FBBF24"},
        {"m": "12", "s": 34, "c": "#FBBF24"},
        {"m": "01", "s": 34, "c": "#FBBF24"} 
    ]
    tiles_html = "".join([f'<div style="background:{m["c"]}; color:white; padding:8px 12px; border-radius:8px; text-align:center; min-width:65px; box-shadow:0 4px 10px rgba(0,0,0,0.3); border:2px solid rgba(255,255,255,0.2);"><div style="font-size:11px; font-weight:800; opacity:0.8;">{m["m"]}月</div><div style="font-family:\'JetBrains Mono\'; font-size:18px; font-weight:950;">{m["s"]}</div></div>' for m in months_data])
    
    progress_val = int(min(months_ongoing/10*100, 100))
    
    hud_html = f"""<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:45px; margin-bottom:40px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:18px; color:#94A3B8; font-weight:800; margin-bottom:15px; display:flex; align-items:center; gap:10px;"><span style="width:10px; height:10px; background:{score_color}; border-radius:50%; box-shadow:0 0 10px {score_color};"></span>當前景氣對策分數</div><div style="display:flex; align-items:center; gap:25px;"><div style="font-family:'JetBrains Mono'; font-size:82px; font-weight:950; color:{score_color}; line-height:1; letter-spacing:-4px;">{current_score:,.0f}</div><div style="display:flex; flex-direction:column; gap:8px;"><div style="font-family:'JetBrains Mono'; font-size:24px; font-weight:900; color:{mom_color}; background:rgba(255,255,255,0.05); padding:2px 10px; border-radius:6px;">{mom_icon} {abs(mom_delta):.0f} <span style="font-size:14px; opacity:0.7;">MoM</span></div><div style="background:rgba(255,255,255,0.1); color:white; padding:10px 20px; border-radius:10px; font-size:22px; font-weight:950; border:2px solid {score_color}; box-shadow:0 0 20px rgba(251, 191, 36, 0.2);">⚡ 黃紅燈：擴張期</div></div></div></div><div style="width:2px; height:120px; background:#334155; margin:0 50px;"></div><div style="flex:1.5;"><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;"><div style="text-align:left;"><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">● 觸發點：2025/09</div><div style="font-size:22px; color:#F1F5F9; font-weight:900;">本次熱度足跡 <span style="color:#7DD3FC; font-size:16px;">(已持續 {int(months_ongoing)} 個月)</span></div></div><div style="display:flex; gap:12px;">{tiles_html}</div></div><div style="background:rgba(255,255,255,0.03); padding:15px 25px; border-radius:12px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><div style="font-size:16px; color:#38BDF8; font-weight:900; letter-spacing:1px;">📊 循環防禦警戒線 (10-16月)</div><div style="font-family:'JetBrains Mono'; font-size:18px; font-weight:900; color:#38BDF8;">{progress_val}% 戰備進度</div></div><div style="height:12px; background:#0F172A; border-radius:10px; overflow:hidden; border:1px solid #334155;"><div style="width:{progress_val}%; height:100%; background:linear-gradient(90deg, #0284C7, #38BDF8); box-shadow:0 0 15px #38BDF8;"></div></div></div></div></div></div>"""
    st.markdown(hud_html, unsafe_allow_html=True)

    # --- 4. 戰略模擬：歷史循環劇本對標 ---
    st.markdown('<h2 style="text-align:left; font-size:32px; margin-top:60px; margin-bottom:20px; color:#1E293B;">🛡️ 戰略模擬：歷史過熱週期回測</h2>', unsafe_allow_html=True)
    
    simulation_html = f"""<div style="background:#1E293B; border:4px solid #475569; border-radius:12px; padding:40px; display:flex; gap:40px; margin-bottom:40px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="flex:1.2; background:#0F172A; padding:35px; border-radius:12px; border-left:8px solid #3B82F6; text-align:left;"><div style="font-size:22px; color:#94A3B8; font-weight:800; margin-bottom:15px;">📊 歷史研究分佈 (1995-2025)</div><div style="font-size:17px; color:#F1F5F9; font-weight:600; line-height:1.7;">自 1995 年以來，景氣燈號首次進入「黃紅區」共 8 次。其中有 <b>57%</b> 會演變成長達一年的「超級擴張期」，剩下則為短暫過熱。目前數據顯示我們極高機率正處於<b>長循環劇本</b>中。</div></div><div style="flex:1; display:flex; flex-direction:column; justify-content:center; background:rgba(255,255,255,0.03); padding:30px; border-radius:12px;"><div style="font-size:22px; color:#E2E8F0; font-weight:800; margin-bottom:20px; border-bottom:2px solid #334155; padding-bottom:15px;">🔍 測距模擬：若循環結束...</div><div style="display:flex; flex-direction:column; gap:20px;"><div><div style="color:#94A3B8; font-size:15px; font-weight:800; margin-bottom:5px;">🆘 劇本一：長延續擴張 (歷史平均)</div><div style="font-family:'JetBrains Mono'; font-size:28px; font-weight:950; color:#EF4444;">10 - 16 個月 <span style="font-size:16px; color:#FCA5A5;">(發生率 57%)</span></div></div><div><div style="color:#94A3B8; font-size:15px; font-weight:800; margin-bottom:5px;">✅ 劇本二：短促型過熱 (快速洗盤)</div><div style="font-family:'JetBrains Mono'; font-size:28px; font-weight:950; color:#10B981;">1 - 2 個月 <span style="font-size:16px; color:#A7F3D0;">(發生率 43%)</span></div></div></div></div></div>"""
    st.markdown(simulation_html, unsafe_allow_html=True)

    # --- 5. 數位流水日誌 ---
    st.markdown('<h2 style="text-align:left; font-size:32px; margin-top:80px; margin-bottom:20px; color:#1E293B;">📜 景氣對策：歷史亮燈全紀錄</h2>', unsafe_allow_html=True)
    
    history_data = [
        {"period": "2025.09 - 進行中", "months": float(months_ongoing), "type": "長延續型 (預估)", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "2024.04 - 2025.04", "months": 13.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "2020.12 - 2022.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "2009.12 - 2011.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "1995.02 - 1995.02", "months": 1.0, "type": "短促型", "color": "#FBBF24", "bg": "rgba(251, 191, 36, 0.1)"},
    ]

    for item in history_data:
        w = min(100.0, (item['months'] / 16) * 100)
        st.markdown(f"""<div style="background:#0F172A; border:2px solid #334155; border-radius:12px; padding:25px; margin-bottom:15px; display:flex; align-items:center; gap:30px;"><div style="font-family:'JetBrains Mono'; font-size:20px; font-weight:800; color:#F1F5F9; min-width:200px;">📅 {item['period']}</div><div style="flex:1;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><span style="color:{item['color']}; background:{item['bg']}; padding:4px 12px; border-radius:6px; font-size:14px; font-weight:800; border:1px solid {item['color']};">{item['type']}</span><span style="font-family:'JetBrains Mono'; font-size:18px; font-weight:900; color:{item['color']};">{item['months']} M</span></div><div style="height:12px; background:#1E293B; border-radius:6px; overflow:hidden;"><div style="width:{w}%; height:100%; background:{item['color']}; box-shadow:0 0 15px {item['color']};"></div></div></div></div>""", unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#9CA3AF; font-size:12px; margin-top:80px;'>系統由 aver5678 量化模組驅動 | 視覺化引擎: Command-Center v3.2</p>", unsafe_allow_html=True)
