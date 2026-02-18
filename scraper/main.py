import os
import json
from chart_api import ChartEngine
from news_api import NewsEngine
from naver_api import NaverImageEngine
from database import DatabaseManager
from supabase import create_client

# Supabase 연결
supa_url = os.environ.get("SUPABASE_URL")
supa_key = os.environ.get("SUPABASE_KEY")
supabase = create_client(supa_url, supa_key) if supa_url and supa_key else None

# 인물 30인 리스트 (추후 DB 관리 권장)
TARGET_PEOPLE = ["임영웅", "뉴진스", "에스파", "아이브", "방탄소년단"] # 예시

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
    should_update_chart = key_idx in [1, 5]
    
    print(f"🚀 [Cycle {run_count}] Key #{key_idx} | Chart Update: {should_update_chart}")
    
    db = DatabaseManager()
    img_engine = NaverImageEngine()
    
    # --- Phase 1: Chart Update ---
    if should_update_chart:
        chart_engine = ChartEngine()
        chart_engine.set_groq_client(api_key)
        for cat in ["k-pop", "k-drama", "k-movie", "k-entertain"]:
            print(f"📊 Processing {cat}...")
            data = json.loads(chart_engine.get_top10_chart(cat)).get("top10", [])
            db_data = []
            for item in data:
                img_url = img_engine.get_image_url(f"{cat} {item['title']}")
                db_data.append({
                    "category": cat, "rank": item.get('rank'),
                    "title": item.get('title'), "meta_info": str(item.get('info', '')),
                    "image_url": img_url, "score": 100
                })
            db.save_rankings(db_data)

    # --- Phase 2: News/Person Generation ---
    print(f"📝 Generating News Articles...")
    news_engine = NewsEngine(api_key)
    for person in TARGET_PEOPLE:
        context = news_engine.fetch_rss_context(keyword=person)
        if context:
            title, body = news_engine.generate_article(person, context)
            img_url = img_engine.get_image_url(f"연예인 {person}")
            # db.save_news({'title': title, 'content': body, 'image_url': img_url, 'target': person})
            print(f"✅ Article for {person} created.")
    
    update_run_count(run_count)

if __name__ == "__main__":
    run_automation()
