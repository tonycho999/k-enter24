# scripts/auto_culture.py
import os, requests, psycopg2, random, uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from AI import get_ai_response
from supabase import create_client, Client

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
CATEGORY_NAME = "K-CULTURE"

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
    except: return []

def filter_recent_24h_news(news_items):
    recent_items = []
    now_utc = datetime.now(timezone.utc)
    for item in news_items:
        try:
            if (now_utc - parsedate_to_datetime(item['pubDate'])).total_seconds() <= 86400:
                recent_items.append(item)
        except: continue
    return recent_items

def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    res = requests.get(url, headers={"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET})
    return res.json().get('items', [])

def extract_trending_entities(news_items, recent_titles, current_keyword):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 기사 제목]\n{recent_titles}\n위 글 주제와 1%라도 겹치면 제외." if recent_titles else ""
    
    system_prompt = f"""한국 트렌드 분석가로서 뷰티/패션/핫플레이스 등 글로벌 팬들이 열광할 트렌드 '3개'를 화제성 순으로 찾아.
    {recent_info}
    JSON 형식 답변: {{"keywords": ["1위", "2위", "3위"]}}"""
    return get_ai_response(system_prompt, str(titles)).get('keywords', [current_keyword])

def is_valid_image(img_url):
    if not img_url or not img_url.startswith('http'): return False
    url_lower = img_url.lower()
    junk_words = ['logo', 'icon', 'blank', 'banner', 'button', 'sns']
    if any(word in url_lower for word in junk_words): return False
    try:
        if int(requests.head(img_url, timeout=3).headers.get('Content-Length', 0)) < 15000: return False
    except: pass 
    return True

# 🚀 Supabase 업로드 공통 함수
def upload_image_to_supabase(img_url):
    try:
        res = requests.get(img_url, timeout=5)
        if res.status_code != 200: return None
        file_name = f"{uuid.uuid4().hex}.jpg"
        supabase.storage.from_("images").upload(path=file_name, file=res.content, file_options={"content-type": "image/jpeg"})
        return supabase.storage.from_("images").get_public_url(file_name)
    except: return None

# 언론사 원본 이미지 스크래핑 + Supabase 업로드 동시 진행
def get_naver_news_images(news_items, min_images=2, max_images=3):
    images = []
    headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36'}
    for item in news_items:
        url = (item.get('originallink') or item.get('link', '')).replace('<b>', '').replace('</b>', '').replace('http://', 'https://')
        if not url or 'naver.com' in url: continue 
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code != 200: continue
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1순위: og:image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image.get('content')
                if is_valid_image(img_url):
                    safe_url = upload_image_to_supabase(img_url)
                    if safe_url and safe_url not in images:
                        images.append(safe_url)
                        if len(images) >= max_images: return images
                            
            # 2순위: 본문 사진
            article_body = soup.find(class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
            if article_body:
                for img in article_body.find_all('img'):
                    img_url = img.get('data-src') or img.get('src')
                    if is_valid_image(img_url):
                        safe_url = upload_image_to_supabase(img_url)
                        if safe_url and safe_url not in images:
                            images.append(safe_url)
                            if len(images) >= max_images: return images
        except: continue
    return images if len(images) >= min_images else []

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    
    keyword_pool = ["팝업스토어", "화장품", "핫플레이스", "패션", "간식", "라면", "먹거리"]
    current_keyword = random.choice(keyword_pool)
    
    broad_news = filter_recent_24h_news(search_naver_news(current_keyword, 50))
    if not broad_news: exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles, current_keyword)
    saved_successfully = False
    
    for entity in trending_entities:
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        if len(deep_news) < 2: continue
            
        images = get_naver_news_images(deep_news, min_images=2, max_images=3)
        if not images: continue 
            
        print(f"🎉 [{entity}] 영구 박제 사진 {len(images)}장 확보 성공!")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        
        # 🚀 글자 수 다변화
        target_length = random.choice([600, 800, 1000, 1200, 1500])
        min_len = target_length - 100
        max_len = target_length + 100
        print(f"📝 타겟 글자수: {min_len} ~ {max_len}자")
        
        system_prompt = f"""
        너는 글로벌 K-Culture 매거진 트렌드 에디터야. 
        해외 팬들에게 이 문화/아이템이 한국에서 왜 대유행인지 세련된 영어로 리뷰 기사를 작성해.
        [규칙]
        1. 본문 길이는 반드시 최소 {min_len}자, 최대 {max_len}자 이내로 엄격하게 맞출 것!
        2. HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용.
        3. 해시태그 5개 추가.
        JSON 형식 답변: {{"title": "영어제목", "content": "영어본문", "tags": "태그"}}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} Trend')
        content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
        
        conn = psycopg2.connect(get_clean_db_url())
        cur = conn.cursor()
        cur.execute("""INSERT INTO "Post" (title, content, category, images, views, "createdAt", "updatedAt") VALUES (%s, %s, %s, %s, 0, NOW(), NOW())""", (title, content, CATEGORY_NAME, images))
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ [{entity}] 기사 완벽 작성 및 DB 저장 완료!")
        saved_successfully = True
        break 

    if not saved_successfully: exit(1)

if __name__ == "__main__":
    main()
