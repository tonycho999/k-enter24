import os
import json
from chart_api import ChartEngine
from database import DatabaseManager
from supabase import create_client

# Supabase 연결
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
    next_count = (current + 1) % 24
    try:
        supabase.table('system_status').upsert({'id': 1, 'run_count': next_count}).execute()
        print(f"🔄 Cycle Updated: {current} -> {next_count}")
    except: pass

def run_automation():
    run_count = get_run_count()
    key_idx = (run_count % 8) + 1
    api_key = os.environ.get(f"GROQ_API_KEY{key_idx}")
    
    # [설정] 1번(0시/8시/16시), 5번(4시/12시/20시) 키일 때 차트 업데이트
    should_update_chart = key_idx in [1, 5]
    
    print(f"🚀 [Cycle {run_count}] Key #{key_idx} | Chart Update: {should_update_chart}")
    
    db = DatabaseManager()
    
    if should_update_chart:
        engine = ChartEngine()
        engine.set_groq_client(api_key) # AI 분석용 키 주입
        
        categories = ["k-pop", "k-drama", "k-movie", "k-entertain"]
        for cat in categories:
            print(f"📊 Processing {cat}...")
            chart_json = engine.get_top10_chart(cat)
            data = json.loads(chart_json).get("top10", [])
            
            if data:
                # live_rankings 테이블 형식에 맞춰 데이터 매핑
                db_data = []
                for item in data:
                    db_data.append({
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'),
                        "meta_info": item.get('info', ''),
                        "score": 100
                    })
                db.save_rankings(db_data)
                print(f"✅ {cat} Rankings Updated.")
            else:
                print(f"⚠️ No data found for {cat}")

    # Phase 2: 기사 작성은 매시간 실행 (여기서 news_api 연동)
    print(f"📝 Generating News Articles for this cycle...")
    
    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
