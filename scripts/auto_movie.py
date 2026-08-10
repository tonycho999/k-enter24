# scripts/auto_pop.py
import os, requests, psycopg2, random, uuid, re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from io import BytesIO
from PIL import Image
from supabase import create_client, Client
from AI import get_ai_response, verify_category_fit

# 🔑 환경변수 세팅
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")
SUPABASE_URL = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Supabase 클라이언트 연결
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
CATEGORY_NAME = "K-MOVIE"
SEARCH_QUERY = "한국영화"
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

def search_naver_images(keyword, count=3):
    search_term = f"{keyword} 무대 고화질"
    url = f"https://openapi.naver.com/v1/search/image?query={search_term}&display={count}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            return [item['link'] for item in res.json().get('items', []) if item.get('link').startswith('http')]
    except Exception as e:
        print(f"⚠️ 네이버 이미지 API 검색 실패: {e}")
    return []

# 🗄️ 🚀 [업그레이드] 이미지 파일명을 SEO 친화적(kpop-keyword-uuid.webp)으로 변경하여 업로드!
def upload_image_to_supabase(img_url, entity_keyword, category):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(img_url, headers=headers, timeout=5)
        if res.status_code != 200: return None
        
        img = Image.open(BytesIO(res.content)).convert('RGB')
        
        if img.width > 800:
            ratio = 800.0 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((800, new_height), Image.Resampling.LANCZOS)

        output_buffer = BytesIO()
        img.save(output_buffer, format='WebP', quality=80)
        
        # SEO를 위한 파일명 정제 (영문, 숫자만 남기고 띄어쓰기는 하이픈으로)
        # 만약 한글(예: 뉴진스)이라 다 지워지면 카테고리명만 씁니다.
        clean_keyword = re.sub(r'[^a-zA-Z0-9]', '', entity_keyword).lower()
        if not clean_keyword: 
            clean_keyword = category.lower().replace("-", "")
            
        short_uuid = uuid.uuid4().hex[:6]
        file_name = f"{category.lower().replace('-', '')}-{clean_keyword}-{short_uuid}.webp"
        
        supabase.storage.from_("images").upload(
            path=file_name,
            file=output_buffer.getvalue(),
            file_options={"content-type": "image/webp"}
        )
        return supabase.storage.from_("images").get_public_url(file_name)
    except Exception as e:
        print(f"이미지 업로드 실패: {e}")
        return None

def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의: 최근 기사 제목]\n{recent_titles}\n위 기사들 내용과 1%라도 겹치는 인물/그룹은 무조건 제외!" if recent_titles else ""
    
    system_prompt = f"""트렌드 분석가로서 뉴스 제목들에서 가장 화제가 되는 아이돌/그룹을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    JSON 형식 답변: {{"keywords": ["1위인물", "2위인물", "3위인물"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

def main():
    print(f"[{CATEGORY_NAME}] 봇 가동 시작...")
    recent_titles = get_recent_titles()
    broad_news = filter_recent_24h_news(search_naver_news(SEARCH_QUERY, 50))
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 종료합니다.")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ [{entity}] 후보 탐색 중...")
        
        deep_news = filter_recent_24h_news(search_naver_news(entity, 20))[:6]
        if len(deep_news) < 2: continue
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        
        # 🛡️ AI 편집장의 카테고리 순수성 검열 (예능 출연 기사 등 차단)
        is_valid = verify_category_fit(CATEGORY_NAME, entity, article_contents)
        if not is_valid:
            print(f"⚠️ [{entity}] 이슈는 순수 '{CATEGORY_NAME}' 성격에 맞지 않아(예능/가십 등) 반려되었습니다. 패스!")
            continue 

        raw_images = search_naver_images(entity, 3)
        if len(raw_images) < 2: continue 
            
        safe_images = []
        for img_url in raw_images:
            # 🚀 [업그레이드] 이미지 업로드 시 키워드와 카테고리를 넘겨 SEO 파일명을 만듭니다!
            safe_url = upload_image_to_supabase(img_url, entity, CATEGORY_NAME)
            if safe_url: safe_images.append(safe_url)
            
        if len(safe_images) < 2: 
            print(f"⚠️ [{entity}] 고화질 사진 업로드 실패로 다음 후보로 패스합니다.")
            continue
            
        print(f"🎉 [{entity}] 영구 박제 사진 {len(safe_images)}장 확보! 기사 작성 돌입.")
        
        # 📝 랜덤 글자 수 생성기
        target_length = random.choice([600, 800, 1000, 1200, 1500])
        min_len = target_length - 100
        max_len = target_length + 100
        print(f"📝 타겟 글자 수: {min_len} ~ {max_len}자")
        
        # 🚀 [업그레이드] 구글 SEO 및 AI 검색(AEO)에 완벽하게 최적화된 프롬프트!
        system_prompt = f"""
        너는 글로벌 K-Culture 매거진의 최고참 SEO/AEO 전문가 겸 수석 에디터야.
        주어진 뉴스를 바탕으로 영어 기사를 작성하되, 아래의 [최적화 규칙]을 무조건 지켜.

        [최적화 규칙]
        1. 분량: 최소 {min_len}자 ~ 최대 {max_len}자.
        2. 제목(Title): 핵심 키워드가 맨 앞에 오도록 하고, 어그로가 아닌 명확한 정보성(Who, What)을 띌 것.
        3. 도입부(Hook): 첫 문단(50단어 이내)에 기사의 핵심 요약(Core Answer)을 넣어, AI 검색 엔진이 즉시 긁어갈 수 있게 만들 것.
        4. 본문 구조(Formatting): 가독성을 위해 반드시 2개 이상의 소제목(Subheading)을 사용할 것. 소제목은 대문자로 시작하며, 소제목 앞뒤로는 반드시 빈 줄(\\n\\n)을 넣을 것.
        5. 정보의 깊이: 단순히 "유행이다"가 아니라, 구체적인 이유(Why)와 데이터/팬 반응을 포함할 것.
        6. 본문은 HTML 태그를 절대 쓰지 말고 오직 줄바꿈(\\n\\n)으로만 문단을 나눌 것.
        7. 마지막에 관련 해시태그 5개 추가. ('SEO' 등 용어 절대 금지)
        
        반드시 JSON 형식으로 답변: {{"title": "영어제목", "content": "영어본문", "tags": "태그"}}
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
        
        print(f"✅ [{entity}] K-POP SEO/AEO 최적화 기사 완벽 작성 및 DB 저장 완료!")
        saved_successfully = True
        break 

    if not saved_successfully:
        print("\n❌ 3개의 후보 모두 조건 미달로 이번 턴은 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
