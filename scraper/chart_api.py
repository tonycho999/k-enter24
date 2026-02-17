import asyncio
import json
from playwright.async_api import async_playwright

class ChartEngine:
    def __init__(self):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        self.rotation_map = {
            "k-pop": ["melon", "genie", "bugs"],
            "k-drama": ["naver_search", "naver_search", "naver_search"],
            "k-movie": ["naver_search", "naver_search", "naver_search"],
            "k-entertain": ["naver_search", "naver_search", "naver_search"]
        }

    async def get_top10_chart(self, category, run_count):
        targets = self.rotation_map.get(category, ["naver_search"])
        target = targets[run_count % 3]
        
        print(f"🔍 [Attempt] Category: {category} | Primary: {target}")
        result = await self._scrape_entry(target, category)
        
        if not result or len(result) < 5:
            print(f"⚠️ {target} failed. Switching to Backup: naver_search")
            result = await self._scrape_entry("naver_search", category)
            
        return json.dumps({"top10": result}, ensure_ascii=False)

    async def _scrape_entry(self, target, category):
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(user_agent=self.ua)
                data = []
                
                if target == "melon":
                    await page.goto("https://www.melon.com/chart/index.htm", timeout=30000)
                    rows = await page.query_selector_all(".lst50")
                    for i, r in enumerate(rows[:10]):
                        t = await (await r.query_selector(".rank01 a")).inner_text()
                        a = await (await r.query_selector(".rank02 a")).inner_text()
                        data.append({"rank": i+1, "title": t.strip(), "info": a.strip()})
                
                elif target == "naver_search":
                    queries = {"k-pop":"멜론차트", "k-drama":"드라마 시청률", "k-movie":"박스오피스", "k-entertain":"예능 시청률"}
                    await page.goto(f"https://search.naver.com/search.naver?query={queries.get(category, category)}")
                    await page.wait_for_timeout(2000)
                    items = await page.query_selector_all(".api_subject_bx .list_box .item")
                    for i, item in enumerate(items[:10]):
                        title_el = await item.query_selector(".name, .title")
                        info_el = await item.query_selector(".figure, .sub_text")
                        if title_el:
                            t = await title_el.inner_text()
                            inf = await info_el.inner_text() if info_el else ""
                            data.append({"rank": i+1, "title": t.strip(), "info": inf.strip()})

                await browser.close()
                return data
            except Exception as e:
                print(f"❌ Scrape Error ({target}): {e}")
                if 'page' in locals():
                    await page.screenshot(path=f"error_{category}.png")
                    with open(f"error_{category}.html", "w", encoding="utf-8") as f:
                        f.write(await page.content())
                await browser.close()
                return None
