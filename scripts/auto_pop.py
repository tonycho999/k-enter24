# scripts/auto_pop.py
import os, requests, psycopg2, uuid
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from PIL import Image
from supabase import create_client, Client
from AI import get_ai_response

# 🔑 환경변수 로드
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL") # Supabase 프로젝트 URL
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")             # 방금 등록하신 anon/public 키

# Supabase 클라이언트 초기화
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
CATEGORY_NAME = "K-POP"
SEARCH_QUERY = "k-pop"
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

# 📰 1. 네이버 뉴스 API (텍스트 정보 수집)
def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

# 🖼️ 2. 네이버 이미지 검색 API (고화질 사진 수집!)
def search_naver_images(keyword, count=3):
    # '고화질' 키워드를 붙이고 filter=large 적용하여 최고 퀄리티 확보
    search_term = f"{keyword} 고화질"
    url = f"https://openapi.naver.com/v1/search/image?query={search_term}&display={count}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return [item['link'] for item in res.json().get('items', []) if item.get('link').startswith('http')]
    except Exception as e:
        print(f"⚠️ 네이버 이미지 API 검색 실패: {e}")
    return []

# 🗄️ 3. Supabase Storage 강제 업로드 (WebP 변환/압축)
def upload_image_to_supabase(img_url):
    try:
        # 네이버가 봇을 차단하지 않도록 브라우저 헤더 필수
        headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(img_url, headers=headers, timeout=5)
        if res.status_code != 200: return None
        
        # 다운받은 이미지를 열어서 WebP로 압축
        img = Image.open(BytesIO(res.content)).convert('RGB')
        
        # 가로 800px로 리사이징하여 용량 다이어트!
        if img.width > 800:
            ratio = 800.0 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        output_buffer = BytesIO()
        img.save(output_buffer, format='WebP', quality=80)
        
        # 고유 파일명 생성 및 업로드
        file_name = f"{uuid.uuid4().hex}.webp"
        supabase.storage.from_("images").upload(
            path=file_name,
            file=output_buffer.getvalue(),
            file_options={"content-type": "image/webp"}
        )
        
        # 내 클라우드에 영구 박제된 주소 반환
        return supabase.storage.from_("images").get_public_url(file_name)
    except Exception as e:
        print(f"이미지 업로드 실패: {e}")
        return None

def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사들 내용과 1%라도 겹치는 인물/그룹은 무조건 제외!" if recent_titles else ""
    
    system_prompt = f"""트렌드 분석가로서 뉴스 제목들에서 가장 화제가 되는 아이돌/그룹을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    JSON 형식 답변: {{"keywords": ["1위인물", "2위인물", "3위인물"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    broad_news = filter_recent_24h_news(search_naver_news(SEARCH_QUERY, 50))
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 종료합니다.")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        deep_news = filter_recent_24h_news(search_naver_news(entity, 20))[:6]
        if len(deep_news) < 2: continue
            
        # 🚀 [핵심] 네이버 이미지 검색 API 호출
        raw_images = search_naver_images(f"{entity} 무대", 3)
        if len(raw_images) < 2: continue 
            
        # 🚀 [핵심] 찾은 이미지를 Supabase Storage에 업로드!
        safe_images = []
        for img_url in raw_images:
            safe_url = upload_image_to_supabase(img_url)
            if safe_url: safe_images.append(safe_url)
            
        if len(safe_images) < 2: 
            print(f"⚠️ [{entity}] 사진 업로드에 실패하여 다음 후보로 패스합니다.")
            continue
            
        print(f"🎉 [{entity}] 영구 박제 사진 {len(safe_images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        
        system_prompt = """
        너는 글로벌 K-Culture 매거진의 수석 에디터야. 
        뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 영어 제목과 전문적인 영어 본문을 작성해.
        [규칙]
        1. 본문 길이는 최소 500자 이상, 최대 1500자 이내일 것.
        2. HTML 태그 없이 줄바꿈(\n\n)만 사용할 것.
        3. 마지막에 해시태그 5개를 추가할 것. ('SEO' 절대 금지)
        JSON 형식 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
        """
        
        article_data = get_ai_response(system_prompt, article_contents)
        title = article_data.get('title', f'{entity} Update')
        content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
        
        conn = psycopg2.connect(get_clean_db_url())
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO "Post" (title, content, category, images, views, "createdAt", "updatedAt") 
               VALUES (%s, %s, %s, %s, 0, NOW(), NOW())""",
            (title, content, CATEGORY_NAME, safe_images) # 🚀 내 클라우드 주소(safe_images)로 DB에 저장!
        )
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ [{entity}] 기사 및 이미지 완벽 저장 완료!")
        saved_successfully = True
        break 

    if not saved_successfully:
        print("\n❌ 3개의 후보를 모두 뒤졌으나 조건 미달로 이번 턴은 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
