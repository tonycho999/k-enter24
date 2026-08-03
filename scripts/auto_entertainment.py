# scripts/auto_pop.py (나머지 파일도 동일한 구조로 변경)
import os, requests, psycopg2
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup # 🚀 뉴스 원본 이미지 추출을 위한 라이브러리 추가
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-ENTERTAINMENT"
SEARCH_QUERY = "예능"

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
            time_diff = now_utc - pub_date
            if time_diff.total_seconds() <= 86400:
                recent_items.append(item)
        except Exception as e:
            continue
    return recent_items

def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

def extract_trending_entity(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의사항: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사들에서 이미 메인으로 다루었던 인물이나 그룹은 절대 중복해서 선택하지 마." if recent_titles else ""
    system_prompt = f"""너는 트렌드 분석가야. 주어진 뉴스 제목들에서 가장 화제가 되는 특정 인물, 아이돌, 또는 작품 이름 딱 1개를 찾아.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keyword": "..."}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keyword', SEARCH_QUERY)

# 🚀 [핵심 신규 기능] 네이버 뉴스 링크에 직접 들어가서 진짜 기사 사진을 훔쳐옵니다!
def get_naver_news_images(news_items, max_images=3):
    images = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    for item in news_items:
        # 네이버 API가 주는 'link' (네이버 뉴스 전용 링크가 파싱하기 좋음)
        url = item.get('link', '')
        if not url or 'naver.com' not in url:
            continue
            
        try:
            # 기사 페이지 HTML을 통째로 가져옴
            res = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 네이버 뉴스 기사 본문에 있는 진짜 사진(img 태그) 찾기
            # 보통 id가 'img1', 'img2' 이거나 본문 영역 안에 있는 img를 찾음
            img_tags = soup.select('.newsct_article img, #dic_area img, .go_trans _article_content img')
            
            for img in img_tags:
                img_url = img.get('data-src') or img.get('src')
                if img_url and img_url.startswith('http'):
                    images.append(img_url)
                    if len(images) >= max_images:
                        return images # 3장 모이면 즉시 리턴!
        except Exception as e:
            print(f"이미지 추출 실패 ({url}): {e}")
            continue
            
    return images

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    recent_titles = get_recent_titles()
    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내의 최신 기사가 없습니다.")
        exit(1)
        
    trending_entity = extract_trending_entity(broad_news, recent_titles)
    print(f"🔥 핫이슈 (중복 필터링 완료): {trending_entity}")
    
    raw_deep_news = search_naver_news(trending_entity, 15)
    deep_news = filter_recent_24h_news(raw_deep_news)[:5] # 사진 확보를 위해 5개로 여유있게 가져옴
    
    if not deep_news:
        print("❌ 해당 핫이슈의 24시간 이내 디테일 기사가 부족합니다.")
        exit(1)
        
    article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
    
    system_prompt = """
    너는 글로벌 K-Culture 매거진의 수석 에디터야. 
    제공된 뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 영어 제목과 전문성 있는 영어 본문을 작성해 줘.
    [규칙]
    1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
    2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
    3. 마지막에 관련된 해시태그 5개를 추가할 것. ('SEO', 'AEO' 등 용어 절대 금지)
    반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
    """
    
    article_data = get_ai_response(system_prompt, article_contents)
    title = article_data.get('title', 'K-Culture Update')
    content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
    
    # 🚀 Unsplash 대신, 우리가 찾은 뉴스 기사에서 진짜 한국 언론사 사진을 뽑아옵니다!
    images = get_naver_news_images(deep_news, 3)
    if not images: # 뉴스에 사진이 진짜 한 장도 없을 때만 임시 로고 노출
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
    print(f"✅ {CATEGORY_NAME} DB 저장 완료! (가져온 이미지: {len(images)}장)")

if __name__ == "__main__":
    main()
