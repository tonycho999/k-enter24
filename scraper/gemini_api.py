# scraper/gemini_api.py
import os
import json
import requests
import time
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_flash_model():
    """
    API에 '사용 가능한 모델 목록'을 물어보고,
    이름에 'flash'가 들어간 녀석을 찾아서 반환함.
    """
    if not API_KEY: return "models/gemini-1.5-flash"

    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            # 1. 목록에서 'flash'가 포함된 모델 찾기
            for m in models:
                if 'flash' in m['name']:
                    # print(f"   ✨ Found Flash Model: {m['name']}")
                    return m['name']
            
            # 2. Flash가 없으면 목록이라도 출력해봄 (디버깅용)
            # print(f"   ⚠️ No 'flash' model found. Available: {[m['name'] for m in models]}")
            
    except Exception as e:
        print(f"   ⚠️ Model List Error: {e}")

    # 실패 시 기본값 강제 반환
    return "models/gemini-1.5-flash"

def ask_gemini(prompt):
    """AI에게 질문 (Flash 전용)"""
    if not API_KEY:
        print("🚨 Google API Key is missing!")
        return None

    # 1. 사용할 모델명을 동적으로 찾아옴
    model_name = get_flash_model()
    
    # URL 생성
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # 2. 요청 전송
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # 3. 성공
        if resp.status_code == 200:
            try:
                text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except Exception:
                return None

        # 4. 실패 분석
        else:
            print(f"   ❌ Gemini Error {resp.status_code} on {model_name}")
            
            # [중요] 404가 뜨면 100% 설정 문제임
            if resp.status_code == 404:
                print("   👉 [Solution] The API is not enabled. Go to Google Cloud Console > Search 'Generative Language API' > Click ENABLE.")
            elif resp.status_code == 400:
                print("   👉 [Solution] Model name might be wrong or API key has no permission.")
                
            return None

    except Exception as e:
        print(f"   ❌ Connection Error: {e}")
        return None
