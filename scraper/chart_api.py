import os
import json
import requests
import time
import random
from datetime import datetime, timedelta
from groq import Groq

class ChartEngine:
    def __init__(self):
        self.groq_client = None
        self.kobis_key = os.environ.get("KOBIS_API_KEY")
        self.selected_model = None

    def set_groq_client(self, api_key):
        """API 키 주입 시 모델 리스트를 조회하여 최적의 모델을 자동 선택합니다."""
        self.groq_client = Groq(api_key=api_key)
        self._auto_select_model()

    def _auto_select_model(self):
        """Groq 가용 모델 중 우선순위에 따라 모델을 결정합니다."""
        try:
            models = self.groq_client.models.list()
            model_ids = [m.id for m in models.data]
            
            preferences = [
                "llama-3.3-70b-specdec",
                "llama-3.1-70b-versatile",
                "llama-3.1-8b-instant"
            ]
            
            for pref in preferences:
                if pref in model_ids:
                    self.selected_model = pref
                    print(f"🤖 AI Model Selected: {self.selected_model}")
                    return
            
            self.selected_model = model_ids[0]
        except Exception as e:
            print(f"❌ Model selection error: {e}")
            self.selected_model = "llama-3.1-8b-instant"

    def get_top10_chart(self, category):
        """실패 시 1회 재시도 및 랜덤 대기를 포함한 메인 수집 함수"""
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                wait_time = random.uniform(4.0, 5.0)
                print(f"⏳ [{category}] Waiting {wait_time:.2f}s (Attempt {attempt+1})...")
                time.sleep(wait_time)

                if category == "k-movie":
                    return self._get_kobis_movie()
                
                # 검색어 고도화: '오늘', '발표', '최신' 키워드 추가
                queries = {
                    "k-pop": "오늘 멜론 써클차트 음원 순위 톱10",
                    "k-drama": "어제 드라마 시청률 순위 닐슨코리아 최신발표",
                    "k-entertain": "어제 예능 프로그램 시청률 순위 닐슨코리아 최신발표",
                    "k-culture": "오늘 가장 핫한 팝업스토어 성수동 한남동 핫플 순위"
                }
                return self._get_chart_via_news(category, queries.get(category, category))

            except Exception as e:
                if attempt < max_retries:
                    print(f"⚠️ Retrying {category} due to: {e}")
                    time.sleep(5)
                else:
                    print(f"❌ Final failure for {category}: {e}")
                    return json.dumps({"top10": []})

    def _get_kobis_movie(self):
        """영화진흥위원회 공식 API (어제 날짜 기준)"""
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={self.kobis_key}&targetDt={target_date}"
        res = requests.get(url, timeout=10)
        data = res.json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        top10 = [{"rank": i+1, "title": m['movieNm'], "info": f"관객 {int(m['audiCnt']):,}"} for i, m in enumerate(data[:10])]
        return json.dumps({"top10": top10}, ensure_ascii=False)

    def _get_chart_via_news(self, category, query):
        """네이버 뉴스 API (날짜순 정렬 적용)"""
        client_id = os.environ.get("NAVER_CLIENT_ID")
        client_secret = os.environ.get("NAVER_CLIENT_SECRET")
        
        # 'sort=date'를 사용하여 가장 최근 기사를 우선적으로 가져옵니다.
        url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=20&sort=date"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        
        res = requests.get(url, headers=headers, timeout=10)
        items = res.json().get('items', [])
        if not items: raise ValueError("No news items found")
            
        # AI가 현재 시점을 인지할 수 있도록 오늘 날짜를 삽입합니다.
        today_str = datetime.now().strftime("%Y년 %m월 %d일")
        context = f"현재 시점: {today_str}\n\n뉴스 데이터:\n"
        context += " ".join([f"[{i['pubDate']}] {i['title']} - {i['description']}" for i in items])
        
        return self._ai_extract_chart(category, context)

    def _ai_extract_chart(self, category, context):
        """Groq AI를 통한 최신 순위 추출"""
        prompt = f"""
        당신은 대한민국 문화 트렌드 분석가입니다. 
        제공된 최신 뉴스 데이터를 분석하여 {category} 카테고리의 현재 Top 10 순위를 추출하세요.

        [지침]
        1. '현재 시점'과 가장 가까운 날짜의 기사 내용을 우선시하세요. 2개월 전과 같은 과거 데이터는 절대 포함하지 마세요.
        2. 순위가 명확하지 않다면 뉴스에서 가장 많이 언급되거나 핫한 순서대로 10개를 선정하세요.
        3. 반드시 다음 JSON 형식으로만 응답하세요:
        {{"top10": [{{"rank": 1, "title": "제목", "info": "수치 또는 최신소식"}}, ...]}}
        
        텍스트: {context[:3500]}
        """
        chat = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.selected_model,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return chat.choices[0].message.content
