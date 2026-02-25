import streamlit as st

def inject_chatbot(token=None):
    """
    實作絕對定位 (Absolute Positioning) 的右側浮動視窗。
    完全不干擾 Streamlit 原生的 main container 寬度，達成疊加效果。
    """
    
    # 這個 HTML 會生成一個固定在畫面右側的區塊
    overlay_html = """
    <div id="ai-sidebar-container" style="position: fixed; top: 80px; right: 20px; width: 380px; height: calc(100vh - 100px); z-index: 999999; display: flex; flex-direction: column; background: transparent; pointer-events: none;">
        
        <!-- 頂部卡片 (需要可以點擊或有背景所以設為 auto) -->
        <div style="background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); border: 1px solid #38BDF8; border-radius: 12px 12px 0 0; padding: 12px; text-align: center; box-shadow: 0 4px 15px rgba(0, 191, 255, 0.2); pointer-events: auto;">
            <div style="font-size: 18px; font-weight: bold; color: white; display: flex; align-items: center; justify-content: center; gap: 8px;">
                🤖 AI 戰情分析師
            </div>
            <div style="color: #94A3B8; font-size: 11px; margin-top: 4px;">由 SiliconFlow 驅動</div>
        </div>
        
        <!-- 聊天機器人 iframe (需要可以對話所以設為 auto) -->
        <div style="flex-grow: 1; pointer-events: auto; border: 1px solid rgba(0, 191, 255, 0.3); border-top: none; border-radius: 0 0 12px 12px; overflow: hidden; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5); background: #ffffff;">
            <iframe
                src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s"
                style="width: 100%; height: 100%;"
                frameborder="0"
                allow="microphone">
            </iframe>
        </div>
    </div>
    """
    
    # 注入這個覆蓋層。高度設為 0 以避免佔用 Streamlit 的標準文件流空間
    st.components.v1.html(overlay_html, height=0)
    
    # 在全域 CSS 中替主畫面增加 padding-right，避免圖表最右邊的數據被 AI 視窗蓋住
    st.markdown("""
        <style>
            /* 給 Streamlit 主容器增加右側邊距，相當於為 AI 視窗留出專屬軌道 */
            .block-container {
                padding-right: 420px !important; 
            }
            
            /* 修正 iframe 容器在某些情況下的錯位 */
            div[data-testid="stHtml"] {
                position: relative;
                z-index: 999999;
            }
        </style>
    """, unsafe_allow_html=True)
