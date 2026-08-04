# scripts/auto_drama.py
import os, requests, psycopg2, json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ==========================================
# 🛑 카테고리 및 드라마 전용 검색어 세팅
CATEGORY_NAME = "K-DRAMA"
SEARCH_QUERY = "드라마"
# ==========================================

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

def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사에 나온 드라마나 배우는 절대 제외해." if recent_titles else ""
    
    system_prompt = f"""너는 트렌드 분석가야. 뉴스 제목들에서 가장 화제가 되는 특정 드라마 제목, 또는 배우 이름을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keywords": ["1위드라마", "2위드라마", "3위배우"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', ["최신 드라마"])

def is_valid_image(img_url):
    if not img_url or not img_url.startswith('http'): return False
    url_lower = img_url.lower()
    
    junk_words = ['logo', 'icon', 'blank', 'banner', 'button', 'btn', 'sns', 'watermark']
    if any(word in url_lower for word in junk_words): return False
    
    try:
        h = requests.head(img_url, timeout=3)
        size = int(h.headers.get('Content-Length', 0))
        if size > 0 and size < 15000: 
            return False
    except: pass 
    return True

def get_naver_news_images(news_items, min_images=2, max_images=3):
    images = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,*/*'}
    
    for item in news_items:
        url = item.get('originallink') or item.get('link', '')
        url = url.replace('<b>', '').replace('</b>', '').replace('http://', 'https://')
        if not url or 'naver.com' in url: continue 
            
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.text, 'html.parser')
            
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image.get('content')
                if is_valid_image(img_url) and img_url not in images:
                    images.append(img_url)
                    if len(images) >= max_images: return images
                            
            article_body = soup.find(class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
            if article_body:
                for img in article_body.find_all('img'):
                    img_url = img.get('data-src') or img.get('src')
                    if is_valid_image(img_url) and img_url not in images:
                        images.append(img_url)
                        if len(images) >= max_images: return images
        except: continue
        
    return images if len(images) >= min_images else []

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    
    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 종료합니다.")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI가 뽑은 K-DRAMA 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        
        if len(deep_news) < 2:
            print(f"⚠️ [{entity}] 관련 기사가 부족합니다. 다음 후보로 패스!")
            continue
            
        images = get_naver_news_images(deep_news, min_images=2, max_images=3)
        
        if not images:
            print(f"⚠️ [{entity}] 고화질 기사 사진을 2장 이상 찾지 못했습니다. 다음 후보로 패스!")
            continue 
            
        print(f"🎉 [{entity}] 완벽한 사진 {len(images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        system_prompt = """
        너는 글로벌 K-Culture 매거진의 수석 에디터야. 
        제공된 K-Drama 뉴스를 바탕으로 해외 팬들이 열광할 만한 흥미로운 영어 제목과 전문성 있는 영어 본문 리뷰를 작성해 줘.
        [규칙]
        1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
        2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
        3. 마지막에 관련된 해시태그 5개를 추가할 것. ('SEO' 등의 검색 관련 용어는 절대 금지)
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
        print("\n❌ 3개의 드라마 후보를 모두 뒤졌지만, 사진 퀄리티 등을 만족하는 이슈가 없어 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
