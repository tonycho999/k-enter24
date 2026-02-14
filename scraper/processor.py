# scraper/processor.py
import database, gemini_api, naver_api
from datetime import datetime

def run_category_process(category):
    print(f"\n🚀 [Autonomous Processing] Category: {category}")

    # 1. AI에게 직접 구글 검색을 통한 트렌드 분석 요청
    rank_rule = "SONG titles and ARTIST names" if category == "K-Pop" else \
                "DRAMA titles and ACTOR names" if category == "K-Drama" else \
                "MOVIE titles and ACTOR names" if category == "K-Movie" else \
                "TV SHOW titles and CAST names" if category == "K-Entertain" else \
                "Hot PLACES and TRADITIONAL culture (Exclude Celebrities)"

    prompt = f"""
    Search Google for the latest {category} trends in Korea as of today.
    1. Identify the TOP 10 trending {rank_rule.split(' and ')[0]}.
    2. Provide the ENGLISH display title and the original KOREAN title for each.
    3. Pick the #1 trending SUBJECT (person or place) in KOREAN for a deep-dive search.

    Return results strictly in JSON:
    {{
      "rankings": [
        {{"rank": 1, "display_title_en": "English Name", "search_keyword_kr": "한국어 원본", "meta": "Reason", "score": 95}}
      ],
      "top_person_kr": "한국어 검색어(재검색용)",
      "top_subject_en": "English Name(DB용)"
    }}
    """
    
    print(f"   1️⃣ AI is searching Google for {category} trends...")
    rank_res = gemini_api.ask_gemini(prompt)
    if not rank_res: return

    # 2. 랭킹 저장 (작품 제목 중심)
    database.save_rankings_to_db(rank_res.get("rankings", []))

    # 3. 쿨타임 체크 (인물/장소 중심)
    target_kr = rank_res.get("top_person_kr")
    target_en = rank_res.get("top_subject_en")

    if database.is_keyword_used_recently(category, target_en, hours=4):
        print(f"   🕒 '{target_en}' is on cooldown.")
        return

    # 4. 기사 작성을 위한 심층 검색 (여기서만 네이버 API 사용)
    # 구글 검색 결과만으로는 본문이 부족할 수 있으므로, 정확한 기사 본문은 네이버에서 가져옵니다.
    print(f"   2️⃣ Deep searching Naver for article details of '{target_kr}'...")
    deep_items = naver_api.search_news_api(target_kr, display=5, sort='date')
    
    full_texts = []
    main_image = ""
    for item in deep_items:
        crawled = naver_api.crawl_article(item['link'])
        if crawled['text'] and len(crawled['text']) > 300:
            full_texts.append(crawled['text'])
            if not main_image and crawled['image'].startswith("https://"):
                main_image = crawled['image']
        if len(full_texts) >= 3: break

    if not full_texts: return

    # 5. 베테랑 기자 스타일로 영어 기사 작성
    article_prompt = f"You are a veteran journalist. Write a professional English news report about {target_en} based on these sources: {str(full_texts)[:5000]}. Return JSON: {{'title': '...', 'content': '...'}}"
    news_res = gemini_api.ask_gemini(article_prompt)

    if news_res:
        news_item = {
            "category": category, "keyword": target_en,
            "title": news_res.get("title"), "summary": news_res.get("content"),
            "image_url": main_image, "score": 100, "created_at": datetime.now().isoformat(), "likes": 0
        }
        database.save_news_to_live([news_item])
        database.save_news_to_archive([news_item])
        print(f"   🎉 SUCCESS: '{target_en}' published via Google Search Grounding.")
