import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import altair as alt
from data_fetcher import fetch_data
from strategy_7pct import analyze_7pct_strategy, calculate_7pct_statistics
from wave_analyzer import analyze_waves
from page_portfolio import page_portfolio_visualizer
from page_ai_sentiment import page_ai_sentiment
import datetime

st.set_page_config(page_title="台股預警儀表板 | 40週乖離率監控", layout="wide", initial_sidebar_state="expanded")

# 初始化模擬資料庫 (存在 session_state 中)
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = 'guest' # 'guest', 'user', 'admin'
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'visit_logs' not in st.session_state:
    st.session_state['visit_logs'] = [] # 儲存 {time, user_email, page}
    
def log_visit(page_name):
    if st.session_state['user_email']:
        user = st.session_state['user_email']
    else:
        user = "訪客 (未登入)"
        
    st.session_state['visit_logs'].append({
        '時間': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        '使用者': user,
        '瀏覽模組': page_name
    })

# 您專屬的管理員信箱
ADMIN_EMAIL = "your_google_email@gmail.com" 

# 自定義 CSS (深色模式與閃爍動畫)
st.markdown("""
<style>
@keyframes blink {
  0% { opacity: 1; background-color: #5a0000; box-shadow: 0 0 10px red; }
  50% { opacity: 0.8; background-color: #2e0000; box-shadow: 0 0 5px darkred; }
  100% { opacity: 1; background-color: #5a0000; box-shadow: 0 0 10px red; }
}
.danger-zone {
  animation: blink 1.5s infinite;
  padding: 20px;
  border-radius: 10px;
  border: 2px solid #ff4b4b;
  text-align: center;
  color: white;
  margin-bottom: 20px;
}
.normal-zone {
  padding: 20px;
  border-radius: 10px;
  background-color: #1e1e1e;
  border: 1px solid #4CAF50;
  text-align: center;
  color: white;
  margin-bottom: 20px;
}
.warning-box {
  background-color: #331a00;
  border-left: 5px solid #ff9900;
  padding: 15px;
  margin: 10px 0;
  border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_data():
    ticker = "^TWII"
    try:
        df = yf.download(ticker, period="max", interval="1wk", progress=False)
        if df.empty:
            return pd.DataFrame()
            
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.dropna(subset=['Close'])
        df['SMA40'] = df['Close'].rolling(window=40).mean()
        df['Bias'] = (df['Close'] - df['SMA40']) / df['SMA40'] * 100
        return df
    except Exception as e:
        st.error(f"獲取資料時發生錯誤：{e}")
        return pd.DataFrame()

def get_regime(df, start_date):
    # 取觸發點前 52 週的資料來尋找最大回檔
    prev_52w = df.loc[:start_date].iloc[:-1].tail(52)
    if prev_52w.empty:
        return "未知", 0
        
    roll_max = prev_52w['High'].cummax()
    drawdowns = (prev_52w['Low'] - roll_max) / roll_max * 100
    max_dd = drawdowns.min()
    
    if max_dd <= -20:
        return "類型 A (低基期反彈)", max_dd
    else:
        return "類型 B (高位末升段)", max_dd

def backtest(df):
    results = []
    in_danger = False
    start_date = None
    trigger_price = None
    trigger_bias = None
    trigger_warning_price = None
    max_price = 0
    max_date = None
    regime = None
    max_dd = 0
    
    for date, row in df.iterrows():
        bias = row['Bias']
        close_p = row['Close']
        if pd.isna(bias):
            continue
            
        if not in_danger and bias > 22:
            in_danger = True
            start_date = date
            trigger_price = close_p
            trigger_bias = bias
            trigger_warning_price = row['SMA40'] * 1.22
            max_price = close_p
            max_date = date
            regime, max_dd = get_regime(df, date)
            
        elif in_danger:
            if close_p > max_price:
                max_price = close_p
                max_date = date
                
            if bias <= 0:
                in_danger = False
                end_date = date
                drop_price = close_p
                
                max_surge = (max_price - trigger_price) / trigger_price * 100
                total_drop = (drop_price - max_price) / max_price * 100
                weeks = (end_date - start_date).days // 7
                
                results.append({
                    '觸發日期': start_date.strftime('%Y-%m-%d'),
                    '類型': regime,
                    '前12月最大回檔(%)': round(max_dd, 2),
                    '觸發時指數': round(trigger_price, 2),
                    '觸發時乖離率(%)': round(trigger_bias, 2),
                    '22%警戒線指數': round(trigger_warning_price, 2),
                    '波段最高日期': max_date.strftime('%Y-%m-%d'),
                    '波段最高指數': round(max_price, 2),
                    '最高噴出漲幅(%)': round(max_surge, 2),
                    '回歸0%日期': end_date.strftime('%Y-%m-%d'),
                    '回歸0%指數': round(drop_price, 2),
                    '回歸0%總跌幅(%)': round(total_drop, 2),
                    '完成回檔所需週數': weeks
                })
                
    if in_danger:
        max_surge = (max_price - trigger_price) / trigger_price * 100
        results.append({
            '觸發日期': start_date.strftime('%Y-%m-%d'),
            '類型': regime,
            '前12月最大回檔(%)': round(max_dd, 2),
            '觸發時指數': round(trigger_price, 2),
            '觸發時乖離率(%)': round(trigger_bias, 2),
            '22%警戒線指數': round(trigger_warning_price, 2),
            '波段最高日期': max_date.strftime('%Y-%m-%d'),
            '波段最高指數': round(max_price, 2),
            '最高噴出漲幅(%)': round(max_surge, 2),
            '回歸0%日期': None,
            '回歸0%指數': None,
            '回歸0%總跌幅(%)': None,
            '完成回檔所需週數': ((df.index[-1] - start_date).days // 7)
        })
        
    return pd.DataFrame(results)

def calc_win_rate(df, current_bias):
    if pd.isna(current_bias):
        return None, 0
    margin = 2.0
    similar_cases = df[(df['Bias'] >= current_bias - margin) & (df['Bias'] <= current_bias + margin)]
    
    total = 0
    drops = 0
    
    for idx in similar_cases.index:
        pos = df.index.get_loc(idx)
        if pos + 4 < len(df):
            total += 1
            future = df.iloc[pos + 4]['Close']
            curr = df.iloc[pos]['Close']
            if future < curr:
                drops += 1
                
    if total == 0:
        return '資料不足', 0
    
    win_rate = (drops / total) * 100
    return round(win_rate, 2), total

def simulate_sma(df, weeks=18):
    latest_close = df['Close'].iloc[-1]
    last_date = df.index[-1]
    
    future_dates = [last_date + pd.Timedelta(days=7 * i) for i in range(1, weeks + 1)]
    past_closes = df['Close'].tolist()
    future_closes = [latest_close] * weeks
    all_closes = past_closes + future_closes
    
    future_smas = []
    for i in range(len(past_closes), len(all_closes)):
        window = all_closes[i-39:i+1]
        sma = sum(window) / 40
        future_smas.append(sma)
        
    return future_dates, future_smas, future_closes

def page_bias_analysis():
    log_visit("40週乖離率分析")
    st.title("📈 台股預警儀表板 (TSE 40W Bias Dashboard)")
    st.markdown("加上 **時空背景過濾器 (Market Regime Filter)** 的台股大數據監控框架。")
    
    with st.spinner('連線抓取最新市場資料中...'):
        df = load_data()
        
    if df.empty:
        st.warning("⚠️ 查無資料，請稍後再試。")
        return
        
    latest_close = df['Close'].iloc[-1]
    latest_sma = df['SMA40'].iloc[-1]
    latest_bias = df['Bias'].iloc[-1]
    
    # 執行回測以獲取所有標籤
    b_df = backtest(df)
    
    # 目前狀態判定
    current_regime_label = "尚未觸發過"
    if not b_df.empty:
        # 取最後一筆事件來了解目前的定位
        curr_event = b_df.iloc[-1]
        current_regime_label = curr_event['類型']
        
    if latest_bias > 20:
        st.markdown(f"""
        <div class="danger-zone">
            <h2>🚨 警告：已進入極端乖離風險區 (Danger Zone)</h2>
            <p style="font-size: 22px;">目前乖離率：<b>{latest_bias:.2f}%</b> (超過 20% 警戒線)</p>
            <p>目前指數：{latest_close:,.2f} | 40週均線：{latest_sma:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="normal-zone">
            <h2>✅ 目前狀態：安全 (Normal)</h2>
            <p style="font-size: 22px;">目前乖離率：<b>{latest_bias:.2f}%</b></p>
            <p>目前指數：{latest_close:,.2f} | 40週均線：{latest_sma:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)
        
    # 如果正在危險區，並且是類型B，顯示專屬警告
    if latest_bias > 20 and "類型 B" in current_regime_label:
        st.markdown(f"""
        <div class="warning-box">
            <h4>🎯 時空背景定位：{current_regime_label}</h4>
            <p style="font-size: 16px; color: #ffcccc;">
               <b>系統警告：</b> 本次回檔判定為高位噴出。歷史數據顯示，此類型背景下的回歸通常更為劇烈，請密切注意移動停利以及風險控管。
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📉 時空背景動態圖表")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                            vertical_spacing=0.05, 
                            subplot_titles=('加權指數與 40週均線 (週線)', '40週乖離率 (%)'),
                            row_width=[0.3, 0.7])

        fig.add_trace(go.Candlestick(x=df.index,
                        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                        name='K線'), row=1, col=1)
                        
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA40'], 
                                 line=dict(color='#FFA500', width=2), 
                                 name='40週均線'), row=1, col=1)
                                 
        fig.add_trace(go.Scatter(x=df.index, y=df['Bias'], 
                                 line=dict(color='#00FFFF', width=1.5), 
                                 name='乖離率'), row=2, col=1)
                                 
        if not b_df.empty:
            type_a_dates = pd.to_datetime(b_df[b_df['類型'].str.contains('類型 A')]['觸發日期'])
            type_b_dates = pd.to_datetime(b_df[b_df['類型'].str.contains('類型 B')]['觸發日期'])
            
            # 使用 get_indexer 以防日期不存在 df index
            type_a_points = df.loc[df.index.intersection(type_a_dates)]
            type_b_points = df.loc[df.index.intersection(type_b_dates)]
            
            fig.add_trace(go.Scatter(x=type_a_points.index, y=type_a_points['Bias'],
                                     mode='markers', marker=dict(color='lime', size=10, symbol='circle', line=dict(width=2, color='white')),
                                     name='類型 A (低基期)'), row=2, col=1)
                                     
            fig.add_trace(go.Scatter(x=type_b_points.index, y=type_b_points['Bias'],
                                     mode='markers', marker=dict(color='red', size=10, symbol='circle', line=dict(width=2, color='white')),
                                     name='類型 B (高位段)'), row=2, col=1)

        fig.add_hline(y=0, line_dash="dash", line_color="gray", row=2, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="yellow", row=2, col=1, annotation_text="20% 警戒線")
        fig.add_hline(y=22, line_dash="solid", line_color="red", row=2, col=1, annotation_text="22% 極端線")
        
        fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False,
                          margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig, use_container_width=True)
        
    with col2:
        st.subheader("📊 歷史勝率估計")
        win_rate, total_cases = calc_win_rate(df, latest_bias)
        st.info(f"📍 歷史上乖離率落在 **{latest_bias - 2:.2f}% ~ {latest_bias + 2:.2f}%** 共發生過 **{total_cases}** 次。")
        
        if isinstance(win_rate, (int, float)):
             st.metric(label="未來一個月內下跌機率", value=f"{win_rate}%")
        else:
             st.metric(label="未來一個月內下跌機率", value=f"{win_rate}")
             
        st.markdown("---")
        st.subheader("🧠 類型數據統計")
        if not b_df.empty:
            finished_df = b_df.dropna(subset=['回歸0%總跌幅(%)'])
            if not finished_df.empty:
                avg_stats = finished_df.groupby('類型').agg({
                    '回歸0%總跌幅(%)': 'mean',
                    '完成回檔所需週數': 'mean'
                }).reset_index()
                
                for _, r in avg_stats.iterrows():
                    st.markdown(f"**{r['類型']}**")
                    st.markdown(f"- 平均總跌幅: **{r['回歸0%總跌幅(%)']:.2f}%**")
                    st.markdown(f"- 平均歷時: **{r['完成回檔所需週數']:.1f} 週**")
            else:
                st.write("尚無完整回歸的歷史數據")

    st.write("---")
    st.subheader("🔮 未來均線路徑預測 (假設維持現價不動)")
    
    future_weeks = 18
    f_dates, f_smas, f_closes = simulate_sma(df, weeks=future_weeks)
    target_sma = f_smas[-1]
    target_date = f_dates[-1]
    
    drop_from_current = (target_sma - latest_close) / latest_close * 100
    
    st.markdown(f"假設加權指數在未來 **{future_weeks} 週** 內都維持在目前的價位 **{latest_close:,.2f}** 不動，隨著時間推移與高檔扣抵：")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("預測到期日期", target_date.strftime('%Y-%m-%d'))
    col_f2.metric("屆時 40 週均線預期攀升至", f"{target_sma:,.2f}")
    col_f3.metric("目前價位距離屆時均線", f"{drop_from_current:.2f}%")
    
    fig_pred = go.Figure()
    lookback = 40
    past_d = list(df.index[-lookback:])
    past_c = list(df['Close'].iloc[-lookback:])
    past_sma = list(df['SMA40'].iloc[-lookback:])
    
    fig_pred.add_trace(go.Scatter(x=past_d + f_dates, y=past_c + f_closes, 
                                 line=dict(color='gray', width=2, dash='dot'), 
                                 name='假設維持現價不變的指數路徑'))
    
    fig_pred.add_trace(go.Scatter(x=past_d, y=past_sma, 
                                 line=dict(color='#FFA500', width=2), 
                                 name='過去 SMA40'))
                                 
    fig_pred.add_trace(go.Scatter(x=f_dates, y=f_smas, 
                                 line=dict(color='magenta', width=2), 
                                 name='預測的 SMA40 上升路徑'))
                                 
    fig_pred.update_layout(height=450, template="plotly_dark", 
                           title=f"未來 {future_weeks} 週 40 週均線扣抵預測圖",
                           margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_pred, use_container_width=True)

    st.write("---")
    st.subheader("📝 歷史回測：時空背景與大於 22% 乖離率追蹤")
    st.markdown("將歷史事件區分為「低基期反彈」與「高位末升段」，並追蹤回歸 0% 期間的波段數據。")
    
    if not b_df.empty:
        st.dataframe(b_df, use_container_width=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter', engine_kwargs={'options': {'nan_inf_to_errors': True}}) as writer:
            b_df.to_excel(writer, index=False, sheet_name='回測結果')
            
        st.download_button(
            label="📥 匯出詳細回測報表 (Excel)",
            data=buffer.getvalue(),
            file_name="台股40週乖離率_時空分類回測報表.xlsx",
            mime="application/vnd.ms-excel"
        )
    else:
        st.success("歷史上沒有發生過大於 22% 乖離率的事件。")

def page_upward_bias():
    log_visit("乖離上漲模組")
    st.title("📈 乖離底部反彈上漲模組")
    st.write("這是一個獨立的分析頁面！\\n計算每一次從低點起漲（經過前波大於 7% 的修正洗盤），一直抱到「下一次再發生 7% 大回檔」前的小波段/大波段真正漲幅。")

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
            start_date = w['start_date'].strftime('%Y-%m-%d')
            status = '進行中' if w.get('ongoing', False) else '已完結'
            
            if status == '進行中':
                end_date_str = f"至今 ({df.index[-1].strftime('%m/%d')})"
                end_price = df['Close'].iloc[-1]
                # for ongoing, end_price is right now, but highest is w['highest_price']
                # But let's show current end_price to track daily
                days = (df.index[-1] - w['start_date']).days
                gain_pct = (end_price - w['start_price']) / w['start_price'] * 100
            else:
                end_date_str = w['end_date'].strftime('%Y-%m-%d')
                end_price = w['end_price']
                days = (w['end_date'] - w['start_date']).days
                gain_pct = (end_price - w['start_price']) / w['start_price'] * 100
            
            results.append({
                '起漲日期 (前波破底)': start_date,
                '最高日期 (下波前高)': end_date_str,
                '起漲價格': round(float(w['start_price']), 2),
                '最高價格 (或現價)': round(float(end_price), 2),
                '漲幅(%)': round(float(gain_pct), 2),
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
        
        # Handle cases where all values fall outside bins
        try:
             count_series = pd.cut(finished_waves['漲幅(%)'], bins=bins, labels=labels, right=False).value_counts().sort_index()
        except:
             count_series = pd.Series(0, index=labels)
        
        dist_results = []
        total = len(finished_waves)
        for label, count in count_series.items():
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
        
    st.markdown("---")

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

def page_downward_bias():
    log_visit("7% 回檔進場分析")
    st.title("📉 股市 7% 回檔進場分析儀表板")
    st.write("即時監測與歷史回測：針對標普 500 (SPX)、那斯達克 (IXIC) 及台股加權指數 (TWII)，分析自歷史高點跌破 7% 後的剩餘跌幅與反彈機率。")
    
    tickers = {
        "S&P 500 (^GSPC)": "^GSPC",
        "NASDAQ (^IXIC)": "^IXIC",
        "台灣加權指數 (^TWII)": "^TWII"
    }

    @st.cache_data(ttl=3600)
    def get_analysis(ticker_symbol):
        df = fetch_data(ticker_symbol, start_date="2000-01-01")
        if df.empty:
            return df, pd.DataFrame(), {}, pd.DataFrame(), 0, "N/A"
            
        events_df = analyze_7pct_strategy(df, trigger_pct=7.0)
        metrics, dist_df = calculate_7pct_statistics(events_df)
        
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

    selected_name = st.selectbox("選擇分析指數", list(tickers.keys()))
    symbol = tickers[selected_name]

    df, events_df, metrics, dist_df, current_dd, last_date = get_analysis(symbol)

    if df.empty or events_df.empty:
        st.warning("目前尚無足夠歷史數據可供分析。")
        return

    st.markdown("---")
    st.subheader(f"📡 即時監控板 ({last_date})")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric(label="目前距離前高跌幅", value=f"-{max(0, current_dd):.2f}%", 
                  delta="已觸發進場標準!" if current_dd >= 7.0 else f"尚未觸發 (剩 {-7 + current_dd:.2f}%)", 
                  delta_color="inverse" if current_dd >= 7.0 else "normal")

    with col2:
        if current_dd >= 7.0:
            prob_worse = metrics.get('Prob Residual DD > 10%', 0)
            st.error(f"🚨 **進場警示**：目前已進入 7% 觸發區間！\n\n根據歷史回測，若您在此時進場，後續這波再跌超過 **10%** 的機率約為 **{prob_worse:.1f}%**。請做好資金控管。")
        else:
            st.success(f"✅ **安全區間**：目前回檔幅度小於 7%，不符合歷史劇烈回檔進場條件。")

    st.markdown("---")
    st.subheader("📊 歷史關鍵數據 (觸發 7% 後的平均表現)")
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)

    kpi1.metric("歷史觸發次數", f"{metrics.get('Recovered Events', 0)} 次")
    kpi2.metric("平均再跌(剩餘)幅度", f"-{metrics.get('Avg Residual Drawdown (%)', 0)}%")
    kpi3.metric("平均見底天數", f"{metrics.get('Avg Days to Bottom', 0)} 天")
    kpi4.metric("平均解套/回歸天數", f"{metrics.get('Avg Days to Recovery', 0)} 天")

    st.markdown("---")
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
    st.subheader("📜 歷史波段詳情清單")
    st.write("列出 2000 年來每一次觸發 7% 回檔的完整歷程：")

    display_cols = ['觸發日期', '前高日期', '破底日期', '解套日期', 
                    '最大跌幅(%)', '剩餘跌幅(%)', '破底花費天數', '解套花費天數', '狀態']
    
    # Check if we have these columns to prevent KeyErrors
    cols_to_show = [c for c in display_cols if c in events_df.columns]
    
    st.dataframe(events_df[cols_to_show].sort_values(by='觸發日期', ascending=False), height=400)

def page_admin_dashboard():
    log_visit("管理員後台")
    st.title("🛡️ 站長專屬觀測後台")
    st.markdown("只有您才看得見的秘密基地！未來所有的登入帳號、付費訂閱、點擊流量都會匯集到這裡。")
    
    st.subheader("👥 即時流量追蹤 (模擬)")
    logs = st.session_state['visit_logs']
    
    if len(logs) > 0:
        logs_df = pd.DataFrame(logs)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("總瀏覽次數", len(logs_df))
            st.dataframe(logs_df.tail(20).iloc[::-1], use_container_width=True) # 顯示最近 20 筆
            
        with col2:
            st.write("📌 **熱門模組分佈**")
            page_counts = logs_df['瀏覽模組'].value_counts().reset_index()
            page_counts.columns = ['模組', '次數']
            fig_pie = go.Figure(data=[go.Pie(labels=page_counts['模組'], values=page_counts['次數'], hole=.3)])
            fig_pie.update_layout(template="plotly_dark", height=300, margin=dict(l=0, r=0, t=30, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            
    else:
        st.info("目前還沒有任何訪客記錄。")
        
    st.write("---")
    st.subheader("⚙️ 假裝的串接說明：Google 登入設定檔")
    st.code("""
# 未來的真實架構：
# 我們會在 Google Cloud Platform 上為您申請一組 OAuth Client ID
# 當任何人訪問網站時，需要先通過 Google 授權：
if user_info := google_login():
    if user_info['email'] == "您指定的站長信箱@gmail.com":
        顯示_管理員側邊欄()
    else:
        顯示_一般會員側邊欄()
""")

def login_simulator():
    """ 這是一個輕量級的登入模擬器，讓您體會一下流程 """
    st.sidebar.markdown("---")
    
    if st.session_state['user_role'] == 'guest':
        st.sidebar.subheader("🔒 會員登入 (體驗版)")
        st.sidebar.write("請輸入信箱以模擬登入流程：")
        
        email_input = st.sidebar.text_input("Google Email", key="login_email")
        
        # 如果輸入的是您的帳號，就變成站長，否則是一般會員
        if st.sidebar.button("登入 (Login)"):
            if email_input == ADMIN_EMAIL:
                st.session_state['user_role'] = 'admin'
                st.session_state['user_email'] = email_input
                st.rerun()
            elif email_input:
                st.session_state['user_role'] = 'user'
                st.session_state['user_email'] = email_input
                st.rerun()
            else:
                st.sidebar.error("請輸入信箱！")
    else:
        st.sidebar.success(f"✅ 您好，{st.session_state['user_email']}")
        st.sidebar.write(f"身分：{'👑 站長' if st.session_state['user_role'] == 'admin' else '👤 一般會員'}")
        
        if st.sidebar.button("登出 (Logout)"):
            st.session_state['user_role'] = 'guest'
            st.session_state['user_email'] = None
            st.rerun()

def main():
    st.sidebar.title("📊 股市分析系統")
    st.sidebar.markdown("請選擇您要查看的功能：")
    
    # 掛載登入模擬器
    login_simulator()
    
    pages = {
        "📊 40週乖離率分析": page_bias_analysis,
        "📉 股市 7% 回檔進場分析": page_downward_bias,
        "📈 乖離底部反彈上漲模組": page_upward_bias,
        "💼 資產配置回測 (Portfolio)": page_portfolio_visualizer,
        "🧠 AI 全球情緒雷達": page_ai_sentiment
    }
    
    # 如果是站長登入，就可以看到私密的後台
    if st.session_state['user_role'] == 'admin':
        pages["🛡️ 管理員後台 (專屬)"] = page_admin_dashboard
        
    selection = st.sidebar.radio("功能導覽", list(pages.keys()))
    
    st.sidebar.write("---")
    st.sidebar.info("這是一個整合多個股市量化分析功能的入口網站。您可以隨時點選不同策略模組。")
    
    # 執行對應的頁面函數
    pages[selection]()

if __name__ == "__main__":
    main()
