# scraper/gemini_api.py
import os
import json
import requests
import time
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

# Flash 모델 고정
MODEL_NAME = "models/gemini-1.5-flash"

def ask_gemini(prompt):
    """AI에게 질문 (타임아웃 방지 및 재시도 로직 포함)"""
    if not API_KEY:
        print("🚨 Google API Key is missing!")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL_NAME}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    # [중요] 최대 3번까지 재시도
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            # [수정됨] timeout을 30초 -> 60초로 늘림
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            
            # 성공 (200 OK)
            if resp.status_code == 200:
                try:
                    text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                    text = text.replace("```json", "").replace("```", "").strip()
                    return json.loads(text)
                except Exception:
                    return None

            # 404 에러 (설정 문제)
            elif resp.status_code == 404:
                print("   👉 [Solution] Please ENABLE 'Generative Language API' in Google Cloud Console.")
                return None
            
            # 429 에러 (너무 많이 요청함) -> 잠시 대기
            elif resp.status_code == 429:
                print(f"   ⏳ Too Many Requests (429). Waiting 5s... (Attempt {attempt+1}/{max_retries})")
                time.sleep(5)
                continue
                
            else:
                print(f"   ❌ Gemini Error {resp.status_code}: {resp.text[:100]}")
                return None

        # [핵심] 타임아웃 발생 시 재시도
        except requests.exceptions.Timeout:
            print(f"   ⏳ Timeout error. Google is slow. Retrying... ({attempt+1}/{max_retries})")
            time.sleep(2)
            continue
            
        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            return None

    return None
