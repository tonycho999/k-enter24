import os
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def search_news_api(keyword, display=20):
    """네이버 API로 뉴스 목록 가져오기"""
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    params = {"query": keyword, "display": display, "sort": "sim"}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        if resp.status_code == 200:
            return resp.json().get('items', [])
        return []
    except Exception:
        return []

def crawl_full_body(url):
    """봇이 기사 링크로 들어가 본문 긁어오기 (네이버 뉴스만)"""
    if "news.naver.com" not in url:
        return "" 

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        time.sleep(0.5) # 차단 방지 딜레이
        resp = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(resp.text, 'html.parser')

        # 네이버 뉴스 본문 추출
        content = ""
        for selector in ["#dic_area", "#articeBody", "#newsEndContents"]:
            element = soup.select_one(selector)
            if element:
                for tag in element(['script', 'style', 'a', 'iframe', 'span']):
                    tag.decompose()
                content = element.get_text(strip=True)
                break
        return content[:3000] # 너무 길면 자름
    except Exception:
        return ""
