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
    current_score = 38.0  # 最新公布分數 (已修正為 1 月份真實紅燈)

    # --- 2. 頂部區域：一體化戰情標頭 (Hero Header) ---
    status_pill_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    status_pill_text = "OVERHEATED" if current_score >= 38 else "EXPANSION" if current_score >= 32 else "STABLE"
    
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;"><div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // BIAS_MACRO_v2.0 // AUTO-SYNC</div><div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div></div><h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2;">💼 景氣信號：長線價值觀測儀</h1><div style="margin-top:20px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.6; max-width:900px; border-left:4px solid #334155; padding-left:20px;">旨在偵測宏觀經濟的「週期水位」。目前分數已達紅燈警戒點，代表市場正處於景氣熱度的轉折高峰。歷史證明，在此高溫下需嚴格執行資產配置調整計畫。</div></div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)

    # --- 3. 戰術即時面板 (Macro HUD) --- 精密重構版
    score_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    score_label = "🚨 紅燈：過熱轉折期" if current_score >= 38 else "⚡ 黃紅燈：擴張期" if current_score >= 32 else "✅ 穩定區間"
    
    # 趨勢數據 (MoM) - 根據您給的圖表，是升溫趨勢
    mom_delta = 1.0 
    mom_color = "#EF4444" if mom_delta > 0 else "#10B981"
    mom_icon = "↑" if mom_delta > 0 else "↓"
    
    # 生成月份足跡序列 (最後 5 個月，同步您提供的官方數據)
    months_data = [
        {"m": "09", "s": 34, "c": "#FBBF24"},
        {"m": "10", "s": 35, "c": "#FBBF24"},
        {"m": "11", "s": 37, "c": "#FBBF24"},
        {"m": "12", "s": 38, "c": "#EF4444"},
        {"m": "01", "s": 38, "c": "#EF4444"} 
    ]
    tiles_html = "".join([f'<div style="background:{m["c"]}; color:white; padding:8px 12px; border-radius:8px; text-align:center; min-width:65px; box-shadow:0 4px 10px rgba(0,0,0,0.3); border:2px solid rgba(255,255,255,0.2);"><div style="font-size:11px; font-weight:800; opacity:0.8;">{m["m"]}月</div><div style="font-family:\'JetBrains Mono\'; font-size:18px; font-weight:950;">{m["s"]}</div></div>' for m in months_data])
    
    progress_val = int(min(months_ongoing/10*100, 100))
    
    hud_html = f"""<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:45px; margin-bottom:40px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:18px; color:#94A3B8; font-weight:800; margin-bottom:15px; display:flex; align-items:center; gap:10px;"><span style="width:10px; height:10px; background:{score_color}; border-radius:50%; box-shadow:0 0 10px {score_color};"></span>當前景氣對策分數</div><div style="display:flex; align-items:center; gap:25px;"><div style="font-family:'JetBrains Mono'; font-size:82px; font-weight:950; color:{score_color}; line-height:1; letter-spacing:-4px;">{current_score:,.0f}</div><div style="display:flex; flex-direction:column; gap:8px;"><div style="font-family:'JetBrains Mono'; font-size:24px; font-weight:900; color:{mom_color}; background:rgba(255,255,255,0.05); padding:2px 10px; border-radius:6px;">{mom_icon} {abs(mom_delta):.0f} <span style="font-size:14px; opacity:0.7;">MoM</span></div><div style="background:rgba(255,255,255,0.1); color:white; padding:10px 20px; border-radius:10px; font-size:22px; font-weight:950; border:2px solid {score_color}; box-shadow:0 0 20px rgba(239, 68, 68, 0.4);">{score_label}</div></div></div></div><div style="width:2px; height:120px; background:#334155; margin:0 50px;"></div><div style="flex:1.5;"><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;"><div style="text-align:left;"><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">● 觸發點：2025/09</div><div style="font-size:22px; color:#F1F5F9; font-weight:900;">本次熱度足跡 <span style="color:#7DD3FC; font-size:16px;">(已持續 {int(months_ongoing)} 個月)</span></div></div><div style="display:flex; gap:12px;">{tiles_html}</div></div><div style="background:rgba(255,255,255,0.03); padding:15px 25px; border-radius:12px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><div style="font-size:16px; color:#38BDF8; font-weight:900; letter-spacing:1px;">📊 循環防禦警戒線 (10-16月)</div><div style="font-family:'JetBrains Mono'; font-size:18px; font-weight:900; color:#38BDF8;">{progress_val}% 戰備進度</div></div><div style="height:12px; background:#0F172A; border-radius:10px; overflow:hidden; border:1px solid #334155;"><div style="width:{progress_val}%; height:100%; background:linear-gradient(90deg, #0284C7, #38BDF8); box-shadow:0 0 15px #38BDF8;"></div></div></div></div></div></div>"""
    st.markdown(hud_html, unsafe_allow_html=True)

    # --- 3.5 數據解讀指南 (Onboarding Guide) ---
    onboarding_html = f"""<div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:35px; margin-bottom:50px; box-shadow:0 10px 30px rgba(0,0,0,0.3);"><h2 style="color:#F1F5F9; font-size:26px; font-weight:900; margin-top:0; margin-bottom:25px; display:flex; align-items:center; gap:12px;">📋 戰術導讀：景氣信號不是「預言」，而是「保命工具」</h2><div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:30px;"><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #3B82F6;"><div style="color:#7DD3FC; font-weight:800; font-size:17px; margin-bottom:12px;">🔹 核心心法：風險控管 > 預測</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;">景氣信號的目的不是預測明天漲跌，而是偵測市場「體溫」。紅燈代表中暑風險劇增，高手此時會檢查防曬（分批獲利），而非新兵式的盲目衝鋒。</div></div><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #EF4444;"><div style="color:#FCA5A5; font-weight:800; font-size:17px; margin-bottom:12px;">🔸 戰術執行：根據顏色調水位</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;"><b>🔴 紅燈(38+)</b>：嚴格執行分批減碼。此時應問：如果明天轉折，我口袋剩多少現金？而非問還會漲多少。回收子彈，轉向防禦狀態。</div></div><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #FBBF24;"><div style="color:#FDE68A; font-weight:800; font-size:17px; margin-bottom:12px;">🔹 歷史規律：時間引力</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;">見到黃紅燈後，歷史平均擴張 10-16 個月。目前進度 50%，代表下半場已開啟。下半場的重點是「優雅收網」，而非在此高溫時投入所有積蓄。</div></div></div></div>"""
    st.markdown(onboarding_html, unsafe_allow_html=True)

    # --- 4. 戰略模擬：歷史過熱週期回測 (旗艦比例重構版) ---
    st.markdown('<div style="margin-top:40px;"></div>', unsafe_allow_html=True)
    
    simulation_html = f"""<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; overflow:hidden; box-shadow:0 25px 50px rgba(0,0,0,0.6); margin-bottom:40px;"><div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border-bottom:3px solid #334155; display:flex; justify-content:space-between; align-items:center;"><div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🛡️ 歷史過熱週期演算系統</div><div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">ENGINE // SCENARIO_v4.2</div></div><div style="padding:50px; display:flex; gap:50px; align-items:stretch;"><div style="flex:1.3; background:rgba(255,255,255,0.02); padding:40px; border-radius:15px; border:1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;"><div style="font-size:24px; color:#38BDF8; font-weight:900; margin-bottom:20px; display:flex; align-items:center; gap:12px; border-bottom:2px solid rgba(56, 189, 248, 0.2); padding-bottom:15px;">📊 核心研究結論</div><div style="font-size:26px; color:#F1F5F9; font-weight:900; line-height:1.4; margin-bottom:25px;">自 1995 年以來，景氣燈號首次見紅共 8 次，其中 <span style="color:#EF4444; font-size:32px;">57%</span> 演變為長循環。</div><div style="font-size:19px; color:#94A3B8; font-weight:600; line-height:1.8; border-left:4px solid #334155; padding-left:25px;">數據運算顯示：目前市場情緒與宏觀背景，極高機率正處於<b>【長延續型劇本】</b>的下半場。這意味著熱度雖高，但尚未觸及最終的天花板。</div></div><div style="flex:1; display:flex; flex-direction:column; gap:30px; justify-content:center;"><div style="background:rgba(239, 68, 68, 0.05); padding:35px; border-radius:15px; border:2px solid rgba(239, 68, 68, 0.2); position:relative; box-shadow:0 10px 20px rgba(0,0,0,0.2);"><div style="position:absolute; top:15px; right:20px; background:#EF4444; color:white; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:900; box-shadow:0 0 10px #EF4444;">發生率 57%</div><div style="color:#FCA5A5; font-size:18px; font-weight:900; margin-bottom:12px; display:flex; align-items:center; gap:8px;">🆘 劇本一：長延續擴張</div><div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#EF4444; line-height:1; text-shadow:0 0 20px rgba(239, 68, 68, 0.6);">10 - 16 <span style="font-size:22px; opacity:0.8;">個月</span></div></div><div style="background:rgba(16, 185, 129, 0.05); padding:35px; border-radius:15px; border:2px solid rgba(16, 185, 129, 0.2); position:relative; box-shadow:0 10px 20px rgba(0,0,0,0.2);"><div style="position:absolute; top:15px; right:20px; background:#10B981; color:white; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:900; box-shadow:0 0 10px #10B981;">發生率 43%</div><div style="color:#A7F3D0; font-size:18px; font-weight:900; margin-bottom:12px; display:flex; align-items:center; gap:8px;">✅ 劇本二：短促型過熱</div><div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#10B981; line-height:1; text-shadow:0 0 20px rgba(16, 185, 129, 0.6);">1 - 2 <span style="font-size:22px; opacity:0.8;">個月</span></div></div></div></div></div>"""
    st.markdown(simulation_html, unsafe_allow_html=True)

    # --- 4.5 劇本操作導讀 (Scenario Strategy Guide) ---
    scenario_onboarding_html = f"""<div style="background:linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border:2px solid #334155; border-radius:12px; padding:35px; margin-bottom:80px; box-shadow:0 10px 30px rgba(0,0,0,0.3);"><h2 style="color:#F1F5F9; font-size:22px; font-weight:900; margin-top:0; margin-bottom:25px; display:flex; align-items:center; gap:12px;">📋 戰術導讀：面對「雙劇本」的進退法則</h2><div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:30px;"><div style="padding:15px; border-right:1px solid rgba(255,255,255,0.05); text-align:left;"><div style="color:#7DD3FC; font-weight:900; font-size:16px; margin-bottom:10px;">🚩 識別路徑：32 分生死線</div><div style="color:#94A3B8; font-size:14px; line-height:1.7;"><b>短劇本(假突破)</b>：若紅燈後 2 個月內迅速跌破 32 分，代表熱度已盡，應果斷撤退。<br><b>長劇本(真擴張)</b>：若穩坐 32 分之上超過 3 個月，長循環確認，此時不應輕易被洗下車。</div></div><div style="padding:15px; border-right:1px solid rgba(255,255,255,0.05); text-align:left;"><div style="color:#FCA5A5; font-weight:900; font-size:16px; margin-bottom:10px;">⚠️ 操作對策：莫在「魚尾」博命</div><div style="color:#94A3B8; font-size:14px; line-height:1.7;">進入紅燈區後的<b>第 8 個月</b>起，嚴格禁止大額加碼。魚尾行情雖然瘋狂，但風險槓桿極高。每多走一個月，就應多回收一成現金，這叫「優雅勝出演習」。</div></div><div style="padding:15px; text-align:left;"><div style="color:#FDE68A; font-weight:900; font-size:16px; margin-bottom:10px;">🧠 心理建設：拒絕預設，果斷執行</div><div style="color:#94A3B8; font-size:14px; line-height:1.7;">57% 雖高，但不代表這一次一定是長循環。同時列出兩套規律是為了讓你在<b>短劇本</b>發生時能果斷執行停利，而不是在那裡祈禱歷史會自動對標長循環。</div></div></div></div>"""
    st.markdown(scenario_onboarding_html, unsafe_allow_html=True)

    # --- 5. 數位流水日誌 ---
    st.markdown('<h2 style="text-align:left; font-size:32px; margin-bottom:30px; color:#1E293B;">📜 景氣對策：歷史過熱週期全紀錄</h2>', unsafe_allow_html=True)
    
    history_data = [
        {"period": "2025.09 - 進行中", "months": float(months_ongoing), "type": "長延續型 (預估)", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.15)"},
        {"period": "2024.04 - 2025.04", "months": 13.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "2020.12 - 2022.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "2009.12 - 2011.02", "months": 15.0, "type": "長延續型", "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"period": "1995.02 - 1995.02", "months": 1.0, "type": "短促型", "color": "#FBBF24", "bg": "rgba(251, 191, 36, 0.1)"},
    ]

    for item in history_data:
        w = min(100.0, (item['months'] / 16) * 100)
        st.markdown(f"""<div style="background:#0F172A; border:2px solid #334155; border-radius:12px; padding:25px; margin-bottom:15px; display:flex; align-items:center; gap:30px; box-shadow:0 10px 20px rgba(0,0,0,0.2);"><div style="font-family:'JetBrains Mono'; font-size:20px; font-weight:800; color:#F1F5F9; min-width:220px;">📅 {item['period']}</div><div style="flex:1;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;"><span style="color:{item['color']}; background:{item['bg']}; padding:4px 12px; border-radius:6px; font-size:14px; font-weight:800; border:1px solid {item['color']};">{item['type']}</span><span style="font-family:'JetBrains Mono'; font-size:20px; font-weight:950; color:{item['color']};">{item['months']} <span style="font-size:14px;">M</span></span></div><div style="height:12px; background:#1E293B; border-radius:6px; overflow:hidden; border:1px solid #334155;"><div style="width:{w}%; height:100%; background:{item['color']}; box-shadow:0 0 15px {item['color']};"></div></div></div></div>""", unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#94A3B8; font-size:13px; margin-top:100px; font-weight:600; letter-spacing:1px;'>系統由 aver5678 量化模組驅動 | 視覺化引擎: Command-Center v3.2</p>", unsafe_allow_html=True)
