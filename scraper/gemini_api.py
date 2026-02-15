import os
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def get_best_available_model():
    """현재 API 키로 사용 가능한 모델 중 가장 적합한 모델명을 자동으로 찾음"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            # 1. 최신인 2.0 시리즈 검색
            for m in models:
                if "gemini-2.0-flash" in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m['name']
            # 2. 없으면 1.5 시리즈 검색
            for m in models:
                if "gemini-1.5-flash" in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m['name']
            # 3. 그것도 없으면 리스트의 첫 번째 모델 반환
            return models[0]['name']
        return "models/gemini-1.5-flash" # 실패 시 기본값
    except:
        return "models/gemini-1.5-flash"

def ask_gemini_with_search_debug(prompt):
    if not API_KEY: return None, "API_KEY_MISSING"

    # [핵심] 시스템이 스스로 사용할 모델을 결정합니다.
    model_name = get_best_available_model()
    print(f"🤖 선택된 최적 모델: {model_name}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY.strip()}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search_retrieval": {}}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code != 200:
                return None, f"HTTP_{resp.status_code}: {resp.text} (Model: {model_name})"

            res_json = resp.json()
            raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            
            # [태그 파싱 로직]
            def get_content(tag, text):
                pattern = rf"(?:\*+|#+)?{tag}(?:\*+|#+)?[:\s-]*(.*?)(?=\s*(?:#+|TARGET|HEADLINE|CONTENT|RANKINGS)|$)"
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                return match.group(1).strip() if match else None

            parsed = {
                'target_kr': get_content("TARGET_KR", raw_text),
                'target_en': get_content("TARGET_EN", raw_text),
                'headline': get_content("HEADLINE", raw_text),
                'content': get_content("CONTENT", raw_text),
                'raw_rankings': get_content("RANKINGS", raw_text)
            }

            if parsed['headline'] and parsed['content']:
                return parsed, raw_text
            return None, raw_text

        except Exception as e:
            time.sleep(5)
            last_err = str(e)
            
    return None, f"EXCEPTION: {last_err}"
