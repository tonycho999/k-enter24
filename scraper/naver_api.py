import os
import requests
from dotenv import load_dotenv

# .env 로드
load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))
CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")

def get_target_image(keyword):
    """
    네이버 이미지 검색 API를 사용하여 키워드와 일치하는 가장 적합한 이미지 URL 반환
    """
    if not CLIENT_ID or not CLIENT_SECRET:
        print(f"   🚨 [Naver API Error] Credentials missing.")
        return ""

    # 네이버 이미지 검색 엔드포인트
    url = "https://openapi.naver.com/v1/search/image"
    
    headers = {
        "X-Naver-Client-Id": CLIENT_ID.strip(),
        "X-Naver-Client-Secret": CLIENT_SECRET.strip()
    }
    
    params = {
        "query": keyword,
        "display": 5,     # 상위 5개 중 적합한 것 선택
        "sort": "sim",    # 유사도순
        "filter": "large" # 고화질 선호
    }

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        
        if resp.status_code == 200:
            items = resp.json().get('items', [])
            for item in items:
                img_url = item.get('link', '')
                # 반드시 https://로 시작하는 원본 이미지만 허용
                if img_url.startswith("https://"):
                    return img_url
        else:
            print(f"   🚨 [Naver API Fail] Status: {resp.status_code}")
            
    except Exception as e:
        print(f"   🚨 [Naver Connection Error] {e}")
        
    return ""

def search_news_api(keyword, display=10, sort='sim'):
    """
    (옵션) 혹시 몰라 남겨두는 뉴스 검색 API
    이미지 검색 실패 시 뉴스 기사의 썸네일이라도 가져오기 위함
    """
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": CLIENT_ID.strip(),
        "X-Naver-Client-Secret": CLIENT_SECRET.strip()
    }
    params = {"query": keyword, "display": display, "sort": sort}
    
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=5)
        return resp.json().get('items', []) if resp.status_code == 200 else []
    except:
        return []
