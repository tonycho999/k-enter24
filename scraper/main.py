import os
import sys
import json
import time
import random
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

# [수정] 시도할 모델 리스트 (최신/고성능 순서)
MODELS_TO_TRY = [
    "llama-3.3-70b-versatile", # 최신 최고 사양
    "llama-3.1-70b-versatile", # 안정적인 고사양
    "llama-3.1-8b-instant",    # 빠르고 가벼운 모델 (최후 보루)
    "mixtral-8x7b-32768"       # 대안 모델
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Referer': 'https://news.naver.com/'
}

SEARCH_KEYWORDS = [
    "배우", "가수", "컴백", "데뷔", "캐스팅", "종영", "개봉", 
    "독점", "빌보드", "공개예정", "시청률 1위", "신인배우", "제작발표회", "어워드"
]

# 2. 랭킹 수집 (셀렉터 보강)
def get_naver_ranking_30():
    print("📡 네이버 연예 실시간 랭킹 30 수집 시도...")
    ranking_url = "https://entertain.naver.com/ranking"
    try:
        res = requests.get(ranking_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        items = []
        news_links = soup.select('.rank_lst li a.tit') or soup.select('.tit_area a') or soup.select('a.tit')
        
        print(f"🔍 랭킹 페이지에서 {len(news_links)}개의 잠재적 링크 발견")
        
        for i, a in enumerate(news_links[:30]):
            title = a.get_text(strip=True)
            link = urljoin(ranking_url, a['href'])
            if title and link:
                items.append({'title': title, 'link': link, 'is_ranking': True})
        return items
    except Exception as e:
        print(f"⚠️ 랭킹 수집 에러: {e}")
        return []

def get_naver_api_news(keyword):
    import urllib.parse
    import urllib.request
    encText = urllib.parse.quote(keyword)
    url = f"https://openapi.naver.com/v1/search/news?query={encText}&display=10&sort=sim"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", naver_client_id)
    req.add_header("X-Naver-Client-Secret", naver_client_secret)
    try:
        res = urllib.request.urlopen(req)
        items = json.loads(res.read().decode('utf-8')).get('items', [])
        return [{'title': i['title'], 'link': i['link'], 'is_ranking': False} for i in items]
    except: return []

def get_article_details(link):
    try:
        res = requests.get(link, headers=HEADERS, timeout=7)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_image = soup.find('meta', property='og:image')
        return og_image['content'] if og_image else None
    except: return None

# 3. [핵심] AI 편집장: 모델 순차 시도 로직 적용
def ai_chief_editor(news_list):
    raw_text = "\n".join([f"[{i}] {n['title']}" for i, n in enumerate(news_list)])
    
    prompt = f"""
    Role: K-ENTER 24 Chief Editor.
    Task: Categorize news into EXACTLY one of these: [k-pop, k-drama, k-movie, k-entertain].
    Output MUST be in JSON format.
    
    Raw News:
    {raw_text}
    
    JSON Output Format:
    {{
        "articles": [
            {{
                "original_index": 0,
                "category": "k-pop",
                "eng_title": "Headline in English",
                "summary": "1 sentence English summary",
                "reactions": {{"excitement": 70, "shock": 30, "sadness": 0}}
            }}
        ]
    }}
    """

    for model_name in MODELS_TO_TRY:
        try:
            print(f"🤖 AI 분석 시도 중... (모델: {model_name})")
            res = groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=model_name,
                response_format={"type": "json_object"}
            )
            return json.loads(res.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ {model_name} 실패: {e}. 다음 모델로 넘어갑니다...")
            continue # 다음 모델로 시도
            
    print("❌ 모든 AI 모델 시도가 실패했습니다.")
    return None

def run():
    wait_time = random.randint(60, 600)
    print(f"🕒 보안을 위해 {wait_time}초 대기 후 시작합니다...")
    time.sleep(wait_time)

    print(f"=== {datetime.now()} 고가용성 수집 모드 가동 ===")
    
    all_raw_news = get_naver_ranking_30()
    for kw in SEARCH_KEYWORDS:
        all_raw_news.extend(get_naver_api_news(kw))
    
    if not all_raw_news:
        print("❌ 수집된 원시 데이터가 없습니다.")
        return

    analysis = ai_chief_editor(all_raw_news)
    if not analysis: return

    saved = 0
    for art in analysis.get('articles', []):
        idx = art['original_index']
        if idx >= len(all_raw_news): continue
        item = all_raw_news[idx]
        
        if supabase.table("live_news").select("id").eq("link", item['link']).execute().data:
            continue
            
        img = get_article_details(item['link'])
        if not img: img = f"https://placehold.co/600x400/111/cyan?text={art['category']}"

        try:
            data = {
                "category": art['category'],
                "title": art['eng_title'],
                "summary": art['summary'],
                "link": item['link'],
                "image_url": img,
                "reactions": art['reactions'],
                "is_ranking": item.get('is_ranking', False),
                "created_at": datetime.now().isoformat()
            }
            supabase.table("live_news").insert(data).execute()
            saved += 1
            print(f"✅ [{art['category']}] 저장 완료")
        except: pass

    print(f"=== 최종 완료: {saved}개 뉴스 업데이트 ===")

if __name__ == "__main__":
    run()
