import streamlit as st

def inject_chatbot(token=None):
    """
    將 Dify 聊天機器人直接嵌入在左側選單下方。
    這能確保在任何環境下（地端/雲端）都能 100% 正常顯示。
    """
    
    with st.sidebar:
        st.markdown("---")
        # 建立一個美觀的小卡片作為提示
        st.markdown("""
            <div style="background: rgba(56, 189, 248, 0.1); border: 2px solid #38BDF8; border-radius: 12px; padding: 15px; text-align: center; margin-bottom: 10px;">
                <div style="font-size: 24px; margin-bottom: 5px;">🤖</div>
                <div style="color: white; font-weight: 800; font-size: 14px;">AI 戰情助理</div>
                <div style="color: #94A3B8; font-size: 11px;">指標教學與數據詢問</div>
            </div>
            
            <style>
            /* 1. 微調側邊欄寬度，給機器人多一點呼吸空間才不會被切掉右邊 */
            [data-testid="stSidebar"] {
                min-width: 360px !important;
            }
            /* 2. 讓 Expander 裡面的內容沒有多餘內距，盡可能撐滿 */
            [data-testid="stExpanderDetails"] {
                padding-left: 0.5rem !important;
                padding-right: 0.5rem !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # 使用 Streamlit 的摺疊按鈕功能，點開後顯示對話視窗
        with st.expander("💬 點擊展開：智能對話視窗", expanded=False):
            # 建立零邊距的 HTML 內核，徹底根除「白色外框」與「擠壓裁切」的問題
            seamless_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    /* 消除預設黑白邊距與滾動條 */
                    body { margin: 0 !important; padding: 0 !important; background-color: transparent !important; overflow: hidden !important; }
                    iframe { border: none !important; border-radius: 8px; }
                </style>
            </head>
            <body>
                <iframe
                    src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                    style="width: 100%; height: 600px;"
                    frameborder="0"
                    allow="microphone">
                </iframe>
            </body>
            </html>
            """
            st.components.v1.html(seamless_html, height=600, scrolling=False)
        
        st.markdown('<p style="color: #64748B; font-size: 10px; text-align: center; margin-top:15px;">Powered by SiliconFlow & aver5678</p>', unsafe_allow_html=True)
