# scripts/auto_culture.py
import os, requests, psycopg2, json
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

# 🚀 뉴스 API가 아니라 쇼핑 API를 찌릅니다. (시간 필터링 안 함!)
def search_naver_shopping(query, display=15):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display={display}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

def extract_trending_product(shop_items, recent_titles):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in shop_items]
    recent_info = f"\n[주의: 최근 작성한 트렌드 글들]\n{recent_titles}\n위 글에서 이미 소개한 상품은 절대 중복 선택하지 마." if recent_titles else ""
    
    system_prompt = f"""너는 한국 트렌드 분석가야. 주어진 쇼핑 아이템 중에서 글로벌 팬들이 가장 흥미를 가질 만한 뷰티/패션/식품 등 트렌디한 상품 딱 '하나'만 골라줘.
    {recent_info}
    반드시 JSON 형식으로 답변: {{"keyword": "..."}}"""
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keyword', '한국 뷰티 템')

def main():
    print(f"[{CATEGORY_NAME}] 쇼핑 기반 작업 시작...")
    
    recent_titles = get_recent_titles()
    print(f"🧐 최근 작성된 K-CULTURE 글: {recent_titles}")

    # 외국인들이 좋아할 만한 키워드 3개를 섞어서 찌릅니다.
    shop_items = search_naver_shopping("한국 화장품 OR 한국 간식 OR 올리브영 추천", 20) 
    
    if not shop_items:
        print("❌ 네이버 쇼핑 API에서 상품을 가져오지 못했습니다.")
        exit(1) # 강제 에러 처리해서 다음 턴에 다시 돌게 만듭니다.
        
    trending_product = extract_trending_product(shop_items, recent_titles)
    print(f"🔥 핫 아이템 (중복 필터링 완료): {trending_product}")
    
    # 딥다이브: 해당 상품 검색
    deep_items = search_naver_shopping(trending_product, 3)
    
    if not deep_items:
        print("❌ 해당 핫 아이템의 쇼핑 정보가 부족합니다.")
        exit(1)
        
    product_contents = "\n".join([f"- 상품명: {n['title'].replace('<b>', '').replace('</b>', '')} / 최저가: {n['lprice']}원" for n in deep_items])
    
    system_prompt = """
    너는 글로벌 K-Culture 매거진의 트렌드 에디터야. 
    제공된 한국 트렌드 상품 정보를 바탕으로, 해외 팬들에게 이 제품(문화)이 왜 한국에서 유행인지 소개하는 세련된 영어 블로그 글을 써 줘.
    [규칙]
    1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
    2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
    3. 마지막에 해시태그 5개를 추가할 것. ('SEO', 'AEO' 등 용어 절대 금지)
    반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
    """
    
    article_data = get_ai_response(system_prompt, product_contents)
    title = article_data.get('title', 'K-Culture Trend')
    content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
    
    # 🚀 쇼핑 아이템은 쇼핑 API가 주는 제품 사진(image)이 최고 화질입니다!
    images = []
    for item in deep_items:
        img_url = item.get('image')
        if img_url and img_url not in images:
            images.append(img_url)
            
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
    print(f"✅ {CATEGORY_NAME} DB 저장 완료! (가져온 쇼핑 이미지: {len(images)}장)")

if __name__ == "__main__":
    main()
