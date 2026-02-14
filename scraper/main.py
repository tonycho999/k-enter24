import os
import json
import time
import requests
import urllib.parse
from supabase import create_client, Client
from dotenv import load_dotenv
from ddgs import DDGS

# 1. Load Environment Variables
load_dotenv()

# 2. Supabase Setup
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 3. Gemini API Key
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")

if GOOGLE_API_KEY:
    print(f"🔑 API Key Loaded: {GOOGLE_API_KEY[:5]}...")
else:
    print("❌ No API Key found!")

# Categories
CATEGORIES = {
    "K-Pop": "k-pop latest news trends",
    "K-Drama": "k-drama ratings news",
    "K-Movie": "korean movie box office news",
    "K-Entertain": "korean variety show news reality show trends", 
    "K-Culture": "seoul travel food trends"
}

# Use Stable Model (1.5 Flash)
CURRENT_MODEL_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

def get_fallback_image(keyword):
    """Finds an image if the news article doesn't have one."""
    try:
        with DDGS() as ddgs:
            imgs = list(ddgs.images(keywords=keyword, region="wt-wt", safesearch="off", max_results=1))
            if imgs and len(imgs) > 0:
                return imgs[0].get('image')
    except Exception:
        return ""
    return ""

def search_web(keyword):
    """DuckDuckGo Search: HTTPS only + Image required + Last 24h Only"""
    print(f"🔍 [Search] Searching for '{keyword}' (Last 24h)...")
    results = []
    
    try:
        with DDGS() as ddgs:
            # ✅ [수정] timelimit="d" 추가 -> '지난 24시간' 기사만 검색
            ddg_results = list(ddgs.news(
                query=keyword, 
                region="wt-wt", 
                safesearch="off", 
                timelimit="d", # <--- 여기가 핵심! (d=day, w=week, m=month)
                max_results=15
            ))
            
            for r in ddg_results:
                title = r.get('title', '')
                body = r.get('body', r.get('snippet', ''))
                link = r.get('url', r.get('href', ''))
                image = r.get('image', r.get('thumbnail', ''))

                if not title or not body or not link or not link.startswith("https"):
                    continue

                if not image:
                    image = get_fallback_image(title)
                    time.sleep(0.5) 

                if not image:
                    continue

                results.append(f"Title: {title}\nBody: {body}\nLink: {link}\nImage: {image}")
                
    except Exception as e:
        print(f"⚠️ Search error: {e}")
    
    return "\n\n".join(results)

def call_gemini_api(category_name, raw_data):
    print(f"🤖 [Gemini] Writing articles for '{category_name}' (English Mode)...")
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""
    [Role]
    You are a veteran K-Entertainment journalist with 20 years of experience writing for an international audience.
    Your writing style is analytical, insightful, and engaging (perfect English).

    [Input Data]
    {raw_data[:25000]} 

    [Task]
    Select the Top 10 most impactful news items for '{category_name}' and rewrite them in ENGLISH.
    
    [Content Requirements - STRICT]
    1. **Language**: MUST be written in **ENGLISH**.
    2. **Length**: Each summary must be between **100 and 500 characters**.
    3. **Depth**: Provide context (why this matters). Do not just copy the headline.
    4. **Image**: You MUST map the 'image_url' from the raw data exactly.

    [Output Format (JSON Only)]
    {{
      "news_updates": [
        {{ 
          "keyword": "Main Subject", 
          "title": "Compelling Title (English)", 
          "summary": "Detailed Article (English, 100-500 chars)", 
          "link": "Original Link",
          "image_url": "URL starting with https"
        }}
      ],
      "rankings": [
        {{ "rank": 1, "title": "Name (English)", "meta": "Short Info (English)", "score": 98 }}
      ]
    }}
    """
    
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    full_url = f"{CURRENT_MODEL_URL}?key={GOOGLE_API_KEY}"

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(full_url, headers=headers, json=payload)
            
            if response.status_code == 200:
                try:
                    text = response.json()['candidates'][0]['content']['parts'][0]['text']
                    text = text.replace("```json", "").replace("```", "").strip()
                    return json.loads(text)
                except Exception as e:
                    print(f"   ⚠️ JSON Parse Error: {e}")
                    return None
            
            elif response.status_code in [429, 503]:
                wait_time = (attempt + 1) * 20
                print(f"   ❌ Temporary Error ({response.status_code}): Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            
            else:
                print(f"   ❌ API Error ({response.status_code}): {response.text[:200]}")
                return None

        except Exception as e:
            print(f"   ❌ Connection Error: {e}")
            time.sleep(10)
            continue
            
    return None

def update_database(category, data):
    # Save News
    news_list = data.get("news_updates", [])
    if news_list:
        clean_news = []
        for item in news_list:
            if not item.get("image_url"): continue

            summary = item.get("summary", "")
            title = item.get("title", "No Title")
            
            if len(summary) < 50: 
                continue

            encoded_query = urllib.parse.quote(f"{title} k-pop news")
            search_link = f"https://www.google.com/search?q={encoded_query}&tbm=nws"

            clean_news.append({
                "category": category,
                "keyword": item.get("keyword", category),
                "title": title,
                "summary": summary,
                "link": search_link,
                "image_url": item.get("image_url"),
                "created_at": "now()",
                "likes": 0,
                "score": 80 + (len(summary) / 10) 
            })
        
        if clean_news:
            try:
                supabase.table("live_news").upsert(clean_news, on_conflict="category,keyword,title").execute()
                supabase.table("search_archive").upsert(clean_news, on_conflict="category,keyword,title").execute()
                print(f"   💾 Saved {len(clean_news)} news items.")
            except Exception as e:
                print(f"   ⚠️ DB Save Error: {e}")

    # Save Rankings
    rank_list = data.get("rankings", [])
    if rank_list:
        clean_ranks = []
        for item in rank_list:
            clean_ranks.append({
                "category": category,
                "rank": item.get("rank"),
                "title": item.get("title"),
                "meta_info": item.get("meta", ""),
                "score": item.get("score", 0),
                "updated_at": "now()"
            })
        try:
            supabase.table("live_rankings").upsert(clean_ranks, on_conflict="category,rank").execute()
            print(f"   🏆 Updated rankings.")
        except Exception as e:
             print(f"   ⚠️ Ranking Save Error: {e}")

def main():
    print(f"🚀 Scraper Started (Last 24h News Only)")
    for category, search_keyword in CATEGORIES.items():
        raw_text = search_web(search_keyword)
        
        if len(raw_text) < 50: 
            print(f"⚠️ {category} : Not enough data.")
            continue

        data = call_gemini_api(category, raw_text)
        if data:
            update_database(category, data)
        
        print("⏳ Cooldown (10s)...")
        time.sleep(10) 

    print("✅ All jobs finished.")

if __name__ == "__main__":
    main()
