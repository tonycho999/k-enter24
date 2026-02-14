# scraper/processor.py
import time
from datetime import datetime
import config
import naver_api
import gemini_api
import database

def run_category_process(category):
    print(f"\n🚀 [Processing] Category: {category}")

    # 1. [광범위 탐색] API로 100개 수집
    keyword = config.SEARCH_KEYWORDS.get(category)
    raw_items = naver_api.search_news_api(keyword, display=100)
    
    if not raw_items:
        print("   ⚠️ No items found from Naver API.")
        return

    titles = "\n".join([f"- {item['title']}" for item in raw_items])

    # 2. [랭킹 선정] AI에게 Top 10 키워드/순위 추출 요청
    rank_prompt = f"""
    [Task]
    Analyze these news titles about {category}.
    1. Identify Top 10 trending keywords (Person, Group, Work).
    2. Provide a short meta info for each.
    
    [Output JSON Format]
    {{
        "rankings": [
            {{ "rank": 1, "keyword": "Name", "meta": "Reason", "score": 95 }}
        ]
    }}
    """
    
    rank_res = gemini_api.ask_gemini(rank_prompt)
    if not rank_res: return

    rankings = rank_res.get("rankings", [])[:10]
    
    # 2-1. 랭킹 DB 저장 (보여주기용)
    db_rankings = []
    for item in rankings:
        db_rankings.append({
            "category": category,
            "rank": item.get("rank"),
            "title": item.get("keyword"),
            "meta_info": item.get("meta", ""),
            "score": item.get("score", 0),
            "updated_at": datetime.now().isoformat()
        })
    database.save_rankings_to_db(db_rankings)

    # 3. [타겟 선정] 도배 방지 (쿨타임 4시간)
    target_keyword = ""
    print("   🛡️ Checking cooldowns (4 hours)...")
    
    for item in rankings:
        candidate = item.get("keyword")
        # DB 체크: 최근에 썼니?
        if database.is_keyword_used_recently(category, candidate, hours=4):
            print(f"      ❌ Skip '{candidate}' (Cooldown active).")
        else:
            print(f"      ✅ Selected target: '{candidate}'!")
            target_keyword = candidate
            break
    
    # 만약 10개 다 쿨타임 걸렸으면? (드물지만) -> 그냥 1위 강제 선택
    if not target_keyword and rankings:
        target_keyword = rankings[0].get("keyword")
        print(f"      ⚠️ All candidates on cooldown. Forced select: '{target_keyword}'")

    if not target_keyword: return

    # 4. [정밀 수집] 확정된 키워드로 기사 3개 수집
    print(f"   🎯 Deep diving into: {target_keyword}")
    target_items = naver_api.search_news_api(target_keyword, display=3)
    
    full_texts = []
    target_link = ""
    target_image = ""

    for item in target_items:
        link = item['link']
        crawled = naver_api.crawl_article(link)
        
        if crawled['text']:
            full_texts.append(crawled['text'])
            if not target_image: target_image = crawled['image']
            if not target_link: target_link = link
        else:
            full_texts.append(item['description'])
            if not target_link: target_link = link

    if not full_texts: return

    # 5. [요약] AI 기사 작성
    summary_prompt = f"""
    [Articles about '{target_keyword}']
    {str(full_texts)[:6000]}

    [Task]
    Write a high-quality news summary in Korean.
    [Output JSON]
    {{ "title": "Catchy Title", "summary": "Detailed summary (3-5 sentences)" }}
    """
    
    sum_res = gemini_api.ask_gemini(summary_prompt)
    
    if sum_res:
        news_item = {
            "category": category,
            "keyword": target_keyword,
            "title": sum_res.get("title", f"{target_keyword} 이슈"),
            "summary": sum_res.get("summary", ""),
            "link": target_link,
            "image_url": target_image,
            "score": 100, # 1위 선정된 건이므로 만점
            "created_at": datetime.now().isoformat(),
            "likes": 0
        }
        
        # 6. [이원화 저장] Live(전시용) + Archive(보관용)
        # 리스트 형태로 전달
        database.save_news_to_live([news_item])     # Live에 저장
        database.save_news_to_archive([news_item])  # Archive에 저장
        
        # 7. [청소] Live 테이블만 30개 유지
        database.cleanup_old_data(category, config.MAX_ITEMS_PER_CATEGORY)
