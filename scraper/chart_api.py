import os
import json
import requests
from datetime import datetime, timedelta
from groq import Groq

class ChartEngine:
    def __init__(self):
        self.groq_client = None
        self.kobis_key = os.environ.get("KOBIS_API_KEY")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

    def set_groq_client(self, api_key):
        """main.py에서 결정된 로테이션 키를 설정합니다."""
        self.groq_client = Groq(api_key=api_key)

    def get_top10_chart(self, category, run_count):
        """카테고리별 데이터 소스 분기"""
        if category == "k-movie":
            return self._get_kobis_movie()
        elif category == "k-pop":
            return self._get_circle_chart_text()
        elif category in ["k-drama", "k-entertain"]:
            return self._get_nielsen_text(category)
        return json.dumps({"top10": []})

    def _get_kobis_movie(self):
        """[영화] 영진위 공식 API 활용 (차단 위험 0%)"""
        target_date = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        url = f"http://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json?key={self.kobis_key}&targetDt={target_date}"
        
        try:
            res = requests.get(url, timeout=10)
            data = res.json().get("boxOfficeResult", {}).get("dailyBoxOfficeList", [])
            top10 = []
            for item in data[:10]:
                top10.append({
                    "rank": int(item['rank']),
                    "title": item['movieNm'],
                    "info": f"관객수: {item['audiCnt']}"
                })
            return json.dumps({"top10": top10}, ensure_ascii=False)
        except:
            return json.dumps({"top10": []})

    def _get_circle_chart_text(self):
        """[가요] 써클차트 텍스트 수집 후 Groq AI 분석"""
        url = "https://circlechart.kr/page_chart/global.circle"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            return self._ai_extract_chart(res.text, "K-Pop Global Chart")
        except: return json.dumps({"top10": []})

    def _get_nielsen_text(self, category):
        """[드라마/예능] 닐슨코리아 텍스트 수집 후 Groq AI 분석"""
        url = "https://www.nielsenkorea.co.kr/tv_terrestrial_day.asp"
        try:
            res = requests.get(url, headers=self.headers, timeout=10)
            return self._ai_extract_chart(res.text, f"Nielsen Korea {category} Ratings")
        except: return json.dumps({"top10": []})

    def _ai_extract_chart(self, raw_html, context):
        """지저분한 HTML/텍스트에서 Groq AI가 순위만 추출"""
        if not self.groq_client: return json.dumps({"top10": []})

        prompt = f"""
        당신은 데이터 추출 전문가입니다. 제공된 텍스트 데이터에서 {context}의 최신 Top 10 순위를 찾아 JSON으로 반환하세요.
        - 형식: {{"top10": [{{"rank": 1, "title": "제목", "info": "수치/가수"}}, ...]}}
        - 텍스트가 부족하면 알려진 가장 최신 정보를 바탕으로 작성하세요.
        - 데이터: {raw_html[:4000]}  # 상위 4000자만 분석
        """
        
        try:
            chat = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192", # 빠른 분석을 위해 8B 모델 사용
                response_format={"type": "json_object"}
            )
            return chat.choices[0].message.content
        except Exception as e:
            print(f"AI 분석 실패: {e}")
            return json.dumps({"top10": []})
