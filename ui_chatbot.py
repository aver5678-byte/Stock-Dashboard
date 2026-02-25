import streamlit as st

def inject_chatbot(token=None):
    if 'chatbot_visible' not in st.session_state:
        st.session_state.chatbot_visible = False

    # --- 1. Global Layout CSS ---
    # Use padding-right on the block-container to push content without breaking flexbox.
    if st.session_state.chatbot_visible:
        st.markdown("""
            <style>
                .block-container {
                    padding-right: 420px !important;
                    transition: padding-right 0.3s ease-in-out;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .block-container {
                    padding-right: 5rem !important; /* Streamlit default wide padding */
                    transition: padding-right 0.3s ease-in-out;
                }
            </style>
        """, unsafe_allow_html=True)

    # --- 2. Sidebar Premium Toggle Button ---
    with st.sidebar:
        # 插入一段專屬的 CSS 來美化這個特定的按鈕
        st.markdown("""
            <style>
                /* AI 按鈕專屬外殼 */
                .ai-toggle-container {
                    margin-top: 30px;
                    padding: 10px 0;
                }
                
                /* AI 按鈕小標籤 */
                .ai-tag-label {
                    font-size: 10px;
                    color: #38BDF8;
                    letter-spacing: 2px;
                    font-weight: 900;
                    margin-bottom: 8px;
                    opacity: 0.8;
                    text-transform: uppercase;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .ai-tag-label::after {
                    content: "";
                    flex: 1;
                    height: 1px;
                    background: linear-gradient(90deg, rgba(56, 189, 248, 0.5), transparent);
                }

                /* 覆蓋這個特定按鈕的 Streamlit 原生樣式 */
                div.stButton > button[key="btn_toggle_ai"] {
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%) !important;
                    color: #38BDF8 !important;
                    border: 1px solid rgba(56, 189, 248, 0.4) !important;
                    border-radius: 12px !important;
                    padding: 20px 15px !important;
                    font-size: 18px !important;
                    font-weight: 800 !important;
                    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
                    backdrop-filter: blur(10px);
                    text-align: center !important;
                    display: flex !important;
                    justify-content: center !important;
                }

                div.stButton > button[key="btn_toggle_ai"]:hover {
                    border-color: #38BDF8 !important;
                    color: #FFFFFF !important;
                    box-shadow: 0 0 25px rgba(56, 189, 248, 0.3) !important;
                    transform: translateY(-2px) !important;
                    background: rgba(30, 41, 59, 0.8) !important;
                }

                /* 當 AI 開啟時的特別樣式 */
                .ai-active-btn button[key="btn_toggle_ai"] {
                    border-color: #38BDF8 !important;
                    background: rgba(56, 189, 248, 0.1) !important;
                    box-shadow: inset 0 0 15px rgba(56, 189, 248, 0.2), 0 0 20px rgba(56, 189, 248, 0.2) !important;
                }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<div class="ai-toggle-container">', unsafe_allow_html=True)
        st.markdown('<div class="ai-tag-label">Intelligence Service</div>', unsafe_allow_html=True)
        
        # 使用容器類別來區分狀態
        container_class = "ai-active-btn" if st.session_state.chatbot_visible else ""
        with st.container():
            st.markdown(f'<div class="{container_class}">', unsafe_allow_html=True)
            label = "❌ 關閉｜分析助理" if st.session_state.chatbot_visible else "🤖 AI｜研究諮詢"
            if st.button(label, key="btn_toggle_ai", use_container_width=True):
                st.session_state.chatbot_visible = not st.session_state.chatbot_visible
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 3. Right Sidebar Persistent Injector ---
    # We use a trick to inject the iframe into the very root of the document ONE TIME via JS.
    # We then use CSS classes to show/hide it based on Streamlit's state, without tearing down the iframe element.
    
    js_code = f"""
    <script>
        // Check if our persistent chatbot container already exists in the parent HTML document
        var parentDoc = window.parent.document;
        var existingSidebar = parentDoc.getElementById("persistent-ai-sidebar");
        
        if (!existingSidebar) {{
            // It does not exist, so we create it ONCE and append it to the body.
            console.log("Initializing persistent AI Sidebar for the first time.");
            
            var sidebarDiv = parentDoc.createElement("div");
            sidebarDiv.id = "persistent-ai-sidebar";
            
            // Set basic styling for the container (will be toggled via CSS injected by Streamlit)
            sidebarDiv.style.position = "fixed";
            sidebarDiv.style.right = "0px";
            sidebarDiv.style.top = "60px";
            sidebarDiv.style.width = "400px";
            sidebarDiv.style.height = "calc(100vh - 60px)";
            sidebarDiv.style.backgroundColor = "#0F172A";
            sidebarDiv.style.borderLeft = "2px solid #38BDF8";
            sidebarDiv.style.zIndex = "999999";
            sidebarDiv.style.display = "flex";
            sidebarDiv.style.flexDirection = "column";
            sidebarDiv.style.boxShadow = "-15px 0 35px rgba(0,0,0,0.6)";
            sidebarDiv.style.visibility = "hidden"; // Hidden by default
            sidebarDiv.style.transform = "translateX(100%)";
            sidebarDiv.style.transition = "transform 0.3s ease-in-out, visibility 0.3s";
            
            // Construct the inner HTML
            sidebarDiv.innerHTML = `
                <div style="position: absolute; left: 0; top: 0; width: 1px; height: 100%; background: linear-gradient(to bottom, transparent, #38BDF8, transparent); box-shadow: 0 0 15px #38BDF8;"></div>
                <div style="padding: 12px; background: #1E293B; color: white; border-bottom: 2px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: bold; font-size: 15px; font-family: sans-serif;">🤖 AI 戰情分析專區</span>
                    <span style="color: #38BDF8; font-size: 10px; font-weight: bold; border: 1px solid #38BDF8; padding: 1px 5px; border-radius: 3px; font-family: sans-serif;">ACTIVE</span>
                </div>
                <iframe src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s" style="width: 100%; flex-grow: 1; border: none;" allow="microphone"></iframe>
            `;
            
            // Append to the root document body (Streamlit's rerender won't touch this!)
            parentDoc.body.appendChild(sidebarDiv);
        }}
    </script>
    """
    
    # 注入這段執行腳本 (由於放在 height=0 的 components裡，不會影響排版)
    st.components.v1.html(js_code, height=0)

    # --- 4. Streamlit 狀態驅動顯示與隱藏 ---
    # 這裡只操作 CSS，去控制剛才利用 JS 創建的外部元素
    if st.session_state.chatbot_visible:
        st.markdown("""
            <style>
                /* 當開啟狀態時，讓外部的這個 div 滑入並顯示 */
                #persistent-ai-sidebar {
                    visibility: visible !important;
                    transform: translateX(0%) !important;
                }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                /* 當關閉狀態時，讓外部的這個 div 隱藏並滑出 */
                #persistent-ai-sidebar {
                    visibility: hidden !important;
                    transform: translateX(100%) !important;
                }
            </style>
        """, unsafe_allow_html=True)
