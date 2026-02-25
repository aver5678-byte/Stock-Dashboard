import streamlit as st

def inject_chatbot(token=None):
    """
    注入 Dify 官方懸浮對話氣泡 (Web Embed)。
    點擊右下角氣泡即可展開對話視窗。
    """
    
    # Dify Web Embed Script (Floating Bubble)
    dify_embed_html = """
    <script>
        window.difyChatbotConfig = {
            token: 'YUWIdfFrAFOsIJ8s',
            isDev: false
        }
    </script>
    <script
        src="https://udify.app/embed.min.js"
        id="YUWIdfFrAFOsIJ8s"
        defer>
    </script>
    <style>
        /* 浮動按鈕顏色微調 (配合系統深色科技主題) */
        #dify-chatbot-bubble-button {
            background-color: #38BDF8 !important;
            box-shadow: 0 10px 25px rgba(56, 189, 248, 0.4) !important;
        }
        /* 聊天視窗尺寸變大，以適應更多指標說明 */
        #dify-chatbot-bubble-window {
            width: 28rem !important;
            height: 45rem !important;
            border-radius: 12px !important;
            box-shadow: 0 20px 50px rgba(0,0,0,0.6) !important;
            border: 1px solid rgba(56, 189, 248, 0.2) !important;
        }
    </style>
    """
    
    # 注入 HTML，設定高度為 0 是為了讓它只作為背景腳本執行，不佔用 Streamlit 版面
    st.components.v1.html(dify_embed_html, height=0)
