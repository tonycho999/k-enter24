import sys
import os
import time
from datetime import datetime, timedelta
from dateutil import parser
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from scraper import crawler, ai_engine, repository
from scraper.config import CATEGORY_SEEDS

load_dotenv()

TARGET_RANK_LIMIT = 30 

def is_within_24h(date_str):
    if not date_str: return False
    try:
        pub_date = parser.parse(date_str)
        if pub_date.tzinfo:
            pub_date = pub_date.replace(tzinfo=None)
        now = datetime.now()
        diff = now - pub_date
        return diff <= timedelta(hours=24)
    except:
        return False

def run_master_scraper():
    print(f"🚀 K-Enter Trend Master 가동 시작: {datetime.now()}")
    
    for category, seeds in CATEGORY_SEEDS.items():
        print(f"\n📂 [{category.upper()}] 트렌드 분석 시작")
        
        # [1단계] 씨앗 데이터 수집
        raw_text_data = [] 
        
        try:
            for seed in seeds:
                # [수정] 20개씩만 가져옴 (토큰 절약)
                news_items = crawler.get_naver_api_news(seed, display=20)
                
                for item in news_items:
                    if is_within_24h(item.get('pubDate')):
                        combined_text = f"Title: {item['title']}\nSummary: {item['description']}"
                        raw_text_data.append(combined_text)
            
            # [수정] AI에게 보낼 데이터를 최대 60개로 제한 (API 제한 방지)
            raw_text_data = raw_text_data[:60]
            
            print(f"   🌱 24시간 내 유효 기사 수집: {len(raw_text_data)}개 (AI 입력용)")
            
            if len(raw_text_data) < 5:
                print("   ⚠️ 기사가 너무 적어 스킵합니다.")
                continue
                
        except Exception as e:
            print(f"   ⚠️ 씨앗 수집 오류: {e}")
            continue
        
        # [2단계] AI 키워드 추출
        top_entities = ai_engine.extract_top_entities(category, "\n".join(raw_text_data))
        
        if not top_entities: 
            print("   ⚠️ 키워드 추출 실패 (AI 응답 없음)")
            continue
            
        print(f"   💎 추출된 키워드 (Top 5): {', '.join([e['keyword'] for e in top_entities[:5]])}...")

        # [3단계] 키워드별 심층 분석
        category_news_list = []
        target_list = top_entities[:TARGET_RANK_LIMIT]
        
        for rank, entity in enumerate(target_list):
            kw = entity.get('keyword')
            k_type = entity.get('type', 'content')
            
            print(f"   🔍 Rank {rank+1}: '{kw}' ({k_type}) 분석 중...")
            
            try:
                # [수정] 10개만 검색
                raw_articles = crawler.get_naver_api_news(kw, display=10)
                if not raw_articles: continue

                full_contents = []
                main_image = None
                valid_article_count = 0
                
                for art in raw_articles:
                    if not is_within_24h(art.get('pubDate')):
                        continue
                        
                    text, img = crawler.get_article_data(art['link'], target_keyword=kw)
                    
                    if text: 
                        full_contents.append(text)
                        valid_article_count += 1
                        if not main_image and img:
                            if img.startswith("http://"): img = img.replace("http://", "https://")
                            main_image = img
                            
                    # [수정] 3개만 모으면 충분 (속도 향상)
                    if valid_article_count >= 3:
                        break

                if not full_contents:
                    print(f"      ☁️ '{kw}': 유효 기사 없음 (Skip)")
                    continue

                # [4단계] AI 브리핑
                briefing = ai_engine.synthesize_briefing(kw, full_contents)
                
                if not briefing:
                    print(f"      🗑️ '{kw}': 내용 부실로 폐기")
                    continue
                
                ai_score = round(9.9 - (rank * 0.1), 1)
                if ai_score < 7.0: ai_score = 7.0

                final_img = main_image or f"https://placehold.co/600x400/111/cyan?text={kw}"

                news_item = {
                    "category": category,
                    "rank": rank + 1,
                    "keyword": kw,
                    "type": k_type,
                    "title": f"[{kw}] News Update",
                    "summary": briefing,
                    "link": None,
                    "image_url": final_img,
                    "score": ai_score,
                    "likes": 0, "dislikes": 0,
                    "created_at": datetime.now().isoformat(),
                    "published_at": datetime.now().isoformat()
                }
                category_news_list.append(news_item)
                # [수정] API 부하 줄이기 위해 2초 대기
                time.sleep(2.0) 
                
            except Exception as e:
                print(f"      ⚠️ '{kw}' 처리 중 에러: {e}")
                continue

        # [5단계] DB 저장
        if category_news_list:
            print(f"   💾 저장 시작: 총 {len(category_news_list)}개")
            repository.refresh_live_news(category, category_news_list)
            
            content_only_list = [n for n in category_news_list if n.get('type') == 'content']
            # 컨텐츠 타입이 너무 적으면 섞여도 나오게 하기 위한 최소한의 조치 (5개 이하일 경우)
            if len(content_only_list) < 5:
                repository.update_sidebar_rankings(category, category_news_list[:10])
            else:
                repository.update_sidebar_rankings(category, content_only_list[:10])
            
            high_score_news = [n for n in category_news_list if n['score'] >= 7.0]
            if high_score_news:
                repository.save_to_archive(high_score_news)

    print("\n🎉 전체 업데이트 완료.")

if __name__ == "__main__":
    run_master_scraper()
