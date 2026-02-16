import os
import requests
import urllib.parse

class NaverManager:
    def __init__(self):
        self.client_id = os.environ.get("NAVER_CLIENT_ID")
        self.client_secret = os.environ.get("NAVER_CLIENT_SECRET")

    def get_image(self, keyword):
        """
        키워드로 네이버 이미지 검색 후 최상단 이미지 URL 반환
        (http:// -> https:// 로 변환하여 보안 문제 해결)
        """
        if not self.client_id or not self.client_secret:
            return None

        url = "https://openapi.naver.com/v1/search/image"
        headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }
        
        # 정확도를 위해 sort='sim'(유사도순) 사용, 화질을 위해 filter='medium' 이상 권장
        params = {
            "query": keyword, 
            "display": 1, 
            "sort": "sim", 
            "filter": "medium" 
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            if res.status_code == 200:
                items = res.json().get('items')
                if items:
                    link = items[0]['link']
                    # [핵심 수정] http를 https로 강제 변환
                    return link.replace("http://", "https://")
            
            return None
            
        except Exception as e:
            print(f"  [Naver API Error] Image search failed for {keyword}: {e}")
            return None
