import os
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def ask_gemini_with_search_debug(prompt):
    if not API_KEY: return None, "API_KEY_MISSING"

    # [수정] 구글 검색(tools) 기능을 지원하는 v1beta 엔드포인트로 복구
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY.strip()}"
    headers = {"Content-Type": "application/json"}
    
    # [구조 최적화] v1beta 규격에 맞춘 페이로드
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{
            "google_search_retrieval": {} # 구글 실시간 검색 활성화
        }],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
            "maxOutputTokens": 2048
        }
    }

    for attempt in range(2):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            
            # 에러 발생 시 상세 로그 기록
            if resp.status_code != 200:
                error_detail = f"HTTP_{resp.status_code}: {resp.text}"
                return None, error_detail

            res_json = resp.json()
            
            # 응답 구조에서 텍스트 추출 (v1beta 대응)
            try:
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
            except (KeyError, IndexError):
                return None, f"RESPONSE_STRUCTURE_ERROR: {str(res_json)}"
            
            # 검색 주석([1]) 제거
            raw_text = re.sub(r'\[\d+\]', '', raw_text)
            
            # 태그 파싱 로직 (기존과 동일하되 더 견고하게)
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
            last_err = f"EXCEPTION: {str(e)}"
            
    return None, last_err
