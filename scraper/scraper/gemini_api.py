import os
import json
import requests
from dotenv import load_dotenv

# 루트 경로의 .env 로드
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_best_model():
    """사용 가능한 모델 중 최신 모델 자동 선택"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            # Pro -> Flash 순서로 우선순위
            for m in models:
                if 'generateContent' in m['supportedGenerationMethods'] and 'gemini-1.5-pro' in m['name']:
                    return m['name']
            for m in models:
                if 'generateContent' in m['supportedGenerationMethods'] and 'gemini-1.5-flash' in m['name']:
                    return m['name']
    except Exception:
        pass
    return "models/gemini-1.5-flash-latest"

def ask_gemini(prompt):
    """AI에게 질문하고 JSON 응답 받기"""
    model_name = get_best_model()
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            try:
                text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                # JSON 포맷 정리
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except (KeyError, json.JSONDecodeError):
                return None
        return None
    except Exception as e:
        print(f"   ❌ Gemini Error: {e}")
        return None
