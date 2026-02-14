# scraper/gemini_api.py
import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_best_model_name():
    """최신 Flash 모델 자동 탐색"""
    if not API_KEY: return "models/gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY.strip()}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            chat_models = [m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
            for m in chat_models:
                if 'gemini-2.5-flash' in m: return m
            for m in chat_models:
                if 'gemini-2.0-flash' in m: return m
            for m in chat_models:
                if 'flash' in m: return m
            if chat_models: return chat_models[0]
    except:
        pass
    return "models/gemini-2.5-flash"

def ask_gemini(prompt):
    """AI에게 질문 (JSON 추출 기능 강화)"""
    if not API_KEY:
        print("🚨 Google API Key is missing!")
        return None

    model_name = get_best_model_name()
    clean_model = model_name.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={API_KEY.strip()}"
    
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if resp.status_code == 200:
                try:
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    # [핵심 수정] 잡담이 섞여 있어도 '{' 부터 '}' 까지만 추출
                    start_idx = text.find('{')
                    end_idx = text.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1:
                        json_str = text[start_idx : end_idx + 1]
                        return json.loads(json_str)
                    else:
                        print(f"   ⚠️ AI Response is not JSON: {text[:100]}...")
                        return None
                        
                except Exception as e:
                    print(f"   ⚠️ JSON Parse Error: {e}")
                    return None
            
            elif resp.status_code in [429, 500, 502, 503]:
                time.sleep(2)
                continue
            else:
                print(f"   ❌ Gemini Error {resp.status_code}: {resp.text[:100]}")
                return None

        except Exception as e:
            print(f"   ⚠️ Connection Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

    return None
