# scripts/auto_pop.py
import os, requests, psycopg2, json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-ENTERTAINMENT"
SEARCH_QUERY = "예능"

def get_clean_db_url():
    return DATABASE_URL.replace("?pgbouncer=true", "") if DATABASE_URL else ""

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
        except: continue
    return recent_items

def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

# 🚀 [변경] AI에게 후보군 3개를 순위별로 뽑아달라고 요청합니다.
def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사에 나온 인물/그룹은 절대 제외해." if recent_titles else ""
    
    system_prompt = f"""너는 트렌드 분석가야. 뉴스 제목들에서 가장 화제가 되는 특정 인물/아이돌/그룹을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keywords": ["1위인물", "2위인물", "3위인물"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

# 🚀 [추가] 이미지 유효성(크기 및 로고 여부)을 깐깐하게 검사하는 함수
def is_valid_image(img_url):
    if not img_url or not img_url.startswith('http'): return False
    url_lower = img_url.lower()
    
    # 1차: URL 이름에 잡동사니 단어가 들어가면 무조건 버림
    junk_words = ['logo', 'icon', 'blank', 'banner', 'button', 'btn', 'sns', 'watermark']
    if any(word in url_lower for word in junk_words): return False
    
    # 2차: 실제 이미지 용량을 체크해서 너무 작으면(15KB 이하) 버림 (로고나 썸네일 방지)
    try:
        h = requests.head(img_url, timeout=3)
        size = int(h.headers.get('Content-Length', 0))
        if size > 0 and size < 15000: # 15KB 미만은 퀄리티 미달로 간주
            return False
    except: pass # 헤더 요청 실패 시 일단 통과시킴
    return True

# 🚀 [변경] 최소 2장을 찾지 못하면 실패(빈 배열)를 반환하도록 변경
def get_naver_news_images(news_items, min_images=2, max_images=3):
    images = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,*/*'}
    
    for item in news_items:
        url = item.get('originallink') or item.get('link', '')
        url = url.replace('<b>', '').replace('</b>', '').replace('http://', 'https://')
        if not url or 'naver.com' in url: continue # 네이버 자체 뉴스는 스크래핑이 어려워 원본 언론사만 타겟팅
            
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1순위: 공유용 고화질 메인 사진 (og:image)
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image.get('content')
                if is_valid_image(img_url) and img_url not in images:
                    images.append(img_url)
                    if len(images) >= max_images: return images
                            
            # 2순위: 기사 본문 속 큼직한 사진들
            article_body = soup.find(class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
            if article_body:
                for img in article_body.find_all('img'):
                    img_url = img.get('data-src') or img.get('src')
                    if is_valid_image(img_url) and img_url not in images:
                        images.append(img_url)
                        if len(images) >= max_images: return images
        except: continue
        
    # 목표한 최소 수량(2장)을 못 채웠으면, 아예 안 가져온 것으로 처리 (포기)
    return images if len(images) >= min_images else []

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    
    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 종료합니다.")
        exit(1)
        
    # 🚀 후보군 3명을 뽑아옵니다!
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI가 뽑은 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    # 🚀 후보 1위부터 순서대로 기사와 '사진'을 뒤져봅니다.
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6] # 사진을 넉넉히 찾기 위해 6개 기사 탐색
        
        if len(deep_news) < 2:
            print(f"⚠️ [{entity}] 관련 기사가 부족합니다. 다음 후보로 패스!")
            continue
            
        # 🚀 깐깐한 이미지 필터링 거치기 (최소 2장 요구)
        images = get_naver_news_images(deep_news, min_images=2, max_images=3)
        
        if not images:
            print(f"⚠️ [{entity}] 고화질 기사 사진을 2장 이상 찾지 못했습니다. 다음 후보로 패스!")
            continue # 사진이 부족하면 미련 없이 버리고 다음 후보로!
            
        print(f"🎉 [{entity}] 완벽한 사진 {len(images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        # 사진을 확보했으므로 AI에게 기사 작성을 지시합니다.
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        system_prompt = """
        너는 글로벌 K-Culture 매거진의 수석 에디터야. 
        제공된 뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 영어 제목과 전문성 있는 영어 본문을 작성해 줘.
        [규칙]
        1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
        2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
        3. 마지막에 관련된 해시태그 5개를 추가할 것.
        반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} - Update')
        content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
        
        # DB 저장
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
        break # 🚀 하나의 글을 성공적으로 썼으니 루프(후보 탐색)를 즉시 종료합니다!

    if not saved_successfully:
        print("\n❌ 3개의 후보를 모두 뒤졌지만, 사진 퀄리티 조건 등을 만족하는 이슈가 없어 이번 턴은 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
