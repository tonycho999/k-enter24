import os
import time
from datetime import datetime
from dotenv import load_dotenv

# 사용자 모듈 임포트
from config import CATEGORY_MAP
from scraper import crawler, ai_engine, repository, update_rankings

# 환경변수 로드
load_dotenv()

def run_scraper():
    """뉴스 수집 및 AI 요약 핵심 로직 (1회 실행)"""
    print("🚀 7단계 마스터 엔진 가동...")
    
    for category, keywords in CATEGORY_MAP.items():
        try:
            print(f"\n📂 {category.upper()} 부문 처리 중...")

            # 1. 수집
            raw_news = []
            for kw in keywords: 
                raw_news.extend(crawler.get_naver_api_news(kw))
            
            # 2. 중복 제거
            existing_links = repository.get_existing_links(category)
            
            new_candidate_news = []
            seen_links = set()
            for n in raw_news:
                if n['link'] not in existing_links and n['link'] not in seen_links:
                    new_candidate_news.append(n)
                    seen_links.add(n['link'])
            
            print(f"   🔎 수집: {len(raw_news)}개 -> 기존 DB 중복 제외: {len(new_candidate_news)}개")

            if not new_candidate_news:
                continue

            # 3. AI 선별
            selected = ai_engine.ai_category_editor(category, new_candidate_news)
            print(f"   ㄴ AI 선별 완료: {len(selected)}개")

            # 4. 신규 뉴스 데이터 생성 및 저장
            if selected:
                new_data_list = []
                for i, art in enumerate(selected):
                    idx = art.get('original_index')
                    if idx is None or idx >= len(new_candidate_news): continue
                    
                    orig = new_candidate_news[idx]
                    img = crawler.get_article_image(orig['link']) or f"https://placehold.co/600x400/111/cyan?text={category}"

                    new_data_list.append({
                        "rank": art.get('rank', 99), 
                        "category": category, 
                        "title": art.get('eng_title', orig['title']),
                        "summary": art.get('summary', 'Detailed summary not available.'), 
                        "link": orig['link'], 
                        "image_url": img,
                        "score": art.get('score', 5.0), 
                        "likes": 0, 
                        "dislikes": 0, 
                        "created_at": datetime.now().isoformat(),
                        "published_at": orig.get('published_at', datetime.now()).isoformat()
                    })
                
                repository.save_news(new_data_list)

            # 5. 슬롯 관리
            repository.manage_slots(category)

        except Exception as e:
            print(f"⚠️ Error processing category {category}: {e}")
            continue

    # 키워드 분석 (옵션)
    try:
        print("\n📊 AI 키워드 트렌드 분석 시작...")
        titles = repository.get_recent_titles()
        if titles and hasattr(ai_engine, 'ai_analyze_keywords'):
            keywords = ai_engine.ai_analyze_keywords(titles)
            if keywords:
                repository.update_keywords_db(keywords)
    except Exception as e:
        print(f"⚠️ 키워드 분석 오류: {e}")
    
    print("🎉 뉴스 데이터 처리 작업 완료.")

def main():
    print("🚀 K-Enter AI News Bot Started...")
    
    # [1] 순위 데이터 업데이트 (안전장치 적용됨)
    update_rankings.update_rankings() 
    
    # [2] 뉴스 수집 시작
    run_scraper()
    
    print("✅ All Tasks Completed.")

if __name__ == "__main__":
    main()
