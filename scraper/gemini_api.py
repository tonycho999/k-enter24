# scraper/gemini_api.py
import os
import json
import requests
import time
import re
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
API_KEY = os.getenv("GOOGLE_API_KEY")

def ask_gemini(prompt):
    """AI에게 질문 (구글 검색 Grounding 활성화)"""
    if not API_KEY:
        print("🚨 Google API Key is missing!")
        return None

    # 최신 모델 사용 (Grounding은 Flash 모델에서 가장 빠름)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY.strip()}"

    headers = {"Content-Type": "application/json"}
    
    # [핵심] 구글 검색 기능(Grounding) 추가
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search_retrieval": {}}], 
        "generationConfig": {
            "temperature": 0.1 # 검색 결과의 사실성을 위해 낮게 설정
        }
    }

    for attempt in range(3):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                res_json = resp.json()
                text = res_json['candidates'][0]['content']['parts'][0]['text']
                
                # 검색 결과에는 잡담이 섞이기 쉬우므로 정규표현식으로 { }만 추출
                match = re.search(r'(\{.*\})', text, re.DOTALL)
                if match:
                    return json.loads(re.sub(r'[\x00-\x1F\x7F]', '', match.group(1)))
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Gemini Error: {e}")
    return None
