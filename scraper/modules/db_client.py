import os
from supabase import create_client, Client

def get_supabase_client():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase 환경변수가 설정되지 않았습니다.")
    return create_client(url, key)

def insert_report(data):
    supabase = get_supabase_client()
    try:
        response = supabase.table("hourly_reports").insert(data).execute()
        print(f"[DB Success] {data['artist_name']} 리포트 저장 완료")
        return response
    except Exception as e:
        print(f"[DB Error] 저장 실패: {e}")
