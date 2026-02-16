import os
import time
import json
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self):
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        self.groq = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )

    def get_trends_and_rankings(self, category):
        """
        Perplexity API 호출
        - 조건 1: 무조건 24시간 이내의 한국어(Korean) 결과만 출력 (소스 정확도 유지)
        - 조건 2: K-Culture는 인물 제외
        """
        
        # 카테고리별 특별 지시사항 (기존 유지)
        additional_rule = ""
        if category == "k-culture":
            additional_rule = """
            [Special Rule for k-culture]
            1. 'people' 리스트에 절대 연예인(가수, 배우, 아이돌) 이름을 넣지 마시오.
            2. 대신 '핫플레이스(장소)', '유행하는 음식', '최신 유행어(밈)', '축제/행사', '패션 아이템'을 'name'에 넣으시오.
            3. 인물이 아닌 '문화 트렌드' 자체에 집중하시오.
            4. 영어로 작성하십시오.
            """
        else:
            additional_rule = "한국에서 활동하는 연예인/작품 위주로 분석하시오."

        system_prompt = "You are a helpful assistant that outputs only valid JSON. Search only Korean domestic news sources."
        
        user_prompt = f"""
        당신은 한국 엔터테인먼트 뉴스 분석가입니다.
        현재 시점(Real-time) 기준으로 '한국 국내'에서 발생한 '{category}' 분야 트렌드를 분석해 JSON으로 답하세요.
        해외 가십이나 한국과 관련 없는 외국 뉴스는 절대 포함하지 마세요.
        
        {additional_rule}

        다음 두 가지 키를 가진 JSON 형식으로 작성하시오:

        1. "people": 지난 24시간 동안 한국 언론과 SNS에서 언급량이 급증한 대상 30개.
           - "name": 이름 (반드시 한국어 표기, Groq이 번역할 것임)
           - "facts": 기자가 기사를 작성하는데 도움이 될수 있도록 화제 이유 핵심 팩트를 상세하게 3줄 요약 (한국어)
        
        2. "top10": 현재 한국에서 가장 인기 있는 {category} 관련 콘텐츠 제목 TOP 10.
           - "rank": 1~10
           - "title": 제목 (노래/드라마/영화/드라마제외한 프로그램/장소명 등)
           - "info": 부가 정보 (가수명/시청률/위치 등)

        응답은 오직 JSON 문자열만 출력하시오. 마크다운이나 설명 금지.
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

    def edit_with_groq(self, person_name, news_facts, category):
        """
        Groq (Llama 3) 기사 작성 - [수정됨] 영어 기사 작성
        """
        # 페르소나를 영어권 독자를 위한 기자로 변경
        personas = {
            "k-pop": "You are an enthusiastic K-POP journalist writing for global fans. Use emojis and fandom slang appropriate for English speakers.",
            "k-drama": "You are a K-Drama specialist analyzing storylines and ratings for international viewers.",
            "k-movie": "You are a film critic reviewing Korean movies for a global audience.",
            "k-entertain": "You are an entertainment reporter covering Korean variety shows for English readers.",
            "k-culture": "You are a trend curator introducing Korea's hottest places and culture to the world."
        }
        
        system_msg = personas.get(category, "You are a professional journalist covering Korean entertainment news for global fans.")
        
        # 유저 프롬프트: 입력은 한국어 팩트지만, 출력은 영어로 요청
        user_msg = f"""
        Topic: {person_name}
        Facts (Korean): {news_facts}

        Based on the facts above, write a news article **in English** for global fans.
        
        [Requirements]
        1. **Headline**: Write a catchy headline on the first line.
        2. **Body**: Write the article body starting from the second line (about 3 paragraphs).
        3. **Language**: Write entirely in **English**.
        4. **Tone**: Natural, engaging, and suitable for the category.
        5. Do not invent facts not present in the source.
        """

        try:
            completion = self.groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.7
            )
            time.sleep(1.5)
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error ({person_name}): {e}")
            # 에러 발생 시 백업 (영어 제목 + 한글 팩트)
            return f"News about {person_name}\n{news_facts}"
