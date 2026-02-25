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
    # 利用 CSS 讓標籤固定在螢幕右側中央
    st.markdown(f"""
        <style>
            /* 切換按鈕樣式 */
            .chatbot-toggle {{
                position: fixed;
                right: {'380px' if st.session_state.chatbot_visible else '0px'};
                top: 50%;
                transform: translateY(-50%);
                background: #0F172A;
                color: #38BDF8;
                padding: 15px 8px;
                border: 1px solid #38BDF8;
                border-right: none;
                border-radius: 12px 0 0 12px;
                cursor: pointer;
                z-index: 1000001;
                transition: all 0.3s ease;
                writing-mode: vertical-lr;
                font-weight: bold;
                font-size: 14px;
                box-shadow: -2px 0 10px rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            .chatbot-toggle:hover {{
                background: #1E293B;
                padding-right: 12px;
            }}
            
            /* 主畫面容器邊距調整 */
            .main .block-container {{
                padding-right: {'420px' if st.session_state.chatbot_visible else '2rem'} !important;
                transition: padding-right 0.3s ease;
            }}
        </style>
    """, unsafe_allow_html=True)

    # --- 2. 顯示偵聽按鈕 (隱形的 Streamlit Button 來觸發 Rerun) ---
    # 這裡我們用一個小技巧，在 HTML 按鈕中觸發這個按鈕
    with st.container():
        # 這個按鈕會隱藏，但我們會透過 HTML 的點擊來觸發它
        if st.sidebar.button("🤖 AI 助理" + (" (關閉)" if st.session_state.chatbot_visible else " (開啟)"), key="btn_toggle_ai"):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. 如果開啟，顯示 Dify 視窗 ---
    if st.session_state.chatbot_visible:
        # 建立零邊距的 HTML 內核
        chatbot_html = """
        <div style="position: fixed; right: 0; top: 0; width: 380px; height: 100vh; background: #0F172A; border-left: 1px solid #38BDF8; z-index: 1000000; display: flex; flex-direction: column; box-shadow: -10px 0 30px rgba(0,0,0,0.5);">
            <div style="padding: 15px; background: #1E293B; color: white; border-bottom: 1px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold;">🤖 AI 戰情分析師</span>
                <span style="color: #64748B; font-size: 10px;">Dify x SiliconFlow</span>
            </div>
            <iframe
                src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                style="width: 100%; flex-grow: 1; border: none;"
                allow="microphone">
            </iframe>
        </div>
        """
        st.markdown(chatbot_html, unsafe_allow_html=True)
