import streamlit as st
import json
import urllib.parse
import streamlit.components.v1 as components

def inject_chatbot():
    """
    雲端安全穩定版：在側邊欄直接嵌入 AI 戰情室，不再嘗試穿透父視窗 (解決 Cross-Origin 阻擋)
    """
    if 'chatbot_visible' not in st.session_state:
        st.session_state.chatbot_visible = False

    # 1. 準備數據打包
    snapshot = st.session_state.get('market_snapshot', {})
    
    # 清洗數據：移除百分比符號與逗號，確保 Dify 變數讀取正常
    clean_data = {
        "index_price": str(snapshot.get("index_price", "None")).replace(",", ""),
        "bias_40w": str(snapshot.get("bias_40w", "None")).replace("%", ""),
        "upward_bounce": str(snapshot.get("upward_bounce", "None")).replace("%", ""),
        "downward_dd": str(snapshot.get("downward_dd", "None")).replace("%", ""),
        # 增加中文 key 以防萬一
        "當前報價": str(snapshot.get("index_price", "None")).replace(",", ""),
        "40週乖離率": str(snapshot.get("bias_40w", "None")).replace("%", "")
    }
    
    inputs_json = json.dumps(clean_data)
    encoded_inputs = urllib.parse.quote(inputs_json)
    
    # 建立 Dify URL (同時帶入 JSON payload 與 直接參數)
    base_url = "https://udify.app/chatbot/3pIdzYREU74lCoy9"
    dify_url = f"{base_url}?inputs={encoded_inputs}&index_price={clean_data['index_price']}&bias_40w={clean_data['bias_40w']}"

    st.sidebar.markdown("---")
    st.sidebar.subheader("🤖 AI 量化戰情室")
    
    label = "🔴 關閉戰情通訊" if st.session_state.chatbot_visible else "🔵 開啟 AI 戰情通訊"
    if st.sidebar.button(label, key="btn_toggle_ai", use_container_width=True):
        st.session_state.chatbot_visible = not st.session_state.chatbot_visible
        st.rerun()

    if st.session_state.chatbot_visible:
        # 使用 st.components 直接在側邊欄渲染，這在雲端 100% 安全
        st.sidebar.info("💡 提示：AI 已同步大盤最新數據，您可以直接詢問分析。")
        st.sidebar.iframe(dify_url, height=600, scrolling=True)
        
        # 增加調試資訊 (折疊)
        with st.sidebar.expander("📡 數據傳輸監控"):
            st.json(clean_data)
