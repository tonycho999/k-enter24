import os
import json
import urllib.parse
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime # 네이버 날짜 파싱용

def get_naver_api_news(keyword):
    """
    네이버 API 뉴스 검색
    [수정] 
    1. sort='date'로 변경하여 최신순 정렬
    2. 24시간 지난 기사는 수집 단계에서 제외
    3. pubDate 파싱하여 반환
    """
    # [수정] sort=sim(유사도) -> sort=date(날짜순) 변경
    url = f"https://openapi.naver.com/v1/search/news?query={urllib.parse.quote(keyword)}&display=100&sort=date"
    
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", os.environ.get("NAVER_CLIENT_ID"))
    req.add_header("X-Naver-Client-Secret", os.environ.get("NAVER_CLIENT_SECRET"))
    
    try:
        res = urllib.request.urlopen(req)
        items = json.loads(res.read().decode('utf-8')).get('items', [])
        
        valid_items = []
        now = datetime.now()
        threshold = now - timedelta(hours=24) # 24시간 제한선

        for item in items:
            try:
                # 네이버 날짜 포맷 파싱 (Fri, 13 Feb 2026 14:00:00 +0900)
                pub_date = parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
                
                # [필터링] 실제 작성 시간이 24시간 지났으면 제외
                if pub_date < threshold:
                    continue

                # 통과한 기사는 파싱된 날짜 객체를 포함하여 리스트에 추가
                item['published_at'] = pub_date
                valid_items.append(item)
            except:
                continue

        return valid_items

    except: return []

def get_article_image(link):
    """기사 본문에서 고해상도 대표 이미지 추출 (아이콘/배너 제외)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        res = requests.get(link, headers=headers, timeout=3)
        soup = BeautifulSoup(res.text, 'html.parser')
        candidates = []

        # 1. 본문 영역 우선 탐색
        main_content = soup.select_one('#dic_area, #articleBodyContents, .article_view, #articeBody, .news_view')
        if main_content:
            imgs = main_content.find_all('img')
            for i in imgs:
                src = i.get('src') or i.get('data-src')
                if src and 'http' in src:
                    # 너무 작은 이미지는 제외 (아이콘 등)
                    width = i.get('width')
                    if width and width.isdigit() and int(width) < 200: continue
                    candidates.append(src)

        # 2. 메타 태그 탐색
        og = soup.find('meta', property='og:image')
        if og and og.get('content'): candidates.append(og['content'])

        # 3. 불량 이미지 필터링
        for img_url in candidates:
            bad_keywords = r'logo|icon|button|share|banner|thumb|profile|default|ranking|news_stand|ssl.pstatic.net'
            if re.search(bad_keywords, img_url, re.IGNORECASE): continue
            return img_url
        return None
    except: return None
