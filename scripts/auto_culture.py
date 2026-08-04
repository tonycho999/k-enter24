# scripts/auto_culture.py
import os, requests, psycopg2, random # 🚀 random 모듈 추가!
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-CULTURE"

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

def extract_trending_entity(news_items, recent_titles, current_keyword):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의사항: 최근 작성한 트렌드 글들]\n{recent_titles}\n위 글들에서 이미 소개했던 아이템이나 장소는 절대 중복해서 선택하지 마." if recent_titles else ""
    
    system_prompt = f"""너는 한국 트렌드 분석가야. 주어진 라이프스타일/유통 뉴스 제목들에서 글로벌 팬들이 가장 흥미를 가질 만한 한국의 특정 유행 아이템이나 핫플레이스 딱 1개만 찾아.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keyword": "..."}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keyword', current_keyword)

def get_naver_news_images(news_items, max_images=3):
    images = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36', 'Accept': 'text/html,*/*'}
    
    for item in news_items:
        url = item.get('originallink') or item.get('link', '')
        url = url.replace('<b>', '').replace('</b>', '').replace('http://', 'https://')
        if not url: continue
            
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code != 200: continue
            soup = BeautifulSoup(res.text, 'html.parser')
            
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image.get('content')
                if img_url.startswith('http') and 'logo' not in img_url.lower() and 'blank' not in img_url.lower():
                    if img_url not in images: images.append(img_url)
                    if len(images) >= max_images: return images
                            
            article_body = soup.find(class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
            if article_body:
                for img in article_body.find_all('img'):
                    img_url = img.get('data-src') or img.get('src')
                    if img_url and img_url.startswith('http') and 'icon' not in img_url.lower():
                        if img_url not in images: images.append(img_url)
                        if len(images) >= max_images: return images
        except Exception: continue
    return images

def main():
    print(f"[{CATEGORY_NAME}] 라이프스타일/트렌드 뉴스 기반 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 K-CULTURE 글: {recent_titles}")

    # 🚀 [핵심] 외국인들이 환장하는 K-Culture 황금 키워드 풀(Pool)
    keyword_pool = [
        "한국 팝업스토어", 
        "올리브영 화장품", 
        "한국 여행지", 
        "한국 스트릿 패션", 
        "한국 편의점 간식",
        "성수동 핫플",
        "한국 라면 신제품",
        "한국 전통 기념품"
    ]
    
    # 봇이 실행될 때마다 위 배열에서 하나를 무작위로 뽑습니다.
    current_keyword = random.choice(keyword_pool)
    print(f"🎯 이번 턴의 랜덤 타겟 키워드: {current_keyword}")

    raw_news = search_naver_news(current_keyword, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print(f"❌ '{current_keyword}' 관련 24시간 이내의 최신 기사가 없습니다. (작업 취소)")
        exit(1)
        
    trending_entity = extract_trending_entity(broad_news, recent_titles, current_keyword)
    print(f"🔥 핫이슈 (중복 필터링 완료): {trending_entity}")
    
    raw_deep_news = search_naver_news(trending_entity, 15)
    deep_news = filter_recent_24h_news(raw_deep_news)[:5]
    
    if not deep_news:
        print("❌ 해당 핫이슈의 24시간 이내 디테일 기사가 부족합니다. (작업 취소)")
        exit(1)
        
    article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
    
    system_prompt = """
    너는 글로벌 K-Culture 매거진의 트렌드 에디터야. 
    제공된 한국 트렌드 뉴스를 바탕으로, 해외 팬들에게 이 제품이나 장소가 왜 요즘 한국에서 대유행인지 소개하는 세련된 영어 블로그 기사를 써 줘.
    [규칙]
    1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
    2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
    3. 마지막에 관련된 해시태그 5개를 추가할 것. ('SEO' 등 검색엔진 용어 절대 금지)
    반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
    """
    
    article_data = get_ai_response(system_prompt, article_contents)
    title = article_data.get('title', f'{trending_entity} - K-Culture Trend')
    content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
    
    images = get_naver_news_images(deep_news, 3)
    if not images:
        images = ['https://k-enter24.com/og-image.png']
    
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
    print(f"✅ {CATEGORY_NAME} DB 저장 완료! (가져온 언론사 트렌드 이미지: {len(images)}장)")

if __name__ == "__main__":
    main()
