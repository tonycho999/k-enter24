import asyncio
import json
from playwright.async_api import async_playwright

class ChartEngine:
    def __init__(self):
        self.ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

    async def get_chart_data(self, category, run_count):
        """카테고리별 3사 로테이션 및 실패 시 백업 전환"""
        # 로테이션 타겟 설정
        rotation_map = {
            "k-pop": ["melon", "genie", "bugs"],
            "k-drama": ["nielsen", "naver_drama", "daum_drama"],
            "k-movie": ["kobis", "naver_movie", "daum_movie"],
            "k-entertain": ["nielsen_ent", "naver_ent", "daum_ent"]
        }
        
        targets = rotation_map.get(category, ["naver_search"])
        target = targets[run_count % 3]
        
        print(f"🔍 [Attempt] Category: {category} | Source: {target}")
        
        # 1. 메인 타겟 시도
        data = await self._scrape_entry(target, category)
        
        # 2. 실패 시 즉시 백업(네이버 통합검색) 시도
        if not data:
            print(f"⚠️ {target} failed. Switching to Emergency Backup (Naver Search)...")
            data = await self._scrape_entry("naver_search", category)
            
        return data

    async def _scrape_entry(self, target, category):
        """실제 스크래핑 로직 (에러 발생 시 None 반환)"""
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(user_agent=self.ua)
                page = await context.new_page()
                
                # 타겟별 분기 (예시: 멜론)
                if target == "melon":
                    await page.goto("https://www.melon.com/chart/index.htm", timeout=30000)
                    # ... 기존 멜론 로직 ...
                elif target == "naver_search":
                    # 통합 검색 백업 로직
                    query = f"{category} 순위"
                    await page.goto(f"https://search.naver.com/search.naver?query={query}")
                    # ... 네이버 리스트 로직 ...
                
                # 데이터 추출 후 성공하면 리스트 반환, 실패하면 None
                # (중간 생략: 실제 태그 추출 코드)
                
                await browser.close()
                return data if data else None
            except Exception as e:
                print(f"❌ Scrape Fatal: {e}")
                # 여기서 에러 로그를 남겨 나중에 Groq가 분석하게 함
                with open("error_structure.html", "w", encoding="utf-8") as f:
                    f.write(await page.content())
                return None
