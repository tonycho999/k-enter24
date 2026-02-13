import os
import json
import urllib.parse
import urllib.request
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

def get_naver_api_news(keyword):
    """네이버 API 뉴스 검색 (타임아웃 설정 추가)"""
    url = f"https://openapi.naver.com/v1/search/news?query={urllib.parse.quote(keyword)}&display=100&sort=date"
    
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", os.environ.get("NAVER_CLIENT_ID"))
    req.add_header("X-Naver-Client-Secret", os.environ.get("NAVER_CLIENT_SECRET"))
    
    try:
        # [중요] timeout=10 추가: 10초 동안 응답 없으면 포기
        print(f"📡 네이버 API 호출 중: {keyword}...")
        res = urllib.request.urlopen(req, timeout=10) 
        items = json.loads(res.read().decode('utf-8')).get('items', [])
        
        valid_items = []
        now = datetime.now()
        threshold = now - timedelta(hours=24)

        for item in items:
            try:
                pub_date = parsedate_to_datetime(item['pubDate']).replace(tzinfo=None)
                if pub_date < threshold:
                    continue
                item['published_at'] = pub_date
                valid_items.append(item)
            except:
                continue

        return valid_items

    except Exception as e:
        print(f"❌ 네이버 API 에러 ({keyword}): {e}")
        return []

def get_article_image(link):
    """기사 본문에서 이미지 추출 (로그 및 타임아웃 강화)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    try:
        # [확인] requests.get 호출 시 timeout=5 설정 (5초)
        # 어디서 멈추는지 확인하기 위해 프린트 추가
        print(f"   🖼️ 이미지 추출 중: {link[:50]}...") 
        res = requests.get(link, headers=headers, timeout=5)
        
        if res.status_code != 200:
            return None

        soup = BeautifulSoup(res.text, 'html.parser')
        candidates = []

        # 1. 본문 영역 우선 탐색
        main_content = soup.select_one('#dic_area, #articleBodyContents, .article_view, #articeBody, .news_view')
        if main_content:
            imgs = main_content.find_all('img')
            for i in imgs:
                src = i.get('src') or i.get('data-src')
                if src and 'http' in src:
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
    except Exception as e:
        print(f"   ⚠️ 이미지 추출 실패: {e}")
        return None
