# scripts/auto_culture.py
import os, requests, psycopg2, random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ==========================================
CATEGORY_NAME = "K-CULTURE"
# ==========================================

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

def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

# 🚀 [핵심 신규 로직] 네이버 공식 이미지 검색 API 사용
def search_naver_images(keyword, count=3):
    # K-Culture 아이템/장소의 경우 '고화질' 보다는 그냥 검색어 자체로 검색하는 것이 더 잘 나옵니다.
    url = f"https://openapi.naver.com/v1/search/image?query={keyword}&display={count}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            images = []
            for item in data.get('items', []):
                img_url = item.get('link')
                if img_url and img_url.startswith('http'):
                    images.append(img_url)
            return images
    except Exception as e:
        print(f"⚠️ 네이버 이미지 API 검색 실패: {e}")
    return []

def extract_trending_entities(news_items, recent_titles, current_keyword):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 작성한 트렌드 글들]\n{recent_titles}\n위 글에 소개된 유행이나 브랜드는 1%라도 겹치면 절대 제외해." if recent_titles else ""
    
    system_prompt = f"""너는 K-Culture 분석가야. 주어진 라이프스타일/유통 뉴스 제목들에서 글로벌 팬들이 가장 흥미를 가질 만한 한국의 특정 유행 아이템, 핫플레이스, 또는 브랜드를 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keywords": ["1위트렌드", "2위트렌드", "3위트렌드"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [current_keyword])

def main():
    print(f"[{CATEGORY_NAME}] 라이프스타일/트렌드 뉴스 기반 작업 시작 (이미지 API 연동)...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 K-CULTURE 글: {recent_titles}")

    # 외국인들이 환장하는 K-Culture 황금 키워드 풀(Pool)
    keyword_pool = [
        "팝업스토어", "화장품", "여행지", "패션", 
        "편의점 간식", "핫플", "라면", "기념품"
    ]
    
    current_keyword = random.choice(keyword_pool)
    print(f"🎯 이번 턴의 랜덤 타겟 키워드: {current_keyword}")

    raw_news = search_naver_news(current_keyword, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print(f"❌ '{current_keyword}' 관련 24시간 이내의 최신 기사가 없습니다. (작업 취소)")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles, current_keyword)
    print(f"🔥 AI가 뽑은 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        
        if len(deep_news) < 2:
            print(f"⚠️ [{entity}] 관련 기사가 부족합니다. 다음 후보로 패스!")
            continue
            
        # 🚀 [변경] 언론사 스크래핑 삭제! 네이버 이미지 API로 해당 아이템(장소) 사진 3장 즉시 요청
        images = search_naver_images(entity, 3)
        
        if not images or len(images) < 2:
            print(f"⚠️ [{entity}] 네이버 API에서 고화질 사진을 2장 이상 찾지 못했습니다. 다음 후보로 패스!")
            continue 
            
        print(f"🎉 [{entity}] 완벽한 사진 {len(images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        system_prompt = """
        너는 글로벌 K-Culture 매거진의 트렌드 에디터야. 
        제공된 한국 트렌드 뉴스를 바탕으로, 해외 팬들에게 이 제품이나 장소가 왜 요즘 한국에서 대유행인지 소개하는 세련된 영어 블로그 기사를 써 줘.
        [규칙]
        1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
        2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
        3. 본문의 적당한 중간 위치에 아마존 상품 검색 유도 텍스트 링크를 딱 1개 자연스럽게 삽입할 것. (장소/여행지 글이더라도 관련된 한국 상품 검색으로 유도할 것)
           형식: "🛒 Find [메인키워드] items on Amazon: https://www.amazon.com/s?k=[메인키워드영어]&tag=kculturetrend-20"
           (띄어쓰기는 + 기호로 변환하여 주소를 완성할 것)
        4. 마지막에 관련된 해시태그 5개를 추가할 것. ('SEO' 등 검색엔진 용어 절대 금지)
        반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} - Trend Update')
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
        print("\n❌ 3개의 후보를 모두 뒤졌지만, 사진 퀄리티 등을 만족하는 이슈가 없어 이번 턴은 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
