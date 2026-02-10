import os
import sys

# 현재 폴더 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules import naver_api, db_client
from datetime import datetime

TARGET_ARTISTS = ["NewJeans", "BTS", "IVE", "BLACKPINK"]

def run():
    print(f"=== {datetime.now()} 크롤링 시작 ===")
    
    for artist in TARGET_ARTISTS:
        print(f"🔍 {artist} 뉴스 수집 중...")
        
        news_items = naver_api.get_naver_news(artist)
        
        if not news_items:
            print(f" - {artist}: 새로운 뉴스가 없습니다.")
            continue
            
        latest_news = news_items[0]
        dummy_summary = f"[AI 요약] {latest_news['title']} (원문: {latest_news['description']})"
        
        report_data = {
            "artist_name": artist,
            "summary_text": dummy_summary,
            "keywords": ["컴백", "트렌드", "화제"],
            "reactions": {"KR": "Positive", "US": "Neutral"},
            "image_url": "https://placehold.co/600x400",
            "original_links": [item['link'] for item in news_items[:3]]
        }
        
        db_client.insert_report(report_data)

    print("=== 모든 작업 완료 ===")

if __name__ == "__main__":
    run()
