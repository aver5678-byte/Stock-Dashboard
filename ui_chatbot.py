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
        """, unsafe_allow_html=True)
        
        # 使用 Streamlit 的摺疊按鈕功能，點開後顯示對話視窗
        with st.expander("💬 點擊開啟對話視窗", expanded=False):
            # 嵌入 Dify 的完整對話網頁
            st.components.v1.html(
                """
                <iframe
                    src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                    style="width: 100%; height: 500px; border-radius: 8px;"
                    frameborder="0"
                    allow="microphone">
                </iframe>
                """,
                height=520,
                scrolling=False
            )
        
        st.markdown('<p style="color: #64748B; font-size: 10px; text-align: center;">Powered by Dify & aver5678</p>', unsafe_allow_html=True)
