import streamlit as st
import json
import urllib.parse

def inject_chatbot():
    if 'chatbot_visible' not in st.session_state:
        st.session_state.chatbot_visible = False

    # --- 1. Global Layout CSS ---
    if st.session_state.chatbot_visible:
        st.markdown("<style>.block-container { padding-right: 420px !important; transition: padding-right 0.3s; }</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>.block-container { padding-right: 5rem !important; transition: padding-right 0.3s; }</style>", unsafe_allow_html=True)

    # --- 2. Sidebar Button ---
    with st.sidebar:
        st.markdown("""
            <style>
                div[data-testid="stSidebar"] div.stButton > button {
                    background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 41, 59, 0.5) 100%) !important;
                    color: #38BDF8 !important;
                    border: 1px solid rgba(56, 189, 248, 0.4) !important;
                    border-radius: 12px !important;
                    padding: 0.5rem 1rem !important;
                    font-weight: 800 !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        label = "❌ 關閉助理" if st.session_state.chatbot_visible else "🤖 啟動 AI 助理"
        if st.button(label, key="btn_toggle_ai", use_container_width=True):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. Data Sync & Iframe ---
    market_snapshot = st.session_state.get('market_snapshot', {
        "bias_40w": "0.0", 
        "index_price": "0", 
        "upward_bounce": "0.0", 
        "downward_dd": "0.0"
    })
    
    # 【全面相容模式】: 同時發送英文 ID 與 中文標籤，確保無論 Dify 後台怎麼設都能抓到
    ai_inputs = {}
    for key in ["bias_40w", "index_price", "upward_bounce", "downward_dd"]:
        val = str(market_snapshot.get(key, "0"))
        clean_val = val.replace("%", "").replace(",", "").replace("待載入...", "0").replace("待載入", "0")
        
        # 1. 發送英文鍵名 (標準 ID)
        ai_inputs[key] = clean_val
        
        # 2. 發送中文鍵名 (作為備援，因 Dify 網頁版有時會將「顯示名稱」誤認為「變數名稱」)
        if key == "bias_40w": ai_inputs["40週乖離率"] = clean_val
        if key == "upward_bounce": ai_inputs["波段上漲幅度"] = clean_val
        if key == "downward_dd": ai_inputs["波段最大回撤"] = clean_val
        if key == "index_price": ai_inputs["當前指數"] = clean_val
            
    # 打包 JSON
    json_payload = json.dumps(ai_inputs)
    encoded_inputs = urllib.parse.quote(json_payload)
    
    # 這裡採用最保險的雙重傳參：inputs={JSON} + 直接參數 (備援)
    query_params = f"inputs={encoded_inputs}"
    for k, v in ai_inputs.items():
        query_params += f"&{k}={urllib.parse.quote(v)}"
        
    chatbot_url = f"https://udify.app/chatbot/YUWIdfFrAFOsIJ8s?{query_params}"
    
    # 側邊欄顯示當前同步狀態 (偵偵用)
    with st.sidebar:
        with st.expander("📡 AI 核心變數同步狀態", expanded=False):
            st.write("這是目前傳遞給 AI 的原始數據 (已去格式化)：")
            st.json(ai_inputs)
            st.info("💡 如果 AI 報錯 None，請確認 Dify 後台變數名稱與上方 Key 是否完全一致。")
    
    if st.session_state.chatbot_visible:
        js_code = f"""
        <script>
            try {{
                var parentDoc = window.parent.document;
                if (!parentDoc) throw new Error("Parent document inaccessible (Cross-Origin)");
                
                var existingSidebar = parentDoc.getElementById("persistent-ai-sidebar");
                var targetUrl = "{chatbot_url}";
                
                if (!existingSidebar) {{
                    var sidebarDiv = parentDoc.createElement("div");
                    sidebarDiv.id = "persistent-ai-sidebar";
                    sidebarDiv.style.cssText = "position:fixed; right:0; top:60px; width:400px; height:calc(100vh - 60px); background:#0F172A; border-left:2px solid #38BDF8; z-index:999999; display:flex; flex-direction:column; box-shadow:-15px 0 35px rgba(0,0,0,0.6); transition: all 0.3s ease;";
                    
                    sidebarDiv.innerHTML = `
                        <div style="padding:10px; background:#1E293B; color:#38BDF8; font-family:sans-serif; font-size:12px; font-weight:bold; border-bottom:1px solid #334155; display:flex; justify-content:space-between;">
                            <span>🤖 量化助理連線中</span>
                            <span style="opacity:0.6;">v2.0 // Real-time Sync</span>
                        </div>
                        <div id="iframe-container" style="flex-grow:1; display:flex; flex-direction:column;">
                            <iframe id="ai-chatbot-iframe" src="${{targetUrl}}" style="width:100%; height:100%; border:none;" allow="microphone"></iframe>
                        </div>
                    `;
                    parentDoc.body.appendChild(sidebarDiv);
                }} else {{
                    existingSidebar.style.display = "flex";
                    var container = parentDoc.getElementById("iframe-container");
                    var iframe = parentDoc.getElementById("ai-chatbot-iframe");
                    
                    if (iframe && iframe.src !== targetUrl) {{
                        container.innerHTML = `<iframe id="ai-chatbot-iframe" src="${{targetUrl}}" style="width:100%; height:100%; border:none;" allow="microphone"></iframe>`;
                    }}
                }}
            }} catch (e) {{
                console.warn("AI Chatbot Bridge Error (likely cross-origin): ", e);
            }}
        </script>
        """
        st.components.v1.html(js_code, height=0, key="ai_bridge_active")
    else:
        # 隱藏 JS
        st.components.v1.html("""<script>
            try {
                var sidebar = window.parent.document.getElementById("persistent-ai-sidebar");
                if (sidebar) sidebar.style.display = "none";
            } catch (e) {
                console.warn("AI Chatbot Switch Error: ", e);
            }
        </script>""", height=0, key="ai_bridge_hidden")
