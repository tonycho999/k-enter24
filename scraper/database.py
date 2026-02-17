def save_live_news(self, news_list):
        """
        Live News 테이블에 저장하고, 카테고리별로 최신 50개만 남기고 나머지는 삭제합니다.
        (Archive는 건드리지 않고 Live News만 정리합니다)
        """
        if not self.supabase or not news_list:
            return

        try:
            # 1. 새로운 뉴스 저장 (Upsert)
            data = self.supabase.table('live_news').upsert(news_list).execute()
            print(f"   > [DB] Live News Saved: {len(news_list)} items.")

            # 2. 청소 작업 (Cleanup) - 방금 업데이트된 카테고리만 확인
            # 중복 제거된 카테고리 목록 추출
            categories = set([item['category'] for item in news_list])

            for cat in categories:
                # 해당 카테고리의 모든 기사 ID를 최신순(내림차순)으로 가져옴
                res = self.supabase.table('live_news') \
                    .select('id') \
                    .eq('category', cat) \
                    .order('created_at', desc=True) \
                    .execute()

                all_articles = res.data if res.data else []

                # 50개가 넘으면, 51번째부터 끝까지 삭제 대상
                if len(all_articles) > 50:
                    ids_to_remove = [item['id'] for item in all_articles[50:]]
                    
                    if ids_to_remove:
                        self.supabase.table('live_news') \
                            .delete() \
                            .in_('id', ids_to_remove) \
                            .execute()
                        print(f"   > 🧹 [Cleanup] Removed {len(ids_to_remove)} old articles from '{cat}'.")

        except Exception as e:
            print(f"   > ⚠️ Error in save_live_news: {e}")
