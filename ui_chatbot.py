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

    # --- 1. 定義全局 CSS 動力學 ---
    # 這是為了確保左側主畫面在 AI 開啟時會「主動讓位」
    if st.session_state.chatbot_visible:
        st.markdown("""
            <style>
                /* 強制主畫面容器縮小並偏移 */
                .main .block-container {
                    max-width: calc(100% - 420px) !important;
                    margin-left: 0 !important;
                    margin-right: 420px !important;
                    transition: all 0.3s ease-in-out !important;
                }
                /* 隱藏原生右側滾動條，避免雙滾動條出現 */
                [data-testid="stSidebar"] + section {
                    overflow-x: hidden !important;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .main .block-container {
                    max-width: 100% !important;
                    margin-right: 0px !important;
                    transition: all 0.3s ease-in-out !important;
                }
            </style>
        """, unsafe_allow_html=True)

    # --- 2. 側邊欄控制按鈕 ---
    with st.sidebar:
        st.markdown("---")
        # 增加一個更亮眼的按鈕樣式
        label = "❌ 關閉 AI 助理" if st.session_state.chatbot_visible else "🤖 開啟 AI 戰情室"
        if st.button(label, key="btn_toggle_ai", use_container_width=True):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. 渲染右側面板 (使用絕對定位組件) ---
    if st.session_state.chatbot_visible:
        # 使用一個絕對定位的容器，高度設為 0 以免在頁面底部佔位
        full_panel_html = """
        <div style="position: fixed; right: 0; top: 0; width: 400px; height: 100vh; background: #0F172A; border-left: 2px solid #38BDF8; z-index: 999999; display: flex; flex-direction: column; box-shadow: -10px 0 30px rgba(0,0,0,0.5);">
            <div style="padding: 15px; background: #1E293B; color: white; border-bottom: 2px solid #334155; font-family: sans-serif; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; letter-spacing: 1px;">🤖 AI 戰情分析專區</span>
                <span style="color: #38BDF8; font-size: 11px; font-weight: bold; padding: 2px 6px; border: 1px solid #38BDF8; border-radius: 4px;">LIVE</span>
            </div>
            <iframe
                src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                style="width: 100%; flex-grow: 1; border: none;"
                frameborder="0"
                allow="microphone">
            </iframe>
        </div>
        """
        # 關鍵：這裡必須用 components.html 且給予足夠權限，或者直接 markdown 執行
        # 為了解決程式碼裸露，我們使用 st.components.v1.html 的沙盒渲染
        st.components.v1.html(full_panel_html, height=1000)
        
        # 同時注入一段 CSS 修正沙盒本身的定位，讓它真正浮在最右邊
        st.markdown("""
            <style>
                iframe[title="st.components.v1.html"] {
                    position: fixed !important;
                    right: 0 !important;
                    top: 0 !important;
                    width: 400px !important;
                    height: 100vh !important;
                    z-index: 1000000 !important;
                    border: none !important;
                }
            </style>
        """, unsafe_allow_html=True)
