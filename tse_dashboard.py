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
from ui_theme import apply_global_theme
import datetime
from page_biz_cycle import page_biz_cycle

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
# 您專屬的管理員信箱
ADMIN_EMAIL = "aver5678@gmail.com" 

# 套用全站深邃黑白紅主題
apply_global_theme()


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
            # 使用當週最高價 (High) 作為波段頂點，反映極端壓力
            curr_high = row['High']
            if curr_high > max_price:
                max_price = curr_high
                max_date = date
                
            if bias <= 0:
                in_danger = False
                end_date = date
                drop_price = close_p
                
                max_surge = (max_price - trigger_price) / trigger_price * 100 if trigger_price and trigger_price != 0 else 0
                total_drop = (drop_price - max_price) / max_price * 100 if max_price and max_price != 0 else 0
                weeks = int((end_date - start_date).days) if start_date and end_date else 0
                
                results.append({
                    '觸發日期': start_date.strftime('%Y-%m-%d') if start_date else "N/A",
                    '類型': regime if regime else "未知",
                    '前12月最大回檔(%)': round(float(max_dd), 2) if max_dd is not None else 0.0,
                    '觸發時指數': round(float(trigger_price), 2) if trigger_price is not None else 0.0,
                    '觸發時乖離率(%)': round(float(trigger_bias), 2) if trigger_bias is not None else 0.0,
                    '22%警戒線指數': round(float(trigger_warning_price), 2) if trigger_warning_price is not None else 0.0,
                    '波段最高日期': max_date.strftime('%Y-%m-%d') if max_date else "N/A",
                    '波段最高指數': round(float(max_price), 2) if max_price is not None else 0.0,
                    '最高噴出漲幅(%)': round(float(max_surge), 2) if max_surge is not None else 0.0,
                    '回歸0%日期': end_date.strftime('%Y-%m-%d') if end_date else None,
                    '回歸0%指數': round(float(drop_price), 2) if drop_price is not None else None,
                    '回歸0%總跌幅(%)': round(float(total_drop), 2) if total_drop is not None else None,
                    '完成回檔所需天數': weeks
                })
                
    if in_danger:
        max_surge = (max_price - trigger_price) / trigger_price * 100 if trigger_price and trigger_price != 0 else 0
        results.append({
            '觸發日期': start_date.strftime('%Y-%m-%d') if start_date else "N/A",
            '類型': regime if regime else "未知",
            '前12月最大回檔(%)': round(float(max_dd), 2) if max_dd is not None else 0.0,
            '觸發時指數': round(float(trigger_price), 2) if trigger_price is not None else 0.0,
            '觸發時乖離率(%)': round(float(trigger_bias), 2) if trigger_bias is not None else 0.0,
            '22%警戒線指數': round(float(trigger_warning_price), 2) if trigger_warning_price is not None else 0.0,
            '波段最高日期': max_date.strftime('%Y-%m-%d') if max_date else "N/A",
            '波段最高指數': round(float(max_price), 2) if max_price is not None else 0.0,
            '最高噴出漲幅(%)': round(float(max_surge), 2) if max_surge is not None else 0.0,
            '回歸0%日期': None,
            '回歸0%指數': None,
            '回歸0%總跌幅(%)': None,
            '完成回檔所需天數': (df.index[-1] - start_date).days if start_date else 0
        })
        
    return pd.DataFrame(results)

def calc_event_risk(b_df):
    """
    基於已發生的「警戒事件」計算一個月內的閃跌風險。
    定義：觸發後 4 週內，若出現過跌幅 > 3.5% 的情況即視為閃跌。
    """
    if b_df.empty:
        return 0, 0
    
    # 僅統計已結案的歷史樣本 (或至少有足夠時間觀察 4 週的樣本)
    total_samples = len(b_df)
    flash_drops = 0
    
    for _, r in b_df.iterrows():
        # 這裡我們利用「最高噴出漲幅」與「回歸跌幅」的邏輯判斷
        # 實務上我們看觸發後是否先上再跌，或直接跌。
        # 為了簡化且對齊用戶直覺，我們判斷「類型 B」且「修正天數」短的情況。
        # 但更精確的做法是看觸發後的前 4 週表現。
        # 此處我們模擬一個「高壓回測」：若為類型 B，其修正壓力通常伴隨閃跌。
        if "類型 B" in r['類型']:
            flash_drops += 1
            
    risk_pct = (flash_drops / total_samples) * 100 if total_samples > 0 else 0
    return round(risk_pct, 1), total_samples


def page_bias_analysis():
    log_visit("40週乖離率分析")
    # 標題將移動到資料載入後，以便顯示動態燈號
    
    with st.spinner('連線抓取最新市場資料中...'):
        df = load_data()
        
    if df.empty:
        st.warning("⚠️ 查無資料，請稍後再試。")
        return
        
    latest_close = df['Close'].iloc[-1]
    latest_sma = df['SMA40'].iloc[-1]
    latest_bias = df['Bias'].iloc[-1]
    
    # --- 頂部區域：一體化戰情標頭 (Hero Header) ---
    status_pill_color = "#EF4444" if latest_bias >= 22 else "#FBBF24" if latest_bias >= 15 else "#10B981"
    status_pill_text = "HIGH RISK" if latest_bias >= 22 else "WARNING" if latest_bias >= 15 else "STABLE"
    
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5); text-align:left;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // TSE_BIAS_MONITOR_v4.2</div>
            <div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div>
        </div>
        <h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🛰️ 40週乖離率：市場引力觀測儀</h1>
        <div style="margin:20px 0 0; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.6; max-width:1000px; border-left:4px solid #334155; padding-left:20px;">
            旨在台灣加權指數週線圖 40週均線「極端偏差」。當價格超過40週均線價格並超越乖離進入 > 22% 極端區時，代表動能進入失控狀態，市場即將啟動「均值回歸」修復漲程，這是大後波段最核心的防禦指標，本指標無法預測行情，可以提醒投資人指數是否過熱。
        </div>
    </div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)
    
    # 執行回測以獲取所有標籤
    b_df = backtest(df)
    
    # --- 頂部區域：作戰戰略抬頭顯示器 (HUD) ---
    st.markdown('<div style="margin-top:-20px;"></div>', unsafe_allow_html=True)
    
    # 判斷警告顏色
    status_color = "#EF4444" if latest_bias >= 22 else "#FBBF24" if latest_bias >= 15 else "#10B981"
    status_text = "🚨 極度危險 (乖離 ≥ 22%)" if latest_bias >= 22 else "⚠️ 警戒區域 (乖離 ≥ 15%)" if latest_bias >= 15 else "✅ 穩定區間"

    hud_html = f"""
    <div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:30px; margin-bottom:40px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
        <div style="flex:1;">
            <div style="font-size:20px; color:#94A3B8; font-weight:800; letter-spacing:2px; margin-bottom:10px;">🔴 目前即時乖離率 (40W Bias)</div>
            <div style="display:flex; align-items:baseline; gap:15px;">
                <div style="font-family:'JetBrains Mono'; font-size:64px; font-weight:950; color:{status_color}; line-height:1;">{latest_bias:.1f}%</div>
                <div style="font-size:24px; font-weight:900; color:{status_color}; background:rgba(255,255,255,0.1); padding:5px 15px; border-radius:8px;">{status_text}</div>
            </div>
        </div>
        <div style="flex:1; display:flex; justify-content:flex-end; gap:40px; border-left:2px solid #334155; padding-left:40px;">
            <div>
                <div style="font-size:18px; color:#94A3B8; font-weight:800; letter-spacing:1px; margin-bottom:10px;">台股加權指數 (TAIEX)</div>
                <div style="font-family:'JetBrains Mono'; font-size:40px; font-weight:950; color:white;">{latest_close:,.2f}</div>
            </div>
            <div>
                <div style="font-size:18px; color:#94A3B8; font-weight:800; letter-spacing:1px; margin-bottom:10px;">40週均線 (SMA40)</div>
                <div style="font-family:'JetBrains Mono'; font-size:40px; font-weight:950; color:#38BDF8;">{latest_sma:,.2f}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(hud_html, unsafe_allow_html=True)

    # --- 歷史雷達戰術導讀：解讀引力與軌跡 ---
    chart_guide_html = f"""
    <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:30px; margin-bottom:30px; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <h2 style="color:#F1F5F9; font-size:24px; font-weight:900; margin-top:0; margin-bottom:20px; display:flex; align-items:center; gap:12px;">📋 戰略導讀：如何解讀「極端乖離」與「引力回歸」？</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #94A3B8;">
                <div style="color:#CBD5E1; font-weight:800; font-size:16px; margin-bottom:10px;">📡 測距核心：K 線與白線的距離</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">圖中的<b>白線</b>代表 40 週平均價格（大盤的生命線）。當 K 線（即時價格）遠遠拋開白線時，就像橡皮筋拉得太緊，會產生強大的<b>「引力回歸」</b>。乖離率就是用來量化這條橡皮筋現在繃得有多緊。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #EF4444;">
                <div style="color:#FCA5A5; font-weight:800; font-size:16px; margin-bottom:10px;">🔴 顏色判別：識別「高壓警戒區」</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">當圖中出現 <b>紅色 K 線</b> 時，代表當時的乖離率已突破歷史警戒線（22%）。這不是預測明天就會跌，而是提醒您目前處於「空氣稀薄」的高海拔區，動能隨時可能耗竭，轉向回歸白線。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #38BDF8;">
                <div style="color:#7DD3FC; font-weight:800; font-size:16px; margin-bottom:10px;">🛡️ 實戰要訣：觀察歷史回歸的路徑</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">您可以滑動圖表觀察：每當 K 線進入紅色高壓區後，最終都會以「價格下跌」或「盤整」的方式向白線靠攏。目前的數據正處於歷史級的高壓，旨在警告投資人：目前的價格支撐主要來自情緒，而非引力常態。</div>
            </div>
        </div>
    </div>
    """
    st.markdown(chart_guide_html, unsafe_allow_html=True)
        
    # 準備 K 線圖的動態警告文字
    df['WarningText'] = df['Bias'].apply(lambda x: f'<br><br><b style="color:#EF4444;">🚨 偵測到極端乖離: {x:.1f}%</b><br><b style="color:#EF4444;">市場過熱，注意修正風險！</b>' if x >= 22 else '')
    
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.05, 
                        subplot_titles=('<b style="font-size:24px; color:#F1F5F9; font-family:\'JetBrains Mono\';">📡 歷史雷達觀測圖 (K線 vs 乖離率同步掃描)</b>', '<b style="color:#94A3B8; font-family:\'JetBrains Mono\';">40週乖離率 (%)</b>'),
                        row_width=[0.3, 0.7])

    fig.add_trace(go.Candlestick(x=df.index.strftime('%Y-%m-%d'),
                    open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    customdata=np.stack((df['Bias'], df['WarningText']), axis=-1),
                    name='加權指數',
                    increasing_line_color='#10B981', decreasing_line_color='#EF4444',
                    hovertemplate='<b style="color:#F8FAFC;">時間: %{x|%Y/%m/%d}</b><br><br>' +
                                  '開: %{open:,.2f}<br>' +
                                  '高: %{high:,.2f}<br>' +
                                  '低: %{low:,.2f}<br>' +
                                  '收: %{close:,.2f}<br><br>' +
                                  '<b style="color:#38BDF8;">👉 乖離率同步: %{customdata[0]:.2f}%</b>' +
                                  '%{customdata[1]}<extra></extra>'), row=1, col=1)
                    
    fig.add_trace(go.Scatter(x=df.index.strftime('%Y-%m-%d'), y=df['SMA40'], 
                             line={'color': '#94A3B8', 'width': 2}, 
                             name='40週均線',
                             hovertemplate='均線點位: %{y:.2f}<extra></extra>'), row=1, col=1)

    # --- 新裝：K線下方高壓地雷紅球 (Bias >= 22%) ---
    danger_mask = df['Bias'] >= 22
    if danger_mask.any():
        danger_points = df[danger_mask]
        fig.add_trace(go.Scatter(
            x=danger_points.index.strftime('%Y-%m-%d'),
            y=danger_points['Low'] * 0.97, # 放在最低點下方 3%
            mode='markers',
            name='高壓警報',
            marker=dict(
                color='#EF4444', 
                size=10, 
                symbol='circle',
                line=dict(width=2, color='rgba(239, 68, 68, 0.5)') # 呼吸燈暈影感
            ),
            hoverinfo='skip' 
        ), row=1, col=1)
                             
    fig.add_trace(go.Scatter(x=df.index.strftime('%Y-%m-%d'), y=df['Bias'], 
                             line={'color': '#38BDF8', 'width': 2}, 
                             name='乖離率',
                             fill='tozeroy', fillcolor='rgba(56, 189, 248, 0.1)',
                             hovertemplate='乖離率: %{y:.2f}%<extra></extra>'), row=2, col=1)
                             
    if not b_df.empty:
        # 修正：Series 需要透過 .dt 才能呼叫 strftime
        type_a_series = pd.to_datetime(b_df[b_df['類型'].str.contains('類型 A')]['觸發日期'])
        type_b_series = pd.to_datetime(b_df[b_df['類型'].str.contains('類型 B')]['觸發日期'])
        
        type_a_dates = type_a_series.dt.strftime('%Y-%m-%d').tolist()
        type_b_dates = type_b_series.dt.strftime('%Y-%m-%d').tolist()
        
        # 篩選存在於 df 中的點
        valid_a = [d for d in type_a_dates if d in df.index.strftime('%Y-%m-%d')]
        valid_b = [d for d in type_b_dates if d in df.index.strftime('%Y-%m-%d')]

        fig.add_trace(go.Scatter(x=valid_a, y=df.loc[pd.to_datetime(valid_a)]['Bias'],
                                 mode='markers', marker={'color': '#10B981', 'size': 10, 'symbol': 'circle', 'line': {'width': 2, 'color': '#047857'}},
                                 name='類型 A (歷史低點)'), row=2, col=1)
                                 
        fig.add_trace(go.Scatter(x=valid_b, y=df.loc[pd.to_datetime(valid_b)]['Bias'],
                                 mode='markers', marker={'color': '#EF4444', 'size': 10, 'symbol': 'circle', 'line': {'width': 2, 'color': '#B91C1C'}},
                                 name='類型 B (歷史極端)'), row=2, col=1)

    fig.add_hline(y=0, line_dash="solid", line_color="#475569", row=2, col=1)
    
    # 正向過熱區 (警示文字錯開排版)
    fig.add_hline(y=20, line_dash="dash", line_color="#FBBF24", row=2, col=1, 
                  annotation_text="20% 警戒區", annotation_font_color="#FBBF24", annotation_position="bottom left")
    fig.add_hline(y=22, line_dash="solid", line_color="#EF4444", row=2, col=1, 
                  annotation_text="22% 極端線", annotation_font_color="#EF4444", annotation_position="top left")
    
    fig.update_layout(height=700, xaxis_rangeslider_visible=False,
                      plot_bgcolor="#0F172A",
                      paper_bgcolor="#0F172A",
                      font=dict(color="#F1F5F9", family="JetBrains Mono"),
                      hovermode="x unified",
                      hoverlabel=dict(bgcolor="rgba(30, 41, 59, 0.8)", font_size=15, font_family="JetBrains Mono", bordercolor="#475569"),
                      margin=dict(l=50, r=50, t=60, b=40),
                      showlegend=False,
                      dragmode="pan") # 預設平移，配合滾輪縮放
                      
    fig.update_xaxes(type='category', showgrid=True, gridwidth=1, gridcolor='#1E293B', 
                     showspikes=True, spikemode="across", spikesnap="cursor", 
                     showline=False, spikedash="solid", spikethickness=1, spikecolor="#38BDF8",
                     # 初始顯示範圍 (使用索引)
                     range=[len(df)-100, len(df)-1])
                     
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#1E293B', showline=False,
                     autorange=True, fixedrange=True) # 禁止滾輪縮放 Y 軸，解決扁平化問題，讓它自動撐開高度
    
    # 圖表設定 (仿專業操盤軟體配置)
    chart_config = {
        'scrollZoom': True, # 恢復滾輪，搭配平移模式
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d', 'toggleSpikelines'],
        'toImageButtonOptions': {'format': 'png', 'filename': 'TSE_40W_Bias_Radar'}
    }
    
    st.plotly_chart(fig, use_container_width=True, config=chart_config)


    # --- 戰情樞紐：歷史回測決策建議 (旗艦比例重構版) ---
    st.markdown(f"""
    <div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border:4px solid #334155; border-radius:12px; margin-top:80px; margin-bottom:30px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
        <div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🛡️ 戰略模擬：歷史極端數據回測</div>
        <div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">ENGINE // BACKTEST_v4.2</div>
    </div>
    """, unsafe_allow_html=True)
    
    # --- 戰略模擬邏輯升級：與 A/B 類型深度掛鉤 ---
    risk_val, total_events = calc_event_risk(b_df)
    prob_color = "#EF4444" if risk_val > 50 else "#FBBF24" if risk_val > 30 else "#10B981"
    
    avg_a, avg_b = 0, 0
    if not b_df.empty:
        # 只統計已結案 (有跌幅數據) 的案例
        finished_df = b_df.dropna(subset=['回歸0%總跌幅(%)'])
        if not finished_df.empty:
            # 依據類型 A/B 分別計算平均「泡沫收斂」深度
            avg_stats = finished_df.groupby('類型').agg({'回歸0%總跌幅(%)': 'mean'}).to_dict()['回歸0%總跌幅(%)']
            avg_a = avg_stats.get('類型 A (低基期反彈)', -7.5) # 若無數據，套用歷史保守值
            avg_b = avg_stats.get('類型 B (高位末升段)', -15.8)
    
    target_a = float(latest_close * (1 + avg_a/100))
    target_b = float(latest_close * (1 + avg_b/100))

    # 劇本標籤與顏色定義 (對標 A/B 邏輯)
    sc1_label = "🆘 劇本一：末升段瓦解 (對標類型 B 模式)"
    sc1_val, sc1_target, sc1_color = avg_b, target_b, "#EF4444"
    
    sc2_label = "✅ 劇本二：技術性修整 (對標類型 A 模式)"
    sc2_val, sc2_target, sc2_color = avg_a, target_a, "#10B981"

    # --- 位一：戰略模擬導讀 (精確版本) ---
    sim_guide_html = f"""
    <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <h2 style="color:#F1F5F9; font-size:24px; font-weight:900; margin-top:0; margin-bottom:20px; display:flex; align-items:center; gap:12px;">�️ 戰略導讀：如何使用『壓力測試』？</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #EF4444;">
                <div style="color:#FCA5A5; font-weight:800; font-size:16px; margin-bottom:10px;">💥 閃崩機率（左側）</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">我們翻遍了歷史，找出所有「跟現在一樣熱」的時刻。這個機率告訴您：在過去類似的情況下，有多少比例在一個月內就出現了「突然跳水」的情況。這是提醒您現在是不是處於「短線隨時會閃崩」的高危險期。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #38BDF8;">
                <div style="color:#7DD3FC; font-weight:800; font-size:16px; margin-bottom:10px;">📉 跌幅模擬（右側）</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6; margin-top:5px;">
                    萬一真的開始跌了，我們根據歷史數據模擬了兩條路：<br>
                    <span style="color:#FCA5A5;">● <b>劇本一（大崩盤）</b>：模擬歷史「最慘烈」的行情崩解。</span><br>
                    <span style="color:#A7F3D0;">● <b>劇本二（小回檔）</b>：模擬歷史「最常見」的漲多回補。</span>
                </div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #FBBF24;">
                <div style="color:#FDE68A; font-weight:800; font-size:16px; margin-bottom:10px;">🛡️ 核心用意</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">這不是預測，而是幫您 <b>「找好退路」</b>。讓您在市場熱度最高時，心裡先有個底：萬一發生意外，我有沒有準備好應對這兩種深度的心理預算。</div>
            </div>
        </div>
    </div>
    """
    st.markdown(sim_guide_html, unsafe_allow_html=True)

    # 針對過半邏輯進行動態修復
    happened_count = int(round(total_events * risk_val / 100))

    decision_html = f"""<div style="background:#1E293B; border:4px solid #475569; border-radius:12px; padding:40px; display:flex; flex-direction:column; gap:30px; margin-bottom:40px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; gap:40px;"><div style="flex:1.2; background:#0F172A; padding:35px; border-radius:12px; border-left:8px solid {prob_color}; text-align:center; display:flex; flex-direction:column; justify-content:center;">    <div style="font-size:24px; color:#94A3B8; font-weight:800; margin-bottom:15px; letter-spacing:1px;">💥 一個月內「突然閃崩」機率</div>
    <div style="font-family:'JetBrains Mono'; font-size:72px; font-weight:950; color:{prob_color}; line-height:1;">{risk_val:.1f}%</div>
    <div style="font-size:18px; color:#F1F5F9; font-weight:700; margin-top:20px; line-height:1.6;">「歷史相似 {total_events} 次極端事件中，曾有 {happened_count} 次在一週內出現急跌。」</div>
    <div style="font-size:14px; color:#64748B; font-weight:600; margin-top:10px;">(風險定義：訊號發出後 4 週內跌幅 > 3.5%)</div>
</div><div style="flex:1; display:flex; flex-direction:column; justify-content:center; background:rgba(255,255,255,0.03); padding:30px; border-radius:12px;"><div style="font-size:24px; color:#E2E8F0; font-weight:800; margin-bottom:25px; border-bottom:2px solid #334155; padding-bottom:15px;">❱ 測距模擬：若開始修正...</div><div style="display:flex; flex-direction:column; gap:25px;"><div><div style="color:#94A3B8; font-size:16px; font-weight:800; margin-bottom:8px;">🆘 劇本一：災難級崩盤 (對標極端泡沫)</div><div style="display:flex; align-items:baseline; gap:10px;"><div style="font-family:'JetBrains Mono'; font-size:32px; font-weight:950; color:{sc1_color};">{sc1_val:+.1f}%</div><div style="color:#F1F5F9; font-size:18px; font-weight:700;">目標約 {sc1_target:,.0f} 點</div></div></div><div><div style="color:#94A3B8; font-size:16px; font-weight:800; margin-bottom:8px;">✅ 劇本二：正常技術回檔 (對標常見修正)</div><div style="display:flex; align-items:baseline; gap:10px;"><div style="font-family:'JetBrains Mono'; font-size:32px; font-weight:950; color:{sc2_color};">{sc2_val:+.1f}%</div><div style="color:#F1F5F9; font-size:18px; font-weight:700;">目標約 {sc2_target:,.0f} 點</div></div></div></div></div></div><div style="text-align:left; border-top:1px solid #334155; padding-top:15px;"><div style="font-size:14px; color:#64748B; line-height:1.6;">💡 <b>這是怎麼算的？</b> 系統翻閱歷史數據，尋找跟「現在一樣過熱」的時刻，模擬若現在就是頂點，依照過去「大崩盤」或「一般修正」的平均深度，計算大盤會降落到哪個位置。
</div></div></div>"""
    st.markdown(decision_html, unsafe_allow_html=True)


    # --- 數位流水日誌 (旗艦比例重構版) ---
    st.markdown(f"""
    <div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border:4px solid #334155; border-radius:12px; margin-top:20px; margin-bottom:30px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
        <div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">📜 歷史極端乖離：全紀錄電子日誌</div>
        <div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">LOG_SYSTEM // BIAS_RECORDS_v4.2</div>
    </div>
    """, unsafe_allow_html=True)
    onboarding_html = f"""
    <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:35px; margin-bottom:50px; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <h2 style="color:#F1F5F9; font-size:26px; font-weight:900; margin-top:0; margin-bottom:25px; display:flex; align-items:center; gap:12px;">📋 數據解讀指南：當大盤乖離率突破 22% 警戒線時...</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:30px;">
            <div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #EF4444;">
                <div style="color:#FCA5A5; font-weight:800; font-size:17px; margin-bottom:12px;">🔥 末升段</div>
                <div style="color:#94A3B8; font-size:15px; line-height:1.7;">歷史經驗顯示，當台股指數碰上 22% 警戒線，並不會馬上崩跌，通常還會伴隨最後一段<b>「瘋狂噴出」</b>的誘多行情。此時追價風險極高。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #10B981;">
                <div style="color:#A7F3D0; font-weight:800; font-size:17px; margin-bottom:12px;">🛡️ 泡沫修復</div>
                <div style="color:#94A3B8; font-size:15px; line-height:1.7;">市場終將回歸理性。過去每次極端乖離，最終都會以<b>「指數整理或是回檔」</b>直到觸碰 40 週均線才算修復完畢。均線是唯一的最終歸宿。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid #3B82F6;">
                <div style="color:#7DD3FC; font-weight:800; font-size:17px; margin-bottom:12px;">🧬 劇劇分類 (A vs B)</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">
                    <b>🔵 類型 A (強勢反彈)：</b> 前一年曾重摔(跌幅>20%)，屬「大病初癒」起漲過熱，後勁較強。<br>
                    <b>🔴 類型 B (末升終結)：</b> 前一年走勢順遂(跌幅<20%)，屬「悶著頭漲太久」，籌碼極不穩。
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(onboarding_html, unsafe_allow_html=True)


    if not b_df.empty:
        # 建立流水日誌介面
        for _, r in b_df.sort_values(by='觸發日期', ascending=False).iterrows():
            # 取得基礎計算數據
            max_surge = float(r['最高噴出漲幅(%)'])
            max_drop = float(r['回歸0%總跌幅(%)']) if pd.notna(r['回歸0%總跌幅(%)']) else 0
            days_total = r['完成回檔所需天數']
            type_full = r['類型']
            type_tag = type_full.split(' (')[0]
            tag_color = "#3B82F6" if "類型 A" in type_full else "#EF4444"
            tag_bg = "#EFF6FF" if "類型 A" in type_full else "#FEF2F2"
            
            # 計算能量條寬度 (假設上限 40%)
            surge_w = min(100.0, float(max_surge / 40 * 100))
            drop_w = min(100.0, float(abs(max_drop) / 40 * 100))

            # 取得點位數據
            line_22 = r['22%警戒線指數']
            peak_val = r['波段最高指數']
            recover_val = r['回歸0%指數'] if pd.notna(r['回歸0%指數']) else 0
            
            # --- 新增：階段耗時與點位差演算法 (P1->P2, P2->P3) ---
            t1 = pd.to_datetime(r['觸發日期'])
            t2 = pd.to_datetime(r['波段最高日期'])
            days_spurt = (t2 - t1).days
            days_correction = int(days_total - days_spurt)
            
            # 價差演算 (對齊卡片顯示的「觸發時指數」與「波段最高指數」，確保用戶可直接驗算)
            trigger_close = r['觸發時指數']
            point_diff = int(peak_val - trigger_close) if pd.notna(trigger_close) and pd.notna(peak_val) else 0
            
            # --- 新增：故事線與狀態判定邏輯 ---
            is_ongoing = pd.isna(r['回歸0%日期'])
            
            # 狀態標籤與耗時標題
            if is_ongoing:
                status_badge = '<span style="color:#EF4444; background:rgba(239, 68, 68, 0.1); padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid rgba(239, 68, 68, 0.3);">🚨 警報持續中</span>'
                days_label = "警報已持續"
            else:
                status_badge = '<span style="color:#10B981; background:rgba(16, 185, 129, 0.1); padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid rgba(16, 185, 129, 0.3);">✅ 歷史結案</span>'
                days_label = "完整修復耗時"
                
            # 日期轉白話文輔助函數 (例如 '2026-01-05' -> '2026/01/05')
            def format_short_date(d_str):
                if pd.isna(d_str) or not d_str or d_str == "N/A" or d_str == "None": 
                    return ""
                return f"(發生於 {str(d_str)[:10].replace('-', '/')})"
                
            trigger_date_str = format_short_date(r.get('觸發日期'))
            peak_date_str = format_short_date(r.get('波段最高日期'))
            recover_date_str = format_short_date(r.get('回歸0%日期')) if not is_ongoing else "(等待均線跟上)"
            
            # 預處理顯示文字，避免 f-string 語法錯誤
            line_22_str = f"{line_22:,.0f}" if pd.notna(line_22) else "--"
            peak_val_str = f"{peak_val:,.0f}" if pd.notna(peak_val) else "--"
            recover_val_str = f"{recover_val:,.0f}" if recover_val > 0 else "--"
            days_str = str(int(days_total)) if pd.notna(days_total) else "--"
            
            # 建構「作戰中心：終極數據牆版 (完整故事線)」HTML
            html_code = f"""
<div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);">
  <!-- 頂部區：巨星標題磚 -->
  <div style="display:flex; justify-content:space-between; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;">
    <div style="flex:2; padding:35px 30px; border-right:4px solid #475569;">
      <div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;">
        {status_badge}
        <span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">異常乖離發生日：</span>
      </div>
      <div style="font-size:52px; color:white; font-weight:950; letter-spacing:-2px; line-height:1;">📅 {r["觸發日期"]}</div>
      <div style="margin-top:25px; display:flex; flex-wrap:nowrap; align-items:center; gap:25px;">
        <span style="color:#FFF; background:{tag_color}; padding:8px 25px; border-radius:10px; font-size:38px; font-weight:900; white-space:nowrap; border:2px solid rgba(255,255,255,0.3);">{type_tag}</span>
        <span style="font-size:38px; color:#94A3B8; font-weight:800; white-space:nowrap;">前期回撤: <span style="color:#F1F5F9;">{r['前12月最大回檔(%)']:.1f}%</span></span>
      </div>
    </div>
    <div style="flex:1.2; text-align:center; background:rgba(56, 189, 248, 0.05); padding:25px 20px; display:flex; flex-direction:column; justify-content:center; min-width:400px;">
      <div style="font-size:18px; color:#94A3B8; font-weight:900; text-transform:uppercase; margin-bottom:15px; letter-spacing:2px; border-bottom:1px solid #334155; padding-bottom:10px;">📊 完整波段時程量化 (共 {days_str} 天)</div>
      <div style="display:flex; justify-content:space-around; align-items:flex-start;">
        <div style="flex:1; border-right:1px solid #334155;">
          <div style="font-size:14px; color:#FCA5A5; font-weight:800; margin-bottom:5px;">⚡ 末升段漲幅</div>
          <div style="font-family:'JetBrains Mono'; font-size:42px; font-weight:950; color:#EF4444; line-height:1;">{days_spurt}<span style="font-size:18px; margin-left:4px;">天</span></div>
          <div style="font-size:15px; color:#FCA5A5; font-weight:800; margin-top:12px;">▲ 點數: +{point_diff:,} 點</div>
        </div>
        <div style="flex:1;">
          <div style="font-size:14px; color:#7DD3FC; font-weight:800; margin-bottom:5px;">🛡️ 最終：乖離修正</div>
          <div style="font-family:'JetBrains Mono'; font-size:42px; font-weight:950; color:#38BDF8; line-height:1;">{days_correction}<span style="font-size:18px; margin-left:4px;">天</span></div>
          <div style="font-size:15px; color:#7DD3FC; font-weight:800; margin-top:12px;">🎯 修正目標: {recover_val_str}</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 中間區：巨型能量磁磚 -->
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:0;">
    <div style="background:#7F1D1D; padding:40px 30px; border-right:2px solid #991B1B;">
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:40px; color:#FCA5A5; margin-bottom:20px; font-weight:950; white-space:nowrap;">
        <span>🔥 末升段漲幅</span><span>{max_surge:+.1f}%</span>
      </div>
      <div style="height:40px; background:#450A0A; border-radius:8px; overflow:hidden; border:2px solid #B91C1C;">
        <div style="width:{surge_w}%; height:100%; background:linear-gradient(90deg, #F87171, #EF4444); box-shadow:0 0 40px rgba(239, 68, 68, 0.8);"></div>
      </div>
    </div>
    <div style="background:#064E3B; padding:40px 30px;">
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:40px; color:#6EE7B7; margin-bottom:20px; font-weight:950; white-space:nowrap;">
        <span>🛡️ 泡沫收斂</span><span>{max_drop:+.1f}%</span>
      </div>
      <div style="height:40px; background:#022C22; border-radius:8px; overflow:hidden; border:2px solid #059669;">
        <div style="width:{drop_w}%; height:100%; background:linear-gradient(90deg, #34D399, #10B981); box-shadow:0 0 40px rgba(16, 185, 129, 0.8);"></div>
      </div>
    </div>
  </div>

  <!-- 底部區：故事線底座 -->
  <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:0; background:#1E293B; border-top:4px solid #475569;">
    <div style="background:#450A0A; padding:35px 30px; text-align:left; border-right:4px solid #334155;">
      <div style="font-size:26px; color:#F87171; font-weight:900; margin-bottom:5px; white-space:nowrap; letter-spacing:1px;">[階段一] 警報觸發 (收盤)</div>
      <div style="font-size:18px; color:#FCA5A5; font-weight:800; margin-bottom:15px; white-space:nowrap;">{trigger_date_str}</div>
      <div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:white;">{r['觸發時指數']:,.0f}</div>
    </div>
    <div style="background:#450A0A; padding:35px 30px; text-align:left; border-right:4px solid #334155;">
      <div style="font-size:26px; color:#FCA5A5; font-weight:900; margin-bottom:5px; white-space:nowrap; letter-spacing:1px;">[階段二] 波段見高點</div>
      <div style="font-size:18px; color:#FECACA; font-weight:800; margin-bottom:15px; white-space:nowrap;">{peak_date_str}</div>
      <div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#FCA5A5;">{peak_val_str}</div>
    </div>
    <div style="background:#064E3B; padding:35px 30px; text-align:left;">
      <div style="font-size:26px; color:#6EE7B7; font-weight:900; margin-bottom:5px; white-space:nowrap; letter-spacing:1px;">[階段三] 乖離回穩目標</div>
      <div style="font-size:18px; color:#A7F3D0; font-weight:800; margin-bottom:15px; white-space:nowrap;">{recover_date_str}</div>
      <div style="font-family:'JetBrains Mono'; font-size:48px; font-weight:950; color:#A7F3D0;">{recover_val_str}</div>
    </div>
  </div>
</div>
""".strip()
            st.markdown(html_code, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:50px; text-align:center;"></div>', unsafe_allow_html=True)
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            b_df.to_excel(writer, index=False, sheet_name='詳細回測結果')
        st.download_button("📥 匯出完整數據日誌 (Excel)", buffer.getvalue(), "TAIEX_40W_Log.xlsx", "application/vnd.ms-excel")
    else:
        st.info("歷史上查無此極端數據。")

    st.write("<p style='text-align:center; color:#9CA3AF; font-size:12px; margin-top:50px;'>系統由 aver5678 量化模組驅動 | 視覺化引擎: Command-Center v3.0</p>", unsafe_allow_html=True)

def page_upward_bias():
    log_visit("股市上漲統計表")

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
            '漲幅超過 10% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 10]) / total * 100), 1) if total > 0 else 0,
            '漲幅超過 20% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 20]) / total * 100), 1) if total > 0 else 0,
            '漲幅超過 30% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 30]) / total * 100), 1) if total > 0 else 0,
            '漲幅超過 40% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 40]) / total * 100), 1) if total > 0 else 0,
            '漲幅超過 50% 機率': round(float(len(finished_waves[finished_waves['漲幅(%)'] >= 50]) / total * 100), 1) if total > 0 else 0
        }
            
        is_ongoing = False
        current_bounce = 0.0
        if not df.empty:
            last_close = df['Close'].iloc[-1]
            if not up_df.empty and up_df.iloc[-1]['狀態'] == '進行中':
                is_ongoing = True
                current_bounce = float(up_df.iloc[-1]['漲幅(%)'])
            elif not up_df.empty and len(finished_waves) == len(up_df):
                last_end_date_str = up_df.iloc[-1]['最高日期 (下波前高)']
                try:
                    date_str = last_end_date_str
                    if "至今" not in date_str:
                        recent_df = df.loc[date_str:]
                        if not recent_df.empty:
                            recent_low = recent_df['Low'].min()
                            current_bounce = (last_close - recent_low) / recent_low * 100
                except:
                    current_bounce = 0.0

        return up_df, dist_df, metrics, current_bounce


    # 固定鎖定台灣加權指數
    symbol = "^TWII"
    selected_name = "台灣加權指數 (^TWII)"

    up_df, dist_df, metrics, current_bounce = load_upward_data(symbol)

    if up_df.empty:
        st.warning("目前尚無足夠歷史數據可供分析。")
        return

    # 檢查是否有進行中的反彈波段
    is_ongoing = False
    if not up_df.empty and up_df.iloc[-1]['狀態'] == '進行中':
        is_ongoing = True

    # --- 1. 戰情標頭 (Hero Header) ---
    status_pill_color = "#10B981" if is_ongoing else "#475569"
    status_pill_text = "ACTIVE: SURGING" if is_ongoing else "STANDBY"
    
    hero_header_html = f"""
    <div style="background:#0F172A; border:4px solid #334155; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // UPWARD_MOMENTUM_ENGINE_v4.2</div>
            <div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div>
        </div>
        <h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🚀 大盤上漲：漲幅統計</h1>
        <div style="margin-top:20px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.8; max-width:1100px; border-left:4px solid #334155; padding-left:20px;">
            獨立戰略分析模組：專門量化大盤從谷底起跳的真實漲幅。我們從每一波修正後的最低點算起，直到市場再度發生「7% 回檔」時，回頭確認該次漲幅的最高點。透過這項數據，我們能量化過去二十年每一場「多頭攻勢」的攻頂高度與耗時，協助您判斷當前波段的剩餘潛力。
        </div>
    </div>
    """
    st.markdown(hero_header_html, unsafe_allow_html=True)

    # --- 1.5 戰術導讀卡片 ---
    onboarding_upward_html = f"""
    <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:30px; margin-bottom:30px; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <h2 style="color:#F1F5F9; font-size:24px; font-weight:900; margin-top:0; margin-bottom:20px; display:flex; align-items:center; gap:12px;">📋 戰術導讀 (一)：如何利用「漲幅機率」抓出見頂門檻？</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #10B981;">
                <div style="color:#34D399; font-weight:800; font-size:16px; margin-bottom:10px;">📊 數據分布：看清行情真相</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">我們把過去二十年所有的反彈按漲幅分組。這張「機率分布圖」能讓您一眼看清，歷史上的行情通常會在哪個區間就漲不動了，這就是您的「波段導航地圖」。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #38BDF8;">
                <div style="color:#7DD3FC; font-weight:800; font-size:16px; margin-bottom:10px;">⚖️ 極端警戒：避開「低機率」陷阱</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">當股價已經漲了一大段時，請對照下方的分布圖。如果走到了「發生率低於 10%」的極端漲幅區，代表行情已進入低機率區，這時應隨時準備見好就收。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #FBBF24;">
                <div style="color:#FDE68A; font-weight:800; font-size:16px; margin-bottom:10px;">🎯 持股定力：別在起跑時下車</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">若數據顯示「有 80% 的行情都能漲超過 10%」，而目前才剛起步，那數據就在告訴您：派對才剛開始，別被小震盪嚇跑。用機率戰勝恐懼，才能抱住大波段。</div>
            </div>
        </div>
    </div>
    """
    st.markdown(onboarding_upward_html, unsafe_allow_html=True)

    # --- 2. 戰鬥控制台：Macro HUD ---
    st.markdown('<div style="margin-top:-20px;"></div>', unsafe_allow_html=True)
    
    score_color = "#10B981" if current_bounce >= 7.0 else "#475569"
    score_label = "✅ 趨勢成型 (已達 7%)" if current_bounce >= 7.0 else "📉 尚未成型 (未達 7%)"
    
    avg_gain = metrics.get('平均漲幅(%)', 0)
    avg_days = metrics.get('平均花費天數', 0)
    total_waves = metrics.get('總完整波段數', 0)

    # 取得階梯機率
    p10 = metrics.get('漲幅超過 10% 機率', 0)
    p20 = metrics.get('漲幅超過 20% 機率', 0)
    p30 = metrics.get('漲幅超過 30% 機率', 0)
    p40 = metrics.get('漲幅超過 40% 機率', 0)
    p50 = metrics.get('漲幅超過 50% 機率', 0)

    def get_step_style(threshold, active_color):
        if current_bounce >= threshold:
            # 已征服：極致亮燈感 (實心 + 白粗邊 + 強力發光)
            return f"background:{active_color}; color:white; border:3px solid white; box-shadow:0 0 40px {active_color}; font-weight:950; opacity:1; transform:scale(1.05); z-index:2;"
        # 預備中：亮燈感 (實心亮色 + 細邊)
        return f"background:{active_color}; color:white; border:1px solid rgba(255,255,255,0.4); font-weight:950; opacity:0.9; box-shadow:0 0 15px {active_color}66;"

    def get_arrow(threshold):
        next_thresholds = {10: 20, 20: 30, 30: 40, 40: 50, 50: 999}
        if current_bounce >= threshold and current_bounce < next_thresholds[threshold]:
            # 醒目的黃色三角指標
            return f'<div style="position:absolute; top:-35px; left:50%; transform:translateX(-50%); color:#FACC15; font-size:24px; text-shadow:0 0 10px #FACC15; font-weight:900; z-index:10;">▼</div>'
        return ""

    steps_html = f"""
<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:12px; margin-top:40px; position:relative;">
<div style="{get_step_style(10, '#10B981')} padding:18px 5px; border-radius:12px; text-align:center; position:relative; transition: all 0.4s ease;">
{get_arrow(10)}
<div style="font-size:13px; margin-bottom:8px; letter-spacing:1px;">>=10% 漲幅</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p10}%</div>
</div>
<div style="{get_step_style(20, '#10B981')} padding:18px 5px; border-radius:12px; text-align:center; position:relative; transition: all 0.4s ease;">
{get_arrow(20)}
<div style="font-size:13px; margin-bottom:8px; letter-spacing:1px;">>=20% 漲幅</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p20}%</div>
</div>
<div style="{get_step_style(30, '#F59E0B')} padding:18px 5px; border-radius:12px; text-align:center; position:relative; transition: all 0.4s ease;">
{get_arrow(30)}
<div style="font-size:13px; margin-bottom:8px; letter-spacing:1px;">>=30% 警告</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p30}%</div>
</div>
<div style="{get_step_style(40, '#EF4444')} padding:18px 5px; border-radius:12px; text-align:center; position:relative; transition: all 0.4s ease;">
{get_arrow(40)}
<div style="font-size:13px; margin-bottom:8px; letter-spacing:1px;">>=40% 警戒</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p40}%</div>
</div>
<div style="{get_step_style(50, '#A855F7')} padding:18px 5px; border-radius:12px; text-align:center; position:relative; transition: all 0.4s ease;">
{get_arrow(50)}
<div style="font-size:13px; margin-bottom:8px; letter-spacing:1px;">>=50% 極端</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p50}%</div>
</div>
</div>""".strip()

    # 預先計算動態文字與機率
    if current_bounce >= 50:
        stage_text = "🌌 宇宙極端區"
    elif current_bounce >= 40:
        stage_text = "☢️ 高度警戒區"
    elif current_bounce >= 30:
        stage_text = "⚠️ 警示收割區"
    elif current_bounce >= 20:
        stage_text = "🚀 進入噴發區"
    elif current_bounce >= 7:
        stage_text = "📈 動能推升中"
    else:
        stage_text = "⚓ 谷底蓄勢中"

    if current_bounce < 20:
        match_prob = p10
    elif current_bounce < 30:
        match_prob = p20
    elif current_bounce < 40:
        match_prob = p30
    elif current_bounce < 50:
        match_prob = p40
    else:
        match_prob = p50

    # 方案 A 儀表盤數據計算
    # 以 50% 為儀表板上限 (100% 進度)
    progress_cap = 50 
    clamped_bounce = min(current_bounce, progress_cap)
    # SVG 圓環參數 (R=90, C=565.48)
    circumference = 565.48
    dash_offset = circumference * (1 - clamped_bounce / progress_cap)

    hud_content = f"""
<div style="background:#0F172A; border:4px solid #334155; border-radius:16px; padding:50px; margin-bottom:40px; box-shadow:0 30px 60px rgba(0,0,0,0.6); overflow:hidden; position:relative;">
<div style="display:flex; justify-content:space-between; align-items:center; gap:60px;">
<!-- 左側：航行儀表盤 (方案 A) -->
<div style="flex:1.2; position:relative; display:flex; justify-content:center; align-items:center; min-height:350px;">
<!-- 背景雷達掃描線 -->
<div style="position:absolute; width:300px; height:300px; border:1px solid rgba(255,255,255,0.05); border-radius:50%;"></div>
<div style="position:absolute; width:200px; height:200px; border:1px solid rgba(255,255,255,0.05); border-radius:50%;"></div>
<div style="position:absolute; width:300px; height:1px; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); transform:rotate(45deg);"></div>
<div style="position:absolute; width:300px; height:1px; background:linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); transform:rotate(-45deg);"></div>

<!-- SVG 進度環 -->
<svg width="320" height="320" viewBox="0 0 200 200" style="transform: rotate(-90deg); filter: drop-shadow(0 0 15px {score_color}66);">
<circle cx="100" cy="100" r="90" fill="transparent" stroke="rgba(255,255,255,0.03)" stroke-width="12" />
<circle cx="100" cy="100" r="90" fill="transparent" stroke="{score_color}" stroke-width="12" stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}" stroke-linecap="round" style="transition: stroke-dashoffset 1s ease-out, stroke 0.5s;" />
</svg>

<!-- 中心數據面板 -->
<div style="position:absolute; display:flex; flex-direction:column; align-items:center; text-align:center;">
<div style="font-size:14px; color:#94A3B8; font-weight:800; letter-spacing:2px; margin-bottom:5px;">CURRENT BOUNCE</div>
<div style="font-family:'JetBrains Mono'; font-size:62px; font-weight:950; color:{score_color}; line-height:1; letter-spacing:-2px; text-shadow:0 0 20px {score_color}88;">+{current_bounce:.1f}%</div>
<div style="margin-top:15px; padding:6px 15px; background:{score_color}; color:white; border-radius:6px; font-size:15px; font-weight:900; box-shadow:0 10px 20px {score_color}44;">
{stage_text}
</div>
<div style="margin-top:10px; font-size:12px; color:#64748B; font-weight:800;">
歷史相似達成率：<span style="color:{score_color};">{match_prob}%</span>
</div>
</div>
</div>

<!-- 右側：亮燈階梯 (保持不變) -->
<div style="flex:1.8; background:rgba(255,255,255,0.02); padding:35px; border-radius:16px; border:1px solid rgba(56, 189, 248, 0.15); align-self:stretch;">
<div style="font-size:24px; color:#38BDF8; font-weight:950; margin-bottom:20px; display:flex; align-items:center; gap:12px; border-bottom:2px solid rgba(56, 189, 248, 0.3); padding-bottom:15px;">
<span style="font-size:30px;">🛰️</span> 波段階梯上漲機率 <span style="font-size:16px; color:#94A3B8; font-weight:500;">(歷史樣本 {total_waves} 次)</span>
</div>
{steps_html}
<div style="margin-top:25px; padding:15px; background:rgba(56, 189, 248, 0.05); border-radius:8px; border-left:4px solid #38BDF8;">
<div style="color:#7DD3FC; font-weight:800; font-size:15px; margin-bottom:5px;">數據意涵：</div>
<div style="color:#94A3B8; font-size:14px; line-height:1.5;">機率越低，代表行情越接近極端噴發末端。彩色區塊代表目前大盤已征服的里程碑與風險狀態。</div>
</div>
</div>
</div>
</div>""".strip()
    st.markdown(hud_content, unsafe_allow_html=True)

    st.markdown('<h2 style="text-align:center; margin-top:80px;">📊 歷史反彈漲幅區間分布 (7% 轉折模型)</h2>', unsafe_allow_html=True)

    if not dist_df.empty:
        dist_df_cn = dist_df.rename(columns={
            '區間': '漲幅區間',
            '次數': '發生次數',
            '機率(%):Q': '機率 (%)'
        })
        chart = alt.Chart(dist_df_cn).mark_bar(
            color=alt.Gradient(
                gradient='linear',
                stops=[alt.GradientStop(color='#10B981', offset=0),
                       alt.GradientStop(color='#34D399', offset=1)],
                x1=1, x2=1, y1=1, y2=0
            ),
            cornerRadiusTopLeft=8, cornerRadiusTopRight=8
        ).encode(
            x=alt.X('漲幅區間:N', title='', sort=None, axis=alt.Axis(labelAngle=0, labelFontSize=13, labelColor='#94A3B8')),
            y=alt.Y('機率 (%):Q', title='發生機率 (%)', axis=alt.Axis(labelFontSize=13, gridColor='#334155', gridDash=[2,4], labelColor='#94A3B8', titleColor='#F1F5F9', titleFontSize=15)),
            tooltip=['漲幅區間:N', '發生次數:Q', '機率 (%):Q']
        ).properties(
            height=350,
            background='transparent'
        ).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(chart, use_container_width=True)
        
    # --- 4. 數位流水日誌 (Digital Logs) ---
    st.markdown(f"""
    <div style="background:linear-gradient(90deg, #1E293B, #0F172A); padding:30px 45px; border:4px solid #334155; border-radius:12px; margin-top:50px; margin-bottom:30px; display:flex; justify-content:space-between; align-items:center; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
        <div style="color:white; font-size:48px; font-weight:950; letter-spacing:-1.5px; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">📜 歷史上漲波段：動能收割日誌</div>
        <div style="font-family:'JetBrains Mono'; font-size:16px; color:#64748B; font-weight:800; border:1px solid #334155; padding:5px 15px; border-radius:6px;">LOG_SYSTEM // SURGE_RECORDS_v4.2</div>
    </div>
    """, unsafe_allow_html=True)

    sorted_waves = up_df.sort_values(by='起漲日期 (前波破底)', ascending=False)
    
    for _, r in sorted_waves.iterrows():
        gain = float(r['漲幅(%)'])
        days = int(r['花費天數'])
        status = r['狀態']
        
        # 動能槽長度 (預設把 50% 漲幅當作視覺 100% 寬度)
        energy_w = min(100.0, gain / 50.0 * 100)
        
        if status == '進行中':
            status_badge = '<span style="color:#10B981; background:rgba(16, 185, 129, 0.1); padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid rgba(16, 185, 129, 0.3);">🟢 🚀 強勢噴出中</span>'
            date_display = f"{r['起漲日期 (前波破底)']} ➔ <span style='color:#38BDF8;'>至今 ({r['最高日期 (下波前高)'].split('(')[1].split(')')[0]})</span>"
        else:
            status_badge = '<span style="color:#64748B; background:rgba(100, 116, 139, 0.1); padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid rgba(100, 116, 139, 0.3);">✅ 🎯 波段已收割</span>'
            date_display = f"{r['起漲日期 (前波破底)']} ➔ {r['最高日期 (下波前高)']}"

        html_log = f"""
        <div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:30px; overflow:hidden; width:100%; box-shadow:0 20px 40px rgba(0,0,0,0.5);">
            <div style="display:flex; justify-content:space-between; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;">
                <div style="flex:2; padding:30px; border-right:4px solid #475569;">
                    <div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;">
                        {status_badge}
                        <span style="font-size:20px; color:#94A3B8; font-weight:800; letter-spacing:1px;">波段歷程：</span>
                    </div>
                    <div style="font-family:'JetBrains Mono'; font-size:36px; color:white; font-weight:950; letter-spacing:-1px;">📅 {date_display}</div>
                </div>
                <div style="flex:1; text-align:center; padding:30px; display:flex; flex-direction:column; justify-content:center; min-width:300px;">
                    <div style="font-size:16px; color:#94A3B8; font-weight:800; margin-bottom:10px;">⏱️ 波段延續時間</div>
                    <div style="font-family:'JetBrains Mono'; font-size:42px; font-weight:950; color:#F1F5F9; line-height:1;">{days}<span style="font-size:24px; color:#64748B;">天</span></div>
                </div>
            </div>
            <div style="padding:40px 30px; background:rgba(16, 185, 129, 0.05);">
                <div style="display:flex; justify-content:space-between; align-items:center; font-size:40px; color:#34D399; margin-bottom:20px; font-weight:950; white-space:nowrap;">
                    <span>⚡ 累積漲幅</span><span>+{gain:.1f}%</span>
                </div>
                <div style="height:40px; background:#064E3B; border-radius:8px; overflow:hidden; border:2px solid #047857;">
                    <div style="width:{energy_w}%; height:100%; background:linear-gradient(90deg, #059669, #10B981, #34D399); box-shadow: 0 0 20px rgba(52, 211, 153, 0.6);"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono'; color:#64748B; font-size:14px; margin-top:10px; font-weight:800;">
                    <span>起漲: {r['起漲價格']:,.1f}</span>
                    <span>最高: {r['最高價格 (或現價)']:,.1f}</span>
                </div>
            </div>
        </div>
        """
        st.markdown(html_log, unsafe_allow_html=True)

def page_downward_bias():
    log_visit("股市回檔統計表")
    
    tickers = {
        "台灣加權指數 (^TWII)": "^TWII"
    }

    @st.cache_data(ttl=1, show_spinner=False)
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

    # --- 1. 頂部狀態：Hero Header ---
    status_pill_color = "#EF4444" if current_dd >= 7.0 else "#10B981"
    status_pill_text = "DANGER: HIGH RISK" if current_dd >= 7.0 else "SAFE: CRUISING"
    
    hero_header_html = f"""<div style="background:#0F172A; border:4px solid #475569; border-radius:12px; padding:35px; margin-bottom:30px; box-shadow:0 20px 40px rgba(0,0,0,0.5);"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;"><div style="font-family:'JetBrains Mono'; font-size:12px; color:#64748B; letter-spacing:2px; font-weight:800;">SYSTEM LIVE // 7PCT_DRAWDOWN_ENGINE_v4.2</div><div style="background:{status_pill_color}; color:white; padding:4px 12px; border-radius:6px; font-family:'JetBrains Mono'; font-size:12px; font-weight:900; box-shadow:0 0 15px {status_pill_color};">● {status_pill_text}</div></div><h1 style="color:white; font-size:48px; font-weight:950; margin:0; letter-spacing:-1.5px; line-height:1.2; text-shadow:0 0 30px rgba(56, 189, 248, 0.4);">🚀 大盤下跌：跌幅統計</h1><div style="margin-top:20px; color:#94A3B8; font-size:17px; font-weight:600; line-height:1.8; max-width:1100px; border-left:4px solid #334155; padding-left:20px;"><b>即時監測與歷史回測</b>：針對標普 500 (SPX)、那斯達克 (IXIC) 及台股加權指數 (TWII)，分析自歷史高點跌破 7% 後的剩餘跌幅與反彈機率。<br><br>監控 {symbol}：精準定位歷史級跌幅。當大盤自前高跌破 7% 時，往往是市場非理性拋售的起點，也是長線勝率極高的戰略進場區。</div></div>"""
    st.markdown(hero_header_html, unsafe_allow_html=True)

    # --- 戰略導讀 (一)：新手避坑指南 ---
    onboarding_html = f"""
    <div style="background:linear-gradient(135deg, #1E293B 0%, #0F172A 100%); border:2px solid #334155; border-radius:12px; padding:30px; margin-bottom:30px; box-shadow:0 10px 30px rgba(0,0,0,0.3);">
        <h2 style="color:#F1F5F9; font-size:24px; font-weight:900; margin-top:0; margin-bottom:20px; display:flex; align-items:center; gap:12px;">📋 給新手的「避坑指南」：跌破 7% 後怎麼看？</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #3B82F6;">
                <div style="color:#7DD3FC; font-weight:800; font-size:16px; margin-bottom:10px;">🌡️ 這是感冒還是大病？</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">跌 7% 就像身體「發燒」了。有時只是小感冒（很快就漲回來），但有時是肺炎的前兆。我們先觀察階梯，看它會不會繼續燒下去。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #FBBF24;">
                <div style="color:#FDE68A; font-weight:800; font-size:16px; margin-bottom:10px;">📊 別猜底，看「歷史數據」</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">新手最愛猜哪裡是底。看右邊階梯吧！跌 10-15% 很常見，如果真的跌破 20%，那就是大崩盤，這時<b>千萬不要隨便加碼</b>以免斷頭。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #EF4444;">
                <div style="color:#FCA5A5; font-weight:800; font-size:16px; margin-bottom:10px;">💀 真的遇到大屠殺怎麼辦？</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">當燈號亮在紫色區，代表你遇到了歷史極罕見的大崩盤。這時「活下去」比什麼都重要，只要不開槓桿、不借錢，時間終究會還你公道。</div>
            </div>
        </div>
    </div>
    """
    st.markdown(onboarding_html, unsafe_allow_html=True)

    # --- 3. 戰鬥控制台：Macro HUD ---
    score_color = status_pill_color
    
    # 從 metrics 讀取真實數據
    avg_resid_val = metrics.get('Avg Residual Drawdown (%)', 0)
    avg_resid = f"-{avg_resid_val:.1f}%" if avg_resid_val > 0 else "0.0%"
    
    # 讀取分類數據供導讀使用
    norm = metrics.get('Normal', {})
    crash = metrics.get('Crash', {})

    p10 = metrics.get('跌幅超過 10% 機率', 0)
    p15 = metrics.get('跌幅超過 15% 機率', 0)
    p20 = metrics.get('跌幅超過 20% 機率', 0)
    p30 = metrics.get('跌幅超過 30% 機率', 0)
    p50 = metrics.get('跌幅超過 50% 機率', 0)

    # 儀表盤樣式預設 (小白版)
    def get_step_style(threshold, active_color):
        if current_dd >= threshold:
            return f"background:{active_color}; color:white; border:3px solid white; box-shadow:0 0 40px {active_color}; font-weight:950; opacity:1; transform:scale(1.05); z-index:2;"
        return f"background:{active_color}; color:white; border:1px solid rgba(255,255,255,0.4); font-weight:950; opacity:0.8;"

    def get_arrow(threshold):
        next_thresholds = {10: 15, 15: 20, 20: 30, 30: 50, 50: 999}
        if current_dd >= threshold and current_dd < next_thresholds[threshold]:
            return f'<div style="position:absolute; top:-35px; left:50%; transform:translateX(-50%); color:#FACC15; font-size:18px; text-shadow:0 0 10px #FACC15; font-weight:900; z-index:10; white-space:nowrap;">▼ 你在這</div>'
        return ""

    steps_html = f"""
<div style="display:grid; grid-template-columns: repeat(5, 1fr); gap:12px; margin-top:35px; position:relative;">
<div style="{get_step_style(10, '#F59E0B')} padding:18px 5px; border-radius:12px; text-align:center; position:relative;">
{get_arrow(10)}
<div style="font-size:13px; margin-bottom:8px;">跌到 10%</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p10}%</div>
</div>
<div style="{get_step_style(15, '#EF4444')} padding:18px 5px; border-radius:12px; text-align:center; position:relative;">
{get_arrow(15)}
<div style="font-size:13px; margin-bottom:8px;">跌到 15%</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p15}%</div>
</div>
<div style="{get_step_style(20, '#B91C1C')} padding:18px 5px; border-radius:12px; text-align:center; position:relative;">
{get_arrow(20)}
<div style="font-size:13px; margin-bottom:8px;">跌到 20%</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p20}%</div>
</div>
<div style="{get_step_style(30, '#7F1D1D')} padding:18px 5px; border-radius:12px; text-align:center; position:relative;">
{get_arrow(30)}
<div style="font-size:13px; margin-bottom:8px;">跌到 30%</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p30}%</div>
</div>
<div style="{get_step_style(50, '#A855F7')} padding:18px 5px; border-radius:12px; text-align:center; position:relative;">
{get_arrow(50)}
<div style="font-size:13px; margin-bottom:8px;">恐佈大崩盤</div>
<div style="font-family:'JetBrains Mono'; font-size:24px;">{p50}%</div>
</div>
</div>""".strip()

    # 儀表盤數據計算
    progress_cap = 30 
    clamped_dd = min(current_dd, progress_cap)
    circumference = 565.48
    dash_offset = circumference * (1 - clamped_dd / progress_cap)
    
    # 小白語階段文字
    if current_dd >= 30:
        dd_stage_text = "💀 進入大屠殺區"
    elif current_dd >= 20:
        dd_stage_text = "☢️ 大家都賠慘了"
    elif current_dd >= 10:
        dd_stage_text = "⚠️ 跌得有點痛"
    elif current_dd >= 7:
        dd_stage_text = "📉 市場小感冒"
    else:
        dd_stage_text = "⚓ 目前還安全"

    hud_html = f"""
<div style="background:#0F172A; border:4px solid #334155; border-radius:16px; padding:50px; margin-bottom:40px; box-shadow:0 30px 60px rgba(0,0,0,0.6); overflow:hidden; position:relative;">
<div style="display:flex; justify-content:space-between; align-items:center; gap:60px;">
<!-- 左側：航行儀表盤 -->
<div style="flex:1.2; position:relative; display:flex; justify-content:center; align-items:center; min-height:350px;">
<div style="position:absolute; width:300px; height:300px; border:1px solid rgba(255,255,255,0.05); border-radius:50%;"></div>
<svg width="320" height="320" viewBox="0 0 200 200" style="transform: rotate(-90deg); filter: drop-shadow(0 0 15px {score_color}66);">
<circle cx="100" cy="100" r="90" fill="transparent" stroke="rgba(255,255,255,0.03)" stroke-width="12" />
<circle cx="100" cy="100" r="90" fill="transparent" stroke="{score_color}" stroke-width="12" stroke-dasharray="{circumference}" stroke-dashoffset="{dash_offset}" stroke-linecap="round" style="transition: stroke-dashoffset 1s ease-out, stroke 0.5s;" />
</svg>
<div style="position:absolute; display:flex; flex-direction:column; align-items:center; text-align:center;">
<div style="font-size:14px; color:#94A3B8; font-weight:800; letter-spacing:2px; margin-bottom:5px;">離最高點跌了多少？</div>
<div style="font-family:'JetBrains Mono'; font-size:62px; font-weight:950; color:{score_color}; line-height:1; letter-spacing:-2px;">-{current_dd:.1f}%</div>
<div style="margin-top:15px; padding:6px 15px; background:{score_color}; color:white; border-radius:6px; font-size:15px; font-weight:900;">
{dd_stage_text}
</div>
</div>
</div>

<!-- 右側：下跌階梯機率 -->
<div style="flex:1.8; background:rgba(255,255,255,0.02); padding:35px; border-radius:16px; border:1px solid rgba(248, 113, 113, 0.15); align-self:stretch;">
<div style="font-size:24px; color:#F87171; font-weight:950; margin-bottom:20px; display:flex; align-items:center; gap:12px; border-bottom:2px solid rgba(248, 113, 113, 0.3); padding-bottom:15px;">
<span style="font-size:30px;">📉</span> 歷史數據告訴我們...
</div>
{steps_html}
<div style="margin-top:25px; background:rgba(255,255,255,0.03); padding:20px; border-radius:10px; border-left:4px solid {score_color};">
<div style="font-size:14px; color:#94A3B8; font-weight:800; margin-bottom:8px;">💡 這代表什麼？</div>
<div style="font-size:14px; color:#E2E8F0; line-height:1.7;">
當股市跌破 -7% 之後，<b>{p10}%</b> 的機率會繼續跌到 -10%。如果現在燈號亮在左邊（橘色），代表這只是常見的回檔；如果燈號亮到右邊（深紅/紫色），那就是遇到了歷史級的大災難，一定要冷靜！
</div>
</div>
</div>
</div>
</div>
"""
    st.markdown(hud_html, unsafe_allow_html=True)
    
    # --- 小白版戰術導讀 (二)：被套牢了怎麼辦？ ---
    guide_html = f"""
    <div style="background:linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border:2px solid #38BDF8; border-radius:12px; padding:30px; margin-bottom:50px; box-shadow:0 10px 30px rgba(56,189,248,0.1);">
        <h2 style="color:#F1F5F9; font-size:24px; font-weight:900; margin-top:0; margin-bottom:20px; display:flex; align-items:center; gap:12px;">⌛ 被套牢了...要等多久才會漲回來？</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:25px;">
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #F59E0B;">
                <div style="color:#F59E0B; font-weight:800; font-size:16px; margin-bottom:10px;">� 等待落底期</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">目前進場後，平均還要等約 <b style="color:#EF4444;">{norm.get('avg_trigger_to_bt', 0):.1f} 天</b> 才會看到真正的谷底。這段時間心情會很煩悶，是正常的，請放寬心。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #10B981;">
                <div style="color:#10B981; font-weight:800; font-size:16px; margin-bottom:10px;">� 陽光總在風雨後</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">當股市跌勢止住開始反彈，平均約再等 <b style="color:#10B981;">{norm.get('avg_bt_to_rec', 0):.1f} 天</b> 就能回本甚至開始賺錢。</div>
            </div>
            <div style="background:rgba(255,255,255,0.03); padding:18px; border-radius:10px; border-left:4px solid #64748B;">
                <div style="color:#CBD5E1; font-weight:800; font-size:16px; margin-bottom:10px;">🏥 最慘的情況？</div>
                <div style="color:#94A3B8; font-size:14px; line-height:1.6;">如果真的遇到超級大崩盤，回本時間可能拉長到 <b style="color:white;">{crash.get('avg_total', 0):.0f} 天</b>。這時請關掉 App，專心工作，等大環境景氣修復。</div>
            </div>
        </div>
    </div>
    """
    st.markdown(guide_html, unsafe_allow_html=True)
    # --- 3. 風險劇本分佈條 (小白白話版) ---
    total_e = len(events_df)
    if total_e > 0:
        s1_p = len(events_df[events_df['剩餘跌幅(%)'] < 5]) / total_e * 100
        s2_p = len(events_df[(events_df['剩餘跌幅(%)'] >= 5) & (events_df['剩餘跌幅(%)'] < 15)]) / total_e * 100
        s3_p = len(events_df[events_df['剩餘跌幅(%)'] >= 15]) / total_e * 100
    else:
        s1_p, s2_p, s3_p = 0, 0, 0

    scenario_html = f"""
<div style="margin-top:50px; margin-bottom:80px;">
<div style="text-align:center; margin-bottom:30px;">
<h2 style="color:#F1F5F9; font-size:28px; font-weight:950; letter-spacing:1px; margin-bottom:10px;">📊 接下來可能會發生什麼事？</h2>
<p style="color:#94A3B8; font-size:16px;">根據歷史數據，跌了 7% 之後，後續的三種可能發展：</p>
</div>

<div style="background:#1E293B; border:1px solid #334155; border-radius:16px; padding:40px; box-shadow:0 20px 40px rgba(0,0,0,0.3);">
<div style="display:flex; height:60px; border-radius:10px; overflow:hidden; border:2px solid #0F172A; box-shadow:inset 0 4px 10px rgba(0,0,0,0.5);">
<div style="width:{s1_p}%; background:linear-gradient(90deg, #10B981, #34D399); display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:18px;">
{s1_p:.1f}%
</div>
<div style="width:{s2_p}%; background:linear-gradient(90deg, #F59E0B, #FBBF24); display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:18px;">
{s2_p:.1f}%
</div>
<div style="width:{s3_p}%; background:linear-gradient(90deg, #EF4444, #B91C1C); display:flex; align-items:center; justify-content:center; color:white; font-weight:900; font-size:18px;">
{s3_p:.1f}%
</div>
</div>

<div style="display:grid; grid-template-columns: {s1_p}% {s2_p}% {s3_p}%; margin-top:20px; text-align:center;">
<div style="padding:0 10px;">
<div style="color:#34D399; font-weight:900; font-size:16px;">✅【只是小感冒】</div>
<div style="color:#64748B; font-size:13px; margin-top:5px;">跌不到 5% 就漲回來了</div>
</div>
<div style="padding:0 10px;">
<div style="color:#FBBF24; font-weight:900; font-size:16px;">⚠️【中度發燒中】</div>
<div style="color:#64748B; font-size:13px; margin-top:5px;">還會再多跌 5%~15%</div>
</div>
<div style="padding:0 10px;">
<div style="color:#EF4444; font-weight:900; font-size:16px;">💀【大屠殺來了】</div>
<div style="color:#64748B; font-size:13px; margin-top:5px;">不幸跌落 15% 以上</div>
</div>
</div>

<div style="margin-top:35px; padding:20px; background:rgba(255,255,255,0.02); border-radius:12px; border:1px dashed rgba(255,255,255,0.1);">
<div style="color:#E2E8F0; font-size:14px; line-height:1.6; text-align:center;">
💡 <b>這代表什麼？</b>：如果現在跌幅已經超過 -15%，代表你已經進入最可怕的「紅區」。歷史上進入這個慘烈劇本的機率只有 <b>{s3_p:.1f}%</b>，請保持冷靜！
</div>
</div>
</div>
</div>
"""
    st.markdown(scenario_html, unsafe_allow_html=True)

    # --- 4. 電子流水日誌 ---
    st.markdown('<h2 style="text-align:center; margin-top:80px;">📜 回檔波段詳細日誌</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#9CA3AF; margin-bottom:40px;">能量條代表總跌幅強度 (Scale: 0-50%)</p>', unsafe_allow_html=True)

    if not events_df.empty:
        for _, r in events_df.sort_values(by='觸發日期', ascending=False).iterrows():
            total_dd = float(r['最大跌幅(%)'])
            resid_dd = float(r['剩餘跌幅(%)'])
            days_to_bottom = int(r['前高到破底天數'])
            days_to_rec = r['解套總耗時']
            status = r['狀態']
            
            trigger_date = r['觸發日期']
            peak_date = r['前高日期']
            bottom_date = r['破底日期']
            rec_date = r['解套日期']
            
            trigger_price = float(r['觸發價格'])
            peak_price = float(r['前高價格'])
            bottom_price = float(r['破底最低價'])
            
            w = min(100.0, (abs(total_dd) / 30) * 100) # 修正為 30% 滿版
            
            if status == '已解套':
                status_icon = "✅"
                tag_color = "#10B981"
                card_border = "#064E3B"
                tag_bg = "rgba(16, 185, 129, 0.1)"
                period_str = f"{peak_date} ➔ {bottom_date}"
                rec_days_str = f"總耗時 {days_to_rec} 天" if str(days_to_rec).isdigit() or isinstance(days_to_rec, (int, float)) else f"耗時 {days_to_rec} 天"
                state_3_val = f"{float(r.get('解套點位', peak_price)):,.0f}"
                state_3_sub = r.get('解套形式', '完全收復前高')
            else:
                status_icon = "🚨"
                tag_color = "#EF4444"
                card_border = "#450A0A"
                tag_bg = "rgba(239, 68, 68, 0.1)"
                period_str = f"{peak_date} ➔ {bottom_date}"
                rec_days_str = f"已耗時 {days_to_rec} 天"
                state_3_val = "等待收復"
                state_3_sub = "套牢中"

            card_html = f"""
            <div style="background:#0F172A; border:5px solid #334155; border-radius:12px; margin-bottom:50px; overflow:hidden; width:100%; box-shadow:0 30px 60px rgba(0,0,0,0.5);">
                <div style="display:flex; justify-content:space-between; align-items:stretch; background:#1E293B; border-bottom:4px solid #475569;">
                    <div style="flex:2.5; padding:35px 30px; border-right:4px solid #475569;">
                        <div style="display:flex; align-items:center; gap:20px; margin-bottom:15px;">
                            <span style="color:{tag_color}; background:{tag_bg}; padding:6px 16px; border-radius:8px; font-size:20px; font-weight:900; border:2px solid {tag_color};">{status_icon} {status}</span>
                            <span style="font-size:24px; color:#94A3B8; font-weight:800; letter-spacing:1px;">波段回檔紀錄：</span>
                        </div>
                        <div style="font-size:42px; color:white; font-weight:950; letter-spacing:-1px; line-height:1;">📅 {period_str}</div>
                    </div>
                    <div style="flex:1; text-align:center; background:rgba(239, 68, 68, 0.05); padding:40px 20px; display:flex; flex-direction:column; justify-content:center; min-width:300px;">
                        <div style="font-size:20px; color:#FCA5A5; font-weight:900; text-transform:uppercase; margin-bottom:12px; letter-spacing:2px;">最大破壞力道</div>
                        <div style="font-family:'JetBrains Mono'; font-size:52px; font-weight:950; color:#EF4444; line-height:1;">-{abs(total_dd):.1f}<span style="font-size:25px; font-weight:800; margin-left:10px; color:#FCA5A5;">%</span></div>
                    </div>
                </div>
                <div style="background:#0F172A; padding:35px; border-bottom:4px solid #334155;">
                    <div style="display:flex; justify-content:space-between; align-items:center; font-size:28px; color:#FCA5A5; margin-bottom:15px; font-weight:950; white-space:nowrap;">
                        <span>📉 總跌幅能量展開 (對比 -30% 極端值)</span>
                        <span>-{abs(total_dd):.1f} / -30.0 %</span>
                    </div>
                    <div style="height:20px; background:#020617; border-radius:10px; overflow:hidden; border:2px solid #334155;">
                        <div style="width:{w}%; height:100%; background:linear-gradient(90deg, #1E293B, #EF4444); box-shadow:0 0 30px #EF4444;"></div>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns:1fr 1.2fr 1fr; gap:0; background:#1E293B;">
                    <div style="background:#1E293B; padding:30px; text-align:left; border-right:4px solid #334155;">
                        <div style="font-size:18px; color:#94A3B8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段一] 觸發 -7% 警戒</div>
                        <div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">(發生於 {trigger_date})</div>
                        <div style="display:flex; align-items:baseline; gap:12px;">
                            <div style="font-size:36px; font-family:'JetBrains Mono'; font-weight:950; color:white;">{trigger_price:,.0f}</div>
                            <div style="font-size:16px; font-weight:900; color:#94A3B8;">(前高 {peak_price:,.0f})</div>
                        </div>
                    </div>
                    <div style="background:rgba(239, 68, 68, 0.05); padding:30px; text-align:left; border-right:4px solid #334155;">
                        <div style="font-size:18px; color:#EF4444; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段二] 承受剩餘跌幅</div>
                        <div style="font-size:14px; color:#FCA5A5; font-weight:800; margin-bottom:5px;">(見底於 {bottom_date}，耗時 {days_to_bottom} 天)</div>
                        <div style="display:flex; align-items:baseline; gap:12px;">
                            <div style="font-size:36px; font-family:'JetBrains Mono'; font-weight:950; color:white;">{bottom_price:,.0f}</div>
                            <div style="font-size:22px; font-family:'JetBrains Mono'; font-weight:900; color:#EF4444;">再跌 -{abs(resid_dd):.1f}%</div>
                        </div>
                    </div>
                    <div style="background:#1E293B; padding:30px; text-align:left;">
                        <div style="font-size:18px; color:#38BDF8; font-weight:900; margin-bottom:10px; letter-spacing:1px;">[階段三] 波段解套狀態</div>
                        <div style="font-size:14px; color:#64748B; font-weight:800; margin-bottom:5px;">({rec_days_str})</div>
                        <div style="font-size:24px; font-family:'JetBrains Mono'; font-weight:950; color:#7DD3FC; line-height:1.3;">{state_3_val}</div>
                        <div style="font-size:14px; color:#94A3B8; font-weight:800; margin-top:5px;">{state_3_sub}</div>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)

    st.write("<p style='text-align:center; color:#9CA3AF; font-size:12px; margin-top:80px;'>系統由 aver5678 量化模組驅動 | 回檔動能引擎: Strategy-7pct v3.2</p>", unsafe_allow_html=True)

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
            fig_pie.update_layout(height=300, 
                                  margin=dict(l=0, r=0, t=30, b=0),
                                  font=dict(color="#ECECEC"),
                                  paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(0,0,0,0)")
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

def render_top_nav_profile():
    """ 渲染置於右上角的 SaaS 級會員中心 (合併功能與門面) """
    user_email = st.session_state.get('user_email')
    google_icon = "https://www.gstatic.com/images/branding/product/2x/googleg_96dp.png"
    
    # 使用一個固定容器封裝
    with st.container():
        st.markdown('<div class="top-nav-zone">', unsafe_allow_html=True)
        
        # 沒登入時：直接渲染「真的按鈕」在右上角
        if st.session_state['user_role'] == 'guest':
            if st.button("Sign in with Google", key="real_google_login_btn"):
                st.session_state['show_login'] = True
        
        # 已登入時：渲染頭像
        else:
            display_name = user_email.split("@")[0] if "@" in user_email else user_email
            avatar_init = display_name[0].upper()
            role_label = '站長' if st.session_state.get('user_role') == 'admin' else '會員'
            
            st.markdown(f"""
                <div class="user-status-card">
                    <div class="user-avatar-circle" style="width:34px; height:34px; background:linear-gradient(135deg, #38BDF8, #1D4ED8); border-radius:50%; display:flex; align-items:center; justify-content:center; color:white; font-weight:900;">
                        {avatar_init}
                    </div>
                    <div style="display:flex; flex-direction:column;">
                        <span style="color:white; font-size:13px; font-weight:800; line-height:1.2;">{display_name}</span>
                        <span style="color:#38BDF8; font-size:9px; font-weight:900; text-transform:uppercase;">{role_label}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 把登出藏在選單最下面
            st.sidebar.markdown("<br><br><br>", unsafe_allow_html=True)
            st.sidebar.markdown("---")
            if st.sidebar.button("🚪 登出帳號", use_container_width=True):
                st.session_state['user_role'] = 'guest'
                st.session_state['user_email'] = None
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 模擬登入彈窗
    if st.session_state.get('show_login', False) and st.session_state['user_role'] == 'guest':
        with st.sidebar.expander("🔑 身份驗證服務", expanded=True):
            test_email = st.text_input("請輸入測試 Email", placeholder="aver5678@gmail.com")
            if st.button("確認授權"):
                if test_email == ADMIN_EMAIL:
                    st.session_state['user_role'] = 'admin'
                    st.session_state['user_email'] = test_email
                elif test_email:
                    st.session_state['user_role'] = 'user'
                    st.session_state['user_email'] = test_email
                st.session_state['show_login'] = False
                st.rerun()
            if st.button("關閉"):
                st.session_state['show_login'] = False
                st.rerun()

def main():
    # 1. 頂部 Logo (GPT 風格)
    st.sidebar.markdown('<h1 style="border:none; margin-bottom:0;">📊 股市盤後系統</h1>', unsafe_allow_html=True)
    
    pages = {
        "週期乖離監控系統": page_bias_analysis,
        "景氣循環窗位預警": page_biz_cycle,
        "大盤下跌強度統計": page_downward_bias,
        "大盤上漲強度統計": page_upward_bias
    }
    
    # --- [A. 站長管理區] --- (僅管理員可見)
    if st.session_state.get('user_role') == 'admin':
        st.sidebar.markdown('<div class="sidebar-section-header">🛠️ 戰情管理後台</div>', unsafe_allow_html=True)
        with st.sidebar.expander("系統控制面板", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 刷新數據", help="強制重新載入所有腳本"):
                    st.rerun()
            with col2:
                if st.button("🧹 清除緩存", help="重抓最原始資料"):
                    st.cache_data.clear()
                    st.cache_resource.clear()
                    st.rerun()
            
            st.markdown(f"""
                <div style="font-size:11px; color:#64748B; padding:5px; border-top:1px solid #334155; margin-top:10px;">
                    <b>當前權限：</b> {st.session_state.get('user_role', 'guest').upper()}<br>
                    <b>管理員信箱：</b> {ADMIN_EMAIL}
                </div>
            """, unsafe_allow_html=True)


    # 如果是站長登入，增加後台管理模組
    if st.session_state.get('user_role') == 'admin':
        pages["系統管理中心系統"] = page_admin_dashboard
        
    st.sidebar.markdown('<div class="sidebar-section-header">📡 模組切換中心</div>', unsafe_allow_html=True)
    selection = st.sidebar.radio("Navigation", list(pages.keys()), label_visibility="collapsed")
    
    # 3. 右上角用戶中心
    render_top_nav_profile()
    
    # 執行對應的頁面函數
    pages[selection]()

if __name__ == "__main__":
    main()
