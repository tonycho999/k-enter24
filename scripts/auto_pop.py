# scripts/auto_pop.py
import os, requests, psycopg2, random, uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from AI import get_ai_response
from supabase import create_client, Client

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") # 프로젝트 고유 주소 (이전에 남겨둔 것 활용)
SUPABASE_KEY = os.environ.get("SUPABASE_KEY") # anon/public 키

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

CATEGORY_NAME = "K-POP"
SEARCH_QUERY = "k-pop"

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
    recent_info = f"\n[주의: 최근 기사 제목]\n{recent_titles}\n위 기사 인물은 1%라도 겹치면 무조건 제외." if recent_titles else ""
    
    system_prompt = f"""트렌드 분석가로서 아래 뉴스에서 가장 화제인 인물/그룹을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    JSON 형식 답변: {{"keywords": ["1위", "2위", "3위"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

def search_naver_images(keyword, count=3):
    url = f"https://openapi.naver.com/v1/search/image?query={keyword} 고화질&display={count}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return [item['link'] for item in res.json().get('items', []) if item.get('link').startswith('http')]
    except: pass
    return []

# 🚀 [핵심] 이미지를 파이썬이 몰래 다운로드한 뒤, 내 Supabase Storage에 영구 박제하는 함수!
def upload_image_to_supabase(img_url):
    try:
        # 1. 원본 이미지 다운로드
        res = requests.get(img_url, timeout=5)
        if res.status_code != 200: return None
        
        # 2. 고유한 파일명 생성 (확장자는 대충 .jpg로 통일)
        file_name = f"{uuid.uuid4().hex}.jpg"
        
        # 3. Supabase 'images' 버킷에 업로드
        # file_options 설정으로 브라우저에서 바로 열리도록(Content-Type) 설정
        supabase.storage.from_("images").upload(
            path=file_name,
            file=res.content,
            file_options={"content-type": "image/jpeg"}
        )
        
        # 4. 내 클라우드에 영구 박제된 URL 반환 (이제 엑스박스 절대 안 뜸!)
        public_url = supabase.storage.from_("images").get_public_url(file_name)
        return public_url
    except Exception as e:
        print(f"이미지 업로드 실패: {e}")
        return None

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    broad_news = filter_recent_24h_news(search_naver_news(SEARCH_QUERY, 50))
    if not broad_news: exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    saved_successfully = False
    
    for entity in trending_entities:
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        if len(deep_news) < 2: continue
            
        raw_images = search_naver_images(entity, 3)
        if not raw_images or len(raw_images) < 2: continue 
            
        # 🚀 훔쳐온 이미지 주소를 내 Supabase에 업로드하여 '영구 주소'로 교체합니다!
        safe_images = []
        for img in raw_images:
            safe_url = upload_image_to_supabase(img)
            if safe_url: safe_images.append(safe_url)
            
        if len(safe_images) < 2: continue # 업로드 실패로 사진 부족하면 패스
        
        print(f"🎉 [{entity}] 영구 박제 사진 {len(safe_images)}장 확보 성공!")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        
        # 🚀 [추가] 다이나믹 글자 수 지정 로직
        target_length = random.choice([600, 800, 1000, 1200, 1500])
        min_len = target_length - 100
        max_len = target_length + 100
        print(f"📝 이번 기사 타겟 글자수: {min_len} ~ {max_len}자")
        
        # 🚀 [수정] 아마존 제거 및 다이나믹 분량 프롬프트 주입
        system_prompt = f"""
        너는 글로벌 K-Culture 매거진의 수석 에디터야. 
        제공된 뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 영어 제목과 영어 본문을 작성해.
        [규칙]
        1. 본문의 길이는 반드시 최소 {min_len}자(characters) 이상, 최대 {max_len}자 이내로 엄격하게 맞출 것!
        2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
        3. 마지막에 관련된 해시태그 5개 추가. ('SEO' 절대 금지)
        JSON 형식 답변: {{"title": "영어제목", "content": "영어본문", "tags": "태그"}}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} Update')
        content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
        
        conn = psycopg2.connect(get_clean_db_url())
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO "Post" (title, content, category, images, views, "createdAt", "updatedAt") 
               VALUES (%s, %s, %s, %s, 0, NOW(), NOW())""",
            (title, content, CATEGORY_NAME, safe_images)
        )
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ [{entity}] 기사 완벽 작성 및 DB 저장 완료!")
        saved_successfully = True
        break 

    if not saved_successfully: exit(1)

if __name__ == "__main__":
    main()
