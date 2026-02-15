import os
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def ask_gemini_with_search(prompt):
    if not API_KEY:
        print("🚨 Google API Key missing")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY.strip()}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search_retrieval": {}}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                res_json = resp.json()
                raw_text = res_json['candidates'][0]['content']['parts'][0]['text']
                
                # 1. 구글 검색 주석([1], [2] 등) 제거
                raw_text = re.sub(r'\[\d+\]', '', raw_text)
                
                # 2. 향상된 태그 기반 파싱 (전방 탐색 활용)
                parsed_data = {}
                
                def extract_tag(tag, text):
                    # AI가 **##TAG##**: 내용 ## 식의 변칙을 써도 대응 가능한 패턴
                    # 다음 태그가 나오거나 문서가 끝날 때까지 긁어옵니다.
                    pattern = rf"(?:\*+|#+)?{tag}(?:\*+|#+)?[:\s-]*(.*?)(?=\s*(?:#+|제목|대상|배경|기사|순위|TARGET|HEADLINE|CONTENT|RANKINGS)|$)"
                    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                    if not match:
                        # 좀 더 단순한 패턴으로 재시도
                        pattern = rf"##{tag}##\s*(.*?)(?=\s*##|$)"
                        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                    
                    return match.group(1).strip() if match else None

                parsed_data['target_kr'] = extract_tag("TARGET_KR", raw_text)
                parsed_data['target_en'] = extract_tag("TARGET_EN", raw_text)
                parsed_data['headline'] = extract_tag("HEADLINE", raw_text)
                parsed_data['content'] = extract_tag("CONTENT", raw_text)
                parsed_data['raw_rankings'] = extract_tag("RANKINGS", raw_text)

                if parsed_data['headline'] and parsed_data['content']:
                    return parsed_data
                else:
                    print(f"⚠️ 태그 인식 실패. 원문 일부: {raw_text[:150]}...")

            time.sleep(5)
        except Exception as e:
            print(f"⚠️ 시도 {attempt+1} 실패: {e}")
    return None
