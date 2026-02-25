import streamlit as st

def inject_chatbot(token=None):
    """
    原生 AI 助理元件：左側觸發按鈕，右側彈出對話視窗。
    """
    
    # 1. 處理側邊欄狀態同步
    if 'show_ai_sidebar' not in st.session_state:
        st.session_state.show_ai_sidebar = False

    # 2. 定義左側「外掛式」啟動按鈕 (HTML/CSS)
    # 這裡利用 st.components 注入一個隱形的 iframe 來監聽點擊，並透過 session_state 切換
    trigger_html = """
    <style>
        .custom-ai-trigger {
            position: fixed;
            left: 0;
            top: 50%;
            transform: translateY(-50%);
            background: rgba(15, 23, 42, 0.9);
            color: #38BDF8;
            padding: 15px 8px;
            border-radius: 0 12px 12px 0;
            cursor: pointer;
            z-index: 999999;
            box-shadow: 4px 0 20px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            transition: all 0.3s;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(56, 189, 248, 0.3);
            border-left: none;
        }
        .custom-ai-trigger:hover {
            background: #0F172A;
            color: white;
            box-shadow: 8px 0 30px rgba(56, 189, 248, 0.5);
        }
    </style>
    <div class="custom-ai-trigger" onclick="parent.window.location.hash = 'ai_chat';">
        <div style="font-size: 22px;">🤖</div>
        <div style="font-size: 11px; font-weight: 900; writing-mode: vertical-lr; letter-spacing: 2px;">戰情助理</div>
    </div>
    
    <script>
        // 監控 Hash 變化來觸發 Streamlit (這是一種簡單的 iframe 通訊方式)
        const checkHash = () => {
            if (parent.window.location.hash === '#ai_chat') {
                parent.window.location.hash = ''; // 重置
                const btn = parent.document.getElementById('ai_trigger_btn');
                if (btn) btn.click();
            }
        };
        setInterval(checkHash, 500);
    </script>
    """
    st.components.v1.html(trigger_html, height=0)

    # 用一個隱藏的按鈕來接收來自 HTML 的點擊信號
    st.markdown("""
        <style>
        div[element-type="stButton"] button:has(div:contains("AI_TRIGGER")) {
            display: none !important;
        }
        div.stButton > button:has(div p:contains("AI_TRIGGER")) {
            display: none !important;
        }
        /* 針對較新版 Streamlit */
        button:contains("AI_TRIGGER") {
            display: none !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("AI_TRIGGER", key="ai_trigger_btn"):
        st.session_state.show_ai_sidebar = not st.session_state.show_ai_sidebar
        st.rerun()

    # 3. 如果狀態為開啟，顯示右側對話窗
    if st.session_state.show_ai_sidebar:
        # 使用自定義的 CSS 讓它看起來像側邊欄
        st.markdown("""
            <style>
            [data-testid="stSidebarNav"] { display: none; } /* 隱藏左側導覽防止混淆 */
            
            /* 右側側邊欄容器樣式 */
            .ai-sidebar {
                position: fixed;
                right: 0;
                top: 0;
                width: 400px;
                height: 100vh;
                background: #0F172A;
                border-left: 2px solid #334155;
                z-index: 1000000;
                padding: 20px;
                box-shadow: -10px 0 30px rgba(0,0,0,0.5);
                display: flex;
                flex-direction: column;
            }
            .ai-header {
                border-bottom: 2px solid #1E293B;
                padding-bottom: 15px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # 建立一個右側的彈出層 (利用 Streamlit 的 st.sidebar 其實最穩定，但如果想在右邊就要用自定義 HTML)
        # 考慮到穩定性，我們直接在頁面右側畫一個區塊
        with st.sidebar:
            st.markdown("### 🤖 AI 戰情小助手")
            st.info("我是內建助理，已經學習了 40週乖離與景氣循環邏輯。你可以直接輸入問題。")
            
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            if prompt := st.chat_input("詢問有關乖離率或景氣循環的问题..."):
                with st.chat_message("user"):
                    st.markdown(prompt)
                st.session_state.messages.append({"role": "user", "content": prompt})

                # 簡單的模擬邏輯 (之後可以接真正的 AI API)
                response = f"收到您的問題：'{prompt}'。根據目前的資料，大盤乖離率處於高位，建議注意風險。"
                with st.chat_message("assistant"):
                    st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            
            if st.button("關閉助理"):
                st.session_state.show_ai_sidebar = False
                st.rerun()
