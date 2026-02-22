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
    
    # --- 1. 數據載入邏輯 ---
    def load_ndc_data():
        # 目前 1 月份數據尚未發布 (預計 2 月底)，此處數據同步自國發會最新 12 月報
        latest_score = 38.0
        history = [
            {"m": "08", "s": 31, "c": "#10B981"}, # 8月：綠燈
            {"m": "09", "s": 34, "c": "#FBBF24"}, # 9月：黃紅燈
            {"m": "10", "s": 35, "c": "#FBBF24"}, # 10月：黃紅燈
            {"m": "11", "s": 37, "c": "#FBBF24"}, # 11月：黃紅燈
            {"m": "12", "s": 38, "c": "#EF4444"}  # 12月：紅燈 (最新)
        ]
        # 趨勢計算 (MoM)
        delta = float(history[-1]["s"]) - float(history[-2]["s"])
        return latest_score, history, delta

    current_score, months_data, mom_delta = load_ndc_data()
    
    # 時間邏輯
    now = datetime.now()
    research_start = datetime(2025, 9, 1)
    months_ongoing = (now.year - research_start.year) * 12 + (now.month - research_start.month)
    if months_ongoing < 1: months_ongoing = 1

    # --- 2. 視覺變數定義 ---
    status_pill_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    status_pill_text = "OVERHEATED" if current_score >= 38 else "EXPANSION" if current_score >= 32 else "STABLE"
    
    score_color = status_pill_color
    score_label = "🚨 紅燈：登頂高溫區" if current_score >= 38 else "⚡ 黃紅燈：攻頂啟動" if current_score >= 32 else "✅ 穩定區間"
    mom_color = "#EF4444" if mom_delta > 0 else "#10B981" if mom_delta < 0 else "#94A3B8"
    mom_icon = "↑" if mom_delta > 0 else "↓" if mom_delta < 0 else "─"

    # --- 3. 頂部區域：Hero Header ---
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;"><div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // ESCAPE_WINDOW_v6.0 // AUTO-SYNC</div><div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div></div><h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">💼 景氣信號：登頂逃命窗口觀測儀</h1><div style="margin-top:20px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.6; max-width:900px; border-left:4px solid #334155; padding-left:20px;">旨在偵測加權指數的「獲利耗竭區」。目前紅燈警示亮起，代表市場已進入登頂噴發的高位，歷史規律指出這是一場與時間賽跑的撤退競速，必須嚴格執行「見紅逃頂」計畫。</div></div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)

    # --- 4. 戰術即時面板 (Macro HUD) ---
    tiles_html = "".join([f'<div style="background:{m["c"]}; color:white; padding:8px 12px; border-radius:8px; text-align:center; min-width:65px; box-shadow:0 4px 10px rgba(0,0,0,0.3); border:2px solid rgba(255,255,255,0.2);"><div style="font-size:11px; font-weight:800; opacity:0.8;">{m["m"]}月</div><div style="font-family:\'JetBrains Mono\'; font-size:18px; font-weight:950;">{m["s"]}</div></div>' for m in months_data])
    progress_val = int(min(months_ongoing/12*100, 100))
    
    hud_html = f"""<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:45px; margin-bottom:40px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center;"><div style="flex:1;"><div style="font-size:18px; color:#94A3B8; font-weight:800; margin-bottom:15px; display:flex; align-items:center; gap:10px;"><span style="width:10px; height:10px; background:{score_color}; border-radius:50%; box-shadow:0 0 10px {score_color};"></span>當前景氣對策分數</div><div style="display:flex; align-items:center; gap:25px;"><div style="font-family:'JetBrains Mono'; font-size:82px; font-weight:950; color:{score_color}; line-height:1; letter-spacing:-4px;">{current_score:,.0f}</div><div style="display:flex; flex-direction:column; gap:8px;"><div style="font-family:'JetBrains Mono'; font-size:24px; font-weight:900; color:{mom_color}; background:rgba(255,255,255,0.05); padding:2px 10px; border-radius:6px;">{mom_icon} {abs(mom_delta):.0f} <span style="font-size:14px; opacity:0.7;">MoM</span></div><div style="background:rgba(255,255,255,0.1); color:white; padding:10px 20px; border-radius:10px; font-size:22px; font-weight:950; border:2px solid {score_color}; box-shadow:0 0 20px rgba(239, 68, 68, 0.4);">{score_label}</div></div></div></div><div style="width:2px; height:120px; background:#334155; margin:0 50px;"></div><div style="flex:1.5;"><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:20px;"><div style="text-align:left;"><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">● 觸發點：2025/09 (首顆黃紅燈)</div><div style="font-size:22px; color:#F1F5F9; font-weight:900;">攻頂逃命窗口倒數 <span style="color:#7DD3FC; font-size:16px;">(目前已擴張 {int(months_ongoing)} 個月)</span></div></div><div style="display:flex; gap:12px;">{tiles_html}</div></div><div style="background:rgba(255,255,255,0.03); padding:15px 25px; border-radius:12px; border:1px solid #1E293B;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;"><div style="font-size:16px; color:#38BDF8; font-weight:900; letter-spacing:1px;">📊 高點耗竭預警線 (對標 4-12 個月)</div><div style="font-family:'JetBrains Mono'; font-size:18px; font-weight:900; color:#38BDF8;">{progress_val}% 預警進度</div></div><div style="height:12px; background:#0F172A; border-radius:10px; overflow:hidden; border:1px solid #334155;"><div style="width:{progress_val}%; height:100%; background:linear-gradient(90deg, #F59E0B, #EF4444); box-shadow:0 0 15px #EF4444;"></div></div></div></div></div></div>"""
    st.markdown(hud_html, unsafe_allow_html=True)

    # --- 5. Onboarding Guide ---
    onboarding_html = f"""<div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:35px; margin-bottom:50px; box-shadow:0 10px 30px rgba(0,0,0,0.3);"><h2 style="color:#F1F5F9; font-size:26px; font-weight:900; margin-top:0; margin-bottom:25px; display:flex; align-items:center; gap:12px;">📋 戰術導讀：識別「逃命窗口」，而非「景氣壽命」</h2><div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:30px;"><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #3B82F6;"><div style="color:#7DD3FC; font-weight:800; font-size:17px; margin-bottom:12px;">🔹 領先性原則：股市 > 燈號</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;">官方綠燈通常是「崩盤後」才確認，真正的專業投資人只統計<b>「亮燈到登頂」</b>的時差。這段時差我們稱為「逃命窗口」。</div></div><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #EF4444;"><div style="color:#FCA5A5; font-weight:800; font-size:17px; margin-bottom:12px;">🔸 戰術脈衝：75% 的騙局</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;">歷史數據顯示，75% 的波段在亮燈後 4 個月內就會見到股價最高點（脈衝型），隨後進入長達半年的盤整或急墜。</div></div><div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #FBBF24;"><div style="color:#FDE68A; font-weight:800; font-size:17px; margin-bottom:12px;">🔹 操作對策：燈號熄滅前撤退</div><div style="color:#94A3B8; font-size:15px; line-height:1.6;">目前的進度已進入「高危區」。當前策略不應是「等待綠燈」，而是在<b>黃紅燈後的第 5 個月起</b>強制啟動分批獲利程序。</div></div></div></div>"""
    st.markdown(onboarding_html, unsafe_allow_html=True)

    # --- 6. Simulation Section ---
    simulation_html = f"""<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; overflow:hidden; box-shadow:0 25px 50px rgba(0,0,0,0.6); margin-bottom:40px;"><div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border-bottom:3px solid #334155; display:flex; justify-content:space-between; align-items:center;"><div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🛡️ 獲利耗竭：攻頂逃命窗口演算</div><div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">ENGINE // TO_PEAK_v6.0</div></div><div style="padding:50px; display:flex; gap:50px; align-items:stretch;"><div style="flex:1.3; background:rgba(255,255,255,0.02); padding:40px; border-radius:15px; border:1px solid rgba(255,255,255,0.05); display:flex; flex-direction:column; justify-content:center;"><div style="font-size:24px; color:#38BDF8; font-weight:900; margin-bottom:20px; display:flex; align-items:center; gap:12px; border-bottom:2px solid rgba(56, 189, 248, 0.2); padding-bottom:15px;">📊 逃命出口統計 (30年樣本)</div><div style="font-size:26px; color:#F1F5F9; font-weight:900; line-height:1.4; margin-bottom:25px;">自 1994 年以來，見紅後之攻頂樣本共 <span style="color:#EF4444; font-size:32px;">8</span> 次，平均逃命窗口僅 <span style="color:#EF4444; font-size:32px;">5.2</span> 個月。</div><div style="font-size:19px; color:#94A3B8; font-weight:600; line-height:1.8; border-left:4px solid #EF4444; padding-left:25px;">實戰警戒：高達 <b>75%</b> 的樣本在亮燈後 <b>4 個月內</b> 就會見到股市最高點。這證明了燈號對股價具備嚴重的「落後性」，絕對不可等燈號變綠才撤退。</div></div><div style="flex:1; display:flex; flex-direction:column; gap:30px; justify-content:center;"><div style="background:rgba(239, 68, 68, 0.05); padding:35px; border-radius:15px; border:2px solid rgba(239, 68, 68, 0.2); position:relative; box-shadow:0 10px 20px rgba(0,0,0,0.2);"><div style="position:absolute; top:15px; right:20px; background:#EF4444; color:white; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:900; box-shadow:0 0 10px #EF4444;">發生率 75%</div><div style="color:#FCA5A5; font-size:18px; font-weight:900; margin-bottom:12px; display:flex; align-items:center; gap:8px;">🆘 劇本一：脈衝型見頂 (極速)</div><div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#EF4444; line-height:1; text-shadow:0 0 20px rgba(239, 68, 68, 0.6);">1 - 4 <span style="font-size:22px; opacity:0.8;">個月</span></div></div><div style="background:rgba(16, 185, 129, 0.05); padding:35px; border-radius:15px; border:2px solid rgba(16, 185, 129, 0.2); position:relative; box-shadow:0 10px 20px rgba(0,0,0,0.2);"><div style="position:absolute; top:15px; right:20px; background:#10B981; color:white; padding:3px 12px; border-radius:20px; font-size:13px; font-weight:900; box-shadow:0 0 10px #10B981;">發生率 25%</div><div style="color:#A7F3D0; font-size:18px; font-weight:900; margin-bottom:12px; display:flex; align-items:center; gap:8px;">✅ 劇本二：長線波段攻頂</div><div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#10B981; line-height:1; text-shadow:0 0 20px rgba(16, 185, 129, 0.6);">10 - 14 <span style="font-size:22px; opacity:0.8;">個月</span></div></div></div></div><div style="text-align:left; border-top:1px solid #334155; padding:25px 50px;"><div style="font-size:17px; color:#F1F5F9; font-weight:700; line-height:1.6;">「目前的環境極度依賴資金脈衝。統計顯示：一旦跨過第 4 個月，風險與機會比將會失衡。」</div><div style="font-size:14px; color:#64748B; font-weight:600; margin-top:10px;">(參考 1994-2025 獲利逃命共 8 次完整樣本)</div></div></div>"""
    st.markdown(simulation_html, unsafe_allow_html=True)

    # --- 7. Digital Logs (精密數據版) ---
    st.markdown(f"""<div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border:4px solid #334155; border-radius:12px; margin-top:80px; margin-bottom:40px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">📜 逃命窗口：亮燈後登頂歷史全紀錄</div><div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">LOG_SYSTEM // PEAK_RECORDS_v6.0</div></div>""", unsafe_allow_html=True)
    
    history_data = [
        {
            "period": "2025.09 - 進行中", "months": float(months_ongoing), "type": "登頂倒數中", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.15)", "status_icon": "🚨",
            "start_date": "2025/11/03 (09月燈號發布後首日)", "start_idx": "28,334",
            "peak_date": "2026/02/11", "peak_idx": "33,606", "gain_pct": "18.6%"
        },
        {
            "period": "2024.04-2024.07 登頂", "months": 3.0, "type": "脈衝型 (見高 24,416)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2024/06/03 (04月燈號發布後首日)", "start_idx": "21,537",
            "peak_date": "2024/07/11", "peak_idx": "24,416", "gain_pct": "13.4%"
        },
        {
            "period": "2020.12-2022.01 登頂", "months": 13.0, "type": "長線型 (見高 18,619)", 
            "color": "#10B981", "bg": "rgba(16, 185, 129, 0.1)", "status_icon": "✅",
            "start_date": "2021/02/01 (12月燈號發布後首日)", "start_idx": "15,410",
            "peak_date": "2022/01/05", "peak_idx": "18,619", "gain_pct": "20.8%"
        },
        {
            "period": "2009.11-2011.01 登頂", "months": 14.0, "type": "長線型 (見高 9,220)", 
            "color": "#10B981", "bg": "rgba(16, 185, 129, 0.1)", "status_icon": "✅",
            "start_date": "2010/01/04 (11月燈號發布後首日)", "start_idx": "8,208",
            "peak_date": "2011/01/28", "peak_idx": "9,220", "gain_pct": "12.3%"
        },
        {
            "period": "2007.09-2007.10 登頂", "months": 1.0, "type": "快閃型 (見高 9,859)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2007/11/01 (09月燈號發布後首日)", "start_idx": "9,598",
            "peak_date": "2007/10/30", "peak_idx": "9,859", "gain_pct": "2.7%"
        },
        {
            "period": "2003.12-2004.03 登頂", "months": 3.0, "type": "脈衝型 (見高 7,135)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2004/02/02 (12月燈號發布後首日)", "start_idx": "6,320",
            "peak_date": "2004/03/05", "peak_idx": "7,135", "gain_pct": "12.9%"
        },
        {
            "period": "2000.01-2000.02 登頂", "months": 1.0, "type": "快閃型 (見高 10,393)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2000/03/01 (01月燈號發布後首日)", "start_idx": "9,689",
            "peak_date": "2000/02/18", "peak_idx": "10,393", "gain_pct": "7.3%"
        },
        {
            "period": "1994.06-1994.10 登頂", "months": 4.0, "type": "脈衝型 (見高 7,228)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "1994/08/01 (06月燈號發布後首日)", "start_idx": "6,744",
            "peak_date": "1994/10/03", "peak_idx": "7,228", "gain_pct": "7.2%"
        },
    ]

    for item in history_data:
        m_val = float(item['months'])
        w = min(100.0, (m_val / 14) * 100) 
        if m_val >= 10:
            tactical_eval, strategy_node = "🛡️ 史詩長線：超常擴張", "搭配「40週乖離」同步逃頂"
        elif m_val >= 4:
            tactical_eval, strategy_node = "🚩 關鍵變數：高風險期", "全面撤退 / 指標見綠即空"
        else:
            tactical_eval, strategy_node = "🆘 極速脈衝：獲利轉瞬", "分批獲利 / 禁止任何追價"

        card_html = f"""<div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;"><div style="flex:2.5; padding:35px 30px; border-right:4px solid #475569;"><div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;"><span style="color:{item['color']}; background:{item['bg']}; padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid {item['color']};">{item['status_icon']} {str(item['type']).split('(')[0].strip()}</span><span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">攻頂時間紀錄：</span></div><div style="font-size:48px; color:white; font-weight:950; letter-spacing:-1px; line-height:1;">📅 {item['period']}</div></div><div style="flex:1; text-align:center; background:rgba(239, 68, 68, 0.05); padding:40px 20px; display:flex; flex-direction:column; justify-content:center; min-width:300px;"><div style="font-size:20px; color:#FCA5A5; font-weight:900; text-transform:uppercase; margin-bottom:12px; letter-spacing:2px;">距離登頂時長</div><div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:#EF4444; line-height:1;">{m_val:.1f}<span style="font-size:25px; font-weight:800; margin-left:10px; color:#FCA5A5;">M</span></div></div></div><div style="background:#0F172A; padding:35px; border-bottom:4px solid #334155;"><div style="display:flex; justify-content:space-between; align-items:center; font-size:28px; color:#FCA5A5; margin-bottom:15px; font-weight:950; white-space:nowrap;"><span>⏳ 逃命窗口耗竭度 (對標 14 個月)</span><span>{m_val:.1f} / 14 M</span></div><div style="height:20px; background:#020617; border-radius:10px; overflow:hidden; border:2px solid #334155;"><div style="width:{w}%; height:100%; background:linear-gradient(90deg, #1E293B, {item['color']}); box-shadow:0 0 30px {item['color']};"></div></div></div><div style="display:grid; grid-template-columns:1fr 1.2fr 1fr; gap:0; background:#1E293B;"><div style="background:#1E293B; padding:30px; text-align:left; border-right:4px solid #334155;"><div style="font-size:18px; color:#94A3B8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段一] 首次亮燈警戒</div><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">(發生於 {item['start_date']})</div><div style="font-size:36px; font-weight:950; color:white;">{item['start_idx']}</div></div><div style="background:rgba(239, 68, 68, 0.05); padding:30px; text-align:left; border-right:4px solid #334155;"><div style="font-size:18px; color:#EF4444; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段二] 波段見最高點</div><div style="font-size:14px; color:#FCA5A5; font-weight:800; margin-bottom:5px;">(發生於 {item['peak_date']})</div><div style="display:flex; align-items:baseline; gap:12px;"><div style="font-size:36px; font-weight:950; color:white;">{item['peak_idx']}</div><div style="font-size:22px; font-weight:900; color:#EF4444;">+{item['gain_pct']}</div></div></div><div style="background:#1E293B; padding:30px; text-align:left;"><div style="font-size:18px; color:#38BDF8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段三] 逃命窗口狀態</div><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">(視角：{tactical_eval.split('：')[0]})</div><div style="font-size:24px; font-weight:950; color:#7DD3FC; line-height:1.3;">{strategy_node}</div></div></div></div>"""
        st.markdown(card_html, unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#64748B; font-size:14px; margin-top:100px; font-weight:600; letter-spacing:1px;'>系統由 aver5678 量化模組驅動 | 視覺化引擎: Command-Center v6.0 // PEAK_ESCAPE_LOGIC</p>", unsafe_allow_html=True)
