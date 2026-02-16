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
        # [핵심] 최적의 모델 자동 선택
        self.model_id = self._get_optimal_model()
        print(f"🤖 Selected AI Model: {self.model_id}")

    def _get_optimal_model(self):
        """
        Groq에서 현재 사용 가능한 모델 리스트를 받아와서,
        텍스트 요약/작문에 가장 적합한 최신 모델을 자동으로 선택함.
        """
        default_model = "llama-3.3-70b-versatile" # API 호출 실패 시 안전장치
        
        try:
            # 1. Groq의 사용 가능한 모델 리스트 가져오기
            models = self.groq.models.list()
            available_ids = [m.id for m in models.data]
            
            # 2. 우선순위 키워드 (성능 좋고 최신인 순서)
            # Llama 3.3 -> 3.2 -> 3.1 (70B가 8B보다 작문 실력이 좋음)
            priorities = [
                "llama-3.3-70b",
                "llama-3.2-90b",
                "llama-3.1-70b",
                "mixtral-8x7b",
                "llama3-70b"
            ]
            
            # 3. 우선순위 순서대로 매칭되는 모델 찾기
            for keyword in priorities:
                for model_id in available_ids:
                    if keyword in model_id:
                        return model_id
            
            # 4. 우선순위에 없으면 'llama'가 들어간 아무 모델이나 선택
            for model_id in available_ids:
                if "llama" in model_id and "70b" in model_id:
                    return model_id
                    
            return default_model

        except Exception as e:
            print(f"⚠️ Failed to fetch model list: {e}. Using default.")
            return default_model

    def _retry_request(self, func, retries=3, base_delay=5):
        """재시도 로직"""
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
        [Step 1] Perplexity: 한국 뉴스/차트 검색 -> 영어 결과 반환
        """
        additional_rule = ""
        
        if category == "k-pop":
            additional_rule = """
            [Special Rule for k-pop]
            1. **'top10' List Requirement**: You MUST search for the current **'Melon Chart (Daily or Real-time)' (멜론 차트)**.
            2. Extract the actual #1 to #10 songs from the Melon Chart.
            3. 'title': Song Title (Translate to English)
            4. 'info': Artist Name (Translate to English)
            """
        elif category == "k-culture":
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
        
        # 시스템 프롬프트: 소스는 한국어, 출력은 영어
        system_prompt = "You are a K-Entertainment expert. Search ONLY Korean domestic news/charts, but output all JSON values in English."
        
        user_prompt = f"""
        Analyze real-time trends in '{category}' based on **Korean domestic sources within the last 24 hours**.
        
        {additional_rule}

        Respond with a JSON object. **Translate all contents into English**, but keep the Korean name for reference.

        1. "people": Top 30 trending subjects (News & Issues).
           - "name_en": Name in English
           - "name_kr": Name in Korean (Required for image search)
           - "facts": 3 bullet points summarizing the news (in English)
        
        2. "top10": Top 10 Ranking.
           - "rank": 1~10
           - "title": Title in English
           - "info": Extra info in English (Artist, Rating, etc.)

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
        - 제목 'News about' 금지
        - 페르소나: Senior Editor
        """
        def _call_api():
            # 페르소나 설정: 단순 기자가 아닌 수석 에디터
            system_msg = "You are a Senior Editor at a top Global K-Pop Magazine (like Billboard or Variety)."
            
            user_msg = f"""
            Topic: {person_name_en}
            Facts: {news_facts_en}

            Write a news article **in English**.

            [Headline Rules]
            1. **Format**: Write a catchy, professional headline on the first line.
            2. ❌ **FORBIDDEN**: Do NOT start with "News about", "Update on", "Report regarding", or the person's name followed by a colon.
            3. ✅ **Style**: Use active verbs and sensational words (e.g., "Dominates", "Reveals", "Shocks", "Confirms", "Breaks Record").
            4. **Example**: 
               - BAD: "News about BTS Jin's military service"
               - GOOD: "BTS Jin Finally Discharged: Fans Celebrate Worldwide"

            [Body Rules]
            1. Write 3 paragraphs starting from the 2nd line.
            2. Use a professional yet engaging tone suitable for global fans.
            
            [Score Rule]
            - At the very end, write "###SCORE: XX" (50-99) based on viral potential.
            """
            
            # 위에서 자동 선택된 최적 모델 사용
            return self.groq.chat.completions.create(
                model=self.model_id, 
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7 
            )

        # 재시도 로직 실행 (기본 5초 대기)
        completion = self._retry_request(_call_api, base_delay=5)

        if completion:
            # Jitter (3~5초 랜덤 대기)
            rest_time = random.uniform(3, 5)
            print(f"     -> Resting for {rest_time:.2f}s...")
            time.sleep(rest_time)
            
            content = completion.choices[0].message.content
            
            # [안전장치] AI가 금지어를 썼을 경우 강제 제거
            lines = content.split('\n')
            first_line_lower = lines[0].lower().strip()
            
            # "News about"으로 시작하면 제거
            if first_line_lower.startswith("news about"):
                lines[0] = lines[0].replace("News about ", "").replace("news about ", "").strip()
                content = "\n".join(lines)
            
            return content
        
        # 실패 시 백업 메시지
        return f"{person_name_en}: Latest Updates & Highlights\n{news_facts_en}\n###SCORE: 50"
