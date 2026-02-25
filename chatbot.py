import streamlit as st
import google.generativeai as genai
import os

# 嘗試從 Streamlit Secrets 中讀取 API Key (未來部署時使用)
# 本機開發時可以在 .streamlit/secrets.toml 中設定 GEMINI_API_KEY
def init_gemini():
    # 1. 優先嘗試從本機檔案讀取 (防止 Streamlit 緩存失效)
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, "r", encoding="utf-8") as f:
                content = f.read()
                import re
                match = re.search(r'GEMINI_API_KEY\s*=\s*"(.*?)"', content)
                if match:
                    api_key = match.group(1)
                    if api_key and "在此貼上" not in api_key:
                        genai.configure(api_key=api_key)
                        return True
        except:
            pass

    # 2. 備案：原生的 st.secrets (用於部署至 Streamlit Cloud)
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
        if api_key and "在此貼上" not in api_key:
            genai.configure(api_key=api_key)
            return True
    except:
        pass
        
    return False

def generate_system_prompt(current_page, current_dd=None, current_bounce=None, current_price=None):
    """
    動態生成 System Prompt，把「量化邏輯」與「當前最新數值」餵給 AI
    """
    base_prompt = """
    你現在是「股市乖離量化分析系統」的虛擬實習研究員。
    你的任務是用白話、專業、量化客觀的口吻，幫助散戶理解當前充滿風險或機會的盤勢。
    
    【核心運作邏輯】
    1. 我們的系統不預測未來，而是統計台股過去 30 年的歷史發生機率。
    2. 我們的 7% 戰術定義了真正的「下跌波段」：從前一波段最高點回落超過 -7% 才算觸發警戒。未達 -7% 只視為震盪。
    3. 我們會計算出大盤跌破某個防線後，繼續跌到更深防線（如 -10%, -15%, -20%）的機率。
    
    【回答守則】
    1. 絕對禁止給予明確的「買進」或「賣出」建議，也不要預測「明天一定漲或跌」。
    2. 當被問及「現在該怎麼辦」，請引導使用者專注於「風報比」、歷史機率，並提醒冷靜應對。
    3. 用詞要有科技感與冷靜的量化分析師感 (如：數據顯示、模型推算、防線、能量消耗等)。
    4. 回答請盡量精簡扼要，針對使用者的提問回答，不要長篇大論。使用條列式幫助閱讀。
    5. 若用戶問無關股市跟量化分析的問題，請禮貌拒絕並引導回盤勢討論。
    """
    
    # 動態注入當前狀態
    dynamic_context = f"\n\n【當前即時盤勢數據 (你在分析時必須參考這組數據)】\n"
    if current_price:
        dynamic_context += f"- 最新大盤收盤指數：大約 {current_price:,.0f} 點\n"
        
    if current_page == "大盤下跌強度統計" and current_dd is not None:
        dynamic_context += f"- 用戶正在看「下跌分析」頁面。\n"
        dynamic_context += f"- 當前大盤從最高點已回落：-{current_dd:.1f}%\n"
        if current_dd < 7:
            dynamic_context += f"- 系統狀態：尚未達 -7% 門檻，目前僅視為一般震盪。\n"
        else:
            dynamic_context += f"- 系統狀態：已觸發 -7% 警戒，正在進行歷史回檔壓力測試。\n"
            
    elif current_page == "大盤上漲強度統計" and current_bounce is not None:
        dynamic_context += f"- 用戶正在看「上漲分析」頁面。\n"
        dynamic_context += f"- 當前大盤從起漲點已反彈：+{current_bounce:.1f}%\n"

    else:
        dynamic_context += f"- 用戶正在首頁掃描整體乖離率狀態。\n"
        
    return base_prompt + dynamic_context

def chat_with_gemini(user_message, system_prompt):
    """
    發送訊息給 Gemini 1.5 Flash 並取得回應串流
    """
    try:
        # 根據診斷，新專案支援 2.0-flash 模型，效能更強
        model = genai.GenerativeModel(
            model_name='models/gemini-2.0-flash',
            system_instruction=system_prompt
        )
        
        # 將 Streamlit 儲存的歷史對話轉換為 Gemini 格式，建立連續對話紀錄
        history = []
        if 'messages' in st.session_state:
             for msg in st.session_state.messages:
                 # 避開第一則預設的系統訊息 (我們不傳給 LLM 當成歷史)
                 if msg['role'] == 'assistant' and "我是您的專屬量化分析實習生" in msg['content']:
                     continue
                 
                 role = 'user' if msg['role'] == 'user' else 'model'
                 history.append({'role': role, 'parts': [msg['content']]})
                 
        chat = model.start_chat(history=history)
        response = chat.send_message(user_message, stream=True)
        return response
    except Exception as e:
        return f"連線至 AI 核心失敗，請檢查系統設定。錯誤代碼: {str(e)}"
