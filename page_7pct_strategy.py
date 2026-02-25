import streamlit as st
import pandas as pd
import altair as alt
from data_fetcher import fetch_data
from strategy_7pct import analyze_7pct_strategy, calculate_7pct_statistics
import datetime

# 抓取與分析資料
@st.cache_data(ttl=3600)
def get_analysis_7pct(ticker_symbol):
    df = fetch_data(ticker_symbol, start_date="2000-01-01")
    if df.empty:
        return df, pd.DataFrame(), {}, pd.DataFrame(), 0, 0
        
    events_df = analyze_7pct_strategy(df, trigger_pct=7.0)
    metrics, dist_df = calculate_7pct_statistics(events_df)
    
    # 尋找當前狀態
    current_high = df['High'].max()
    last_close = df['Close'].iloc[-1]
    last_date = df.index[-1].strftime('%Y-%m-%d')
    
    is_ongoing = False
    ongoing_event = None
    if not events_df.empty:
        if events_df.iloc[-1]['狀態'] == '進行中':
            is_ongoing = True
            ongoing_event = events_df.iloc[-1]
            
    if is_ongoing:
        current_dd = (ongoing_event['前高價格'] - last_close) / ongoing_event['前高價格'] * 100
    else:
        last_rec_date_str = events_df.iloc[-1]['解套日期'] if not events_df.empty else '2000-01-01'
        try:
             recent_df = df.loc[last_rec_date_str:]
             recent_high = recent_df['High'].max()
             current_dd = (recent_high - last_close) / recent_high * 100
        except:
             recent_high = df['High'].iloc[-1]
             current_dd = 0

    return df, events_df, metrics, dist_df, current_dd, last_date


def page_7pct_strategy():
    st.title("📉 股市 7% 回檔進場分析儀表板")
    st.write("即時監測與歷史回測：針對標普 500 (SPX)、那斯達克 (IXIC) 及台股加權指數 (TWII)，分析自歷史高點跌破 7% 後的剩餘跌幅與反彈機率。")

    tickers = {
        "S&P 500 (^GSPC)": "^GSPC",
        "NASDAQ (^IXIC)": "^IXIC",
        "台灣加權指數 (^TWII)": "^TWII"
    }

    selected_name = st.selectbox("選擇分析指數", list(tickers.keys()))
    symbol = tickers[selected_name]

    # 取資料
    df, events_df, metrics, dist_df, current_dd, last_date = get_analysis_7pct(symbol)

    if df.empty or events_df.empty:
        st.warning("目前尚無足夠歷史數據可供分析。")
        st.stop()

    st.markdown("---")

    # ============== 1. 即時監控區塊 ==============
    st.subheader(f"📡 即時監控板 ({last_date})")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(label="目前距離前高跌幅", value=f"-{max(0, current_dd):.2f}%", 
                  delta="已觸發進場標準!" if current_dd >= 7.0 else f"尚未觸發 (剩 {-7 + current_dd:.2f}%)", 
                  delta_color="inverse" if current_dd >= 7.0 else "normal")

    with col2:
        if current_dd >= 7.0:
            residual_dd = current_dd - 7.0
            prob_worse = metrics.get('Prob Residual DD > 10%', 0)
            st.error(f"🚨 **進場警示**：目前已進入 7% 觸發區間！\n\n根據歷史回測，若您在此時進場，後續這波再跌超過 **10%** 的機率約為 **{prob_worse:.1f}%**。請做好資金控管。")
        else:
            st.success(f"✅ **安全區間**：目前回檔幅度小於 7%，不符合歷史劇烈回檔進場條件。")

    st.markdown("---")

    # ============== 2. 關鍵數據看板 (KPI) ==============
    st.subheader("📊 歷史關鍵數據 (觸發 7% 後的平均表現)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("歷史觸發次數", f"{metrics['Recovered Events']} 次")
    kpi2.metric("平均再跌(剩餘)幅度", f"-{metrics['Avg Residual Drawdown (%)']}%")
    kpi3.metric("平均見底天數", f"{metrics['Avg Days to Bottom']} 天")
    kpi4.metric("平均解套/回歸天數", f"{metrics['Avg Days to Recovery']} 天")

    st.markdown("---")

    # ============== 3. 視覺化圖表 ==============
    st.subheader("📉 觸發 7% 後的「剩餘跌幅」機率分布")
    st.write("這張圖顯示當市場跌破 7% 後，歷史上還「額外跌了多少」才見底的機率分配。")

    if not dist_df.empty:
        chart = alt.Chart(dist_df).mark_bar(color='#fc5185', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('Range:N', title='剩餘跌幅區間 (%)', sort=None),
            y=alt.Y('Probability (%):Q', title='發生機率 (%)'),
            tooltip=['Range:N', 'Count:Q', 'Probability (%):Q']
        ).properties(height=350)
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='white'
        ).encode(
            text=alt.Text('Probability (%):Q', format='.1f')
        )
        
        st.altair_chart(chart + text, use_container_width=True)

    st.markdown("---")

    # ============== 4. 歷史詳細清單 ==============
    st.subheader("📜 歷史波段詳情清單")
    st.write("列出 2000 年來每一次觸發 7% 回檔的完整歷程：")

    display_cols = ['觸發日期', '前高日期', '破底日期', '解套日期', 
                    '最大跌幅(%)', '剩餘跌幅(%)', '破底花費天數', '解套花費天數', '狀態']

    # 隱藏預設表格，改用高質感戰情室卡片
    sorted_events = events_df.sort_values(by='觸發日期', ascending=False)
    for _, r in sorted_events.iterrows():
        status = r.get('狀態', '進行中')
        trigger_date = r.get('觸發日期', 'N/A')
        peak_date = r.get('前高日期', 'N/A')
        peak_price = r.get('前高價格', 0)
        trigger_price = r.get('觸發價格', 0)
        bottom_date = r.get('破底日期', 'N/A')
        bottom_price = r.get('破底最低價', 0)
        max_dd = r.get('最大跌幅(%)', 0)
        res_dd = r.get('剩餘跌幅(%)', 0)
        days_to_bottom = r.get('觸發到破底天數', 0)
        days_total = r.get('解套總耗時', 0)
        recover_type = r.get('解套形式', '')

        # UI 變數設計
        is_recovered = (status == "已解套")
        
        # 狀態標籤
        label_status_bg = "rgba(16, 185, 129, 0.15)" if is_recovered else "rgba(239, 68, 68, 0.15)"
        label_status_color = "#10B981" if is_recovered else "#EF4444"
        label_status_icon = "✅" if is_recovered else "🚨"
        label_status_text = f"{label_status_icon} {status}"

        # 下拉標籤 (深度洗盤/一般回檔)
        is_deep = max_dd >= 15.0
        custom_tag_text = "深度洗盤" if is_deep else "一般回檔"
        custom_tag_bg = "#8B5CF6" if is_deep else "#06B6D4" # 紫色代表深度洗盤，青色一般回檔
        if max_dd >= 20.0: custom_tag_bg = "#EF4444" # 崩盤級別用紅色

        # 頂部右側數值 (剩餘跌幅)
        top_right_bg = "rgba(239, 68, 68, 0.05)" if res_dd > 10 else "rgba(16, 185, 129, 0.05)"
        top_right_val_color = "#EF4444" if res_dd > 10 else "#10B981"
        res_dd_display = f"-{res_dd:.1f}%" if res_dd > 0 else f"{res_dd:.1f}%"
        
        # 底部面板的霓虹樣式
        bot_right_neon_text = f"最大跌幅 -{max_dd:.1f}%"
        
        # 建立專屬 HTML
        card_html = f"""
        <div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);">
          <!-- 頂部區：巨星標題磚 -->
          <div style="display:grid; grid-template-columns: 1fr 1fr; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;">
            <div style="padding:35px 30px; border-right:4px solid #475569;">
              <div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;">
                <span style="background:{label_status_bg}; color:{label_status_color}; padding:6px 16px; border-radius:6px; font-weight:950; font-size:18px; border:2px solid {label_status_color}; box-shadow:0 0 15px {label_status_color}44;">{label_status_text}</span>
                <span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">觸發 7% 修正日：</span>
              </div>
              <div style="font-size:52px; color:white; font-weight:950; letter-spacing:-2px; line-height:1;">📅 {trigger_date}</div>
              <div style="margin-top:25px; display:flex; align-items:center; gap:25px;">
                <span style="color:#FFF; background:{custom_tag_bg}; padding:8px 25px; border-radius:10px; font-size:38px; font-weight:900; white-space:nowrap; border:2px solid rgba(255,255,255,0.3);">{custom_tag_text}</span>
                <span style="font-size:32px; color:#94A3B8; font-weight:800; white-space:nowrap;">前高位階: <span style="color:#F1F5F9;">{peak_price:,.0f} 點</span></span>
              </div>
            </div>
            <div style="text-align:center; background:{top_right_bg}; padding:35px 30px; display:flex; flex-direction:column; justify-content:center; align-items:center;">
              <div style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px; margin-bottom:15px;">觸發後剩餘最深跌幅：</div>
              <div style="font-size:52px; color:{top_right_val_color}; font-weight:950; letter-spacing:-1px; line-height:1; margin-bottom:20px;">📉 {res_dd_display}</div>
              <div style="font-size:32px; color:#64748B; font-weight:900; white-space:nowrap;">觸發後再耗 <span style="color:#F87171;">{days_to_bottom}</span> 天見底</div>
            </div>
          </div>

          <!-- 中間層：故事線點位 -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:0; border-bottom:4px solid #475569;">
            <div style="background:#450A0A; padding:45px 20px; text-align:center; border-right:4px solid #475569; display:flex; flex-direction:column; align-items:center;">
              <div style="font-size:26px; color:#FCA5A5; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段一] 觸發警報點</div>
              <div style="font-size:18px; color:#F87171; font-weight:800; margin-bottom:25px;">(發生於 {trigger_date})</div>
              <div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:white; line-height:1; margin-bottom:20px;">{trigger_price:,.0f}</div>
              <div style="background: rgba(69, 10, 10, 0.8); color: #FCA5A5; border: 2px solid #EF4444; padding: 4px 16px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size:22px; font-weight:900;">距離前高約 -7%</div>
            </div>
            <div style="background:#0F172A; padding:45px 20px; text-align:center; display:flex; flex-direction:column; align-items:center;">
              <div style="font-size:26px; color:#A7F3D0; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段二] 波段最低谷</div>
              <div style="font-size:18px; color:#34D399; font-weight:800; margin-bottom:25px;">(發生於 {bottom_date})</div>
              <div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:white; line-height:1; margin-bottom:20px;">{bottom_price:,.0f}</div>
              <div style="background: rgba(30, 41, 59, 0.8); color: #CBD5E1; border: 2px solid #94A3B8; padding: 4px 16px; border-radius: 6px; font-family: 'JetBrains Mono'; font-size:22px; font-weight:900;">{bot_right_neon_text}</div>
            </div>
          </div>

          <!-- 底部層：最終處置 -->
          <div style="background:#0F172A; padding:35px 50px; border:3px solid #3B82F6; margin:0;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
              <div style="font-size:30px; color:white; font-weight:950; display:flex; align-items:center; gap:15px; line-height:1;">⚖️ 波段最終處置：</div>
              <div style="font-size:36px; color:#60A5FA; font-weight:950; letter-spacing:-1px; line-height:1; display:flex; align-items:baseline; gap:15px;">
                <span>{recover_type} ({days_total} 天)</span>
              </div>
            </div>
          </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
