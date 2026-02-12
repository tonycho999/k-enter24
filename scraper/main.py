import os
import sys
import json
import time
import requests
import re
from supabase import create_client, Client
from datetime import datetime, timedelta
from dateutil.parser import isoparse 
from dotenv import load_dotenv
from groq import Groq
from bs4 import BeautifulSoup

load_dotenv()
sys.stdout.reconfigure(encoding='utf-8')

supabase: Client = create_client(os.environ.get("NEXT_PUBLIC_SUPABASE_URL"), os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY"))
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CATEGORY_MAP = {
    "k-pop": ["컴백", "빌보드", "아이돌", "뮤직", "비디오", "챌린지", "포토카드", "월드투어", "가수"],
    "k-drama": ["드라마", "시청률", "넷플릭스", "OTT", "배우", "캐스팅", "대본리딩", "종영"],
    "k-movie": ["영화", "개봉", "박스오피스", "시사회", "영화제", "관객", "무대인사"],
    "k-entertain": ["예능", "유튜브", "개그맨", "코미디언", "방송", "개그우먼"],
    "k-culture": ["푸드", "뷰티", "웹툰", "팝업스토어", "패션", "음식", "해외반응"]
}

# [핵심 1] 미래지향적 AI 모델 자동 선택 함수
def get_best_model():
    try:
        models_raw = groq_client.models.list()
        available_models = [m.id for m in models_raw.data]
        
        def model_scorer(model_id):
            score = 0
            model_id = model_id.lower()
            if "llama" in model_id: score += 1000
            elif "mixtral" in model_id: score += 500
            elif "gemma" in model_id: score += 100
            
            version_match = re.search(r'(\d+\.?\d*)', model_id)
            if version_match:
                try:
                    version = float(version_match.group(1))
                    score += version * 100 
                except: pass

            if "70b" in model_id: score += 50
            elif "8b" in model_id: score += 10
            if "versatile" in model_id: score += 5
            return score

        available_models.sort(key=model_scorer, reverse=True)
        print(f"🤖 AI 모델 자동 선택 완료: {available_models[:3]}")
        return available_models
    except Exception as e:
        print(f"⚠️ 모델 리스트 조회 실패 (안전모드 진입): {e}")
        return ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"]

MODELS_TO_TRY = get_best_model()

def get_naver_api_news(keyword):
    import urllib.parse, urllib.request
    url = f"https://openapi.naver.com/v1/search/news?query={urllib.parse.quote(keyword)}&display=100&sort=sim"
    req = urllib.request.Request(url)
    req.add_header("X-Naver-Client-Id", os.environ.get("NAVER_CLIENT_ID"))
    req.add_header("X-Naver-Client-Secret", os.environ.get("NAVER_CLIENT_SECRET"))
    try:
        res = urllib.request.urlopen(req)
        return json.loads(res.read().decode('utf-8')).get('items', [])
    except: return []

def get_article_image(link):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        res = requests.get(link, headers=headers, timeout=3)
        soup = BeautifulSoup(res.text, 'html.parser')
        candidates = []

        main_content = soup.select_one('#dic_area, #articleBodyContents, .article_view, #articeBody, .news_view')
        if main_content:
            imgs = main_content.find_all('img')
            for i in imgs:
                src = i.get('src') or i.get('data-src')
                if src and 'http' in src:
                    width = i.get('width')
                    if width and width.isdigit() and int(width) < 200: continue
                    candidates.append(src)

        og = soup.find('meta', property='og:image')
        if og and og.get('content'): candidates.append(og['content'])

        for img_url in candidates:
            bad_keywords = r'logo|icon|button|share|banner|thumb|profile|default|ranking|news_stand|ssl.pstatic.net'
            if re.search(bad_keywords, img_url, re.IGNORECASE): continue
            return img_url
        return None
    except: return None

# [핵심 수정] 요약 길이 대폭 확대 (30~50% 수준)
def ai_category_editor(category, news_batch):
    if not news_batch: return []
    
    # AI 입력 데이터 50개로 제한
    limited_batch = news_batch[:50]
    
    # [수정] 제목만 주는 게 아니라 '본문 요약(description)'도 함께 제공하여 정보량 확보
    raw_text = ""
    for i, n in enumerate(limited_batch):
        # 네이버 API 특유의 태그(<b>, &quot;) 제거
        clean_desc = n['description'].replace('<b>', '').replace('</b>', '').replace('&quot;', '"')
        raw_text += f"[{i}] Title: {n['title']} / Context: {clean_desc}\n"
    
    # [수정] 프롬프트: '3-line summary' -> 'Detailed Narrative'로 변경
    prompt = f"""
    Task: Select exactly 30 news items for '{category}'. If fewer than 30, select ALL valid ones.
    
    Constraints: 
    1. Rank 1-30.
    2. English Title: Translate naturally.
    3. English Summary: Write a DETAILED, rich narrative summary (approx. 5~8 sentences).
       - Do NOT use bullet points. Write as a cohesive paragraph.
       - Elaborate on the 'Context' provided to make the content substantial (30-50% length of a short article).
       - Ensure specific details (Who, When, Where, Why) are included.
    4. AI Score (0.0-10.0).
    5. Return JSON format strictly.

    News List:
    {raw_text}

    Output JSON Format:
    {{
        "articles": [
            {{ "original_index": 0, "rank": 1, "category": "{category}", "eng_title": "Detailed Title...", "summary": "Longer and richer summary text goes here...", "score": 9.5 }}
        ]
    }}
    """
    
    for model in MODELS_TO_TRY:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": f"You are a professional K-Enter Journalist for {category}."},
                          {"role": "user", "content": prompt}], 
                model=model, 
                response_format={"type": "json_object"}
            )
            data = json.loads(res.choices[0].message.content)
            articles = data.get('articles', [])
            if articles: return articles
        except Exception as e:
            print(f"      ⚠️ {model} 실패 ({str(e)[:60]}...). 다음 모델 시도.")
            continue
    return []

# [핵심 3] AI 기반 키워드 트렌드 분석 함수
def update_hot_keywords():
    print("📊 AI 키워드 트렌드 분석 시작...")
    
    res = supabase.table("live_news").select("title").order("created_at", desc=True).limit(100).execute()
    titles = [item['title'] for item in res.data]
    
    if not titles:
        print("   ⚠️ 분석할 기사가 없습니다.")
        return

    titles_text = "\n".join([f"- {t}" for t in titles])
    
    prompt = f"""
    Analyze the following K-Entertainment news titles and identify the TOP 10 most trending keywords.
    
    [Rules]
    1. Extract specific Entities: Person Name (e.g., "Lee Min-ho", NOT "Lee"), Group Name (e.g., "BTS"), Drama/Movie Title (e.g., "Squid Game").
    2. Merge related concepts: If "Jin" and "BTS" are both popular, use "BTS Jin".
    3. EXCLUDE generic words: Do NOT use words like "Variety", "Actor", "K-pop", "Review", "Netizens", "Update", "Official", "Comeback", "Teaser".
    4. Return JSON format with 'keyword' and estimated 'count' (importance score 1-100).

    [Titles]
    {titles_text}

    [Output Format JSON]
    {{
        "keywords": [
            {{ "keyword": "BTS Jin", "count": 95, "rank": 1 }},
            {{ "keyword": "Squid Game 2", "count": 80, "rank": 2 }}
        ]
    }}
    """

    for model in MODELS_TO_TRY:
        try:
            res = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": "You are a K-Trend Analyst."},
                          {"role": "user", "content": prompt}], 
                model=model, 
                response_format={"type": "json_object"}
            )
            
            result = json.loads(res.choices[0].message.content)
            keywords = result.get('keywords', [])
            
            if not keywords: continue

            print(f"   🔥 AI가 추출한 진짜 트렌드: {[k['keyword'] for k in keywords[:5]]}...")

            supabase.table("trending_keywords").delete().neq("id", 0).execute()
            
            insert_data = []
            for item in keywords:
                insert_data.append({
                    "keyword": item['keyword'],
                    "count": item['count'],
                    "rank": item['rank'],
                    "updated_at": datetime.now().isoformat()
                })
            
            if insert_data:
                supabase.table("trending_keywords").insert(insert_data).execute()
                print("   ✅ 키워드 랭킹 DB 업데이트 완료.")
                return 

        except Exception as e:
            print(f"      ⚠️ {model} 분석 실패: {e}")
            continue

def run():
    print("🚀 7단계 마스터 엔진 가동 (긴 요약 + 정밀 이미지 + 키워드 분석)...")
    
    for category, keywords in CATEGORY_MAP.items():
        print(f"📂 {category.upper()} 부문 처리 중...")

        raw_news = []
        for kw in keywords: raw_news.extend(get_naver_api_news(kw))
        
        db_res = supabase.table("live_news").select("link").eq("category", category).execute()
        db_links = {item['link'] for item in db_res.data}
        new_candidate_news = [n for n in raw_news if n['link'] not in db_links]
        new_candidate_news = list({n['link']: n for n in new_candidate_news}.values())
        
        print(f"   🔎 수집: {len(raw_news)}개 -> 신규 후보: {len(new_candidate_news)}개")

        selected = ai_category_editor(category, new_candidate_news)
        num_new = len(selected)
        print(f"   ㄴ AI 선별 완료: {num_new}개")

        if num_new > 0:
            new_data_list = []
            for art in selected:
                idx = art['original_index']
                if idx >= len(new_candidate_news): continue
                
                orig = new_candidate_news[idx]
                
                img = get_article_image(orig['link']) 
                if not img: 
                    img = f"https://placehold.co/600x400/111/cyan?text={category}"

                new_data_list.append({
                    "rank": art['rank'], "category": category, "title": art['eng_title'],
                    "summary": art['summary'], "link": orig['link'], "image_url": img,
                    "score": art['score'], "likes": 0, "dislikes": 0, "created_at": datetime.now().isoformat()
                })
            
            if new_data_list:
                supabase.table("live_news").upsert(new_data_list, on_conflict="link").execute()
                print(f"   ✅ 신규 {len(new_data_list)}개 삽입 완료.")

        res = supabase.table("live_news").select("id", "created_at", "score").eq("category", category).execute()
        current_articles = res.data
        
        if len(current_articles) > 30:
            now = datetime.now()
            threshold = now - timedelta(hours=24)
            
            old_articles = []
            fresh_articles = []
            for a in current_articles:
                try:
                    dt_obj = isoparse(a['created_at']).replace(tzinfo=None)
                except:
                    dt_obj = datetime(2000, 1, 1)

                if dt_obj < threshold: old_articles.append(a)
                else: fresh_articles.append(a)
            
            delete_ids = []
            current_count = len(current_articles)
            
            old_articles.sort(key=lambda x: x['created_at'])
            for oa in old_articles:
                if current_count <= 30: break
                delete_ids.append(oa['id'])
                current_count -= 1
            
            if current_count > 30:
                fresh_articles.sort(key=lambda x: x['score'])
                for fa in fresh_articles:
                    if current_count <= 30: break
                    delete_ids.append(fa['id'])
                    current_count -= 1

            if delete_ids:
                supabase.table("live_news").delete().in_("id", delete_ids).execute()
                print(f"   🧹 슬롯 조정: {len(delete_ids)}개 삭제 완료.")

    update_hot_keywords()
    
    print(f"🎉 작업 완료.")

if __name__ == "__main__":
    run()
