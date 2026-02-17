import json
import re
import os
import time
from news_api import NewsEngine
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

# ---------------------------------------------------------
# [Supabase 연결 및 Run Count 관리]
# ---------------------------------------------------------
supa_url = os.environ.get("SUPABASE_URL")
supa_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supa_url, supa_key) if supa_url and supa_key else None

def get_run_count():
    """
    이미지의 system_status 테이블에서 현재 실행 번호를 가져옵니다.
    """
    if not supabase: return 0
    try:
        # id가 1인 row의 run_count를 가져옴
        res = supabase.table('system_status').select('run_count').eq('id', 1).single().execute()
        return res.data['run_count'] if res.data else 0
    except:
        # 테이블이 비어있거나 에러나면 0부터 시작
        return 0

def update_run_count(current):
    """
    작업 완료 후 실행 번호를 +1 업데이트합니다 (0~23 사이 순환).
    """
    if not supabase: return
    next_count = current + 1
    if next_count >= 24: next_count = 0  # 24가 되면 다시 0으로 초기화
    try:
        supabase.table('system_status').upsert({'id': 1, 'run_count': next_count}).execute()
        print(f"🔄 Cycle Count Updated: {current} -> {next_count}")
    except Exception as e:
        print(f"⚠️ Failed to update run count: {e}")

# 순위 변동 체크용 (이전 랭킹 로딩)
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
    # 1. 현재 몇 번째 실행인지 확인 (DB에서 로드)
    run_count = get_run_count()
    print(f"🚀 Automation Started (Cycle: {run_count}/23)")
    
    db = DatabaseManager()
    engine = NewsEngine(run_count)  # run_count에 따라 API 키를 바꿔서 엔진 시작
    naver = NaverManager()
    
    # K-Pop의 경우에만 차트를 갱신할지 결정 (옵션)
    is_key1 = engine.is_using_primary_key() 
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        print(f"\n[{cat}] Starting Analysis...")
        
        # [Phase 1] Top 10 차트 조사 및 저장
        should_update_chart = (cat == 'k-pop') or is_key1
        if should_update_chart:
            try:
                chart_json = engine.get_top10_chart(cat)
                cleaned_chart = clean_json_text(chart_json)
                if cleaned_chart and cleaned_chart != "{}":
                    parsed_chart = json.loads(cleaned_chart)
                    top10_list = parsed_chart.get('top10', [])
                    if top10_list:
                        print(f"  > 📊 Saving Top 10 Chart ({len(top10_list)} items)...")
                        db_data = []
                        for item in top10_list:
                            db_data.append({
                                "category": cat,
                                "rank": item.get('rank'),
                                "title": item.get('title'),
                                "meta_info": item.get('info', ''),
                                "score": item.get('score', 0)
                            })
                        db.save_rankings(db_data)
            except Exception as e:
                print(f"  > ❌ Phase 1 Error: {e}")

        # =========================================================
        # [Phase 2] Top 30 인물 뉴스 조사 및 필터링
        # =========================================================
        try:
            prev_ranks = get_previous_rank_map(cat)
            people_json = engine.get_top30_people(cat)
            cleaned_people = clean_json_text(people_json)
            
            if not cleaned_people or cleaned_people == "{}":
                continue
                
            parsed_people = json.loads(cleaned_people)
            people_list = parsed_people.get('people', [])
            
            if people_list:
                print(f"  > 👥 Analyzing {len(people_list)} Candidates...")
                live_news_buffer = []

                for person in people_list:
                    # [필터 1] 목표 인원(10명) 채웠으면 해당 카테고리 종료
                    if len(live_news_buffer) >= TARGET_COUNTS:
                        print("  > ✅ Target count (10) reached. Stopping loop.")
                        break

                    rank = person.get('rank')
                    name_en = person.get('name_en')
                    name_kr = person.get('name_kr')
                    if not name_kr: name_kr = name_en
                    
                    if not name_en or not rank: continue

                    # [필터 2] 쿨타임 체크 (DB 확인 - 최근에 작성했으면 패스)
                    if engine.is_in_cooldown(name_en):
                        continue

                    # [로직] 기사 작성 대상 선정 (Top 3 or 순위 변동 or 신규 진입)
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

                        # (B) Groq AI로 기사 작성
                        full_text = engine.edit_with_groq(name_en, facts, cat)
                        
                        # (C) 점수 파싱 (기본 70점)
                        score = 70
                        if "###SCORE:" in full_text:
                            try:
                                parts = full_text.split("###SCORE:")
                                full_text = parts[0].strip()
                                m = re.search(r'\d+', parts[1])
                                if m: score = int(m.group())
                            except: pass

                        # (D) 제목/본문 분리
                        lines = full_text.split('\n')
                        title = lines[0].replace('Headline:', '').strip()
                        summary = "\n".join(lines[1:]).strip()

                        # (E) DB 저장용 데이터 생성
                        # ★★★ 중요: 여기서 run_count를 넣지 않습니다 (live_news 테이블에 없으므로) ★★★
                        article_data = {
                            "category": cat,
                            "keyword": name_en,
                            "title": title,
                            "summary": summary,
                            "image_url": naver.get_image(name_kr), # 네이버 이미지 검색
                            "score": score,
                            "likes": 0,
                            # "run_count": run_count  <-- [삭제됨] 에러 방지용
                        }
                        
                        # 아카이브용 데이터 (여기엔 run_count나 query 정보를 넣고 싶다면 별도로 구성 가능)
                        archive_data = article_data.copy()
                        archive_data["query"] = f"{cat} top 30 rank {rank}"
                        # archive_data["run_count"] = run_count # search_archive 테이블에 컬럼이 있다면 주석 해제

                        # 실제 DB 저장 (Archive는 7일치 보관)
                        db.save_to_archive(archive_data)
                        
                        # 라이브 뉴스 버퍼 추가 (Live는 최신 50개 유지)
                        live_news_buffer.append(article_data)
                        
                        # [중요] 작성 성공했으므로 쿨타임 DB에 기록! (중복 작성 방지)
                        engine.update_history(name_en, cat)
                        
                        time.sleep(1)

                # 한 카테고리 루프가 끝나면 모인 기사들을 한 번에 Live News에 저장
                if live_news_buffer:
                    print(f"  > 💾 Saving {len(live_news_buffer)} articles to Live News...")
                    db.save_live_news(live_news_buffer)
                else:
                    print("  > 💤 No valid news found this cycle.")

        except Exception as e:
            print(f"  > ❌ Phase 2 Error: {e}")

    # 모든 카테고리 작업이 끝나면 Run Count 업데이트 (+1)
    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
