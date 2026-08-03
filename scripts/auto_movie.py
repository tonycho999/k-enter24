# scripts/auto_pop.py
import os
import requests
import psycopg2
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from AI import get_ai_response

# 환경 변수 로드
NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ==========================================
# 🛑 다른 카테고리 봇 생성 시 이 두 줄만 변경하세요!
CATEGORY_NAME = "K-MOVIE"
SEARCH_QUERY = "영화"
# ==========================================

# 파이썬이 싫어하는 pgbouncer 쿼리를 제거한 깔끔한 DB 주소 반환
def get_clean_db_url():
    if DATABASE_URL:
        return DATABASE_URL.replace("?pgbouncer=true", "")
    return ""

# DB에서 최근 작성한 글 5개 제목 가져오기 (중복 작성 방지용)
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

# 네이버 뉴스 중 24시간 이내의 팔팔한 기사만 걸러내기
def filter_recent_24h_news(news_items):
    recent_items = []
    now_utc = datetime.now(timezone.utc)
    for item in news_items:
        try:
            pub_date = parsedate_to_datetime(item['pubDate'])
            time_diff = now_utc - pub_date
            if time_diff.total_seconds() <= 86400: # 24시간(86400초) 이내
                recent_items.append(item)
        except Exception as e:
            continue
    return recent_items

# 네이버 뉴스 API 검색 (최신순)
def search_naver_news(query, display=50):
    url = f"https://openapi.naver.com/v1/search/news.json?query={query}&display={display}&sort=date"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

# AI를 이용해 최근 기사 목록과 겹치지 않는 가장 핫한 트렌드 키워드 추출
def extract_trending_entity(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    recent_info = f"\n[주의사항: 최근 작성한 기사 제목들]\n{recent_titles}\n위 기사들에서 이미 메인으로 다루었던 인물이나 그룹은 절대 중복해서 선택하지 마." if recent_titles else ""
    
    system_prompt = f"""너는 트렌드 분석가야. 주어진 뉴스 제목들에서 가장 화제가 되는 특정 인물, 아이돌, 또는 작품 이름 딱 1개를 찾아.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keyword": "..."}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keyword', SEARCH_QUERY)

# 🚀 [핵심] 해당 언론사 사이트에 쳐들어가서 원본 메인 사진(og:image) 훔쳐오기
def get_naver_news_images(news_items, max_images=3):
    images = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    }
    
    for item in news_items:
        url = item.get('originallink') or item.get('link', '')
        url = url.replace('<b>', '').replace('</b>', '').replace('http://', 'https://')
        
        if not url:
            continue
            
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code != 200:
                continue
                
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 1순위: 기자가 설정한 공유용 최고화질 썸네일 (og:image)
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                img_url = og_image.get('content')
                if img_url.startswith('http') and 'logo' not in img_url.lower() and 'blank' not in img_url.lower():
                    if img_url not in images:
                        images.append(img_url)
                        if len(images) >= max_images:
                            return images
                            
            # 2순위: 본문 안의 가장 큰 이미지
            article_body = soup.find(class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
            if article_body:
                img_tags = article_body.find_all('img')
                for img in img_tags:
                    img_url = img.get('data-src') or img.get('src')
                    if img_url and img_url.startswith('http') and 'icon' not in img_url.lower():
                        if img_url not in images:
                            images.append(img_url)
                        if len(images) >= max_images:
                            return images

        except Exception as e:
            print(f"⚠️ 언론사 사이트 이미지 추출 실패 ({url}): {e}")
            continue
            
    return images

# 메인 실행 함수
def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 기사들: {recent_titles}")

    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내의 최신 기사가 없습니다. (작업 취소)")
        exit(1)
        
    print(f"✅ 24시간 이내 기사 {len(broad_news)}개 확보 완료!")
    
    trending_entity = extract_trending_entity(broad_news, recent_titles)
    print(f"🔥 핫이슈 (중복 필터링 완료): {trending_entity}")
    
    raw_deep_news = search_naver_news(trending_entity, 15)
    deep_news = filter_recent_24h_news(raw_deep_news)[:5] # 사진 확보를 위해 5개 넉넉히 가져옴
    
    if not deep_news:
        print("❌ 해당 핫이슈의 24시간 이내 디테일 기사가 부족합니다. (작업 취소)")
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
    
    # AI 모듈을 호출하여 최종 기사 작성
    article_data = get_ai_response(system_prompt, article_contents)
    title = article_data.get('title', f'{trending_entity} - Latest Update')
    content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
    
    # 🚀 언론사 사이트에서 실제 뉴스 사진 추출
    images = get_naver_news_images(deep_news, 3)
    if not images:
        images = ['https://k-enter24.com/og-image.png'] # 정 못 찾으면 내 사이트 로고 출력
    
    # DB에 영구 저장 (INSERT)
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
    print(f"✅ {CATEGORY_NAME} DB 저장 완료! (가져온 실제 기사 이미지: {len(images)}장)")

if __name__ == "__main__":
    main()
