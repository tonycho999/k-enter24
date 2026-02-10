import os
import requests

def get_naver_news(keyword, display=10):
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }
    params = {
        "query": keyword,
        "display": display,
        "sort": "sim"
    }
    
    try:
        res = requests.get(url, headers=headers, params=params)
        res.raise_for_status()
        return res.json().get('items', [])
    except Exception as e:
        print(f"[Naver Error] {e}")
        return []
