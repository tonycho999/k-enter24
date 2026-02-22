import os
import json
from datetime import datetime
from chart_api import ChartEngine
from supabase import create_client

supabase = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

def run_automation():
    # 키 로테이션 (기존 로직 유지)
    res = supabase.table('system_status').select('run_count').eq('id', 1).single().execute()
    run_count = res.data['run_count'] if res.data else 0
    key_idx = (run_count % 8) + 1
    api_key = os.environ.get(f"GROQ_API_KEY{key_idx}")

    engine = ChartEngine()
    engine.set_groq_client(api_key)
    
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]
    
    for cat in categories:
        print(f"📊 Processing {cat} (Translating to English)...")
        translated_json = engine.get_top10_chart(cat)
        
        try:
            data = json.loads(translated_json).get("top10", [])
            if data:
                db_data = []
                for item in data:
                    db_data.append({
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'), # 영문 제목
                        "meta_info": str(item.get('info', '')), # 영문 정보
                        "score": 100,
                        "updated_at": datetime.now().isoformat()
                    })
                
                # DB 업데이트
                supabase.table('live_rankings').delete().eq('category', cat).execute()
                supabase.table('live_rankings').insert(db_data).execute()
                print(f"✅ {cat} Rankings Updated (English).")
        except Exception as e:
            print(f"❌ Error: {e}")

    # 다음 사이클 업데이트
    supabase.table('system_status').update({"run_count": (run_count + 1) % 24}).eq('id', 1).execute()

if __name__ == "__main__":
    run_automation()
