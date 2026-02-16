import json
import re
import os
from news_api import NewsEngine
from naver_api import NaverManager
from database import DatabaseManager

def clean_json_text(text):
    """AI 응답에서 마크다운 코드 블록을 제거하고 순수 JSON만 추출"""
    match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()

def run_automation():
    print("🚀 K-Enter24 Automation Started (Minute 11 Schedule)")
    
    db = DatabaseManager()
    engine = NewsEngine()
    naver = NaverManager()
    
    # 런 카운트 (GitHub Actions 환경변수 없으면 0)
    run_count = int(os.environ.get("RUN_COUNT", 0))
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        print(f"\n[{cat}] Processing...")
        try:
            # 1. Perplexity 데이터 수집
            raw_data_str, original_query = engine.get_trends_and_rankings(cat)
            
            # 2. JSON 파싱
            cleaned_str = clean_json_text(raw_data_str)
            if not cleaned_str or cleaned_str == "{}":
                print(f"⚠️ [{cat}] No data returned from AI.")
                continue

            parsed_data = json.loads(cleaned_str)
            
            # ---------------------------------------------------
            # A. [사이드바] TOP 10 랭킹 저장 (live_rankings)
            # ---------------------------------------------------
            top10_list = parsed_data.get('top10', [])
            if top10_list:
                print(f"  > Saving {len(top10_list)} Rankings...")
                for item in top10_list:
                    # DB 스키마: category, rank, title, meta_info, score, created_at
                    db.save_rankings([{
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'),
                        "meta_info": item.get('info', ''),
                        "score": 0, # 초기값
                        "run_count": run_count
                    }])

            # ---------------------------------------------------
            # B. [메인 피드] 인물 뉴스 저장 (live_news + archive)
            # ---------------------------------------------------
            people_list = parsed_data.get('people', [])
            if people_list:
                print(f"  > Processing {len(people_list)} People Articles...")
                
                for person in people_list:
                    name = person.get('name')
                    facts = person.get('facts')
                    
                    if not name: continue

                    # Groq 기사 생성
                    full_text = engine.edit_with_groq(name, facts, cat)
                    lines = full_text.split('\n')
                    title = lines[0].replace('제목:', '').strip()
                    summary = "\n".join(lines[1:]).strip()
                    
                    # 네이버 이미지 검색
                    img_url = naver.get_image(name)
                    
                    # DB 저장용 데이터 객체
                    article_data = {
                        "category": cat,
                        "keyword": name,
                        "title": title,
                        "summary": summary,
                        "link": person.get('link', ''),
                        "image_url": img_url,
                        "score": 0,
                        "likes": 0,
                        "query": original_query,
                        "raw_result": str(person),
                        "run_count": run_count
                    }

                    # 1. 아카이브 저장 (영구 보관)
                    db.save_to_archive(article_data)
                    
                    # 2. 라이브 뉴스 저장 (실시간 노출용)
                    # archive용 필드(query, raw_result 등) 제외하고 전달
                    live_data = {
                        "category": article_data['category'],
                        "keyword": article_data['keyword'],
                        "title": article_data['title'],
                        "summary": article_data['summary'],
                        "link": article_data['link'],
                        "image_url": article_data['image_url'],
                        "score": 0,
                        "likes": 0
                    }
                    db.save_live_news([live_data])
                    print(f"    - Article updated: {name}")

        except json.JSONDecodeError:
            print(f"❌ [{cat}] JSON Parsing Error. Raw: {raw_data_str[:50]}...")
        except Exception as e:
            print(f"❌ [{cat}] Unknown Error: {e}")

if __name__ == "__main__":
    run_automation()
