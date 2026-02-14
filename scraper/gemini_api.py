# scraper/gemini_api.py
import os
import json
import requests
import time
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_best_model_name():
    """사용 가능한 최신 모델 자동 탐색"""
    if not API_KEY: return "models/gemini-1.5-flash"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY.strip()}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            chat_models = [m['name'] for m in models if 'generateContent' in m.get('supportedGenerationMethods', [])]
            
            # 우선순위: 1.5-flash (가장 안정적이고 빠름) -> 2.0 -> 그 외
            for m in chat_models:
                if 'gemini-1.5-flash' in m: return m
            for m in chat_models:
                if 'gemini-2.0-flash' in m: return m
            
            if chat_models: return chat_models[0]
    except:
        pass
    return "models/gemini-1.5-flash"

def ask_gemini(prompt):
    """AI에게 질문 (JSON 강제 출력 모드 적용)"""
    if not API_KEY:
        print("🚨 Google API Key is missing!")
        return None

    model_name = get_best_model_name()
    # URL에 models/ 중복 방지
    clean_model = model_name.replace("models/", "")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={API_KEY.strip()}"
    
    headers = {"Content-Type": "application/json"}
    
    # [핵심] JSON 포맷 강제 설정 (JSON Mode)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json" 
        }
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            if resp.status_code == 200:
                try:
                    # 응답 텍스트 가져오기
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    
                    # JSON 모드를 썼으므로 바로 파싱 시도
                    return json.loads(text)
                    
                except json.JSONDecodeError:
                    # JSON 파싱 실패 시 원문 출력 (디버깅용)
                    print(f"   ⚠️ JSON Parsing Failed. AI Output:\n{text[:500]}...") 
                    return None
                except Exception as e:
                    print(f"   ⚠️ Unexpected Error: {e}")
                    return None
            
            # 429(Too Many Requests) 등재
            elif resp.status_code in [429, 500, 502, 503]:
                time.sleep(2)
                continue
            
            # 400번대 에러 (모델이 JSON 모드 미지원일 수도 있음)
            else:
                print(f"   ❌ Gemini Error {resp.status_code}: {resp.text[:200]}")
                # 혹시 모델이 JSON 모드를 지원 안 해서 400이 떴다면, config 빼고 재시도
                if resp.status_code == 400 and "generationConfig" in resp.text:
                    print("   🔄 Retrying without JSON Mode...")
                    del payload["generationConfig"]
                    continue
                return None

        except Exception as e:
            print(f"   ⚠️ Connection Error (Attempt {attempt+1}): {e}")
            time.sleep(2)

    return None
