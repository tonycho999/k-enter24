import os
import time
import json
from openai import OpenAI
from groq import Groq

class NewsEngine:
    def __init__(self):
        # Perplexity 클라이언트 설정 (OpenAI 인터페이스 호환)
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )
        # Groq 클라이언트 설정
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
                temperature=0.1  # 정확한 포맷을 위해 낮게 설정
            )
            return response.choices[0].message.content, user_prompt
            
        except Exception as e:
            print(f"Perplexity API 호출 중 오류: {e}")
            # 오류 발생 시 빈 JSON 문자열과 프롬프트 반환하여 멈춤 방지
            return json.dumps({"people": [], "top10": []}), user_prompt

    def edit_with_groq(self, person_name, news_facts, category):
        """
        Groq API (Llama 3)를 사용하여 팩트 정보를 바탕으로 기사(제목+본문)를 작성합니다.
        """
        # 카테고리별 페르소나 설정
        personas = {
            "k-pop": "너는 아이돌 팬덤 용어를 잘 아는 열정적인 K-POP 전문 기자야. 이모지를 적절히 섞어서 생동감 있게 써.",
            "k-drama": "너는 드라마의 감정선과 시청률 추이를 분석하는 드라마 전문 에디터야.",
            "k-movie": "너는 영화의 연출과 연기력을 깊이 있게 평론하는 영화 기자야.",
            "k-entertain": "너는 예능 프로그램의 재미 요소를 콕 집어내는 방송 연예 기자야.",
            "k-culture": "너는 MZ세대가 좋아하는 핫플레이스와 축제를 소개하는 트렌드 큐레이터야. 연예인은 제외해줘"
        }
        
        system_msg = personas.get(category, "너는 한국 엔터테인먼트 전문 기자야.")
        user_msg = f"""
        주제: {person_name}
        팩트: {news_facts}

        위 정보를 바탕으로 사람들이 클릭하고 싶게 만드는 '기사 제목'과 '본문'을 작성해줘.
        
        [조건]
        1. 제목은 첫 줄에 쓰고, 본문은 둘째 줄부터 써.
        2. 본문은 3~10문단 정도로 요약해.
        3. 팩트에 없는 내용은 지어내지 마.
        4. 영어로 작성해.
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
            # 무료 티어 API 속도 제한(Rate Limit) 방지를 위한 대기
            time.sleep(2) 
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Groq API 호출 중 오류 ({person_name}): {e}")
            return f"{person_name} 관련 소식입니다.\n{news_facts}" # 오류 시 기본 팩트 반환
