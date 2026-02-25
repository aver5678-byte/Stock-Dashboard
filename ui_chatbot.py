import streamlit as st

def inject_chatbot(token=None):
    """
    使用 iframe 嵌入 Dify 聊天機器人，並透過 CSS 強制將其固定在螢幕右側。
    """
    
    # 1. 建立對話框 HTML
    # 注意：這裡不在內部使用 position:fixed，而是交給外部的 Streamlit 容器處理
    chatbot_iframe = f"""
    <div style="height: 100vh; display: flex; flex-direction: column;">
        <div style="background: #0F172A; color: white; padding: 10px; border-radius: 8px 8px 0 0; border: 1px solid #38BDF8; text-align: center; font-weight: bold;">
            🤖 AI 戰情助理
        </div>
        <iframe
            src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
            style="width: 100%; flex-grow: 1; border: 1px solid #38BDF8; border-radius: 0 0 8px 8px;"
            frameborder="0"
            allow="microphone">
        </iframe>
    </div>
    """

    # 2. 注入全局 CSS 將這個組件鎖定在右側
    # 我們利用 [data-testid="stSidebar"] 以外的容器來定位
    st.markdown("""
        <style>
            /* 強制讓這個 HTML 組件在頁面上「飄起來」並靠右 */
            iframe[title="st.components.v1.html"] {
                position: fixed !important;
                right: 10px !important;
                top: 70px !important;
                width: 380px !important;
                height: 85vh !important;
                z-index: 999999 !important;
                border: none !important;
                box-shadow: -5px 0 20px rgba(0,0,0,0.5) !important;
            }
            
            /* 調整主頁面間距，讓圖表不會被擋住 */
            .main .block-container {
                padding-right: 400px !important;
            }
            
            /* 行動裝置適應：如果螢幕太小就隱藏或縮小 (可選) */
            @media (max-width: 768px) {
                iframe[title="st.components.v1.html"] {
                    display: none;
                }
                .main .block-container {
                    padding-right: 1rem !important;
                }
            }
        </style>
    """, unsafe_allow_html=True)

    # 3. 實際注入組件 (給予高度，讓它能畫出來)
    st.components.v1.html(chatbot_iframe, height=800)
