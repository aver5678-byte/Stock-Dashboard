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

    # --- 2. Sidebar Toggle Button ---
    with st.sidebar:
        st.markdown("---")
        label = "❌ 關閉 AI 助理" if st.session_state.chatbot_visible else "🤖 開啟 AI 戰情室"
        if st.button(label, key="btn_toggle_ai", use_container_width=True):
            st.session_state.chatbot_visible = not st.session_state.chatbot_visible
            st.rerun()

    # --- 3. Right Sidebar Panel ---
    if st.session_state.chatbot_visible:
        # NOTE: EXACTLY ZERO blank lines in this HTML string. 
        # Blank lines cause Streamlit's Markdown parser to treat subsequent HTML tags as raw text!
        chatbot_html = """<div id="ai-sidebar" style="position: fixed; right: 0; top: 60px; width: 400px; height: calc(100vh - 60px); background: #0F172A; border-left: 2px solid #38BDF8; z-index: 999999; display: flex; flex-direction: column; box-shadow: -15px 0 35px rgba(0,0,0,0.6);">
            <div style="position: absolute; left: 0; top: 0; width: 1px; height: 100%; background: linear-gradient(to bottom, transparent, #38BDF8, transparent); box-shadow: 0 0 15px #38BDF8;"></div>
            <div style="padding: 12px; background: #1E293B; color: white; border-bottom: 2px solid #334155; display: flex; justify-content: space-between; align-items: center;">
                <span style="font-weight: bold; font-size: 15px;">🤖 AI 戰情分析專區</span>
                <span style="color: #38BDF8; font-size: 10px; font-weight: bold; border: 1px solid #38BDF8; padding: 1px 5px; border-radius: 3px;">ACTIVE</span>
            </div>
            <iframe src="https://udify.app/chatbot/YUWIdfFrAFOsIJ8s" style="width: 100%; flex-grow: 1; border: none;" allow="microphone"></iframe>
        </div>"""
        st.markdown(chatbot_html, unsafe_allow_html=True)
