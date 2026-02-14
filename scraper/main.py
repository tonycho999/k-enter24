import os
import json
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
from duckduckgo_search import DDGS

# 1. 환경변수 로드
load_dotenv()

# 2. Supabase 설정
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Gemini 설정
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# [핵심] 검색 도구 없이 '순수 텍스트 생성' 모델 사용 (에러 원천 차단)
model = genai.GenerativeModel('gemini-1.5-flash')

CATEGORIES = {
    "K-Pop": "k-pop news latest trends ranking",
    "K-Drama": "k-drama news ratings ranking actor controversy",
    "K-Movie": "korean movie box office news actor interview",
    "K-Variety": "korean variety show ratings news funny moments",
    "K-Culture": "korea travel hot place seoul festival food trend"
}

def search_web(keyword):
    """DuckDuckGo를 이용해 최신 뉴스를 검색합니다."""
    print(f"🔍 [Search] '{keyword}' 검색 중...")
    results = []
    try:
        # ddg 인스턴스 생성
        with DDGS() as ddgs:
            # 뉴스 검색 (최신순)
            ddg_results = list(ddgs.news(keywords=keyword, region="kr-kr", safesearch="off", max_results=15))
            
            for r in ddg_results:
                results.append(f"제목: {r.get('title')}\n링크: {r.get('url')}\n내용: {r.get('body')}\n출처: {r.get('source')}")
                
    except Exception as e:
        print(f"⚠️ 검색 중 오류 발생: {e}")
    
    return "\n\n".join(results)

def fetch_data_from_gemini(category_name, raw_data):
    """검색된 텍스트 데이터를 Gemini에게 던져서 JSON으로 정리하게 시킵니다."""
    print(f"🤖 [Gemini] '{category_name}' 데이터 정리 중...")
    
    prompt = f"""
    [Role]
    You are a veteran K-Entertainment journalist.
    
    [Context]
    Here is the latest raw search data about '{category_name}':
    {raw_data}

    [Task]
    Analyze the raw data above and extract the most important trends.
    Return the result in strict JSON format.

    [Requirements]
    1. **news_updates**: Select 10 most important news.
       - 'summary' must be in Korean (Hangul).
       - 'title' must be in Korean.
    2. **rankings**: Extract or infer Top 10 rankings based on the buzz.
       - If exact ranking data is missing, rank them by mention frequency.
       - Items must be unique.

    [Output Format (JSON Only)]
    {{
      "news_updates": [
        {{
          "keyword": "Main Subject (e.g. NewJeans)",
          "title": "News Title (Korean)",
          "summary": "Summary (Korean, 150 chars)",
          "link": "Source URL from raw data"
        }},
        ...
      ],
      "rankings": [
        {{ "rank": 1, "title": "Song/Drama/Movie Title", "meta": "Artist/Actor/Channel" }},
        ...
      ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"❌ [Error] Gemini 처리 중 오류: {e}")
        return None

def update_database(category, data):
    # 1. 뉴스 저장
    news_list = data.get("news_updates", [])
    if news_list:
        clean_news = []
        for item in news_list:
            clean_news.append({
                "category": category,
                "keyword": item.get("keyword", category),
                "title": item.get("title", ""),
                "summary": item.get("summary", ""),
                "link": item.get("link", ""),
                "created_at": "now()"
            })
        
        try:
            supabase.table("search_archive").upsert(clean_news, on_conflict="category,keyword,title").execute()
            supabase.table("live_news").upsert(clean_news, on_conflict="category,keyword,title").execute()
            print(f"   💾 뉴스 {len(clean_news)}개 저장 완료")
        except Exception as e:
            print(f"   ⚠️ 뉴스 저장 실패: {e}")

    # 2. 롤링 업데이트 (30개 유지)
    try:
        res = supabase.table("live_news").select("id").eq("category", category).order("created_at", desc=True).execute()
        all_ids = [row['id'] for row in res.data]
        if len(all_ids) > 30:
            ids_to_delete = all_ids[30:]
            supabase.table("live_news").delete().in_("id", ids_to_delete).execute()
    except Exception:
        pass

    # 3. 랭킹 저장
    rank_list = data.get("rankings", [])
    if rank_list:
        clean_ranks = []
        for item in rank_list:
            clean_ranks.append({
                "category": category,
                "rank": item.get("rank"),
                "title": item.get("title"),
                "meta_info": item.get("meta", ""),
                "updated_at": "now()"
            })
        try:
            supabase.table("live_rankings").upsert(clean_ranks, on_conflict="category,rank").execute()
            print(f"   🏆 랭킹 갱신 완료")
        except Exception as e:
            print(f"   ⚠️ 랭킹 저장 실패: {e}")

def main():
    print("🚀 뉴스 크롤링 및 AI 요약 시작 (DuckDuckGo + Gemini)")
    
    for category, search_keyword in CATEGORIES.items():
        # 1. DuckDuckGo로 검색
        raw_text = search_web(search_keyword)
        
        if len(raw_text) < 50:
            print(f"⚠️ {category} 검색 결과 부족. 건너뜀.")
            continue

        # 2. Gemini에게 요약 요청
        data = fetch_data_from_gemini(category, raw_text)
        
        # 3. DB 저장
        if data:
            update_database(category, data)
        
        time.sleep(3) # 밴 방지용 대기

    print("✅ 모든 작업 완료")

if __name__ == "__main__":
    main()
