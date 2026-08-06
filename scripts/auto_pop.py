# scripts/auto_pop.py
import os, requests, psycopg2
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-POP"
SEARCH_QUERY = "가수"

def get_clean_db_url():
    if DATABASE_URL:
        return DATABASE_URL.replace("?pgbouncer=true", "")
    return ""

def get_recent_titles():
    try:
        conn = psycopg2.connect(get_clean_db_url())
        cur = conn.cursor()
        cur.execute("""SELECT title FROM "Post" WHERE category = %s ORDER BY "createdAt" DESC LIMIT 5""", (CATEGORY_NAME,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [row[0] for row in rows]
    except Exception as e:
        print(f"DB 조회 에러: {e}")
        return []

def filter_recent_24h_news(news_items):
    recent_items = []
    now_utc = datetime.now(timezone.utc)
    for item in news_items:
        try:
            pub_date = parsedate_to_datetime(item['pubDate'])
            if (now_utc - pub_date).total_seconds() <= 86400:
                recent_items.append(item)
        except Exception:
            continue
    return recent_items

# 1. 네이버 뉴스 검색 API (텍스트 정보 수집용)
def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

# 🚀 2. [신규 핵심] 네이버 이미지 검색 API (사진 수집 전용!)
def search_naver_images(query, display=3):
    """
    언론사 사이트를 뒤지지 않고, 네이버 이미지 검색에 '아이돌 이름 + 고화질'로 직접 검색하여 
    가장 관련도 높고 깨끗한 이미지를 다이렉트로 가져옵니다.
    """
    # filter=large (큰 사이즈), sort=sim (유사도/정확도 순) 옵션으로 퀄리티를 보장합니다.
    url = f"https://openapi.naver.com/v1/search/image?query={query}&display={display}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    try:
        res = requests.get(url, headers=headers)
        items = res.json().get('items', [])
        
        # 원본 이미지 링크(link)들만 쏙쏙 뽑아냅니다.
        images = []
        for item in items:
            img_url = item.get('link')
            # 네이버 블로그/카페의 썸네일 등 확실한 이미지만 취합합니다.
            if img_url and img_url.startswith('http'):
                images.append(img_url)
                
        return images
    except Exception as e:
        print(f"⚠️ 네이버 이미지 API 검색 실패: {e}")
        return []

def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의사항: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사들 내용과 1%라도 겹치는 인물이나 그룹은 무조건 제외하고 완전히 새로운 핫이슈를 골라!" if recent_titles else ""
    
    system_prompt = f"""너는 트렌드 분석가야. 주어진 뉴스 제목들에서 가장 화제가 되는 특정 인물, 아이돌, 또는 작품 이름 '3개'를 화제성 순으로 찾아.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keywords": ["1위인물", "2위인물", "3위인물"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 기사들: {recent_titles}")

    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 작업을 종료합니다.")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI가 뽑은 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        
        if len(deep_news) < 2:
            print(f"⚠️ [{entity}] 관련 기사가 부족합니다. 다음 후보로 패스!")
            continue
            
        # 🚀 [변경] 언론사 스크래핑 삭제! 네이버 이미지 API에 "인물이름 + 공식" 으로 검색
        # 예: "에스파 공식 사진", "방탄소년단 무대 고화질"
        image_search_keyword = f"{entity} 무대 고화질"
        images = search_naver_images(image_search_keyword, display=3)
        
        if len(images) < 2:
            print(f"⚠️ [{entity}] 네이버 이미지 검색 결과가 2장 미만입니다. 다음 후보로 패스!")
            continue 
            
        print(f"🎉 [{entity}] 완벽한 사진 {len(images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        system_prompt = """
        너는 글로벌 K-Culture 매거진의 수석 에디터야. 
        제공된 뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 영어 제목과 전문성 있는 영어 본문을 작성해 줘.
        [규칙]
        1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
        2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
        3. 본문 중간에 자연스럽게 아마존 쇼핑 링크를 삽입해 줘. 형식: "🛒 Find [메인키워드] merch on Amazon: https://www.amazon.com/s?k=[영어키워드]&tag=kculturetrend-20"
        4. 마지막에 관련된 해시태그 5개를 추가할 것. ('SEO' 등 용어 절대 금지)
        반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} - Update')
        content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
        
        conn = psycopg2.connect(get_clean_db_url())
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO "Post" (title, content, category, images, views, "createdAt", "updatedAt") 
               VALUES (%s, %s, %s, %s, 0, NOW(), NOW())""",
            (title, content, CATEGORY_NAME, images)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ [{entity}] 기사 완벽하게 작성 및 DB 저장 완료!")
        saved_successfully = True
        break 

    if not saved_successfully:
        print("\n❌ 3개의 후보를 모두 뒤졌지만, 조건을 만족하는 이슈가 없어 이번 턴은 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
