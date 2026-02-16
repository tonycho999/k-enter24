import os
import time
import json
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self):
        # Perplexity (검색 엔진)
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        # Groq (요약 엔진)
        self.groq = Groq(
            api_key=os.environ.get("GROQ_API_KEY")
        )

    def get_trends_and_rankings(self, category):
        """
        Perplexity API를 사용하여 특정 카테고리의 
        1. 화제의 인물 30명 (people)
        2. 인기 프로그램/콘텐츠 TOP 10 (top10)
        정보를 한 번에 JSON으로 가져옵니다.
        """
        system_prompt = "You are a helpful assistant that outputs only valid JSON."
        user_prompt = f"""
        한국의 '{category}' 분야에 대해 현재 시점 기준으로 가장 핫한 트렌드를 분석해서 다음 두 가지 키를 가진 JSON 형식으로만 답해줘. 마크다운이나 잡담은 하지 마.

        1. "people": 지난 24시간 동안 언론과 SNS에서 언급량이 가장 급증한 화제의 인물 30명 리스트.
           - 각 항목: "name" (이름), "facts" (데스크급 편집자의 시선으로, 보도자료 작성을 위해 이 내용 중 대중이 주목할 핵심 팩트 3가지만 객관적으로 추출해 줘.)
        
        2. "top10": 현재 가장 인기 있는 {category} 관련 콘텐츠(노래 제목, 드라마 제목, 영화 제목, 방송 프로그램명, 핫플레이스 이름 등) TOP 10 리스트.
           - 각 항목: "rank" (1~10), "title" (제목/이름)

        반드시 유효한 JSON 포맷으로 출력해.
        """
        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1 # JSON 형식을 지키기 위해 창의성 낮춤
            )
            return response.choices[0].message.content, user_prompt
            
        except Exception as e:
            print(f"Perplexity API Error: {e}")
            return "{}", user_prompt

    def edit_with_groq(self, person_name, news_facts, category):
        """
        Groq (Llama 3)을 사용하여 팩트를 기반으로 '클릭을 유도하는 기사' 작성
        """
        personas = {
            "k-pop": "K-POP 전문 기자. 팬덤 용어와 이모지를 사용해 생동감 있게.",
            "k-drama": "드라마 전문 에디터. 감정선과 시청률 분석 위주.",
            "k-movie": "영화 평론가. 연출과 연기력 분석 위주.",
            "k-entertain": "연예부 기자. 재미와 화제성 위주.",
            "k-culture": "라이프스타일 큐레이터. 핫플레이스와 트렌드 소개."
        }
        
        system_msg = personas.get(category, "한국 엔터테인먼트 전문 기자")
        user_msg = f"""
        주제: {person_name}
        팩트: {news_facts}

        위 팩트를 바탕으로 다음 형식에 맞춰 기사를 작성해줘:
        1. 첫 줄: 호기심을 자극하는 제목 (이모지 포함 가능)
        2. 두 번째 줄부터: 본문 (3문단 내외로 요약)
        3. 팩트에 없는 내용은 지어내지 말 것.
        4. 영어로 작성해줘.
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
            time.sleep(1.5) # 무료 티어 Rate Limit 고려
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API Error ({person_name}): {e}")
            return f"{person_name} 소식\n{news_facts}"
