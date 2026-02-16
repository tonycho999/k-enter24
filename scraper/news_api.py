import os
import time
import json
import random
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self):
        # Perplexity (검색 및 데이터 수집)
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        # Groq (기사 작성)
        self.groq = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )

    def _retry_request(self, func, retries=3, base_delay=5):
        """재시도 로직 (Groq API 제한 대응)"""
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                wait_time = base_delay * (attempt + 1)
                print(f"  ⚠️ API Error (Attempt {attempt+1}/{retries}): {e}")
                print(f"     -> Cooling down for {wait_time} seconds...")
                time.sleep(wait_time)
        print("  ❌ Final Failure.")
        return None

    def get_trends_and_rankings(self, category):
        """
        [Step 1] Perplexity: 한국 뉴스 검색 -> 영어 결과 반환
        * 중요: 네이버 이미지 검색을 위해 'name_kr'(한국어 이름)도 같이 요청함
        """
        additional_rule = ""
        if category == "k-culture":
            additional_rule = """
            [Special Rule for k-culture]
            1. In 'people' list, DO NOT include celebrities. 
            2. Instead, include 'Hot Places', 'Food', 'Memes', 'Festivals'.
            """
        elif category == "k-entertain":
            additional_rule = """
            [Special Rule for k-entertain]
            1. 'top10' list must be 'Korean TV Variety Show' titles only.
            2. Do not include scandals or person names in top10.
            """
        
        # [핵심] 시스템 프롬프트: 소스는 한국어, 출력은 영어
        system_prompt = "You are a K-Entertainment expert. Search ONLY Korean domestic news sources from the last 24 hours."
        
        user_prompt = f"""
        Analyze real-time trends in '{category}' based on **Korean domestic news within the last 24 hours**.
        
        {additional_rule}

        Respond with a JSON object. **Translate all contents into English**, but keep the Korean name for reference.

        1. "people": Top 30 trending subjects.
           - "name_en": Name in English (e.g., "Yoo Jae-suk")
           - "name_kr": Name in Korean (e.g., "유재석") - *Required for image search*
           - "facts": 3 bullet points summarizing why they are trending (in English)
        
        2. "top10": Top 10 most popular content in {category}.
           - "rank": 1~10
           - "title": Title in English (e.g., "Running Man")
           - "info": Extra info in English (e.g., "Rating 15%")

        Output ONLY the valid JSON string. No markdown.
        """

        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            return response.choices[0].message.content, user_prompt
            
        except Exception as e:
            print(f"Perplexity API Error: {e}")
            return "{}", user_prompt

    def edit_with_groq(self, person_name_en, news_facts_en, category):
        """
        [Step 2] Groq: 영어 팩트 -> 영어 기사 작성
        """
        def _call_api():
            system_msg = "You are a professional K-Pop journalist for global fans."
            user_msg = f"""
            Topic: {person_name_en}
            Facts: {news_facts_en}

            Write a news article **in English**.
            1. **Headline**: Catchy English headline (1st line).
            2. **Body**: 3 paragraphs (from 2nd line).
            3. **Score**: End with "###SCORE: XX" (50-99) based on viral potential.
            """
            return self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )

        completion = self._retry_request(_call_api, base_delay=5)

        if completion:
            # 3~5초 랜덤 휴식 (Jitter)
            rest_time = random.uniform(3, 5)
            print(f"     -> Resting for {rest_time:.2f}s...")
            time.sleep(rest_time)
            return completion.choices[0].message.content
        
        return f"News about {person_name_en}\n{news_facts_en}\n###SCORE: 50"
