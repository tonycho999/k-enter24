import os
from supabase import create_client, Client

class DatabaseManager:
    def __init__(self):
        # [FIX] Changed environment variable names to match main.py and YAML
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")  # Changed from SUPABASE_SERVICE_ROLE_KEY

        if not url or not key:
            print("⚠️ Warning: Supabase Credentials missing in DatabaseManager.")
            self.supabase = None
        else:
            try:
                self.supabase: Client = create_client(url, key)
            except Exception as e:
                print(f"⚠️ Failed to initialize Supabase Client: {e}")
                self.supabase = None

    def save_live_news(self, data_list):
        """Save data to public.live_news table"""
        if not self.supabase: return
        try:
            self.supabase.table("live_news").insert(data_list).execute()
        except Exception as e:
            print(f"  [DB Error] Live News Insert Failed: {e}")

    def save_rankings(self, data_list):
        """Save data to public.live_rankings table"""
        if not self.supabase: return
        try:
            self.supabase.table("live_rankings").insert(data_list).execute()
        except Exception as e:
            print(f"  [DB Error] Rankings Insert Failed: {e}")

    def save_to_archive(self, article_data):
        """Save data to public.search_archive table"""
        if not self.supabase: return
        try:
            self.supabase.table("search_archive").insert(article_data).execute()
        except Exception as e:
            print(f"  [DB Error] Archive Insert Failed: {e}")
