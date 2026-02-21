import streamlit as st
import pandas as pd
import altair as alt
from data_fetcher import fetch_data
from wave_analyzer import analyze_waves

st.set_page_config(page_title="股市上漲波段分析", page_icon="📈", layout="wide")

@st.cache_data(ttl=3600)
def load_upward_data(ticker_symbol):
    df = fetch_data(ticker_symbol, start_date="2000-01-01")
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), {}
    
    # 使用 7% 轉折模型 (跌 7% 確認頭部，漲 7% 確認底部)
    waves = analyze_waves(df, reversal_percent=7.0)
    
    # 取出所有向上波段 (type == 'up')
    up_waves = [w for w in waves if w['type'] == 'up']
    
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
            '起漲價格': round(float(start_price), 2) if start_price is not None else 0.0,
            '最高價格': round(float(end_price), 2) if end_price is not None else 0.0,
            '漲幅(%)': round(float(gain_pct), 2) if gain_pct is not None else 0.0,
            '花費天數': int(days),
            '狀態': status
        })
        
    up_df = pd.DataFrame(results)
    
    # 統計機率 (排除進行中)
    finished_waves = up_df[up_df['狀態'] == '已完結']
    if finished_waves.empty:
        finished_waves = up_df
        
    # 分配區間
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 10000]
    labels = ['     0~10%', '  10~20%', '  20~30%', '  30~40%', '  40~50%', '  50~60%', '  60~70%', '70% 以上']
    
    counts = pd.cut(finished_waves['漲幅(%)'], bins=bins, labels=labels, right=False).value_counts().sort_index()
    
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

st.title("📈 乖離底部反彈上漲模組")
st.write("這是一個獨立的分析頁面！\n計算每一次從低點起漲（經過前波大於 7% 的修正洗盤），一直抱到「下一次再發生 7% 大回檔」前的小波段/大波段真正漲幅。")

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
st.subheader("📊 歷史【反彈上漲波段】爆發力")
c1, c2, c3, c4 = st.columns(4)
c1.metric("歷史完整波段數", f"{metrics.get('總完整波段數', 0)} 次")
c2.metric("平均波段漲幅", f"{metrics.get('平均漲幅(%)', 0)}%")
c3.metric("平均耗時 (天)", f"{metrics.get('平均花費天數', 0)}")
c4.metric("漲幅破 20% 勝率", f"{metrics.get('漲幅超過 20% 機率', 0)}%")

st.markdown("---")

st.subheader("📊 歷史漲幅機率區間分布 (7% 轉折模型)")

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
