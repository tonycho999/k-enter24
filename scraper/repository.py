import os
from supabase import create_client, Client
from datetime import datetime, timedelta

# 환경변수 로드
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# [수정] 클라이언트 생성을 함수 내부나 try-catch로 감싸서, import 시점에 에러가 나지 않도록 변경
supabase: Client = None

def init_supabase():
    global supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            print(f"❌ Supabase Connection Error: {e}")
    else:
        print("⚠️ Warning: Supabase 환경변수가 설정되지 않았습니다. DB 저장을 건너뜁니다.")

# 파일이 로드될 때 초기화 시도
init_supabase()

def get_existing_links(category):
    """기존 뉴스 링크 가져오기 (중복 방지용)"""
    if not supabase: return set()
    
    try:
        # 최근 7일치만 비교 (속도 최적화)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        res = supabase.table("live_news").select("link").eq("category", category).gt("created_at", week_ago).execute()
        return {item['link'] for item in res.data}
    except Exception as e:
        print(f"⚠️ DB Read Error ({category}): {e}")
        return set()

def save_news(news_list):
    """뉴스 데이터 일괄 저장"""
    if not supabase or not news_list: return

    try:
        # Supabase는 한 번에 많은 데이터를 넣을 때 배치 처리가 좋음
        data, count = supabase.table("live_news").insert(news_list).execute()
        print(f"   ✅ 신규 {len(news_list)}개 DB 저장 완료.")
    except Exception as e:
        print(f"❌ DB Save Error: {e}")

def manage_slots(category):
    """카테고리별 30개 슬롯 유지 (오래된 기사 삭제)"""
    if not supabase: return

    try:
        # 1. 해당 카테고리의 전체 기사 수 확인
        res = supabase.table("live_news").select("id", count="exact").eq("category", category).execute()
        total_count = res.count
        
        if total_count > 30:
            # 2. 삭제해야 할 개수 계산
            to_delete = total_count - 30
            
            # 3. 가장 오래된 기사 ID 가져오기 (created_at 오름차순)
            # range(0, to_delete-1) -> 오래된 순서대로 가져옴
            old_posts = supabase.table("live_news")\
                .select("id")\
                .eq("category", category)\
                .order("created_at", desc=False)\
                .range(0, to_delete - 1)\
                .execute()
            
            if old_posts.data:
                delete_ids = [item['id'] for item in old_posts.data]
                supabase.table("live_news").delete().in_("id", delete_ids).execute()
                print(f"   🧹 공간 확보: {len(delete_ids)}개 삭제 완료.")
                
    except Exception as e:
        print(f"⚠️ Slot Management Error: {e}")

def archive_top_articles():
    """(선택) 인기 기사를 아카이브 테이블로 이동하거나 플래그 처리"""
    pass

def get_recent_titles():
    """트렌드 분석용 최신 타이틀 가져오기"""
    if not supabase: return []
    try:
        res = supabase.table("live_news").select("title").order("created_at", desc=True).limit(50).execute()
        return [item['title'] for item in res.data]
    except:
        return []

def update_keywords_db(keywords):
    """분석된 키워드 저장"""
    if not supabase: return
    # 나중에 구현
    pass
