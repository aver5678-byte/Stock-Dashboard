import streamlit as st

def inject_chatbot(token=None):
    """
    實作可切換的右側 AI 助理：
    1. 平常隱藏，只顯示右側切換標籤。
    2. 點擊後展開，並自動調整主畫面邊距（不遮擋資訊）。
    """
    
    # 初始化顯示狀態
    if 'chatbot_visible' not in st.session_state:
        st.session_state.chatbot_visible = False

    # --- 1. 定義切換標籤與動畫樣式 ---
    st.markdown(f"""
        <style>
            /* 主畫面容器動力學調整 */
            .main .block-container {{
                max-width: { 'calc(100% - 400px)' if st.session_state.chatbot_visible else '100%' } !important;
                margin-right: { '400px' if st.session_state.chatbot_visible else '0px' } !important;
                transition: all 0.3s ease-in-out !important;
            }}
            
            /* 修正 Streamlit 預設佈局對排版的限制 */
            [data-testid="stAppViewContainer"] {{
                display: flex;
                flex-direction: row;
            }}
        </style>
    """, unsafe_allow_html=True)

    # --- 2. 顯示按鈕 ---
    with st.sidebar:
        st.markdown("---")
        if st.button("🤖 AI 助理" + (" (關閉)" if st.session_state.chatbot_visible else " (開啟)"), key="btn_toggle_ai"):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. 如果開啟，顯示 Dify 視窗 ---
    if st.session_state.chatbot_visible:
        # 建立帶有邊界感的 HTML 內核
        chatbot_html = """
        <div style="position: fixed; right: 0; top: 0; width: 400px; height: 100vh; background: #0F172A; border-left: 2px solid #38BDF8; z-index: 1000000; display: flex; flex-direction: column; box-shadow: -15px 0 35px rgba(0,0,0,0.6);">
            <!-- 分隔裝飾線 -->
            <div style="position: absolute; left: 0; top: 0; width: 1px; height: 100%; background: linear-gradient(to bottom, transparent, #38BDF8, transparent); box-shadow: 0 0 15px #38BDF8;"></div>
            
            <div style="padding: 15px; background: #1E293B; color: white; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; letter-spacing: 1px;">🤖 AI 戰情分析專區</span>
                <span style="color: #38BDF8; font-size: 10px; font-weight: bold;">LIVE</span>
            </div>
            <iframe
                src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                style="width: 100%; flex-grow: 1; border: none;"
                allow="microphone">
            </iframe>
        </div>
        """
        st.markdown(chatbot_html, unsafe_allow_html=True)
