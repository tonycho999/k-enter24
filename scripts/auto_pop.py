# scripts/auto_pop.py
import os, requests, psycopg2
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-POP"
# '가수' 하나만 쓰면 검색 폭이 좁으므로, 더 풍부하게 검색되도록 OR 연산자를 붙였습니다.
SEARCH_QUERY = "가수"

# 🚀 [추가] 파이썬이 싫어하는 pgbouncer 글자를 지워주는 공통 함수
def get_clean_db_url():
    if DATABASE_URL:
        return DATABASE_URL.replace("?pgbouncer=true", "")
    return ""

def get_recent_titles():
    try:
        # pgbouncer가 제거된 깔끔한 주소로 접속!
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

# 🚀 [추가] 24시간 이내의 팔팔한 최신 뉴스만 걸러내는 함수
def filter_recent_24h_news(news_items):
    recent_items = []
    now_utc = datetime.now(timezone.utc)
    for item in news_items:
        try:
            pub_date = parsedate_to_datetime(item['pubDate'])
            time_diff = now_utc - pub_date
            # 86400초(24시간) 이내인 기사만 통과!
            if time_diff.total_seconds() <= 86400:
                recent_items.append(item)
        except Exception as e:
            continue
    return recent_items

# 🚀 [수정] 24시간 필터링을 위해 sort=date(최신순)으로 50개를 넉넉히 가져옴
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

def get_unsplash_images(keyword, count=2):
    url = f"https://api.unsplash.com/search/photos?query={keyword}&per_page={count}&client_id={UNSPLASH_ACCESS_KEY}"
    res = requests.get(url)
    return [img['urls']['regular'] for img in res.json().get('results', [])]

def main():
    print(f"[{CATEGORY_NAME}] 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 기사들: {recent_titles}")

    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내의 최신 기사가 없습니다. 작업을 취소하고 다음 턴을 노립니다.")
        exit(1)
        
    print(f"✅ 24시간 이내 기사 {len(broad_news)}개 확보 완료!")
    
    trending_entity = extract_trending_entity(broad_news, recent_titles)
    print(f"🔥 핫이슈 (중복 필터링 완료): {trending_entity}")
    
    raw_deep_news = search_naver_news(trending_entity, 15)
    deep_news = filter_recent_24h_news(raw_deep_news)[:3]
    
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
    
    images = get_unsplash_images(f"{CATEGORY_NAME} {trending_entity} korea", 2)
    if not images:
        images = ['https://via.placeholder.com/800x500.png?text=No+Image']
    
    # 🚀 pgbouncer가 제거된 깔끔한 주소로 접속!
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
    print(f"✅ {CATEGORY_NAME} DB 저장 완료!")

if __name__ == "__main__":
    main()
