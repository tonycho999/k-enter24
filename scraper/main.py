import os
import json
from datetime import datetime
from chart_api import ChartEngine
from supabase import create_client

# Supabase 연결
supa_url = os.environ.get("SUPABASE_URL")
supa_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supa_url, supa_key) if supa_url and supa_key else None

def run_automation():
    # 1. 로테이션 키 결정
    res = supabase.table('system_status').select('run_count').eq('id', 1).single().execute()
    run_count = res.data['run_count'] if res.data else 0
    key_idx = (run_count % 8) + 1
    api_key = os.environ.get(f"GROQ_API_KEY{key_idx}")

    print(f"🚀 [Cycle {run_count}] Using Key #{key_idx}")

    # 2. 엔진 초기화
    engine = ChartEngine()
    engine.set_groq_client(api_key)
    
    # 3. 모든 카테고리 순회 (k-culture 포함)
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]
    for cat in categories:
        print(f"📊 Processing {cat}...")
        chart_json = engine.get_top10_chart(cat)
        
        try:
            data = json.loads(chart_json).get("top10", [])
            if data:
                db_data = []
                for item in data:
                    db_data.append({
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'),
                        "meta_info": str(item.get('info', '')),
                        "score": 100,
                        "updated_at": datetime.now().isoformat()
                    })
                
                # 기존 데이터 삭제 후 삽입
                supabase.table('live_rankings').delete().eq('category', cat).execute()
                supabase.table('live_rankings').insert(db_data).execute()
                print(f"✅ {cat} Rankings Updated.")
            else:
                print(f"⚠️ {cat} data is empty.")
        except Exception as e:
            print(f"❌ Error parsing/saving {cat}: {e}")

    # 4. 카운트 업데이트
    next_count = (run_count + 1) % 24
    supabase.table('system_status').update({"run_count": next_count}).eq('id', 1).execute()

if __name__ == "__main__":
    run_automation()
