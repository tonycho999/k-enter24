import json
import re
import os
import time
from datetime import datetime, timedelta
from news_api import NewsEngine
from naver_api import NaverManager
from database import DatabaseManager
from supabase import create_client

# ---------------------------------------------------------
# [설정] 실행 사이클
# ---------------------------------------------------------
# K-Pop은 매시간 차트 갱신, 나머지는 특정 시간에만 차트 갱신
# 하지만 "인물 뉴스"는 매시간 트렌드를 체크합니다.
TARGET_COUNTS_FOR_OTHERS = [5, 17] 

def clean_json_text(text):
    match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
    if match: text = match.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1: return text[start:end+1]
    return text.strip()

# ---------------------------------------------------------
# [DB 연동]
# ---------------------------------------------------------
supa_url = os.environ.get("SUPABASE_URL")
supa_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supa_url, supa_key) if supa_url and supa_key else None

def get_run_count():
    if not supabase: return 0
    try:
        res = supabase.table('system_status').select('run_count').eq('id', 1).single().execute()
        return res.data['run_count'] if res.data else 0
    except: return 0

def update_run_count(current):
    if not supabase: return
    next_count = current + 1
    if next_count >= 24: next_count = 0
    try:
        supabase.table('system_status').upsert({'id': 1, 'run_count': next_count}).execute()
        print(f"🔄 Cycle Count Updated: {current} -> {next_count}")
    except Exception as e:
        print(f"⚠️ Failed to update run count: {e}")

# ---------------------------------------------------------
# [Helper] 이전에 작성된 기사 목록 가져오기 (중복/신규 체크용)
# ---------------------------------------------------------
def get_recent_keywords(category):
    """
    최근 12시간 내에 해당 카테고리에서 작성된 인물 이름(keyword)을 가져옴
    """
    if not supabase: return []
    try:
        # 12시간 전 시간 구하기
        time_limit = (datetime.utcnow() - timedelta(hours=12)).isoformat()
        
        res = supabase.table('search_archive') \
            .select('keyword') \
            .eq('category', category) \
            .gte('created_at', time_limit) \
            .execute()
            
        if res.data:
            return set([item['keyword'] for item in res.data])
        return set()
    except Exception as e:
        print(f"⚠️ Failed to fetch history: {e}")
        return set()

# ---------------------------------------------------------
# [메인 로직]
# ---------------------------------------------------------
def run_automation():
    run_count = get_run_count()
    print(f"🚀 Automation Started (Cycle: {run_count}/23)")
    
    db = DatabaseManager()
    engine = NewsEngine(run_count) # Run count 전달 (키 로테이션용)
    naver = NaverManager()
    
    # Key 1번 사용 여부 (차트 갱신용)
    is_key1 = engine.is_using_primary_key()
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        print(f"\n[{cat}] Analyzing Trends...")
        
        # 1. 최근에 다룬 인물 목록 가져오기 (신규 진입 판별용)
        recent_people = get_recent_keywords(cat)

        try:
            # -----------------------------------------------------------
            # Step 1. 리스트 확보 (Top 10 Chart + Top 30 People List)
            # -----------------------------------------------------------
            list_json = engine.get_rankings_list(cat)
            
            cleaned_list = clean_json_text(list_json)
            if not cleaned_list or cleaned_list == "{}":
                print(f"⚠️ [{cat}] No list data returned. Skipping.")
                continue
                
            parsed_list = json.loads(cleaned_list)
            
            # -----------------------------------------------------------
            # Step 2. Top 10 차트 저장
            # -----------------------------------------------------------
            # 규칙: K-POP은 매시간, 나머지는 Key 1번일 때만 저장
            should_update_chart = (cat == 'k-pop') or is_key1
            
            top10_data = parsed_list.get('top10', [])
            if top10_data and should_update_chart:
                print(f"  > 📊 Saving Top 10 Chart ({len(top10_data)} items)...")
                db_data = []
                for item in top10_data:
                    db_data.append({
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'),
                        "meta_info": item.get('info', ''),
                        "score": 0
                    })
                db.save_rankings(db_data)
            elif top10_data:
                print(f"  > ⏩ Skipping Chart Update (Not Key 1).")

            # -----------------------------------------------------------
            # Step 3. 인물별 기사 작성 (조건부)
            # -----------------------------------------------------------
            people_list = parsed_list.get('people', [])
            if people_list:
                print(f"  > 👥 Reviewing {len(people_list)} People for updates...")
                
                live_news_buffer = [] 

                for person in people_list:
                    rank = person.get('rank')
                    name_en = person.get('name_en')
                    name_kr = person.get('name_kr')
                    
                    if not name_en or not rank: continue
                    if not name_kr: name_kr = name_en
                    
                    # [조건 로직]
                    # 1위~3위: 무조건 작성 (변화 없어도 최신 이슈 체크)
                    # 4위~30위: 최근(12시간)에 다룬 적 없는 "신규 진입자"만 작성
                    
                    should_write = False
                    reason = ""
                    
                    if rank <= 3:
                        should_write = True
                        reason = "Top 3 Rank"
                    elif name_en not in recent_people:
                        should_write = True
                        reason = "New Entry"
                    
                    if should_write:
                        print(f"    -> 📝 Processing Rank #{rank}: {name_en} ({reason})...")
                        
                        # (1) 심층 취재 (Perplexity) - 기사 개수 자동 조절됨
                        # fetch_article_details 내부에서 rank에 따라 4개/3개/2개 읽음
                        facts = engine.fetch_article_details(name_kr, name_en, cat, rank)
                        
                        if "Failed" in facts:
                            print(f"       ⚠️ Skip: Facts collection failed.")
                            continue

                        # (2) 기사 작성 (Groq)
                        full_text = engine.edit_with_groq(name_en, facts, cat)
                        
                        # (3) 데이터 파싱
                        score = 70
                        if "###SCORE:" in full_text:
                            try:
                                parts = full_text.split("###SCORE:")
                                full_text = parts[0].strip()
                                import re
                                m = re.search(r'\d+', parts[1])
                                if m: score = int(m.group())
                            except: pass
                            
                        lines = full_text.split('\n')
                        title = lines[0].replace('Headline:', '').strip()
                        summary = "\n".join(lines[1:]).strip()
                        img_url = naver.get_image(name_kr)
                        
                        article_data = {
                            "category": cat,
                            "keyword": name_en,
                            "title": title,
                            "summary": summary,
                            "link": "", # 링크 없음
                            "image_url": img_url,
                            "score": score,
                            "likes": 0,
                            "query": f"{cat} top 30 rank {rank}",
                            "raw_result": str(person),
                            "run_count": run_count
                        }
                        
                        # (4) DB 저장
                        db.save_to_archive(article_data)
                        
                        live_news_buffer.append({
                            "category": article_data['category'],
                            "keyword": article_data['keyword'],
                            "title": article_data['title'],
                            "summary": article_data['summary'],
                            "link": "",
                            "image_url": article_data['image_url'],
                            "score": score,
                            "likes": 0
                        })
                        
                        # API 속도 조절을 위해 약간 대기 (너무 빠르면 에러남)
                        time.sleep(1) 
                    else:
                        pass # 이미 다뤘고 순위도 4위 밖이면 스킵

                # Live News 테이블 업데이트 (새로 쓴 기사들)
                if live_news_buffer:
                    db.save_live_news(live_news_buffer)
                    print(f"  > ✅ Published {len(live_news_buffer)} New Articles.")
                else:
                    print("  > 💤 No new articles needed.")

        except Exception as e:
            print(f"❌ [{cat}] Critical Error: {e}")

    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
