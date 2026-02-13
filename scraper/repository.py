import os
from supabase import create_client, Client
from datetime import datetime, timedelta

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = None

def init_supabase():
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except: pass

init_supabase()

def save_to_archive(news_list):
    """
    [New] 상위 랭킹 뉴스(Top 10)를 영구 보존용 아카이브에 저장
    """
    if not supabase or not news_list: return
    
    try:
        # 아카이브용 데이터로 변환 (필요한 필드만)
        archive_data = []
        for n in news_list:
            archive_data.append({
                "category": n['category'],
                "keyword": n.get('keyword'),
                "title": n['title'],
                "summary": n['summary'],
                "rank": n.get('rank'),
                "image_url": n['image_url'],
                "created_at": datetime.now().isoformat()
            })
            
        supabase.table("search_archive").insert(archive_data).execute()
        print(f"   🏆 Archive: Top {len(archive_data)} 기사 저장 완료.")
    except Exception as e:
        print(f"   ⚠️ 아카이브 저장 실패 (중복 등): {e}")

def refresh_live_news(category, news_list):
    """
    [New] 해당 카테고리의 기존 뉴스를 모두 삭제하고, 
    새로운 랭킹 뉴스(30개)로 교체 (Refresh)
    """
    if not supabase or not news_list: return
    
    try:
        # 1. 기존 해당 카테고리 데이터 전체 삭제
        supabase.table("live_news").delete().eq("category", category).execute()
        
        # 2. 신규 데이터 일괄 삽입
        supabase.table("live_news").insert(news_list).execute()
        
        print(f"   ✅ Live News: '{category}' 카테고리 {len(news_list)}개로 전면 교체 완료.")
        
    except Exception as e:
        print(f"   ❌ Live News 교체 오류: {e}")

# 기존 함수들 (사용하지 않지만 호환성을 위해 남겨둘 경우)
def get_existing_links(category): return set()
def save_news(news_list): pass
def manage_slots(category): pass
