import os
import json
import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from openai import OpenAI

class ChartEngine:
    def __init__(self):
        # Perplexity for chart searching (non-Kpop)
        self.pplx = OpenAI(
            api_key=os.environ.get("PERPLEXITY_API_KEY"), 
            base_url="https://api.perplexity.ai"
        )

    # ----------------------------------------------------------------
    # [Method A] Direct Scraping (Melon)
    # ----------------------------------------------------------------
    def scrape_melon_chart(self):
        print("  🕷️ [Melon] Scraping Real-time Chart directly...")
        try:
            url = "https://www.melon.com/chart/index.htm"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200: return "{}"

            soup = BeautifulSoup(response.text, 'html.parser')
            song_rows = soup.select('tr.lst50') + soup.select('tr.lst100')
            
            top10_list = []
            for i, row in enumerate(song_rows[:10]):
                try:
                    title = row.select_one('div.ellipsis.rank01 > span > a').text.strip()
                    artist = row.select_one('div.ellipsis.rank02 > span > a').text.strip()
                    top10_list.append({"rank": i + 1, "title": title, "info": artist})
                except: continue
            return json.dumps({"top10": top10_list}, ensure_ascii=False)
        except Exception as e:
            print(f"  ❌ Melon Scraping Error: {e}")
            return "{}"

    # ----------------------------------------------------------------
    # [Method B] AI Search (Time-Aware)
    # ----------------------------------------------------------------
    def get_top10_chart(self, category):
        # 1. K-Pop: Use Scraper
        if category == "k-pop":
            return self.scrape_melon_chart()

        # 2. Others: Use AI with Time Injection
        kst = timezone(timedelta(hours=9))
        current_time_str = datetime.now(kst).strftime("%Y년 %m월 %d일 %H시")

        target_info = ""
        if category == "k-drama": target_info = "Target: Drama Titles (Source: Nielsen Korea, Naver)."
        elif category == "k-movie": target_info = "Target: Movie Titles (Source: KOBIS, Naver)."
        elif category == "k-entertain": target_info = "Target: Variety Show Titles."
        elif category == "k-culture": target_info = "Target: Trending Keywords (Place, Food)."

        system_prompt = "You are a specialized researcher. Search ONLY official Korean sources."
        user_prompt = f"""
        **Current Time: {current_time_str}**
        Search for official rankings in Korea for '{category}'.

        **Task: Extract Top 10 Ranking**
        {target_info}
        - Use data closest to **{current_time_str}**. Do NOT use old data.
        - **Translate Titles to English.**

        **Output JSON ONLY:**
        {{ "top10": [ {{ "rank": 1, "title": "...", "info": "..." }} ] }}
        """
        print(f"  🔍 [Perplexity] Fetching Top 10 Chart ({current_time_str})...")
        try:
            response = self.pplx.chat.completions.create(
                model="sonar-pro",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                temperature=0.1,
                timeout=180
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ Chart API Error: {e}")
            return "{}"
