import os
import sys
import urllib.request
import urllib.parse
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_naver_api_news(keyword, display=10, sort='date'):
    """
    네이버 뉴스 검색 API 호출
    :param keyword: 검색어
    :param display: 검색 결과 개수 (기본 10, 최대 100)
    :param sort: 정렬 순서 (date: 최신순, sim: 정확도순)
    """
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print("⚠️ 네이버 API 키가 설정되지 않았습니다.")
        return []

    try:
        encText = urllib.parse.quote(keyword)
        # display와 sort 파라미터를 동적으로 반영하도록 수정
        url = f"https://openapi.naver.com/v1/search/news.json?query={encText}&display={display}&start=1&sort={sort}"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", NAVER_CLIENT_ID)
        request.add_header("X-Naver-Client-Secret", NAVER_CLIENT_SECRET)

        response = urllib.request.urlopen(request)
        res_code = response.getcode()

        if res_code == 200:
            response_body = response.read()
            data = json.loads(response_body.decode('utf-8'))
            
            # HTML 태그 제거 및 데이터 정리
            items = []
            for item in data.get('items', []):
                clean_item = {
                    'title': BeautifulSoup(item['title'], 'html.parser').get_text(),
                    'link': item['link'], # 여기서 http 여부는 main.py에서 거름
                    'description': BeautifulSoup(item['description'], 'html.parser').get_text(),
                    'pubDate': item['pubDate']
                }
                items.append(clean_item)
            return items
        else:
            print(f"Error Code: {res_code}")
            return []

    except Exception as e:
        print(f"⚠️ 네이버 API 요청 실패 ({keyword}): {e}")
        return []

def get_article_data(url):
    """
    뉴스 기사 본문 및 이미지 크롤링 (User-Agent 추가하여 차단 방지)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # 타임아웃 5초 설정
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            return None, None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. 이미지 추출 (OpenGraph 태그 우선)
        image_url = None
        og_image = soup.find("meta", property="og:image")
        if og_image:
            image_url = og_image.get("content")
        
        # 2. 본문 추출 (네이버 뉴스 vs 일반 언론사 분기 처리)
        content = ""
        
        # 네이버 뉴스 포맷인 경우
        if "news.naver.com" in url:
            article_body = soup.find('div', id='dic_area') or soup.find('div', id='articleBodyContents')
            if article_body:
                content = article_body.get_text(strip=True)
        else:
            # 일반 언론사 사이트 (p 태그 긁어오기)
            paragraphs = soup.find_all('p')
            content = " ".join([p.get_text(strip=True) for p in paragraphs])
            
        # 본문이 너무 짧으면(광고 등) 무시
        if len(content) < 50:
            return None, image_url

        return content[:1500], image_url # 너무 길면 AI 비용 문제로 1500자 커팅

    except Exception:
        # 크롤링 실패 시 조용히 넘어감
        return None, None
