import os
import requests
import time
import re
import random  # 랜덤 시간 생성을 위해 추가
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
            # 1. 1.5-flash-latest (무료 티어에서 가장 안정적임)
            for m in models:
                if "gemini-1.5-flash-latest" in m['name']:
                    return m['name']
            # 2. 최신인 2.0 시리즈
            for m in models:
                if "gemini-2.0-flash" in m['name'] and 'generateContent' in m.get('supportedGenerationMethods', []):
                    return m['name']
            return models[0]['name']
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def ask_gemini_with_search_debug(prompt):
    if not API_KEY: return None, "API_KEY_MISSING"

    model_name = get_best_available_model()
    print(f"🤖 선택된 최적 모델: {model_name}")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={API_KEY.strip()}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search_retrieval": {}}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2048}
    }

    # API 호출 전후에 카테고리 간 간격을 벌리기 위해 main.py나 호출 루프에서 사용할 랜덤 함수
    def random_sleep():
        wait_ms = random.randint(60000, 180000) # 60초 ~ 180초 사이의 ms
        wait_sec = wait_ms / 1000.0
        print(f"💤 할당량 보호를 위해 {wait_ms}ms ({wait_sec:.2f}초) 동안 휴식합니다...")
        time.sleep(wait_sec)

    for attempt in range(3): # 시도 횟수를 3회로 증가
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            
            # 429 에러(할당량 초과) 발생 시 즉시 랜덤 휴식 후 재시도
            if resp.status_code == 429:
                print(f"⚠️ 429 에러 감지! 모델: {model_name}")
                random_sleep()
                continue

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
            last_err = str(e)
            random_sleep() # 예외 발생 시에도 휴식
            
    return None, f"EXCEPTION: {last_err}"
