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

    def get_rankings_list(self, category):
        chart_inst = ""
        ppl_inst = ""

        if category == "k-pop":
            chart_inst = "Source: **Melon Chart (Real-time)**. Target: Song Titles & Artists."
            ppl_inst = "Singers / Idol Groups"
        elif category == "k-drama":
            chart_inst = "Source: **Naver TV Ratings (Drama)**. Target: Drama Titles."
            ppl_inst = "Actors / PDs (Drama related)"
        elif category == "k-movie":
            chart_inst = "Source: **Naver Movie Box Office**. Target: Movie Titles."
            ppl_inst = "Actors / Directors (Movie related)"
        elif category == "k-entertain":
            chart_inst = "Source: **Naver TV Ratings**. Target: Show Titles."
            ppl_inst = "Variety Show Cast / MCs"
        elif category == "k-culture":
            chart_inst = "Source: Trending Keywords. Target: Place, Festival, Food."
            ppl_inst = "Figures related to K-Culture (EXCLUDING Celebrities)"

        system_prompt = "You are a specialized researcher. Search ONLY Korean domestic sources (Naver, Daum, Melon)."
        
        user_prompt = f"""
        Search **Korean domestic portals** within the **last 24 hours**. Category: {category}

        **Task 1: Top 10 Ranking Chart**
        {chart_inst}
        - Translate Titles/Names to English.

        **Task 2: Top 30 Trending People (Buzz Ranking)**
        - Identify Top 30 people ({ppl_inst}) mentioned most in Korean news (Naver News).
        - Rank them 1 to 30 based on news volume.
        - Output JUST their names (English & Korean).

        **Output JSON ONLY:**
        {{
            "top10": [{{"rank": 1, "title": "...", "info": "..."}}, ...],
            "people": [{{"rank": 1, "name_en": "...", "name_kr": "..."}}, ...]
        }}
        """

        print(f"  🔍 [Perplexity] Searching Trends for {category}... (Timeout: 180s)")
        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.1,
                timeout=180
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ PPLX List Error: {e}")
            return "{}"

    def fetch_article_details(self, name_kr, name_en, category, rank):
        # 랭크별 기사 수 조절
        article_count = 2
        if rank <= 3: article_count = 4
        elif rank <= 10: article_count = 3
        
        system_prompt = "You are a reporter summarizing Korean news."
        user_prompt = f"""
        Search **Korean news** about '{name_kr}' ({category}) in the **last 24 hours**.
        - Read {article_count} distinct articles.
        - Summarize key facts in English.
        - Use ONLY Naver/Dispatch/Korean media.
        """
        
        print(f"    ... [Perplexity] Digging details for {name_en} (Rank {rank})...")
        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.1,
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    ⚠️ Detail Fetch Error: {e}")
            return "Failed."

    def edit_with_groq(self, name_en, facts, category):
        system_msg = "You are a Senior Editor at a top Global K-Pop Magazine."
        user_msg = f"""
        Topic: {name_en}
        Facts: {facts}
        Write a news article **in English**.
        - Headline: Catchy, No "News about" prefix.
        - Body: 3 paragraphs, professional tone.
        - End with "###SCORE: XX".
        """
        try:
            completion = self.groq.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": user_msg}],
                temperature=0.7,
                timeout=60
            )
            content = completion.choices[0].message.content
            lines = content.split('\n')
            if lines[0].lower().startswith("news about"):
                lines[0] = lines[0].replace("News about ", "").replace("news about ", "").strip()
                return "\n".join(lines)
            return content
        except Exception as e:
            print(f"    ⚠️ Groq Error: {e}")
            return f"{name_en}: Latest Updates\n{facts}\n###SCORE: 50"
