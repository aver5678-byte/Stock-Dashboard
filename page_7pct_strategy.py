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
    st.dataframe(events_df[display_cols].sort_values(by='觸發日期', ascending=False), height=400)
