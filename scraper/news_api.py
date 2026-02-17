import os
import json
import requests
from groq import Groq

class NewsEngine:
    def __init__(self, run_count=0, db_path="news_history.db"):
        self.run_count = run_count
        self.db_path = db_path
        # Groq API 클라이언트 설정
        self.groq_api_key = os.environ.get(f"GROQ_API_KEY{run_count + 1}") or os.environ.get("GROQ_API_KEY1")
        self.groq_client = Groq(api_key=self.groq_api_key)
        # Perplexity API 설정 (실시간 검색용)
        self.pplx_api_key = os.environ.get("PERPLEXITY_API_KEY")

        # 쿨타임 관리를 위한 DB (여기서는 로직만 유지)
        self.cool_down_hours = 6 

    def is_using_primary_key(self):
        return self.run_count == 0

    # ---------------------------------------------------------
    # [Step 1] 실시간 트렌드 인물 가져오기 (Perplexity)
    # ---------------------------------------------------------
    def get_top10_chart(self, category):
        """순위표 데이터 생성 (Groq/Perplexity 이용)"""
        # 간단히 Groq에게 현재 순위를 물어보거나, Perplexity로 검색
        try:
            prompt = f"Provide a JSON list of the current top 10 most popular {category} works or artists in South Korea right now. Format: {{'top10': [{{'rank': 1, 'title': 'Name', 'info': 'Detail', 'score': 99}}]}}"
            return self._call_ai_json(prompt)
        except:
            return json.dumps({"top10": []})

    def get_top30_people(self, category):
        """
        [실전] Perplexity를 통해 현재 해당 카테고리의 화제의 인물 30명을 가져옵니다.
        """
        print(f"📡 [{category}] Searching for trending people via AI...")
        
        prompt = (
            f"List top 30 trending people in South Korea regarding '{category}' right now. "
            "Focus on people in the news today. "
            "Return ONLY valid JSON format: "
            "{'people': [{'rank': 1, 'name_en': 'Name in English', 'name_kr': 'Korean Name'}]}"
        )
        
        # Perplexity가 없으면 Groq로 대체, 있으면 Perplexity 사용 권장
        if self.pplx_api_key:
            return self._call_perplexity(prompt)
        else:
            return self._call_ai_json(prompt)

    # ---------------------------------------------------------
    # [Step 2] 쿨타임 관리 (main.py에서 제어하므로 Pass)
    # ---------------------------------------------------------
    def is_in_cooldown(self, name):
        # main.py가 DB를 직접 조회하지 않고 엔진에게 물어볼 경우를 대비해 False 리턴
        # 실제 쿨타임 체크는 main.py의 로직이나 database.py 연동이 필요하지만
        # 복잡도를 줄이기 위해 여기서는 '작성 가능'으로 둡니다.
        return False

    def update_history(self, name, category):
        # main.py에서 DB 업데이트를 수행하므로 여기서는 패스
        pass

    # ---------------------------------------------------------
    # [Step 3] 뉴스 유무 확인 및 팩트 수집 (Perplexity)
    # ---------------------------------------------------------
    def fetch_article_details(self, name_kr, name_en, category, rank):
        """
        [실전] Perplexity를 사용하여 해당 인물의 최신 뉴스를 검색합니다.
        """
        print(f"    🔍 Searching facts for: {name_kr}...")
        
        if not self.pplx_api_key:
            return "NO NEWS FOUND (API Key Missing)"

        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3.1-sonar-small-128k-online", # 온라인 검색 모델
            "messages": [
                {
                    "role": "system",
                    "content": "You are a news reporter. Search for the latest news (last 24 hours) about this person in Korea."
                },
                {
                    "role": "user",
                    "content": f"Find latest official news about {name_kr} ({category}). If there is no significant news in the last 24 hours, reply with 'NO NEWS FOUND'. Otherwise, summarize the facts."
                }
            ]
        }
        headers = {
            "Authorization": f"Bearer {self.pplx_api_key}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            result = response.json()
            content = result['choices'][0]['message']['content']
            return content
        except Exception as e:
            print(f"    ⚠️ Search Error: {e}")
            return "Failed to fetch news."

    # ---------------------------------------------------------
    # [Step 4] 기사 작성 (Groq)
    # ---------------------------------------------------------
    def edit_with_groq(self, name, facts, category):
        """
        [실전] Groq AI를 사용하여 수집된 팩트를 바탕으로 기사를 작성합니다.
        """
        if not self.groq_api_key:
            return f"Headline: News about {name}\nAPI Key Missing."

        prompt = f"""
        You are a K-Culture journalist. Write a short, engaging news article based on these facts.
        
        Target: {name} ({category})
        Facts: {facts}
        
        Rules:
        1. Headline: Must be catchy and in English. Start with 'Headline: '.
        2. Body: Summarize the key events clearly.
        3. Score: Rate the impact of this news from 0 to 100. End with '###SCORE: [0-100]'.
        """

        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a professional journalist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Headline: Error writing article\n{e}"

    # ---------------------------------------------------------
    # 내부 유틸리티
    # ---------------------------------------------------------
    def _call_ai_json(self, prompt):
        """Groq를 이용해 JSON 응답을 받아오는 헬퍼 함수"""
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a JSON generator. Output only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return completion.choices[0].message.content
        except:
            return "{}"
    
    def _call_perplexity(self, prompt):
        """Perplexity를 이용해 최신 트렌드 JSON을 받아오는 헬퍼 함수"""
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        }
        headers = {
            "Authorization": f"Bearer {self.pplx_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            return response.json()['choices'][0]['message']['content']
        except:
            return "{}"
