# scripts/auto_pop.py
import os, requests, psycopg2
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
DATABASE_URL = os.environ.get("DATABASE_URL")

# ==========================================
# 🛑 카테고리 봇 설정 (다른 파일 복사 시 이 두 줄만 변경하세요)
CATEGORY_NAME = "K-ENTERTAINMENT"
SEARCH_QUERY = "예능"
# ==========================================

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

def extract_trending_entities(news_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in news_items]
    
    # 🚀 강력한 응급조치 프롬프트 적용: 최근 다룬 인물/주제 절대 중복 불가!
    recent_info = f"\n[CRITICAL WARNING: 최근 작성 기사 제목]\n{recent_titles}\n위 기사들에 이미 등장한 인물이나 그룹은 1%라도 겹치면 절대 안 돼. 무조건 새로운 인물을 찾아." if recent_titles else ""
    
    system_prompt = f"""너는 트렌드 분석가야. 뉴스 제목들에서 가장 화제가 되는 특정 인물/아이돌/그룹을 화제성 순으로 '3개' 찾아줘.
    {recent_info}
    반드시 JSON 형식으로 답변해. 형식: {{"keywords": ["1위인물", "2위인물", "3위인물"]}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keywords', [SEARCH_QUERY])

# 🚀 [완전 신규 로직] 네이버 공식 이미지 검색 API 사용
def search_naver_images(keyword, count=3):
    # 최적의 결과를 위해 검색어 뒤에 "고화질"을 붙여서 검색합니다.
    search_term = f"{keyword} 고화질"
    # sort=sim(유사도순), filter=large(큰 사이즈만) 옵션 적용
    url = f"https://openapi.naver.com/v1/search/image?query={search_term}&display={count}&sort=sim&filter=large"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    
    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            data = res.json()
            # 이미지 원본 링크(link)만 쏙 뽑아냅니다.
            return [item['link'] for item in data.get('items', [])]
    except Exception as e:
        print(f"이미지 API 검색 실패: {e}")
    
    return []

def main():
    print(f"[{CATEGORY_NAME}] 네이버 이미지 API 연동 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 기사들: {recent_titles}")

    raw_news = search_naver_news(SEARCH_QUERY, 50)
    broad_news = filter_recent_24h_news(raw_news)
    
    if not broad_news:
        print("❌ 24시간 이내 최신 기사가 없어 종료합니다.")
        exit(1)
        
    trending_entities = extract_trending_entities(broad_news, recent_titles)
    print(f"🔥 AI가 뽑은 후보군 Top 3: {trending_entities}")
    
    saved_successfully = False
    
    for entity in trending_entities:
        print(f"\n▶ 후보 탐색 중: {entity}")
        
        raw_deep_news = search_naver_news(entity, 20)
        deep_news = filter_recent_24h_news(raw_deep_news)[:6]
        
        if len(deep_news) < 2:
            print(f"⚠️ [{entity}] 관련 기사가 부족합니다. 다음 후보로 패스!")
            continue
            
        # 🚀 [핵심] 언론사 사이트 뒤질 필요 없이, 네이버 API에게 "뉴진스 사진 3장 줘" 하고 즉시 받아옵니다!
        images = search_naver_images(entity, 3)
        
        if not images or len(images) < 2:
            print(f"⚠️ [{entity}] 네이버 API에서 고화질 사진을 2장 이상 찾지 못했습니다. 다음 후보로 패스!")
            continue 
            
        print(f"🎉 [{entity}] 완벽한 사진 {len(images)}장 확보 성공! 기사 작성을 시작합니다.")
        
        article_contents = "\n".join([f"- {n['title']}: {n['description']}" for n in deep_news])
        system_prompt = """
너는 글로벌 한국 엔터테인먼트 매거진의 수석 에디터야. 
제공된 뉴스를 바탕으로 해외 팬들이 흥미를 가질 만한 감각적인 영어 제목과 전문성 있는 영어 본문을 작성해 줘.

[작성 및 분량 규칙]
1. 본문 분량: 영문 기준 공백 포함 '800자 ~ 1,200자 내외' (최소 600자 이상, 최대 1500자 이내 필수)
2. 500자 수준의 단편 요약글이 되지 않도록 아래 4단계 구조를 반드시 모두 갖추어 작성할 것:
   - 1단락: 사건/뉴스 요약 및 해외 팬들의 흥미를 끄는 도입부
   - 2단락: 상세한 배경 설명 및 이번 소식의 핵심 포인트 (구체적 예시 포함)
   - 3단락: 글로벌 팬들의 반응 및 엔터 산업에 미칠 영향/의미
   - 4단락: 향후 일정이나 기대감을 나타내는 맺음말
3. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
4. 본문의 자연스러운 위치(2~3단락 사이)에 아래 형식의 아마존 상품 검색 링크를 딱 1개 삽입할 것:
   - 형식: "🛒 Find [메인키워드] merch on Amazon: https://www.amazon.com/s?k=[메인키워드영어]&i=specialty-aps&tag=kculturetrend-20"
   - 키워드 띄어쓰기는 '+' 기호로 변환할 것 (예: BTS V -> BTS+V)
5. 글 마지막에 관련 해시태그 5개를 작성할 것 ('SEO' 등 검색/마케팅 관련 용어 절대 금지).

[출력 형식]
반드시 유효한 JSON 형식으로만 답변할 것 (본문 내 큰따옴표가 들어갈 경우 역슬래시 \" 처리 필수):
{"title": "영어제목", "content": "영어본문", "tags": "태그"}
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
        print("\n❌ 3개의 후보를 모두 뒤졌지만, 사진 퀄리티 등을 만족하는 이슈가 없어 포기합니다.")
        exit(1)

if __name__ == "__main__":
    main()
