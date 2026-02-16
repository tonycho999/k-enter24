import json
import re
import os
from news_api import NewsEngine
from naver_api import NaverManager
from database import DatabaseManager

def clean_json_text(text):
    match = re.search(r"```(?:json)?\s*(.*)\s*```", text, re.DOTALL)
    if match: text = match.group(1)
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1: return text[start:end+1]
    return text.strip()

def run_automation():
    print("🚀 K-Enter24 Automation Started (KR Search -> EN Save)")
    
    db = DatabaseManager()
    engine = NewsEngine()
    naver = NaverManager()
    
    run_count = int(os.environ.get("RUN_COUNT", 0))
    categories = ["k-pop", "k-drama", "k-movie", "k-entertain", "k-culture"]

    for cat in categories:
        print(f"\n[{cat}] Processing...")
        try:
            # 1. Perplexity: 한국 소스 검색 -> 영어 JSON 반환
            raw_data_str, original_query = engine.get_trends_and_rankings(cat)
            
            cleaned_str = clean_json_text(raw_data_str)
            if not cleaned_str or cleaned_str == "{}":
                print(f"⚠️ [{cat}] No data returned.")
                continue

            parsed_data = json.loads(cleaned_str)
            
            # ---------------------------------------------------
            # A. [사이드바] TOP 10 랭킹 (영어)
            # ---------------------------------------------------
            top10_list = parsed_data.get('top10', [])
            if top10_list:
                print(f"  > Saving {len(top10_list)} Rankings...")
                for item in top10_list:
                    db.save_rankings([{
                        "category": cat,
                        "rank": item.get('rank'),
                        "title": item.get('title'),
                        "meta_info": item.get('info', ''),
                        "score": 0
                    }])

            # ---------------------------------------------------
            # B. [메인 피드] 기사 작성
            # ---------------------------------------------------
            people_list = parsed_data.get('people', [])
            if people_list:
                print(f"  > Processing {len(people_list)} Articles...")
                
                for person in people_list:
                    name_en = person.get('name_en') # 영어 이름 (DB 저장용)
                    name_kr = person.get('name_kr') # 한국어 이름 (이미지 검색용)
                    facts = person.get('facts')     # 영어 팩트
                    
                    # 둘 중 하나라도 없으면 대체
                    if not name_en: name_en = name_kr 
                    if not name_kr: name_kr = name_en
                    
                    if not name_en: continue

                    # Groq: 영어 팩트로 영어 기사 작성
                    full_text = engine.edit_with_groq(name_en, facts, cat)
                    
                    # 점수 파싱
                    score = 70
                    final_text = full_text
                    if "###SCORE:" in full_text:
                        try:
                            parts = full_text.split("###SCORE:")
                            final_text = parts[0].strip()
                            import re
                            score_match = re.search(r'\d+', parts[1])
                            if score_match: score = int(score_match.group())
                        except: pass

                    lines = final_text.split('\n')
                    title = lines[0].replace('Headline:', '').strip()
                    summary = "\n".join(lines[1:]).strip()
                    
                    # [핵심] 이미지는 '한국어 이름'으로 검색해야 정확함
                    img_url = naver.get_image(name_kr)
                    
                    article_data = {
                        "category": cat,
                        "keyword": name_en, # DB엔 영어 이름
                        "title": title,
                        "summary": summary,
                        "link": person.get('link', ''),
                        "image_url": img_url,
                        "score": score,
                        "likes": 0,
                        "query": original_query,
                        "raw_result": str(person),
                        "run_count": run_count 
                    }
                    
                    db.save_to_archive(article_data)
                    
                    live_data = {
                        "category": article_data['category'],
                        "keyword": article_data['keyword'],
                        "title": article_data['title'],
                        "summary": article_data['summary'],
                        "link": article_data['link'],
                        "image_url": article_data['image_url'],
                        "score": score,
                        "likes": 0
                    }
                    db.save_live_news([live_data])
                    print(f"    - Published: {name_en} (Score: {score})")

        except Exception as e:
            print(f"❌ [{cat}] Error: {e}")

if __name__ == "__main__":
    run_automation()
