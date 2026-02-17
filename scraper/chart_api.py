import os
import json
from datetime import datetime, timedelta, timezone
from openai import OpenAI

class ChartEngine:
    def __init__(self):
        # Perplexity API Client
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )

    def get_top10_chart(self, category):
        """
        Perplexity에게 '현재 시간'을 주고 검색하여 차트를 가져옵니다.
        크롤링을 사용하지 않습니다.
        """
        # 1. 한국 시간(KST) 구하기
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        # 예: "2024년 5월 21일 15시"
        current_time_str = now.strftime("%Y년 %m월 %d일 %H시")
        
        # 2. 카테고리별 검색어 및 타겟 설정
        search_keywords = ""
        target_info = ""
        
        if category == "k-pop":
            # [핵심] 멜론 공홈 대신 실시간 정보가 올라오는 커뮤니티/뉴스 검색 유도
            search_keywords = f"{current_time_str} 멜론 실시간 차트 1위 10위 인스티즈 더쿠 트위터"
            target_info = "Target: Song Titles & Artists (Melon Real-time)."
        elif category == "k-drama":
            search_keywords = f"{current_time_str} 기준 한국 드라마 시청률 순위 닐슨코리아"
            target_info = "Target: Drama Titles."
        elif category == "k-movie":
            search_keywords = f"{current_time_str} 기준 한국 박스오피스 영화 순위"
            target_info = "Target: Movie Titles."
        elif category == "k-entertain":
            search_keywords = f"{current_time_str} 기준 한국 예능 프로그램 시청률 순위"
            target_info = "Target: Variety Show Titles."
        elif category == "k-culture":
            search_keywords = f"{current_time_str} 한국 요즘 유행하는 핫플레이스 음식 트렌드"
            target_info = "Target: Trending Keywords (Place, Food)."

        # 3. 프롬프트 작성
        system_prompt = "You are a specialized researcher. Search ONLY Korean domestic sources to find the latest real-time rankings."
        
        user_prompt = f"""
        **Current Time (KST): {current_time_str}**
        
        Perform a search for: "**{search_keywords}**"
        
        **Task: Extract the Top 10 Ranking Chart**
        Category: {category}
        {target_info}
        
        **Strict Constraints:**
        1. **DATA MUST BE FROM {current_time_str} (or within the last 1-2 hours).**
        2. Do NOT use data from last year or last month. Check the upload time of the search results.
        3. If specific ranking numbers aren't found, find the most mentioned/trending items right now.
        4. **Translate all Titles/Names to English.**

        **Output JSON Format ONLY:**
        {{
            "top10": [
                {{"rank": 1, "title": "...", "info": "..."}},
                ...
                {{"rank": 10, "title": "...", "info": "..."}}
            ]
        }}
        """
        
        print(f"  🔍 [Perplexity] Searching Chart for '{category}' at {current_time_str}...")
        
        try:
            # 타임아웃 180초 (검색 시간이 좀 걸릴 수 있음)
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                timeout=180
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Chart API Error: {e}")
            return "{}"
