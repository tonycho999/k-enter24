import os
import sys
import json
import urllib.request
import urllib.parse
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from urllib.parse import urljoin

# 1. 환경 설정
load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
groq_api_key = os.environ.get("GROQ_API_KEY")
naver_client_id = os.environ.get("NAVER_CLIENT_ID")
naver_client_secret = os.environ.get("NAVER_CLIENT_SECRET")

supabase: Client = create_client(supabase_url, supabase_key)
groq_client = Groq(api_key=groq_api_key)
AI_MODEL = "llama-3.3-70b-versatile"

SEARCH_KEYWORDS = ["K-POP 아이돌", "한국 인기 드라마", "한국 영화 화제", "한국 예능 레전드"]

def get_real_news_image(link):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Referer': 'https://news.naver.com/'
        }
        response = requests.get(link, headers=headers, timeout=10)
        if response.status_code != 200: return None
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. og:image 탐색
        og_image = soup.find('meta', property='og:image')
        img_url = og_image['content'] if og_image and og_image.get('content') else None
        
        # 2. 본문 이미지 탐색
        if not img_url or "static.naver.net" in img_url:
            selectors = ['#dic_area img', '#articleBodyContents img', '.article_kanvas img', '.article_body img']
            for s in selectors:
                tag = soup.select_one(s)
                if tag and tag.get('src'):
                    img_url = tag['src']
                    break
        
        return urljoin(link, img_url) if img_url else None
    except: return None

def get_naver_api_news(keyword):
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display=15&sort=sim"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", naver_client_id)
    req.add_header("X-Naver-Client-Secret", naver_client_secret)
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode('utf-8')).get('items', [])
    except: return []

def ai_chief_editor(news_batch):
    news_text = ""
    for idx, item in enumerate(news_batch):
        clean_title = item['title'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
        news_text += f"{idx+1}. {clean_title}\n"

    # 프롬프트 상세화 (AI가 헷갈리지 않게)
    prompt = f"""
    Role: Chief Editor of 'K-ENTER 24'.
    Analyze these news titles and select exactly 12 most interesting ones.
    Output MUST be a valid JSON object with "global_insight" and an "articles" array.
    
    Raw Titles:
    {news_text}
    
    JSON Schema:
    {{
        "global_insight": "summary",
        "articles": [
            {{
                "category": "K-POP",
                "artist": "Subject",
                "title": "Headline",
                "summary": "Short summary",
                "score": 9,
                "reactions": {{"excitement": 80, "sadness": 0, "shock": 20}},
                "original_title_index": 1
            }}
        ]
    }}
    """
    try:
        res = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=AI_MODEL,
            response_format={"type": "json_object"}
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"❌ AI 분석 실패: {e}")
        return None

def run():
    print(f"=== {datetime.now()} 실전 모드 시작 ===")
    all_news = []
    for keyword in SEARCH_KEYWORDS:
        items = get_naver_api_news(keyword)
        print(f"📡 {keyword}: {len(items)}건 발견")
        all_news.extend(items)
    
    print(f"🔍 총 {len(all_news)}건의 뉴스 수집됨. AI 분석 시작...")
    
    result = ai_chief_editor(all_news)
    if not result or 'articles' not in result:
        print("❌ AI가 결과를 생성하지 못했습니다.")
        return

    print(f"📝 AI가 {len(result['articles'])}개의 뉴스를 선정했습니다. 이미지 추출 중...")

    saved_count = 0
    for article in result.get('articles', []):
        idx = article.get('original_title_index', 1) - 1
        if idx < 0 or idx >= len(all_news): idx = 0
        original = all_news[idx]

        real_img = get_real_news_image(original['link'])
        
        if not real_img:
            # 여전히 실패 시 보조 수단 (네이버 로고라도 안 나오게 하기 위해 가수명으로 생성)
            real_img = f"https://placehold.co/600x400/111/cyan?text={article.get('artist', 'K-News').replace(' ', '+')}"
        else:
            print(f"📸 이미지 추출 성공: {article['title'][:20]}...")

        try:
            # 중복 체크 (DB가 비어있다면 무조건 통과해야 함)
            data = {
                "category": article.get('category', 'General'),
                "artist": article.get('artist', 'Trend'),
                "title": article['title'],
                "summary": article['summary'],
                "score": article.get('score', 5),
                "link": original['link'],
                "source": "Naver News",
                "image_url": real_img,
                "reactions": article['reactions'],
                "is_published": True,
                "created_at": datetime.now().isoformat()
            }
            supabase.table("live_news").insert(data).execute()
            saved_count += 1
            print(f"✅ 저장됨: {article['title'][:30]}")
        except Exception as e:
            print(f"💾 저장 실패: {e}")

    print(f"=== 최종 완료: {saved_count}개 업데이트됨 ===")

if __name__ == "__main__":
    run()
