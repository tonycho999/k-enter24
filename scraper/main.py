import json
import re
import os
import time
from news_api import NewsEngine
from naver_api import NaverManager
from database import DatabaseManager
from supabase import create_client

# 설정
TARGET_COUNTS_FOR_OTHERS = [5, 17] 

def clean_json_text(text):
    match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
    if match: text = match.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1: return text[start:end+1]
    return text.strip()

# DB 연결
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
    except Exception as e: print(f"⚠️ Update Count Error: {e}")

# ---------------------------------------------------------
# [Helper] 이전 실행의 순위 정보를 가져오는 함수
# ---------------------------------------------------------
def get_previous_rank_map(db_manager, category):
    """
    DB(search_archive)에서 해당 카테고리의 가장 최근 30개 기사를 가져와서
    { "keyword": rank } 형태의 맵을 만듭니다.
    """
    try:
        # DB 매니저에 get_latest_articles 메서드가 있다고 가정하거나 직접 쿼리
        # 여기서는 supabase client를 직접 사용하여 구현
        res = supabase.table('search_archive') \
            .select('keyword, raw_result') \
            .eq('category', category) \
            .order('created_at', desc=True) \
            .limit(50) \
            .execute()
            
        rank_map = {}
        if res.data:
            for item in res.data:
                # raw_result에 저장된 JSON 등에서 rank를 파싱하거나
                # 단순히 "이전에 존재했는지" 여부만 체크해도 됩니다.
                # 여기서는 keyword(이름)가 존재하면 이전 순위를 알 수 있다고 가정.
                # 편의상 '존재 여부'만 체크하거나, 정확한 Rank 비교를 위해 로직 추가 가능.
                rank_map[item['keyword']] = 0 # 0은 '존재했음' 표시
        return rank_map
    except:
        return {}

def run_automation():
    run_count = get_run_count()
    print(f"🚀 Automation Started (Cycle: {run_count}/23)")
    
    db = DatabaseManager()
    engine = NewsEngine(run_count)
    naver = NaverManager()
    
    is_key1 = engine.is_using_primary_key()
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        # [스케줄 체크] 인물 뉴스는 매시간 갱신 체크하므로 여기서는 스킵 안함.
        # 단, Top 10 차트 저장 여부는 아래에서 결정.
        
        print(f"\n[{cat}] Analyzing Trends...")
        
        # 1. 이전 시간대 순위 정보 로드 (비교용)
        prev_ranks = get_previous_rank_map(db, cat)

        try:
            # 2. Perplexity로 'Top 10 차트' + 'Top 30 인물 리스트' 가져오기
            list_json = engine.get_rankings_list(cat)
            parsed_list = json.loads(clean_json_text(list_json))
            
            # -----------------------------------------------------------
            # A. Top 10 Chart 처리 (조건부 저장)
            # -----------------------------------------------------------
            # 조건: K-POP은 매시간, 나머지는 Key 1번일 때만
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
                print(f"  > ⏩ Skipping Chart Update (Not Key 1 & Not K-Pop).")

            # -----------------------------------------------------------
            # B. Top 30 People Articles 처리 (조건부 작성)
            # -----------------------------------------------------------
            people_list = parsed_list.get('people', [])
            if people_list:
                print(f"  > 👥 Checking {len(people_list)} People for updates...")
                
                processed_count = 0
                live_news_buffer = [] # 라이브 뉴스용 버퍼

                for person in people_list:
                    rank = person.get('rank')
                    name_en = person.get('name_en')
                    name_kr = person.get('name_kr')
                    if not name_en or not rank: continue
                    
                    # [결정 로직] 기사를 새로 쓸 것인가?
                    # 1. 1~3위: 무조건 작성
                    # 2. 4~30위: 이전에 없던 사람이거나(New), 순위 변동이 있을 때(로직상 단순화하여 '이름이 없으면'으로 처리 가능)
                    # (정확한 Rank 비교를 원하시면 prev_ranks에 rank값 저장해서 비교하면 됨)
                    
                    should_write = False
                    if rank <= 3:
                        should_write = True
                    else:
                        # 이전에 없던 사람이면 작성
                        if name_en not in prev_ranks:
                            should_write = True
                        # (선택) 순위 변동 로직을 추가하려면 여기서 비교
                    
                    if should_write:
                        print(f"    -> 📝 Writing Article: #{rank} {name_en}...")
                        
                        # 2-1. 심층 기사 내용 수집 (Perplexity)
                        # 여기서 rank를 넘겨줘서 4개/3개/2개 기사를 읽게 함
                        facts = engine.fetch_article_details(name_kr, name_en, cat, rank)
                        
                        # 2-2. 기사 작성 (Groq)
                        full_text = engine.edit_with_groq(name_en, facts, cat)
                        
                        # 2-3. 파싱 및 저장
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
                            "link": "", # 링크 수집 안 함
                            "image_url": img_url,
                            "score": score,
                            "likes": 0,
                            "query": f"{cat} top 30 rank {rank}",
                            "raw_result": json.dumps(person), # 원본 데이터 저장
                            "run_count": run_count
                        }
                        
                        # 아카이브 저장 (새로 쓴 기사만)
                        db.save_to_archive(article_data)
                        
                        # 라이브 데이터 준비
                        live_news_buffer.append({
                            "category": cat,
                            "keyword": name_en,
                            "title": title,
                            "summary": summary,
                            "link": "",
                            "image_url": img_url,
                            "score": score,
                            "likes": 0
                        })
                        processed_count += 1
                        
                # [중요] 라이브 뉴스 테이블 업데이트
                # 매시간 새로 쓴 기사 + (쓰지 않았더라도 순위권인 기사들은 DB에서 불러와야 완벽하지만)
                # 요청하신대로 "새로 작성된 기사" 위주로 처리하거나, 
                # 기존 로직대로 덮어씌웁니다. 여기서는 '새로 쓴 것'만 라이브에 올립니다.
                if live_news_buffer:
                    db.save_live_news(live_news_buffer)
                    print(f"  > ✅ Updated {len(live_news_buffer)} Live Articles.")
                    
        except Exception as e:
            print(f"❌ [{cat}] Error: {e}")

    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
