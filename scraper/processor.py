def process_person_news(category, person_info, summary, img_url, raw_response):
    db = DatabaseManager()
    
    # 공통 데이터 객체 생성
    article_entry = {
        "category": category,
        "keyword": person_info['name'],
        "title": person_info['title'],
        "summary": summary,
        "link": person_info.get('link', ''), # Perplexity가 준 출처 링크
        "image_url": img_url,
        "query": f"{category} 분야 {person_info['name']} 최신 뉴스",
        "raw_result": raw_response, # AI 응답 원문 저장 (검색 품질 개선용)
        "score": person_info.get('score', 0) # 화제성 점수
    }

    # 1. 사용자가 검색 가능한 [전체 아카이브]에 저장
    db.save_to_archive(article_entry)

    # 2. 웹사이트 메인 [실시간 피드]에 저장 (최신성 유지)
    db.supabase.table("live_news").insert({
        "category": category,
        "keyword": person_info['name'],
        "title": person_info['title'],
        "summary": summary,
        "link": article_entry['link'],
        "image_url": img_url,
        "score": article_entry['score']
    }).execute()
