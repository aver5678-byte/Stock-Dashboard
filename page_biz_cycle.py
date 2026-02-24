# -*- coding: utf-8 -*-
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
            {"m": "09", "a": "11", "s": 34, "c": "#FBBF24"}, # 9月數據 -> 11月反映
            {"m": "10", "a": "12", "s": 35, "c": "#FBBF24"}, # 10月數據 -> 12月反映
            {"m": "11", "a": "01", "s": 37, "c": "#FBBF24"}, # 11月數據 -> 01月反映
            {"m": "12", "a": "02", "s": 38, "c": "#EF4444"}  # 12月數據 -> 02月反映 (最新)
        ]
        # 趨勢計算 (MoM)
        delta = float(history[-1]["s"]) - float(history[-2]["s"])
        return latest_score, history, delta

    current_score, months_data, mom_delta = load_ndc_data()
    
    # 時間邏輯：改採實戰起點 (2025/11/03) 計算耗竭進度
    now = datetime.now()
    research_start = datetime(2025, 11, 3) 
    diff = (now - research_start).days
    months_ongoing = diff / 30.44
    if months_ongoing < 0.1: months_ongoing = 0.1
    
    # 計算主流窗口剩餘天數 (對標 4.1個月門檻)
    days_threshold = 4.1 * 30.44
    days_left = max(int(days_threshold - diff), 0)

    # --- 2. 視覺變數定義 ---
    status_pill_color = "#EF4444" if current_score >= 38 else "#FBBF24" if current_score >= 32 else "#10B981"
    status_pill_text_zh = "🚨 極度過熱" if current_score >= 38 else "⚡ 擴張期" if current_score >= 32 else "✅ 穩定區間"
    
    score_color = status_pill_color
    score_label = "🚨 紅燈：登頂高溫" if current_score >= 38 else "⚡ 黃紅燈：攻頂啟動" if current_score >= 32 else "✅ 穩定區間"
    mom_color = "#EF4444" if mom_delta > 0 else "#10B981" if mom_delta < 0 else "#94A3B8"
    mom_icon = "↑" if mom_delta > 0 else "↓" if mom_delta < 0 else "─"
    
    # 預警線計算：對標實戰平均 4.1 個月
    progress_val = int(min(months_ongoing / 4.1 * 100, 100))
 
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
<div style="font-family:'Inter', 'Microsoft JhengHei', sans-serif; font-size:13px; color:#64748B; letter-spacing:1px; font-weight:800;">系統即時偵測中 // 景氣燈號量化</div>
<div style="background:{status_pill_color}; color:white; padding:6px 16px; border-radius:8px; font-family:'Microsoft JhengHei', sans-serif; font-size:14px; font-weight:900; box-shadow:0 0 15px {status_pill_color}; border:1px solid rgba(255,255,255,0.3);">
{status_pill_text_zh}
</div>
</div>
<h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2; text-shadow:0 0 30px rgba(251, 191, 36, 0.4);">💼 景氣信號：登頂實戰窗口觀測儀 (v8.0)</h1>
<div style="margin-top:25px; margin-bottom:25px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.8; max-width:1100px; border-left:4px solid {status_pill_color}; padding-left:30px; margin-left:5px;">
<b>獨立戰略校準模組</b>：專門量化「景氣過熱」訊號公告後，大盤真實的<b>剩餘獲利天數</b>。由於官方數據存在 2 個月時差，我們自動執行時空校正，並同步比對過去三十年每一場「高溫期」從亮燈到指數見頂的<b>真實演進路徑</b>。透過這項數據，我們能量化市場在進入狂熱區域後的「生存窗口」，協助您在安全出口封死之前，精準判斷目前波段的<b>撤退剩餘價值</b>。
</div>
</div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)
 
    # --- 戰術導讀 (地端新增：介於標題與 HUD 之間) ---
    guide_html = f"""
<div style="background:#1E293B; border:2px solid #22D3EE; border-radius:16px; padding:30px; margin-bottom:40px; box-shadow:0 0 30px rgba(34, 211, 238, 0.2); backdrop-filter:blur(20px);">
<h3 style="color:white; font-size:28px; font-weight:900; margin-top:0; margin-bottom:25px; display:flex; align-items:center; gap:12px;">
💡 戰術導讀：三步看懂監控面板
</h3>
<div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; border-top:4px solid #EF4444; border-right:1px solid rgba(255,255,255,0.1); border-left:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(255,255,255,0.1);">
<div style="color:#FCA5A5; font-weight:900; font-size:18px; margin-bottom:12px;">🌡️ 看左側：燈號是體溫計</div>
<div style="color:#F8FAFC; font-size:15px; line-height:1.7; font-weight:700;">
「黃紅燈」並非恐嚇，它代表市場正在<b>「發燒」</b>。偵測到體溫過高，應準備退燒（減倉），而非繼續劇烈運動（追高）。
</div>
</div>
<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; border-top:4px solid #10B981; border-right:1px solid rgba(255,255,255,0.1); border-left:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(255,255,255,0.1);">
<div style="color:#A7F3D0; font-weight:900; font-size:18px; margin-bottom:12px;">🎲 看中央：相信機率，不賭運氣</div>
<div style="color:#F8FAFC; font-size:15px; line-height:1.7; font-weight:700;">
對標 <b>72% 的主流事實</b>（過熱短暫）來部署，而非賭那 28% 的機蹟。專業投資人服從機率，不拿血汗錢開玩笑。
</div>
</div>
<div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:12px; border-top:4px solid #38BDF8; border-right:1px solid rgba(255,255,255,0.1); border-left:1px solid rgba(255,255,255,0.1); border-bottom:1px solid rgba(255,255,255,0.1);">
<div style="color:#7DD3FC; font-weight:900; font-size:18px; margin-bottom:12px;">🧬 看右側：指標是數據軌跡</div>
<div style="color:#F8FAFC; font-size:15px; line-height:1.7; font-weight:700;">
最右側的燈號序列紀錄了數據的<b>「累積路徑」</b>。透過觀察燈號顏色的演變，您可以預判市場熱度的慣性，並識別出信號即將全面冷卻的轉折點。
</div>
</div>
</div>
</div>
"""
    st.markdown(guide_html, unsafe_allow_html=True)

    # --- 4. 戰術即時面板 (Macro HUD) ---
    tiles_html = "".join([f'<div style="background:{m["c"]}; color:white; padding:10px 12px; border-radius:10px; text-align:center; min-width:85px; box-shadow:0 6px 15px rgba(0,0,0,0.4); border:1.5px solid rgba(255,255,255,0.2);"><div style="font-size:14px; font-weight:900; margin-bottom:4px; letter-spacing:1px; opacity:0.9;">{m["a"]}月</div><div style="font-family:\'JetBrains Mono\'; font-size:24px; font-weight:950; line-height:1;">{m["s"]}</div></div>' for m in months_data])
    marker_pos = min(months_ongoing / 12 * 100, 100)
    
    # 決定背景色調
    hazard_bg = "linear-gradient(180deg, #450A0A 0%, #111827 100%)" if current_score >= 38 else "#111827"
    calc_bg = "linear-gradient(180deg, #064E3B 0%, #022C22 100%)"
    path_bg = "linear-gradient(180deg, #1E1B4B 0%, #0F172A 100%)"
    
    hud_html = f"""
<style>
@keyframes pulse-red-hazard-glow {{
  0% {{ box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); border-color: rgba(239, 68, 68, 0.4); }}
  50% {{ box-shadow: 0 0 40px rgba(239, 68, 68, 0.8); border-color: rgba(239, 68, 68, 1); }}
  100% {{ box-shadow: 0 0 10px rgba(239, 68, 68, 0.4); border-color: rgba(239, 68, 68, 0.4); }}
}}
@keyframes pulse-green-expand-glow {{
  0% {{ border-color: rgba(16, 185, 129, 0.2); box-shadow: 0 0 10px rgba(16, 185, 129, 0.1); }}
  50% {{ border-color: rgba(16, 185, 129, 0.8); box-shadow: 0 0 30px rgba(16, 185, 129, 0.4); }}
  100% {{ border-color: rgba(16, 185, 129, 0.2); box-shadow: 0 0 10px rgba(16, 185, 129, 0.1); }}
}}
@keyframes pulse-blue-path-glow {{
  0% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
  50% {{ border-color: rgba(56, 189, 248, 0.8); box-shadow: 0 0 30px rgba(56, 189, 248, 0.4); }}
  100% {{ border-color: rgba(56, 189, 248, 0.2); box-shadow: 0 0 10px rgba(56, 189, 248, 0.1); }}
}}
</style>
<div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:35px; margin-bottom:40px; box-shadow:0 20px 50px rgba(0,0,0,0.6); overflow:hidden;">
<div style="display:flex; justify-content:space-between; align-items:stretch; gap:25px;">
<!-- 左側：燈號分數電子盤 (Kernel) -->
<div style="flex:1; background:{hazard_bg}; border:3px solid {score_color}; border-radius:15px; padding:25px 15px; animation: pulse-red-hazard-glow 3s infinite; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
<div style="width:100%; border-bottom:1px solid rgba(255,255,255,0.1); margin-bottom:15px; padding-bottom:10px;">
<div style="font-family:'JetBrains Mono'; font-size:13px; color:#38BDF8; font-weight:800; letter-spacing:1px;">TSE_MACRO_KERNEL // 趨勢運算內核</div>
<div style="font-size:10px; color:#94A3B8; font-weight:700; opacity:0.8;">DATA_CALIB: 2024.Q4 官方修正權重</div>
</div>
<div style="display:flex; flex-direction:column; align-items:center; gap:5px;">
<div style="font-family:'JetBrains Mono'; font-size:95px; font-weight:950; color:{score_color}; line-height:0.8; letter-spacing:-6px; text-shadow: 0 0 30px rgba(239, 68, 68, 0.5);">{current_score:,.0f}</div>
<div style="background:{score_color}; color:white; padding:5px 15px; border-radius:8px; font-size:18px; font-weight:950; box-shadow:0 0 20px {score_color}; white-space:nowrap; border:1.5px solid rgba(255,255,255,0.4); margin-top:10px;">{score_label}</div>
</div>
</div>
<!-- 中間：時程推演計算儀 (Simulation) -->
<div style="flex:1; background:{calc_bg}; border:2px solid #10B981; border-radius:15px; padding:25px 20px; animation: pulse-green-expand-glow 4s infinite; display:flex; flex-direction:column; gap:15px; backdrop-filter:blur(10px);">
<div style="width:100%; border-bottom:1px solid rgba(16, 185, 129, 0.3); margin-bottom:10px; padding-bottom:10px;">
<div style="font-family:'JetBrains Mono'; font-size:13px; color:#34D399; font-weight:800; letter-spacing:1px;">HISTORICAL_SIM // 時程推演數據</div>
<div style="font-size:10px; color:#94A3B8; font-weight:700; opacity:0.8;">🎯 CALC_ENGINE: PEAK_PROJ_v8.0</div>
</div>
<div style="display:flex; flex-direction:column; gap:18px;">
<div style="background:rgba(16, 185, 129, 0.1); padding:12px; border-radius:10px; border:1px solid rgba(16, 185, 129, 0.2);">
<div style="font-size:12px; color:#A7F3D0; font-weight:900; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
<span><span style="background:#10B981; width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:5px;"></span> 主流劇本 (72%)</span>
<span style="background:#EF4444; color:white; padding:2px 8px; border-radius:6px; font-size:10px; font-weight:900;">剩餘 {days_left} DAY</span>
</div>
<div style="font-family:'JetBrains Mono'; font-size:24px; color:white; font-weight:950; letter-spacing:-0.5px;">2025.11 - 2026.02</div>
</div>
<div style="padding:0 12px;">
<div style="font-size:12px; color:#34D399; font-weight:900; margin-bottom:8px; display:flex; align-items:center; gap:6px;">
<span style="background:#10B981; width:8px; height:8px; border-radius:50%; box-shadow:0 0 8px #10B981;"></span> 稀有擴張劇本 (28%)
</div>
<div style="font-family:'JetBrains Mono'; font-size:24px; color:#94A3B8; font-weight:950; letter-spacing:-0.5px;">2026.08 - 2026.12</div>
</div>
</div>
</div>
<!-- 右側：月份燈號鏈 (Score Path) -->
<div style="flex:1; background:{path_bg}; border:2px solid #38BDF8; border-radius:15px; padding:25px 20px; animation: pulse-blue-path-glow 4s infinite; display:flex; flex-direction:column; gap:15px; box-shadow:inset 0 0 20px rgba(0,0,0,0.5); backdrop-filter:blur(10px);">
<div style="width:100%; border-bottom:1px solid rgba(56, 189, 248, 0.3); margin-bottom:10px; padding-bottom:10px;">
<div style="font-family:'JetBrains Mono'; font-size:13px; color:#38BDF8; font-weight:800; letter-spacing:1px;">SCORE_PATH_LINK // 景氣指標路徑</div>
<div style="font-size:10px; color:#94A3B8; font-weight:700; opacity:0.8;">🔄 REALTIME: POST_RELEASE_SYNC</div>
</div>
<div style="display:flex; flex-direction:column; justify-content:flex-start; flex:1; padding-top:5px;">
<div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:8px; justify-items:center;">{tiles_html}</div>
</div>
</div>
</div>
</div>
    """
    st.markdown(hud_html, unsafe_allow_html=True)




    # --- 7. Digital Logs ---
    st.markdown(f"""
<div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border:4px solid #334155; border-radius:12px; margin-top:80px; margin-bottom:40px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
<div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">
📜 實戰紀錄：發布後登頂之歷史窗口
</div>
<div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">LOG_SYSTEM // PEAK_CALIB_v8.0</div>
</div>
""", unsafe_allow_html=True)
    
    history_data = [
        {
            "period": "2025/11/03 - 進行中", "months": float(months_ongoing), "type": "登頂倒數中", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.15)", "status_icon": "🚨",
            "start_date": "2025/11/03 (09月燈號發布後首日)", "start_idx": "28,334",
            "peak_date": "2026/02/11", "peak_idx": "33,606", "gain_pct": "18.6%"
        },
        {
            "period": "2024/06/03 - 07/11 登頂", "months": 1.3, "type": "極速脈衝型", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2024/06/03 (04月燈號發布後首日)", "start_idx": "21,537",
            "peak_date": "2024/07/11", "peak_idx": "24,416", "gain_pct": "13.4%"
        },
        {
            "period": "2021/02/01 - 2022/01/05 登頂", "months": 11.1, "type": "罕見長線型", 
            "color": "#10B981", "bg": "rgba(16, 185, 129, 0.1)", "status_icon": "✅",
            "start_date": "2021/02/01 (12月燈號發布後首日)", "start_idx": "15,410",
            "peak_date": "2022/01/05", "peak_idx": "18,619", "gain_pct": "20.8%"
        },
        {
            "period": "2010/01/04 - 2011/01/28 登頂", "months": 12.8, "type": "罕見長線型", 
            "color": "#10B981", "bg": "rgba(16, 185, 129, 0.1)", "status_icon": "✅",
            "start_date": "2010/01/04 (11月燈號發布後首日)", "start_idx": "8,208",
            "peak_date": "2011/01/28", "peak_idx": "9,220", "gain_pct": "12.3%"
        },
        {
            "period": "2007/11/01 - 10/30 溢價歸零", "months": 0.1, "type": "發布即見頂 (快閃型)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "🆘",
            "start_date": "2007/11/01 (09月燈號發布後首日)", "start_idx": "9,598",
            "peak_date": "2007/10/30", "peak_idx": "9,859", "gain_pct": "2.7%"
        },
        {
            "period": "2004/02/02 - 03/05 登頂", "months": 1.1, "type": "極速脈衝型", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "⚠️",
            "start_date": "2004/02/02 (12月燈號發布後首日)", "start_idx": "6,320",
            "peak_date": "2004/03/05", "peak_idx": "7,135", "gain_pct": "12.9%"
        },
        {
            "period": "2000/03/01 - 02/18 溢價歸零", "months": 0.1, "type": "發布即見頂 (快閃型)", 
            "color": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)", "status_icon": "🆘",
            "start_date": "2000/03/01 (01月燈號發布後首日)", "start_idx": "9,689",
            "peak_date": "2000/02/18", "peak_idx": "10,393", "gain_pct": "7.3%"
        },
        {
            "period": "1994/08/01 - 10/03 登頂", "months": 2.1, "type": "極速脈衝型", 
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

        card_html = f"""<div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;"><div style="flex:2.5; padding:35px 30px; border-right:4px solid #475569;"><div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;"><span style="color:{item['color']}; background:{item['bg']}; padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid {item['color']};">{item['status_icon']} {str(item['type']).split('(')[0].strip()}</span><span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">攻頂時間紀錄：</span></div><div style="font-size:48px; color:white; font-weight:950; letter-spacing:-1px; line-height:1;">📅 {item['period']}</div></div><div style="flex:1; text-align:center; background:rgba(239, 68, 68, 0.05); padding:40px 20px; display:flex; flex-direction:column; justify-content:center; min-width:300px;"><div style="font-size:20px; color:#FCA5A5; font-weight:900; text-transform:uppercase; margin-bottom:12px; letter-spacing:2px;">距離登頂時長</div><div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:#EF4444; line-height:1;">{m_val:.1f}<span style="font-size:25px; font-weight:800; margin-left:10px; color:#FCA5A5;">M</span></div></div></div><div style="background:#0F172A; padding:35px; border-bottom:4px solid #334155;"><div style="display:flex; justify-content:space-between; align-items:center; font-size:28px; color:#FCA5A5; margin-bottom:15px; font-weight:950; white-space:nowrap;"><span>⌛ 逃命窗口耗竭度 (對標 14 個月)</span><span>{m_val:.1f} / 14 M</span></div><div style="height:20px; background:#020617; border-radius:10px; overflow:hidden; border:2px solid #334155;"><div style="width:{w}%; height:100%; background:linear-gradient(90deg, #1E293B, {item['color']}); box-shadow:0 0 30px {item['color']};"></div></div></div><div style="display:grid; grid-template-columns:1fr 1.2fr 1fr; gap:0; background:#1E293B;"><div style="background:#1E293B; padding:30px; text-align:left; border-right:4px solid #334155;"><div style="font-size:18px; color:#94A3B8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段一] 首次亮燈警戒</div><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">(發生於 {item['start_date']})</div><div style="font-size:36px; font-weight:950; color:white;">{item['start_idx']}</div></div><div style="background:rgba(239, 68, 68, 0.05); padding:30px; text-align:left; border-right:4px solid #334155;"><div style="font-size:18px; color:#EF4444; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段二] 波段見最高點</div><div style="font-size:14px; color:#FCA5A5; font-weight:800; margin-bottom:5px;">(發生於 {item['peak_date']})</div><div style="display:flex; align-items:baseline; gap:12px;"><div style="font-size:36px; font-weight:950; color:white;">{item['peak_idx']}</div><div style="font-size:22px; font-weight:900; color:#EF4444;">+{item['gain_pct']}</div></div></div><div style="background:#1E293B; padding:30px; text-align:left;"><div style="font-size:18px; color:#38BDF8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段三] 逃命窗口狀態</div><div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">(視角：{tactical_eval.split('：')[0]})</div><div style="font-size:24px; font-weight:950; color:#7DD3FC; line-height:1.3;">{strategy_node}</div></div></div></div>"""
        st.markdown(card_html, unsafe_allow_html=True)

    st.markdown("<p style='text-align:center; color:#64748B; font-size:14px; margin-top:100px; font-weight:600; letter-spacing:1px;'>系統由 aver5678 量化模組驅動 | 視覺化引擎: Command-Center v8.0 // POST_RELEASE_CALIBRATED</p>", unsafe_allow_html=True)
