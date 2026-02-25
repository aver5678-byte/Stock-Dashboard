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

    # --- 1. 定義全局佈局動力學 ---
    # 只有在開啟時才對主畫面進行「物理推擠」
    if st.session_state.chatbot_visible:
        st.markdown("""
            <style>
                /* 讓主畫面內容主動避開右側 400px 空間 */
                .main .block-container {
                    max-width: calc(100% - 410px) !important;
                    margin-left: 10px !important;
                    margin-right: 400px !important;
                    transition: all 0.3s ease-in-out !important;
                }}
            </style>
        """, unsafe_allow_html=True)

    # --- 2. 側邊欄按鈕 ---
    with st.sidebar:
        st.markdown("---")
        label = "❌ 關閉 AI 助理" if st.session_state.chatbot_visible else "🤖 開啟 AI 戰情室"
        if st.button(label, key="btn_toggle_ai", use_container_width=True):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. 渲染右側面板 ---
    if st.session_state.chatbot_visible:
        # 外層包裹 HTML，鎖定在右上角
        full_panel_html = """
        <div style="position: fixed; right: 0; top: 60px; width: 400px; height: calc(100vh - 60px); background: #0F172A; border-left: 2px solid #38BDF8; z-index: 999999; display: flex; flex-direction: column; box-shadow: -15px 0 35px rgba(0,0,0,0.6);">
            <div style="padding: 12px; background: #1E293B; color: white; border-bottom: 2px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; font-size: 15px;">🤖 AI 戰情分析專區</span>
                <span style="color: #38BDF8; font-size: 10px; font-weight: bold; border: 1px solid #38BDF8; padding: 1px 5px; border-radius: 3px;">ACTIVE</span>
            </div>
            <iframe
                src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                style="width: 100%; height: 100%; border: none;"
                allow="microphone">
            </iframe>
        </div>
        """
        # 利用一個隱形的小組件來注入這段 HTML 定位代碼
        st.components.v1.html(full_panel_html, height=0)
        
        # 額外 CSS 確保 Streamlit 的 iframe wrapper 不會影響定位
        st.markdown("""
            <style>
                iframe[title="st.components.v1.html"] {
                    position: fixed !important;
                    top: 0px !important;
                    right: 0px !important;
                    z-index: 1000000 !important;
                    width: 400px !important;
                    height: 100vh !important;
                }
            </style>
        """, unsafe_allow_html=True)
