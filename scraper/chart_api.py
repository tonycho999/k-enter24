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
            
            # 우선순위: 고성능 70B 모델 -> 최신 70B -> 경량 8B
            preferences = [
                "llama-3.3-70b-specdec",
                "llama-3.1-70b-versatile",
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant"
            ]
            
            for pref in preferences:
                if pref in model_ids:
                    self.selected_model = pref
                    print(f"🤖 AI Model Selected: {self.selected_model}")
                    return
            
            self.selected_model = model_ids[0]
            print(f"⚠️ Preferred models not found. Selected fallback: {self.selected_model}")
        except Exception as e:
            print(f"❌ Model selection error: {e}")
            self.selected_model = "llama-3.1-8b-instant"

    def get_top10_chart(self, category):
        """실패 시 1회 재시도 및 랜덤 대기를 포함한 메인 수집 함수"""
        max_retries = 1
        for attempt in range(max_retries + 1):
            try:
                # 작업 전 랜덤 대기 (4.0s ~ 5.0s)
                wait_time = random.uniform(4.0, 5.0)
                print(f"⏳ [{category}] Waiting {wait_time:.2f}s (Attempt {attempt+1})...")
                time.sleep(wait_time)

                if category == "k-movie":
                    return self._get_kobis_movie()
                
                # 뉴스 기반 카테고리
                queries = {
                    "k-pop": "오늘 실시간 음원 차트 순위 멜론 써클차트",
                    "k-drama": "드라마 시청률 순위 닐슨코리아 최신",
                    "k-entertain": "예능 프로그램 시청률 순위 닐슨코리아 최신"
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
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={self.kobis_key}&targetDt={target_date}"
        res = requests.get(url, timeout=10)
        data = res.json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
        top10 = [{"rank": i+1, "title": m['movieNm'], "info": f"관객 {m['audiCnt']}"} for i, m in enumerate(data[:10])]
        return json.dumps({"top10": top10}, ensure_ascii=False)

    def _get_chart_via_news(self, category, query):
        client_id = os.environ.get("NAVER_CLIENT_ID")
        client_secret = os.environ.get("NAVER_CLIENT_SECRET")
        url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display=15&sort=sim"
        headers = {"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret}
        
        res = requests.get(url, headers=headers, timeout=10)
        items = res.json().get('items', [])
        if not items: raise ValueError("No news items found")
            
        context = " ".join([f"{i['title']} {i['description']}" for i in items])
        return self._ai_extract_chart(category, context)

    def _ai_extract_chart(self, category, context):
        prompt = f"""
        당신은 한국 대중문화 데이터 전문가입니다. 뉴스 텍스트를 분석하여 {category}의 최신 Top 10 순위표를 작성하세요.
        - 반드시 다음 JSON 형식만 응답하세요:
        {{"top10": [{{"rank": 1, "title": "제목", "info": "수치/정보"}}, ...]}}
        텍스트: {context[:3000]}
        """
        chat = self.groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.selected_model,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        return chat.choices[0].message.content
