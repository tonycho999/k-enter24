import os
import json
import time
import random
import email.utils
from datetime import datetime, timedelta
from groq import Groq

class ChartEngine:
    def __init__(self):
        self.groq_client = None
        self.kobis_key = os.environ.get("KOBIS_API_KEY")
        self.active_model = None # 실시간으로 결정될 모델 저장용

    def set_groq_client(self, api_key):
        """클라이언트 설정 및 가용 모델 실시간 조회"""
        self.groq_client = Groq(api_key=api_key)
        self._set_available_model()

    def _set_available_model(self):
        """[중요] 모델명을 지정하지 않고 가용 리스트에서 동적 선택"""
        try:
            models = self.groq_client.models.list()
            # 사용 가능한 모델 ID 리스트 추출
            available_ids = [m.id for m in models.data]
            
            # 성능이 좋은 순서대로 선호도를 두되, 리스트에 있는 것만 선택
            preferences = [
                "llama-3.3-70b-versatile",
                "llama-3.3-70b-specdec",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant"
            ]
            
            for pref in preferences:
                if pref in available_ids:
                    self.active_model = pref
                    print(f"🤖 Dynamic Model Selection: {self.active_model}")
                    return
            
            # 선호 모델이 하나도 없으면 리스트의 첫 번째 모델 강제 선택
            self.active_model = available_ids[0]
            print(f"⚠️ Preferred models not found. Using fallback: {self.active_model}")
            
        except Exception as e:
            print(f"❌ Failed to fetch models: {e}")
            self.active_model = "llama-3.1-8b-instant" # 최후의 수단

    def get_top10_chart(self, category):
        """24시간 내 데이터 수집 및 영문 번역 (재시도 로직 포함)"""
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                time.sleep(random.uniform(2.0, 4.0))

                # 영화 데이터는 공식 API 활용
                if category == "k-movie":
                    raw_data = self._get_kobis_movie()
                else:
                    # 뉴스 데이터 필터링 수집
                    queries = {
                        "k-pop": "오늘 실시간 음원 차트 1위 멜론 써클차트",
                        "k-drama": "오늘 드라마 시청률 순위 닐슨코리아",
                        "k-entertain": "오늘 예능 시청률 순위 닐슨코리아",
                        "k-culture": "오늘 성수동 한남동 팝업스토어 핫플레이스 추천"
                    }
                    raw_data = self._get_fresh_news(category, queries.get(category))

                return self._ai_process(category, raw_data)

            except Exception as e:
                if attempt < max_retries:
                    time.sleep(5)
                else:
                    return json.dumps({"top10": []})

    def _get_fresh_news(self, category, query):
        """24시간 이내 기사 필터링"""
        url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=30&sort=date"
        headers = {
            "X-Naver-Client-Id": os.environ.get("NAVER_CLIENT_ID"),
            "X-Naver-Client-Secret": os.environ.get("NAVER_CLIENT_SECRET")
        }
        res = requests.get(url, headers=headers, timeout=10)
        items = res.json().get('items', [])
        
        now = datetime.now()
        fresh = []
        for i in items:
            p_date = email.utils.parsedate_to_datetime(i['pubDate']).replace(tzinfo=None)
            if now - p_date <= timedelta(hours=24):
                fresh.append(f"{i['title']} {i['description']}")
        
        if not fresh: raise ValueError("No fresh news")
        return "\n".join(fresh)[:4000]

    def _get_kobis_movie(self):
        t_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={self.kobis_key}&targetDt={t_date}"
        return requests.get(url, timeout=10).text

    def _ai_process(self, category, data):
        """실시간 선택된 모델로 분석 및 영문 번역"""
        # K-Culture 연예인 배제 규칙
        k_culture_rule = "STRICT: NO celebrities or idols. Focus on places, food, or trends." if category == "k-culture" else ""
        
        prompt = f"""
        Analyze news from the last 24h for {category}.
        1. Extract Top 10 rankings.
        2. Translate everything to English.
        3. {k_culture_rule}
        Format: {{"top10": [{{"rank": 1, "title": "Title", "info": "Info"}}, ...]}}
        Data: {data}
        """
        
        # 선택된 self.active_model을 사용합니다.
        chat = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.active_model,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return chat.choices[0].message.content
