import streamlit as st
import pandas as pd
import altair as alt
from data_fetcher import fetch_data
from wave_analyzer import analyze_waves
from ui_theme import apply_global_theme

@st.cache_data(ttl=3600)
def load_upward_data(ticker_symbol):
    df = fetch_data(ticker_symbol, start_date="2000-01-01")
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    
    # 使用 7% 轉折模型 (跌 7% 確認頭部，漲 7% 確認底部)
    waves = analyze_waves(df, reversal_percent=7.0)
    
    # 取出所有向上波段 (type == 'up') 並加入前波清洗度
    up_waves = []
    for i, w in enumerate(waves):
        if w['type'] == 'up':
            prev_w = waves[i-1] if i > 0 else None
            pre_dd = 0.0
            if prev_w and prev_w['type'] == 'down':
                pre_dd = (prev_w['lowest_price'] - prev_w['highest_price']) / prev_w['highest_price'] * 100
            w['pre_drawdown'] = pre_dd
            up_waves.append(w)
            
    if not up_waves:
        return pd.DataFrame(), pd.DataFrame(), {}
        
    results = []
    for w in up_waves:
        s_date = w.get('start_date')
        e_date = w.get('end_date')
        start_date_str = s_date.strftime('%Y-%m-%d') if s_date else "N/A"
        end_date_str = e_date.strftime('%Y-%m-%d') if e_date else "N/A"
        
        start_price = w.get('start_price', 0)
        end_price = w.get('end_price', 0)
        gain_pct = (end_price - start_price) / start_price * 100 if start_price and start_price != 0 else 0
        days = (e_date - s_date).days if s_date and e_date else 0
        
        status = '進行中' if w.get('ongoing', False) else '已完結'
        
        results.append({
            '起漲日期 (前波破底)': start_date_str,
            '最高日期 (下波前高)': end_date_str,
            '起漲價格': float(start_price) if start_price is not None else 0.0,
            '最高價格': float(end_price) if end_price is not None else 0.0,
            '漲幅(%)': float(gain_pct) if gain_pct is not None else 0.0,
            '花費天數': int(days),
            '狀態': status,
            '前波清洗度(%)': w.get('pre_drawdown', 0.0)
        })
        
    up_df = pd.DataFrame(results)
    
    # 統計機率 (排除進行中)
    finished_waves = up_df[up_df['狀態'] == '已完結']
    if finished_waves.empty:
        finished_waves = up_df
        
    # 分配區間
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 10000]
    labels = ['     0~10%', '  10~20%', '  20~30%', '  30~40%', '  40~50%', '  50~60%', '  60~70%', '70% 以上']
    
    try:
        counts = pd.cut(finished_waves['漲幅(%)'], bins=bins, labels=labels, right=False).value_counts().sort_index()
    except:
        counts = pd.Series(0, index=labels)
    
    dist_results = []
    total = len(finished_waves)
    for label, count in counts.items():
        prob = (count / total * 100) if total > 0 else 0
        dist_results.append({
            '區間': label.strip(),
            '次數': count,
            '機率(%):Q': round(float(prob), 2),
            '機率(%)': round(float(prob), 2)
        })
    dist_df = pd.DataFrame(dist_results)
    
    metrics = {
        '總完整波段數': total,
        '平均漲幅(%)': round(float(finished_waves['漲幅(%)'].mean()), 2) if total > 0 else 0,
        '平均花費天數': round(float(finished_waves['花費天數'].mean()), 1) if total > 0 else 0,
        '漲幅超過 20% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 20]) / total * 100), 2) if total > 0 else 0
    }
        
    return up_df, dist_df, metrics

def page_upward_bias():
    st.markdown('<h1 class="centered-title">📈 股市上漲統計表 (Bottom Bounce Analysis)</h1>', unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#6B7280; margin-bottom:50px;'>計算每一次從低點起漲（經過前波大於 7% 的修正洗盤），一直抱到『下一次再發生 7% 大回檔』前的小波段/大波段真正漲幅。</p>", unsafe_allow_html=True)
    
    tickers = {
        "S&P 500 (^GSPC)": "^GSPC",
        "NASDAQ (^IXIC)": "^IXIC",
        "台灣加權指數 (^TWII)": "^TWII"
    }

    selected_name = st.selectbox("選擇分析指數 (上漲模組)", list(tickers.keys()))
    symbol = tickers[selected_name]

    up_df, dist_df, metrics = load_upward_data(symbol)

    if up_df.empty:
        st.warning("目前尚無足夠歷史數據可供分析。")
        return
        
    # --- 1. KPI 數據卡片 (Tech Card Style) ---
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'''<div class="tech-card"><div class="summary-label">歷史完整波段數</div><div class="summary-value" style="color:#111827;">{metrics.get('總完整波段數', 0)}<span style="font-size:14px;">次</span></div></div>''', unsafe_allow_html=True)
    with c2:
        st.markdown(f'''<div class="tech-card"><div class="summary-label">平均波段漲幅</div><div class="summary-value" style="color:#10B981;">{metrics.get('平均漲幅(%)', 0):+.1f}%</div></div>''', unsafe_allow_html=True)
    with c3:
        st.markdown(f'''<div class="tech-card"><div class="summary-label">平均耗時 (天)</div><div class="summary-value" style="color:#3B82F6;">{metrics.get('平均花費天數', 0)}<span style="font-size:14px;">天</span></div></div>''', unsafe_allow_html=True)
    with c4:
        st.markdown(f'''<div class="tech-card"><div class="summary-label">漲幅破 20% 勝率</div><div class="summary-value" style="color:#EF4444;">{metrics.get('漲幅超過 20% 機率', 0)}%</div></div>''', unsafe_allow_html=True)

    # --- 2. 歷史分佈圖 (Premium Theme) ---
    st.markdown('<h2 style="text-align:center; margin-top:80px;">📊 歷史漲幅機率區間分布</h2>', unsafe_allow_html=True)

    if not dist_df.empty:
        chart = alt.Chart(dist_df).mark_bar(color='#10B981', cornerRadiusTopLeft=8, cornerRadiusTopRight=8).encode(
            x=alt.X('區間:N', title='反彈漲幅區稱 (%)', sort=None),
            y=alt.Y('機率(%):Q', title='發生機率 (%)'),
            tooltip=['區間:N', '次數:Q', '機率(%):Q']
        ).properties(height=350).configure_view(strokeWidth=0).configure_axis(grid=False, domain=False)
        
        st.altair_chart(chart, use_container_width=True)
        
    # --- 3. 電子流水日誌 (Timeline Logs) ---
    st.markdown('<h2 style="text-align:center; margin-top:80px;">📜 上漲波段電子日誌</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#9CA3AF; margin-bottom:40px;">透過能量條直觀判定：歷史爆發力 (Scale: 0-70%)</p>', unsafe_allow_html=True)

    if not up_df.empty:
        sorted_up = up_df.sort_values(by='起漲日期 (前波破底)', ascending=False)
        for _, r in sorted_up.iterrows():
            gain = float(r['漲幅(%)'])
            days = int(r['花費天數'])
            status = r['狀態']
            # Scale 0-70%
            w = min(100.0, (gain / 70) * 100)
            tag_color = "#10B981" if status == '已完結' else "#EF4444"
            tag_bg = "rgba(16, 185, 129, 0.15)" if status == '已完結' else "rgba(239, 68, 68, 0.15)"
            icon = "✅" if status == '已完結' else "🚀"
            
            # --- 自訂欄位邏輯 ---
            # 左下角標籤：依漲幅判斷
            is_strong = gain >= 20.0
            custom_tag_text = "強勢多頭" if is_strong else "一般反彈"
            custom_tag_bg = "#EF4444" if is_strong else "#06B6D4" # 紅色代表強勢多頭，青色一般反彈
            
            pre_dd = r.get('前波清洗度(%)', 0)
            pre_dd_display = f"{pre_dd:.1f}%" if pre_dd < 0 else "N/A"
            
            top_right_bg = "rgba(16, 185, 129, 0.05)" if gain > 0 else "rgba(239, 68, 68, 0.05)"
            top_right_val_color = "#10B981" if gain > 0 else "#EF4444"
            
            # 建立專屬 HTML
            card_html = f"""
            <div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);">
              <!-- 頂部區：巨星標題磚 -->
              <div style="display:grid; grid-template-columns: 1fr 1fr; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;">
                <div style="padding:35px 30px; border-right:4px solid #475569;">
                  <div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;">
                    <span style="background:{tag_bg}; color:{tag_color}; padding:6px 16px; border-radius:6px; font-weight:950; font-size:18px; border:2px solid {tag_color}; box-shadow:0 0 15px {tag_color}44;">{icon} {status}</span>
                    <span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">波段起漲確認日：</span>
                  </div>
                  <div style="font-size:52px; color:white; font-weight:950; letter-spacing:-2px; line-height:1;">📅 {r['起漲日期 (前波破底)']}</div>
                  <div style="margin-top:25px; display:flex; align-items:center; gap:25px;">
                    <span style="color:#FFF; background:{custom_tag_bg}; padding:8px 25px; border-radius:10px; font-size:38px; font-weight:900; white-space:nowrap; border:2px solid rgba(255,255,255,0.3);">{custom_tag_text}</span>
                    <span style="font-size:32px; color:#94A3B8; font-weight:800; white-space:nowrap;">前波清洗度: <span style="color:#F1F5F9;">{pre_dd_display}</span></span>
                  </div>
                </div>
                <div style="text-align:center; background:{top_right_bg}; padding:35px 30px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
                  <div style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px; margin-bottom:15px;">波段噴發總週期：</div>
                  <div style="font-size:52px; color:{top_right_val_color}; font-weight:950; letter-spacing:-1px; line-height:1; margin-bottom:20px;">🔥 {days} <span style="font-size:28px; font-weight:800;">天</span></div>
<div style="font-size:42px; color:#10B981; font-weight:900; white-space:nowrap;">▲ {gain:+.1f}%</div>
                </div>
              </div>

              <!-- 中間層：故事線點位 -->
              <div style="display:grid; grid-template-columns:1fr 1fr; gap:0; border-bottom:4px solid #475569;">
                <div style="background:#450A0A; padding:45px 20px; text-align:center; border-right:4px solid #475569; display:flex; flex-direction:column; align-items:center;">
                  <div style="font-size:26px; color:#FCA5A5; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段一] 波段起漲點</div>
                  <div style="font-size:18px; color:#F87171; font-weight:800; margin-bottom:25px;">(起漲於 {r['起漲日期 (前波破底)']})</div>
                  <div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:white; line-height:1; margin-bottom:20px;">{r['起漲價格']:,.0f}</div>
                  <div style="background: rgba(69, 10, 10, 0.8); color: #FCA5A5; border: 2px solid #EF4444; padding: 4px 16px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size:22px; font-weight:900;">跌勢終結</div>
                </div>
                <div style="background:#064E3B; padding:45px 20px; text-align:center; display:flex; flex-direction:column; align-items:center;">
                  <div style="font-size:26px; color:#86EFAC; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段二] 波段最高點</div>
                  <div style="font-size:18px; color:#4ADE80; font-weight:800; margin-bottom:25px;">(攻頂於 {r['最高日期 (下波前高)']})</div>
                  <div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:white; line-height:1; margin-bottom:20px;">{r['最高價格']:,.0f}</div>
                  <div style="background: rgba(6, 78, 59, 0.8); color: #86EFAC; border: 2px solid #22C55E; padding: 4px 16px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size:22px; font-weight:900;">多頭盛極轉折</div>
                </div>
              </div>

              <!-- 底部層：能量總結 -->
              <div style="background:#0F172A; padding:45px 50px; border:3px solid #10B981; margin:0;">
                <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:35px;">
                  <div style="font-size:34px; color:white; font-weight:950; display:flex; align-items:center; gap:15px; line-height:1;">🔥 波段爆發能量展示：</div>
                  <div style="font-size:42px; color:#34D399; font-weight:950; letter-spacing:-1.5px; line-height:1; text-shadow: 0 0 20px rgba(52, 211, 153, 0.4); display:flex; align-items:baseline; gap:15px;">
                    <span>+{gain:.1f}%</span>
                  </div>
                </div>
                <div style="height:38px; background:rgba(2,6,23,0.95); border-radius:12px; overflow:hidden; border:3px solid #10B981; padding:3px; box-shadow:inset 0 4px 10px rgba(0,0,0,0.6);">
                  <div style="width:{w}%; height:100%; background:linear-gradient(90deg, #A7F3D0 0%, #34D399 50%, #10B981 100%); border-radius:8px; box-shadow:0 0 25px rgba(16, 185, 129, 0.4);"></div>
                </div>
                <div style="margin-top:25px; display:flex; justify-content:flex-end; align-items:center;">
                  <div style="color:#94A3B8; font-family:'JetBrains Mono'; font-size:16px; font-weight:900;">爆發里程 {w:.1f}%</div>
                </div>
              </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#9CA3AF; font-size:12px; margin-top:80px;'>系統由 aver5678 量化模組驅動 | 上漲爆發力引擎: Wave-Analyzer v2.1</p>", unsafe_allow_html=True)
