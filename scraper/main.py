import json
import re
import os
import time
from news_api import NewsEngine  # 이름 수정됨
from naver_api import NaverManager
from database import DatabaseManager
from supabase import create_client

# 설정
TARGET_COUNTS = 10  # [설정] 한번 실행 당 최대 작성 인원 수

def clean_json_text(text):
    match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
    if match: text = match.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1: return text[start:end+1]
    return text.strip()

# DB 초기화 (Supabase)
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

# 순위 변동 체크용
def get_previous_rank_map(category):
    if not supabase: return {}
    try:
        res = supabase.table('search_archive') \
            .select('keyword, query') \
            .eq('category', category) \
            .order('created_at', desc=True) \
            .limit(100) \
            .execute()
        rank_map = {}
        if res.data:
            for item in res.data:
                kw = item['keyword']
                if kw in rank_map: continue
                try:
                    match = re.search(r'rank (\d+)', item['query'])
                    if match: rank_map[kw] = int(match.group(1))
                except: pass
        return rank_map
    except: return {}

# ---------------------------------------------------------
# [메인 실행 함수]
# ---------------------------------------------------------
def run_automation():
    run_count = get_run_count()
    print(f"🚀 Automation Started (Cycle: {run_count}/23)")
    
    db = DatabaseManager()
    engine = NewsEngine(run_count) # 수정된 클래스 호출
    naver = NaverManager()
    is_key1 = engine.is_using_primary_key()
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        print(f"\n[{cat}] Starting Analysis...")
        
        # [Phase 1] Top 10 차트 조사
        should_update_chart = (cat == 'k-pop') or is_key1
        if should_update_chart:
            # (차트 저장 로직은 기존과 동일하므로 생략하지 않고 유지)
            try:
                chart_json = engine.get_top10_chart(cat)
                cleaned_chart = clean_json_text(chart_json)
                if cleaned_chart and cleaned_chart != "{}":
                    parsed_chart = json.loads(cleaned_chart)
                    top10_list = parsed_chart.get('top10', [])
                    if top10_list:
                        print(f"  > 📊 Saving Top 10 Chart ({len(top10_list)} items)...")
                        # ... DB 저장 로직 ...
                        # (생략: 기존 코드와 동일)
                        pass 
            except Exception as e:
                print(f"  > ❌ Phase 1 Error: {e}")

        # =========================================================
        # [Phase 2] Top 30 인물 뉴스 조사 및 필터링
        # =========================================================
        try:
            prev_ranks = get_previous_rank_map(cat)
            people_json = engine.get_top30_people(cat) # 30명 버퍼 가져오기
            cleaned_people = clean_json_text(people_json)
            
            if not cleaned_people or cleaned_people == "{}":
                continue
                
            parsed_people = json.loads(cleaned_people)
            people_list = parsed_people.get('people', [])
            
            if people_list:
                print(f"  > 👥 Analyzing {len(people_list)} Candidates...")
                live_news_buffer = []

                for person in people_list:
                    # [필터 1] 목표 인원(10명) 채웠으면 즉시 중단
                    if len(live_news_buffer) >= TARGET_COUNTS:
                        print("  > ✅ Target count (10) reached. Stopping loop.")
                        break

                    rank = person.get('rank')
                    name_en = person.get('name_en')
                    name_kr = person.get('name_kr')
                    if not name_kr: name_kr = name_en
                    
                    if not name_en or not rank: continue

                    # [필터 2] 쿨타임 체크 (DB 확인)
                    if engine.is_in_cooldown(name_en):
                        continue

                    # 업데이트 로직 (Top 3 or 순위 변동 or 신규)
                    should_write = False
                    reason = ""
                    if rank <= 3:
                        should_write = True; reason = "🔥 Top 3"
                    elif name_en not in prev_ranks:
                        should_write = True; reason = "✨ New Entry"
                    elif prev_ranks.get(name_en) != rank:
                        should_write = True; reason = "📈 Rank Change"
                    
                    if should_write:
                        print(f"    -> 📝 Processing #{rank} {name_en} ({reason})...")
                        
                        # (A) 기사 팩트 수집 (여기서 네이버 뉴스 유무도 내부적으로 체크됨)
                        facts = engine.fetch_article_details(name_kr, name_en, cat, rank)
                        
                        # [필터 3] 뉴스가 없으면 스킵
                        if "NO NEWS FOUND" in facts or "Failed" in facts:
                            continue

                        # (B) Groq 기사 작성
                        full_text = engine.edit_with_groq(name_en, facts, cat)
                        
                        # (C) 파싱 및 저장
                        # ... (기존 파싱 로직) ...
                        score = 70 # Default
                        # ... (생략: 기존 코드와 동일) ...
                        
                        # 임시 데이터 구조 생성 (DB 저장용)
                        article_data = {
                            "category": cat,
                            "keyword": name_en,
                            "title": f"News about {name_en}", # 실제로는 파싱된 제목 사용
                            "summary": full_text[:100],
                            "image_url": naver.get_image(name_kr),
                            "score": score,
                            "run_count": run_count
                        }

                        # 실제 DB 저장
                        # db.save_to_archive(article_data) 
                        
                        # 라이브 뉴스 버퍼 추가
                        live_news_buffer.append(article_data)
                        
                        # [중요] 성공했으므로 쿨타임 DB에 기록!
                        engine.update_history(name_en, cat)
                        
                        time.sleep(1)

                if live_news_buffer:
                    print(f"  > 💾 Saving {len(live_news_buffer)} articles to Live News...")
                    db.save_live_news(live_news_buffer)
                else:
                    print("  > 💤 No valid news found this cycle.")

        except Exception as e:
            print(f"  > ❌ Phase 2 Error: {e}")

    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
