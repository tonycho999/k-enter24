import os
import json
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
            "temperature": 0.0, # 가장 기계적이고 일관된 답변 유도
            "topP": 0.8
        }
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                res_json = resp.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                
                # 1. 텍스트 내의 모든 구글 검색 주석([1], [2] 등)을 선제적으로 제거
                text = re.sub(r'\[\d+\]', '', text)
                
                # 2. 마크다운 기호 제거
                text = text.replace("```json", "").replace("```", "")

                # 3. 가장 바깥쪽의 { } 구간 추출
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    
                    # 4. JSON 내부의 줄바꿈 문자가 파싱을 깨뜨리지 않게 처리
                    # 본문 내 실제 줄바꿈을 \\n으로 치환
                    json_str = json_str.replace('\n', '\\n')
                    # 하지만 키/값 사이의 구조적 줄바꿈은 복원해야 하므로 다시 정제 (복잡한 작업 생략하고 클린업)
                    clean_json = re.sub(r'[\x00-\x1F\x7F]', '', json_str)
                    
                    try:
                        # 텍스트가 이미 정제되었으므로 바로 로드 시도
                        return json.loads(json_str) 
                    except json.JSONDecodeError:
                        # 위에서 \n 치환이 문제를 일으켰을 수 있으므로 원본 매치에서 다시 시도
                        try:
                            return json.loads(match.group(1).strip())
                        except Exception as e:
                            print(f"❌ JSON 파싱 에러 상세: {e}")
            time.sleep(5)
        except Exception as e:
            print(f"⚠️ 시도 {attempt+1} 실패: {e}")
    return None
