import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

def page_biz_cycle():
    st.title("景氣指標與大盤對照分析")
    st.write("本模組分析台灣景氣對策信號與加權指數的長期關聯性。")

    # 定義檔案路徑 (嘗試從可能的路徑讀取)
    data_dir = r"c:\Users\user\Desktop\AI代理專案\景氣訊號"
    taiex_path = os.path.join(data_dir, "taiex_monthly.csv")
    
    # 讀取大盤數據
    if not os.path.exists(taiex_path):
        st.error(f"找不到大盤數據檔案：{taiex_path}")
        return

    try:
        df_taiex = pd.read_csv(taiex_path)
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
        line=dict(color='#F87171', width=2)
    ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="年份",
        yaxis_title="指數點數"
    )
    
    st.plotly_chart(fig, use_container_width=True)

    st.info("💡 提示：目前的「景氣燈號」數據檔案需要進一步整理。系統目前顯示大盤長期趨勢，請確保景氣信號 Excel 檔存於正確路徑以啟用完整對照功能。")
