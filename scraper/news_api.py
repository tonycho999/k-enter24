import os
import time
import json
import re
import random
from datetime import datetime, timedelta, timezone
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self):
        # Perplexity (검색 및 데이터 수집)
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        
        # ---------------------------------------------------------
        # [핵심] 시간 기반 키 로테이션 (Time-based Key Rotation)
        # ---------------------------------------------------------
        self.groq_keys = []
        
        # [수정] 명확하게 1번부터 8번까지만 로드 (range(1, 9) -> 1,2,3,4,5,6,7,8)
        for i in range(1, 9): 
            key_name = f"GROQ_API_KEY{i}"
            val = os.environ.get(key_name)
            if val:
                self.groq_keys.append(val)
        
        if not self.groq_keys:
            print("⚠️ No Groq API Keys found (Checked GROQ_API_KEY1...8)!")
            self.current_key = None
            self.current_key_index = -1
        else:
            # [현재 시간(KST) 구하기]
            kst_zone = timezone(timedelta(hours=9))
            current_hour = datetime.now(kst_zone).hour
            
            # [공식] 시간 % 키 개수
            # 키가 8개면: 0시->Key1, 1시->Key2 ... 7시->Key8, 8시->Key1 ...
            self.current_key_index = current_hour % len(self.groq_keys)
            self.current_key = self.groq_keys[self.current_key_index]
            
            # (인덱스는 0부터 시작하므로 출력할 때는 +1)
            print(f"🔑 [Key Rotation] Hour: {current_hour}h -> Using GROQ_API_KEY{self.current_key_index + 1}")

        # [필수] Groq 클라이언트 및 모델 초기화
        self.groq = self._create_groq_client()
        self.model_id = self._get_optimal_model()
        print(f"🤖 Selected AI Model: {self.model_id}")

    def _create_groq_client(self):
        if not self.current_key: return None
        return Groq(api_key=self.current_key)

    def _switch_api_key(self):
        """
        [비상용] 만약 할당된 시간의 키가 터지면(429), 다음 키로 임시 교체
        """
        if len(self.groq_keys) <= 1:
            return False
        
        # 다음 순번으로 강제 이동
        self.current_key_index = (self.current_key_index + 1) % len(self.groq_keys)
        self.current_key = self.groq_keys[self.current_key_index]
        self.groq = self._create_groq_client()
        print(f"  🔄 [Emergency Switch] Switched to Key #{self.current_key_index + 1}")
        return True

    # ------------------------------------------------------------------
    # [Helper] 현재 Key 1번을 쓰고 있는지 확인하는 함수 (랭킹 업데이트용)
    # ------------------------------------------------------------------
    def is_using_primary_key(self):
        # 인덱스 0번이 GROQ_API_KEY1 입니다.
        return self.current_key_index == 0

    def _get_optimal_model(self):
        """
        Groq에서 현재 사용 가능한 모델 리스트를 받아와서,
        텍스트 요약/작문에 가장 적합한 최신 모델을 자동으로 선택함.
        """
        default_model = "llama-3.3-70b-versatile" # API 호출 실패 시 안전장치
        if not self.groq: return default_model
        
        try:
            # 1. Groq의 사용 가능한 모델 리스트 가져오기
            models = self.groq.models.list()
            available_ids = [m.id for m in models.data]
            
            # 2. 우선순위 키워드 (성능 좋고 최신인 순서)
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

    def _extract_wait_time(self, error_message):
        """에러 메시지에서 대기 시간 추출"""
        try:
            match = re.search(r'in (\d+)m(\d+\.?\d*)s', error_message)
            if match:
                return (float(match.group(1)) * 60) + float(match.group(2)) + 2
            match_s = re.search(r'in (\d+\.?\d*)s', error_message)
            if match_s:
                return float(match_s.group(1)) + 2
            return 10
        except:
            return 10

    def _retry_request(self, func, retries=3, base_delay=5):
        """재시도 로직 (429 에러 시 키 교체 시도)"""
        for attempt in range(retries):
            try:
                return func()
            except Exception as e:
                error_str = str(e)
                print(f"  ⚠️ API Error (Attempt {attempt+1}/{retries}): {e}")
                
                if "429" in error_str or "Rate limit" in error_str:
                    # 키 교체 시도 (비상시)
                    if self._switch_api_key():
                        time.sleep(1)
                        continue
                    
                    # 키 교체 실패 시 대기
                    wait_time = self._extract_wait_time(error_str)
                    if wait_time > 300:
                         print(f"     -> Wait time too long ({wait_time}s). Skipping.")
                         return None
                    print(f"     -> Cooling down for {wait_time:.1f}s...")
                    time.sleep(wait_time)
                else:
                    wait_time = base_delay * (attempt + 1)
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
        
        system_prompt = "You are a K-Entertainment expert. Search ONLY Korean domestic news/charts, but output all JSON values in English."
        
        user_prompt = f"""
        Analyze real-time trends in '{category}' based on **Korean domestic sources within the last 24 hours**.
        
        {additional_rule}

        Respond with a JSON object. **Translate all contents into English**, but keep the Korean name for reference.

        1. "people": Top 30 trending subjects (News & Issues).
           - "name_en": Name in English
           - "name_kr": Name in Korean (Required for image search)
           - "facts": 3 bullet points summarizing the news (in English)
           - "link": Original Korean news link
        
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
            1. Style: Write in the style of a professional Korean entertainment journalist, known for insightful and descriptive storytelling.
            2. Tone: Maintain a professional yet engaging tone that resonates with a global fan base.
            3. Structure: The article must be at least 3 paragraphs long.
            4. Formatting: Start the body text from the second line (leaving the first line for a headline).
            
            [Score Rule]
            - At the very end, write "###SCORE: XX" (10-99) based on viral potential.
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
