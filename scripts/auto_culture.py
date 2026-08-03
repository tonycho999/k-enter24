# scripts/auto_culture.py
import os, requests, psycopg2
from AI import get_ai_response

NAVER_CLIENT_ID = os.environ.get("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.environ.get("NAVER_CLIENT_SECRET")
UNSPLASH_ACCESS_KEY = os.environ.get("UNSPLASH_ACCESS_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

CATEGORY_NAME = "K-CULTURE"

def search_naver_shopping(query, display=10):
    url = f"https://openapi.naver.com/v1/search/shop.json?query={query}&display={display}&sort=sim"
    headers = {"X-Naver-Client-Id": NAVER_CLIENT_ID, "X-Naver-Client-Secret": NAVER_CLIENT_SECRET}
    res = requests.get(url, headers=headers)
    return res.json().get('items', [])

def extract_trending_product(shop_items):
    titles = [item['title'].replace('<b>', '').replace('</b>', '') for item in shop_items]
    system_prompt = "너는 한국 트렌드 분석가야. 주어진 쇼핑 아이템 중에서 글로벌 팬들이 가장 흥미를 가질 만한 뷰티/패션/식품 등 트렌디한 상품 딱 '하나'만 골라줘. 반드시 JSON 형식으로 답변: {\"keyword\": \"...\"}"
    
    response_data = get_ai_response(system_prompt, str(titles))
    return response_data.get('keyword', '한국 트렌드 아이템')

def get_unsplash_images(keyword, count=2):
    url = f"https://api.unsplash.com/search/photos?query={keyword}&per_page={count}&client_id={UNSPLASH_ACCESS_KEY}"
    res = requests.get(url)
    return [img['urls']['regular'] for img in res.json().get('results', [])]

def main():
    print(f"[{CATEGORY_NAME}] 쇼핑 기반 작업 시작...")
    shop_items = search_naver_shopping("한국 트렌드 아이템", 15) 
    if not shop_items: return
    
    trending_product = extract_trending_product(shop_items)
    print(f"🔥 핫 아이템: {trending_product}")
    
    deep_items = search_naver_shopping(trending_product, 3)
    product_contents = "\n".join([f"- 상품명: {n['title'].replace('<b>', '').replace('</b>', '')} / 최저가: {n['lprice']}원" for n in deep_items])
    
    system_prompt = """
    너는 글로벌 K-Culture 매거진의 트렌드 에디터야. 
    제공된 한국 트렌드 상품 정보를 바탕으로, 이 제품(문화)이 왜 한국에서 유행인지 소개하는 세련된 영어 블로그 글을 써 줘.
    [규칙]
    1. 본문의 길이는 반드시 최소 500자 이상, 최대 1500자 이내일 것.
    2. 본문은 HTML 태그 없이 문단 구분을 위한 줄바꿈(\n\n)만 사용할 것.
    3. 마지막에 해시태그 5개를 추가할 것. ('SEO', 'AEO' 등 용어 절대 금지)
    반드시 JSON 형식으로 답변: {"title": "영어제목", "content": "영어본문", "tags": "태그"}
    """
    
    article_data = get_ai_response(system_prompt, product_contents)
    
    title = article_data.get('title', 'K-Culture Trend')
    content = article_data.get('content', '') + "\n\nTags: " + article_data.get('tags', '')
    
    # 썸네일은 쇼핑 API의 실제 제품 이미지 활용
    main_image = deep_items[0]['image'] if deep_items else 'https://via.placeholder.com/800x500.png?text=No+Image'
    sub_images = get_unsplash_images(f"{trending_product} korea style", 2)
    images = [main_image] + sub_images
    
    conn = psycopg2.connect(DATABASE_URL)
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
