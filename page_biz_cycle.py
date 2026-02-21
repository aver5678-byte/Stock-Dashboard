import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def page_biz_cycle():
    st.markdown('<h1 class="centered-title">景氣指標與大盤對照分析</h1>', unsafe_allow_html=True)
    st.write("<p style='text-align:center; color:#6B7280;'>本模組分析台灣景氣對策信號與加權指數的長期關聯性。</p>", unsafe_allow_html=True)

    # 定義檔案路徑 (優先嘗試相對路徑，再嘗試絕對路徑)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    taiex_path = os.path.join(current_dir, "taiex_monthly.csv")
    
    # 備用路徑 (原絕對路徑)
    backup_path = r"c:\Users\user\Desktop\AI代理專案\景氣訊號\taiex_monthly.csv"
    
    if not os.path.exists(taiex_path):
        if os.path.exists(backup_path):
            taiex_path = backup_path
        else:
            st.error(f"找不到大盤數據檔案 (taiex_monthly.csv)。請確保檔案存在。")
            return

    try:
        df_taiex = pd.read_csv(taiex_path)
        if df_taiex.empty:
            st.warning("大盤數據檔案為空。")
            return
        df_taiex['Date'] = pd.to_datetime(df_taiex['Date'])
        df_taiex = df_taiex.sort_values('Date')
    except Exception as e:
        st.error(f"讀取大盤數據時出錯：{e}")
        return

    st.subheader("📊 加權指數月線趨勢")
    
    # 建立圖表
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_taiex['Date'], 
        y=df_taiex['^TWII'],
        mode='lines',
        name='加權指數',
        line=dict(color='#3B82F6', width=2)
    ))

    fig.update_layout(
        template="plotly_white",
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="年份",
        yaxis_title="指數點數"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 提示：目前的「景氣燈號」數據檔案需要進一步整理。系統目前顯示大盤長期趨勢，請確保景氣信號 Excel 檔存於正確路徑以啟用完整對照功能。")
