import os
import json
import requests
import re
from datetime import datetime, timedelta
from groq import Groq

class NewsEngine:
    def __init__(self, run_count=0, db_path="news_history.db"):
        self.run_count = run_count
        
        self.groq_api_key = os.environ.get(f"GROQ_API_KEY{run_count + 1}") or os.environ.get("GROQ_API_KEY1")
        self.pplx_api_key = os.environ.get("PERPLEXITY_API_KEY")
        
        self.groq_client = Groq(api_key=self.groq_api_key)

    def is_using_primary_key(self):
        return self.run_count == 0

    # ---------------------------------------------------------
    # [설정] 카테고리별 검색 타겟 (구체적 지시사항 포함)
    # ---------------------------------------------------------
    def _get_target_description(self, category):
        """
        카테고리별 검색 대상을 '24시간 내 네이버 뉴스 최다 언급' 조건으로 구체적으로 정의합니다.
        """
        mapping = {
            "k-pop": "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스 기사에서 가장 많이 언급된 대한민국 가수 및 아이돌 그룹 30명 (Top 30 K-Pop Singers/Idols with highest news coverage in last 24h)",
            "k-drama": "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스 기사에서 가장 많이 언급된 한국 드라마 출연 배우 30명 (Top 30 K-Drama Actors with highest news coverage in last 24h)",
            "k-movie": "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스 기사에서 가장 많이 언급된 한국 영화 배우 및 감독 30명 (Top 30 Korean Movie Actors/Directors with highest news coverage in last 24h)",
            "k-entertain": "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스 기사에서 가장 많이 언급된 한국 예능인, 방송인, 개그맨 30명 (Top 30 Korean Entertainers/Comedians with highest news coverage in last 24h)",
            "k-culture": "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스 기사에서 가장 많이 언급된 한국 문화계 인사, 유명 유튜버 및 인플루언서 30명 (Top 30 Korean Cultural Figures/Influencers with highest news coverage in last 24h)"
        }
        # 매핑되지 않은 카테고리는 기본값 설정
        return mapping.get(category, "현재 시간으로부터 과거 24시간 이내에 네이버 뉴스에서 가장 많이 언급된 유명인 30명")

    # ---------------------------------------------------------
    # [유틸] 현재 시간 (서버 시간 기준)
    # ---------------------------------------------------------
    def _get_current_time_str(self):
        """AI에게 알려줄 현재 시간 포맷"""
        now = datetime.now()
        # 예: 2026년 02월 17일 15시 30분
        return now.strftime("%Y년 %m월 %d일 %H시 %M분")

    # ---------------------------------------------------------
    # [핵심] JSON 청소기 (오류 방지)
    # ---------------------------------------------------------
    def _clean_and_parse_json(self, text):
        try:
            # 마크다운 제거
            match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
            if match: text = match.group(1)
            # 중괄호 추출
            start = text.find('{')
            end = text.rfind('}')
            if start != -1 and end != -1: text = text[start:end+1]
            return json.loads(text)
        except:
            return {}

    # ---------------------------------------------------------
    # [Step 1] Top 10 차트
    # ---------------------------------------------------------
    def get_top10_chart(self, category):
        current_time = self._get_current_time_str()
        target_desc = self._get_target_description(category)
        
        print(f"📊 [{category}] Fetching Top 10 Chart ({current_time} 기준)...")
        
        if not self.pplx_api_key: return "{}"

        # 프롬프트: 24시간 뉴스 언급량 기준 차트 생성
        prompt = (
            f"Current Time: {current_time}. "
            f"Search Source: ONLY site:news.naver.com. "
            f"Target Description: {target_desc}. "
            "Task: Identify the Top 10 specific works or artists that fit the target description. "
            "Ranking Criteria: Strictly based on the volume of official news articles published in the last 24 hours. "
            "Output Requirement: Translate Titles and Names into English. "
            "Return ONLY valid JSON. "
            "Format: {'top10': [{'rank': 1, 'title': 'English Name/Title', 'info': 'Reason for trend', 'score': 95}]}"
        )
        
        raw_text = self._call_perplexity_text(prompt)
        parsed_json = self._clean_and_parse_json(raw_text)
        return json.dumps(parsed_json)

    # ---------------------------------------------------------
    # [Step 2] 인물 30인 리스트 (핵심)
    # ---------------------------------------------------------
    def get_top30_people(self, category):
        current_time = self._get_current_time_str()
        target_desc = self._get_target_description(category)
        
        print(f"📡 [{category}] Searching for Top 30 People ({current_time} 기준)...")
        
        if not self.pplx_api_key:
            print("   > ⚠️ Perplexity API Key missing.")
            return "{}"

        # 프롬프트: 구체적인 타겟 설명을 바탕으로 리스트 추출
        prompt = (
            f"Current Time: {current_time}. "
            f"Search Source: ONLY site:news.naver.com. "
            f"Target: {target_desc}. "
            "Task: List the top 30 people exactly matching the target description above. "
            "Constraint 1: Exclude people who are generally famous but NOT in the news within the last 24 hours. "
            "Constraint 2: Sort the list by news coverage volume (Highest mention count first). "
            "Output Requirement: Translate Names into English. "
            "Return ONLY valid JSON. "
            "Format: {'people': [{'rank': 1, 'name_en': 'English Name', 'name_kr': 'Korean Name'}]}"
        )
        
        try:
            raw_text = self._call_perplexity_text(prompt)
            parsed_data = self._clean_and_parse_json(raw_text)
            
            if "people" in parsed_data and len(parsed_data["people"]) > 0:
                return json.dumps(parsed_data)
            else:
                print(f"   > ⚠️ Empty data. Raw text start: {raw_text[:100]}...")
                return "{}"
        except Exception as e:
            print(f"   > ⚠️ Search Failed: {e}")
            return "{}"

    # ---------------------------------------------------------
    # [Step 3] 쿨타임 (Pass - main.py에서 처리)
    # ---------------------------------------------------------
    def is_in_cooldown(self, name):
        return False

    def update_history(self, name, category):
        pass

    # ---------------------------------------------------------
    # [Step 4] 팩트 체크 (24시간 이내 기사만)
    # ---------------------------------------------------------
    def fetch_article_details(self, name_kr, name_en, category, rank):
        current_time = self._get_current_time_str()
        print(f"    🔍 Searching facts for: {name_kr} (Latest 24h)...")
        
        if not self.pplx_api_key:
            return "NO NEWS FOUND (API Key Missing)"

        # 팩트 체크도 24시간 이내로 강력하게 제한
        prompt = (
            f"Current Time: {current_time}. "
            f"Search Source: ONLY site:news.naver.com. "
            f"Target Person: '{name_kr}'. "
            "Task: Find the official news articles published within the last 24 hours. "
            "Output Requirement: Summarize the key facts in English (3 sentences). "
            "Constraint: If there are no news articles published in the last 24 hours, explicitly say 'NO NEWS FOUND'."
        )

        try:
            content = self._call_perplexity_text(prompt)
            if not content or len(content) < 10:
                return "Failed to fetch news."
            return content
        except Exception as e:
            print(f"    ⚠️ Fact Check Error: {e}")
            return "Failed to fetch news."

    # ---------------------------------------------------------
    # [Step 5] 기사 작성 (Groq)
    # ---------------------------------------------------------
    def edit_with_groq(self, name, facts, category):
        if "NO NEWS FOUND" in facts or "Failed" in facts:
            return "Headline: Error\nNO NEWS FOUND"

        prompt = f"""
        You are a K-Culture journalist. Write a short news article.
        
        Target: {name} ({category})
        Facts from Naver News (Last 24h): {facts}
        
        Format:
        Headline: [Catchy English Title]
        [Body text in English]
        ###SCORE: [0-100]
        """
        try:
            completion = self.groq_client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Headline: Error\n{e}"

    # ---------------------------------------------------------
    # API 호출 헬퍼
    # ---------------------------------------------------------
    def _call_perplexity_text(self, prompt):
        url = "https://api.perplexity.ai/chat/completions"
        payload = {
            "model": "llama-3.1-sonar-small-128k-online",
            "messages": [{"role": "user", "content": prompt}]
        }
        headers = {
            "Authorization": f"Bearer {self.pplx_api_key}",
            "Content-Type": "application/json"
        }
        try:
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return ""
        except:
            return ""
