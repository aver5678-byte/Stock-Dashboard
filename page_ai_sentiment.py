import streamlit as st
import feedparser
from textblob import TextBlob
import pandas as pd
import plotly.graph_objects as go
import datetime

# --- 定義 CSS 黑科技風格 UI ---
def apply_tech_ui():
    st.markdown("""
        <style>
        /* 整體背景與字體 */
        .stApp {
            background-color: #0f111a;
            color: #e0e6ed;
            font-family: 'Inter', 'Segoe UI', sans-serif;
        }
        
        /* 側邊欄改為暗藍色 */
        [data-testid="stSidebar"] {
            background-color: #1a1e29;
            border-right: 1px solid #2a3040;
        }
        
        /* 指標卡片 (Metric) 毛玻璃效果 */
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 700;
            color: #00ffcc !important;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
        }
        [data-testid="stMetric"] {
            background: rgba(30, 36, 51, 0.6);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }
        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border: 1px solid rgba(0, 255, 204, 0.2);
        }
        
        /* 漸層標題 */
        h1, h2, h3 {
            background: linear-gradient(90deg, #00ffcc 0%, #00aaff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
        }
        
        /* 按鈕美化 */
        .stButton>button {
            background: linear-gradient(90deg, #0055ff 0%, #00aaff 100%);
            border: none;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(0, 170, 255, 0.4);
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            box-shadow: 0 6px 20px rgba(0, 170, 255, 0.6);
            transform: translateY(-2px);
        }
        </style>
    """, unsafe_allow_html=True)

# --- 抓取新聞與情緒分析核心 ---
@st.cache_data(ttl=1800) # 每半小時更新一次
def fetch_and_analyze_news():
    # 這裡我們使用 Yahoo Finance 的 RSS 新聞來源作為示範
    url = "https://search.yahoo.com/mrss/s?p=stock+market" 
    feed = feedparser.parse(url)
    
    news_data = []
    total_polarity = 0
    total_subjectivity = 0
    valid_entries = 0
    
    for entry in feed.entries[:20]: # 抓取最新 20 則
        title = entry.title
        summary = entry.summary
        
        # 使用 TextBlob 進行非常基礎的英文 NLP 情緒分析
        # Polarity: -1 (極度負面) 到 1 (極度正面)
        blob = TextBlob(title + " " + summary)
        polarity = blob.sentiment.polarity
        
        # 轉換為百分比 (-1~1 -> 0~100) 以便於呈現
        sentiment_score = (polarity + 1) / 2 * 100 
        
        # 判斷標籤
        if polarity > 0.1:
            label = "🟢 樂觀 (Bullish)"
        elif polarity < -0.1:
            label = "🔴 悲觀 (Bearish)"
        else:
            label = "⚪ 中立 (Neutral)"
            
        news_data.append({
            "發布時間": entry.published if hasattr(entry, 'published') else "Just now",
            "新聞標題": title,
            "AI 情緒分數": round(sentiment_score, 1),
            "市場訊號": label
        })
        
        total_polarity += polarity
        valid_entries += 1
        
    avg_polarity = total_polarity / valid_entries if valid_entries > 0 else 0
    # 轉換為 0-100 的「市場恐慌/貪婪指數」
    market_index = (avg_polarity + 1) / 2 * 100
    
    return pd.DataFrame(news_data), market_index

def page_ai_sentiment():
    if 'visit_logs' in st.session_state:
        user = st.session_state.get('user_email') or "訪客 (未登入)"
        st.session_state['visit_logs'].append({
            '時間': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            '使用者': user,
            '瀏覽模組': "AI 新聞情緒感知"
        })

    apply_tech_ui() # 套用全新黑科技 UI
    
    st.title("🧠 AI 全球市場情緒雷達 (Beta)")
    st.markdown("這個模組配備了 **自然語言處理 (NLP)** 引擎。它會全自動爬取華爾街與全球英文財經新聞 RSS 標題，拔取隱藏在字裡行間的情緒，為您即時計算目前的市場氛圍。")
    
    with st.spinner("AI 正在光速閱讀全球最新 20 則財經新聞並運算情緒矩陣..."):
        news_df, market_index = fetch_and_analyze_news()
        
    st.markdown("---")
    
    # 決定大盤狀態文案
    if market_index >= 65:
        status_color = "#00ff99"
        status_text = "極度貪婪 (Extreme Greed) - 市場充滿樂觀消息，請注意追高風險。"
    elif market_index <= 35:
        status_color = "#ff4b4b"
        status_text = "極度恐慌 (Extreme Fear) - 利空瀰漫，或許是人棄我取的 7% 乖離進場好時機。"
    else:
        status_color = "#00aaff"
        status_text = "中立觀望 (Neutral) - 多空消息交雜，適合依圖表紀律操作。"

    cols = st.columns([1, 2])
    
    with cols[0]:
        # 繪製高科技儀表板指針 (Gauge Chart)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = market_index,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "全球財經 AI 情緒指數", 'font': {'color': 'white', 'size': 20}},
            gauge = {
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': status_color},
                'bgcolor': "rgba(255,255,255,0.1)",
                'borderwidth': 2,
                'bordercolor': "rgba(255,255,255,0.2)",
                'steps': [
                    {'range': [0, 35], 'color': "rgba(255, 75, 75, 0.3)"},
                    {'range': [35, 65], 'color': "rgba(0, 170, 255, 0.3)"},
                    {'range': [65, 100], 'color': "rgba(0, 255, 153, 0.3)"}],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': market_index}
            }
        ))
        fig.update_layout(
            paper_bgcolor = "rgba(0,0,0,0)", 
            font = {'color': "white", 'family': "Inter"},
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)
        
    with cols[1]:
        st.subheader("💡 AI 綜合判定結論")
        st.info(f"**{status_text}**")
        
        st.subheader("📊 即時數據剖析")
        c1, c2, c3 = st.columns(3)
        c1.metric("掃描新聞篇數", f"{len(news_df)} 篇")
        
        bullish_count = len(news_df[news_df['市場訊號'] == '🟢 樂觀 (Bullish)'])
        bearish_count = len(news_df[news_df['市場訊號'] == '🔴 悲觀 (Bearish)'])
        
        c2.metric("樂觀利多新聞", f"{bullish_count} 篇", f"+{bullish_count}")
        c3.metric("悲觀利空新聞", f"{bearish_count} 篇", f"-{bearish_count}")
        
    st.markdown("---")
    st.subheader("🗞️ AI 即時快讀清單 (News Feed)")
    st.dataframe(
        news_df, 
        column_config={
            "AI 情緒分數": st.column_config.ProgressColumn(
                "情緒分數 (0-100)",
                help="越高代表該篇新聞越樂觀",
                format="%.1f",
                min_value=0,
                max_value=100,
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=400
    )
