import google.generativeai as genai
import streamlit as st
import os

def check_models():
    # 讀取金鑰
    api_key = ""
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        with open(secrets_path, "r", encoding="utf-8") as f:
            import re
            match = re.search(r'GEMINI_API_KEY\s*=\s*"(.*?)"', f.read())
            if match:
                api_key = match.group(1)
    
    if not api_key:
        print("未找到金鑰")
        return

    genai.configure(api_key=api_key)
    print(f"正在使用金鑰: {api_key[:10]}...")
    
    try:
        print("\n--- 可用模型列表 ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"模型名稱: {m.name}")
    except Exception as e:
        print(f"發生錯誤: {e}")

if __name__ == "__main__":
    check_models()
