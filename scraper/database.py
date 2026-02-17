import os
from supabase import create_client, Client

class DatabaseManager:
    def __init__(self):
        # [수정] main.py 및 YAML 설정과 동일하게 SUPABASE_KEY 사용
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            print("⚠️ [DB Init] Warning: Supabase Credentials missing.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(url, key)
            except Exception as e:
                print(f"⚠️ [DB Init] Failed to initialize Supabase Client: {e}")
                self.supabase = None

    def save_live_news(self, data_list):
        """public.live_news 테이블에 데이터 저장 (기존 데이터 유지하고 추가)"""
        if not self.supabase or not data_list: return
        try:
            # 배치 insert
            self.supabase.table("live_news").insert(data_list).execute()
        except Exception as e:
            print(f"❌ [DB Error] Live News Insert Failed: {e}")

    def save_rankings(self, data_list):
        """public.live_rankings 테이블에 데이터 저장"""
        if not self.supabase or not data_list: return
        try:
            self.supabase.table("live_rankings").insert(data_list).execute()
        except Exception as e:
            print(f"❌ [DB Error] Rankings Insert Failed: {e}")

    def save_to_archive(self, article_data):
        """public.search_archive 테이블에 데이터 저장"""
        if not self.supabase: return
        try:
            self.supabase.table("search_archive").insert(article_data).execute()
        except Exception as e:
            print(f"❌ [DB Error] Archive Insert Failed: {e}")
