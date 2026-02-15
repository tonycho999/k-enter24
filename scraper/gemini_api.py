import os
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def ask_gemini_with_search_debug(prompt):
    if not API_KEY: return None, "API_KEY_MISSING"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY.strip()}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search_retrieval": {}}],
        "generationConfig": {"temperature": 0.7, "topP": 0.9}
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                
                # 정규표현식 태그 추출 로직
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

                # 파싱 성공 여부와 상관없이 원문을 함께 보냄
                if parsed['headline'] and parsed['content']:
                    return parsed, raw_text
                return None, raw_text # 파싱 실패 시 원문만 보냄
            
            return None, f"HTTP_ERROR_{resp.status_code}"
        except Exception as e:
            time.sleep(5)
            last_err = str(e)
            
    return None, f"EXCEPTION: {last_err}"
