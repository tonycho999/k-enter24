import os
import time
import json
import re
import random
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self, run_count=0):
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        
        # ---------------------------------------------------------
        # [키 로테이션] Run Count 기반 (0~7)
        # ---------------------------------------------------------
        self.groq_keys = []
        for i in range(1, 9): 
            key_name = f"GROQ_API_KEY{i}"
            val = os.environ.get(key_name)
            if val: self.groq_keys.append(val)
        
        if not self.groq_keys:
            self.current_key = None
            self.current_key_index = -1
        else:
            self.current_key_index = run_count % len(self.groq_keys)
            self.current_key = self.groq_keys[self.current_key_index]
            print(f"🔑 [Key Rotation] Run: {run_count} -> Using GROQ_API_KEY{self.current_key_index + 1}")

        self.groq = self._create_groq_client()
        self.model_id = self._get_optimal_model()

    def _create_groq_client(self):
        if not self.current_key: return None
        return Groq(api_key=self.current_key)

    def is_using_primary_key(self):
        return self.current_key_index == 0

    def _get_optimal_model(self):
        default = "llama-3.3-70b-versatile"
        if not self.groq: return default
        try:
            models = self.groq.models.list()
            ids = [m.id for m in models.data]
            for k in ["llama-3.3-70b", "llama-3.2-90b", "llama-3.1-70b", "mixtral"]:
                for mid in ids:
                    if k in mid: return mid
            return default
        except: return default

    # ----------------------------------------------------------------
    # [1단계] 순위 및 차트 데이터 수집 (Top 30 인물 리스트 + Top 10 차트)
    # ----------------------------------------------------------------
    def get_rankings_list(self, category):
        """
        인물 30위 리스트와 Top 10 차트 데이터만 JSON으로 가져옵니다. (기사 내용은 아직 안 가져옴)
        """
        
        # 1. Top 10 차트 소스 정의
        chart_instruction = ""
        if category == "k-pop":
            chart_instruction = "Source: **Melon Chart (Real-time or Daily)**. Target: Song Titles & Artists."
        elif category == "k-drama":
            chart_instruction = "Source: **Naver TV Ratings (Drama)**. Target: Drama Titles only."
        elif category == "k-movie":
            chart_instruction = "Source: **Naver Movie Box Office**. Target: Movie Titles (Foreign allowed)."
        elif category == "k-entertain":
            chart_instruction = "Source: **Naver TV Ratings (Variety/Entertainment)**. Target: Show Titles."
        elif category == "k-culture":
            chart_instruction = "Source: Current Trending Keywords (Place, Festival, Food). Target: Keywords."

        # 2. 인물(People) 정의
        people_instruction = ""
        if category == "k-pop": people_instruction = "Singers / Idol Groups"
        elif category == "k-drama": people_instruction = "Actors / PDs (Drama related)"
        elif category == "k-movie": people_instruction = "Actors / Directors (Movie related)"
        elif category == "k-entertain": people_instruction = "Variety Show Cast / MCs / PDs"
        elif category == "k-culture": people_instruction = "Figures related to K-Culture (EXCLUDING Celebrities)"

        system_prompt = "You are a specialized researcher for Korean Entertainment. Search ONLY Korean domestic sources (Naver, Daum, Melon)."
        
        user_prompt = f"""
        Perform a search on **Korean domestic portals (Naver, Melon)** within the **last 24 hours**.
        Category: {category}

        **Task 1: Top 10 Ranking Chart**
        {chart_instruction}
        - Get the actual current ranking data. Translate Titles/Names to English.

        **Task 2: Top 30 Trending People (Buzz Ranking)**
        - Identify the Top 30 people ({people_instruction}) mentioned most in Korean news in the last 24 hours.
        - Rank them from 1 to 30 based on news volume/buzz.
        - Output JUST their names (English & Korean).

        **Output JSON Format ONLY:**
        {{
            "top10": [
                {{"rank": 1, "title": "...", "info": "..."}}, ...
            ],
            "people": [
                {{"rank": 1, "name_en": "...", "name_kr": "..."}},
                ...
                {{"rank": 30, "name_en": "...", "name_kr": "..."}}
            ]
        }}
        """

        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ PPLX List Error: {e}")
            return "{}"

    # ----------------------------------------------------------------
    # [2단계] 개별 인물 심층 기사 조사 (기사 N개 참조)
    # ----------------------------------------------------------------
    def fetch_article_details(self, name_kr, name_en, category, rank):
        """
        특정 인물에 대해 한국 뉴스 N개를 읽고 영어로 요약합니다.
        """
        # 순위에 따른 참조 기사 수 결정
        article_count = 2
        if rank <= 3: article_count = 4
        elif rank <= 10: article_count = 3
        
        system_prompt = "You are a reporter summarizing Korean news for global readers."
        
        user_prompt = f"""
        Search for **Korean news articles** about '{name_kr}' ({category}) published within the **last 24 hours**.
        
        **Constraint:**
        1. Read at least **{article_count} distinct articles**.
        2. Summarize the key facts in English.
        3. Ignore international sources (Allkpop, etc). Use ONLY Naver/Dispatch/Korean media.
        
        Output format: Just the factual summary points in English.
        """
        
        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Failed to fetch details for {name_en}."

    # ----------------------------------------------------------------
    # [3단계] Groq 기사 작성
    # ----------------------------------------------------------------
    def edit_with_groq(self, name_en, facts, category):
        system_msg = "You are a Senior Editor at a top Global K-Pop Magazine."
        user_msg = f"""
        Topic: {name_en}
        Facts: {facts}
        
        Write a news article **in English**.
        - Headline: Catchy, No "News about" prefix.
        - Body: 3 paragraphs, professional journalist tone.
        - End with "###SCORE: XX" (10-99).
        """
        try:
            completion = self.groq.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.7
            )
            content = completion.choices[0].message.content
            # 후처리
            lines = content.split('\n')
            if lines[0].lower().startswith("news about"):
                lines[0] = lines[0].replace("News about ", "").replace("news about ", "").strip()
                return "\n".join(lines)
            return content
        except:
            return f"{name_en}: Latest Updates\n{facts}\n###SCORE: 50"
