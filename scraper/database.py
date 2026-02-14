import os
from supabase import create_client, Client
from dotenv import load_dotenv
import config  # 같은 폴더에 있으므로 바로 import 가능

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# 연결 실패 시 예외 처리
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except:
    supabase = None

def save_news(data_list):
    """뉴스 데이터 저장"""
    if not supabase or not data_list: return
    try:
        supabase.table("live_news").upsert(data_list).execute()
        print(f"   💾 Saved {len(data_list)} articles.")
    except Exception as e:
        print(f"   ⚠️ DB Save Error: {e}")

def cleanup_old_news(category):
    """카테고리별 오래된 뉴스 삭제"""
    if not supabase: return
    try:
        # 개수 확인
        resp = supabase.table("live_news").select("id", count="exact").eq("category", category).execute()
        count = resp.count
        
        if count > config.MAX_ITEMS_PER_CATEGORY:
            limit = count - config.MAX_ITEMS_PER_CATEGORY
            # 오래된 순으로 ID 조회
            old_rows = supabase.table("live_news").select("id").eq("category", category).order("created_at", desc=False).limit(limit).execute()
            ids = [row['id'] for row in old_rows.data]
            
            if ids:
                supabase.table("live_news").delete().in_("id", ids).execute()
                print(f"   🧹 Cleaned up {len(ids)} old items.")
    except Exception as e:
        print(f"   ⚠️ Cleanup Error: {e}")
