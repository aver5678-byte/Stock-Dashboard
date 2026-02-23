import streamlit as st
import pandas as pd
import altair as alt
from data_fetcher import fetch_data
from strategy_7pct import analyze_7pct_strategy
from strategy_upward_wave import get_upward_waves

@st.cache_data(ttl=3600)
def load_upward_data(ticker_symbol):
    df = fetch_data(ticker_symbol, start_date="2000-01-01")
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    # 使用與下跌空頭同樣的 7% 邏輯尋找轉折點
    events_df = analyze_7pct_strategy(df, trigger_pct=7.0)
    up_df, dist_df, metrics = get_upward_waves(events_df, df)
    return up_df, dist_df, metrics

def page_upward_bias():
    st.title("📈 乖離上漲模組 (波段低點反彈)")
    st.write("計算每一次從「波段低點（經歷 >7% 跌幅後）」起漲，一直抱到「下一次大回檔」前夕，平均能夠吃到的完整上漲漲幅。")

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
        st.stop()
        
    st.markdown("---")
    
    # KPI metrics
    st.subheader("📊 歷史波段平均上漲爆發力")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("歷史完整波段數", f"{metrics.get('總完整波段數', 0)} 次")
    c2.metric("平均波段漲幅", f"{metrics.get('平均漲幅(%)', 0)}%")
    c3.metric("平均耗時 (天)", f"{metrics.get('平均花費天數', 0)}")
    c4.metric("漲幅破 20% 勝率", f"{metrics.get('漲幅超過 20% 機率', 0)}%")
    
    st.markdown("---")
    
    st.subheader("📊 歷史【底部反彈】漲幅區間機率分布")
    
    if not dist_df.empty:
        chart = alt.Chart(dist_df).mark_bar(color='#00ff99', cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('區間:N', title='反彈漲幅區間 (%)', sort=None),
            y=alt.Y('機率(%):Q', title='發生機率 (%)'),
            tooltip=['區間:N', '次數:Q', '機率(%):Q']
        ).properties(height=350)
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-5,
            color='white'
        ).encode(
            text=alt.Text('機率(%):Q', format='.1f')
        )
        
        st.altair_chart(chart + text, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("📜 歷史上漲波段詳情清單")
    st.dataframe(up_df.sort_values(by='起漲日期 (前波破底)', ascending=False), height=400)
