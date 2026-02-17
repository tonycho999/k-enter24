import os
import json
import asyncio
from chart_api import ChartEngine
from database import DatabaseManager
from supabase import create_client
from groq import Groq

# ... (clean_json_text, get_run_count, update_run_count 함수는 기존과 동일)

def analyze_with_groq(api_key, category):
    """실패한 카테고리의 HTML을 Groq Llama 3로 분석"""
    file_path = f"error_{category}.html"
    if not os.path.exists(file_path): return
    
    print(f"🤖 [Groq AI] Analyzing HTML for {category} to suggest fixes...")
    try:
        client = Groq(api_key=api_key)
        with open(file_path, "r", encoding="utf-8") as f:
            html_snippet = f.read()[:4000] # 분석을 위해 상단 일부만 추출

        prompt = f"""
        당신은 전문 웹 스크래퍼 개발자입니다. 아래 HTML 소스에서 {category} 순위 정보(제목, 가수 또는 수치)가 들어있는 태그의 새로운 CSS Selector를 찾아주세요. 
        만약 구조가 완전히 바뀌었다면 바뀐 구조에 대해 설명하고 Python Playwright용 selector를 제안하세요.
        HTML: {html_snippet}
        """
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
        )
        print(f"📝 [AI Suggestion]:\n{chat_completion.choices[0].message.content}")
        os.remove(file_path) # 분석 후 파일 삭제
    except Exception as e:
        print(f"⚠️ AI Analysis Failed: {e}")

async def run_automation():
    db = DatabaseManager()
    run_count = get_run_count()
    
    # Groq 키 로테이션 및 차트 타이밍 (1번, 5번 키)
    key_idx = (run_count % 8) + 1
    api_key = os.environ.get(f"GROQ_API_KEY{key_idx}")
    is_chart_time = key_idx in [1, 5]

    print(f"🚀 [Cycle {run_count}] Key #{key_idx} | Chart Time: {is_chart_time}")

    if is_chart_time:
        engine = ChartEngine()
        categories = ["k-pop", "k-drama", "k-movie", "k-entertain"]
        
        for cat in categories:
            chart_json = await engine.get_top10_chart(cat, run_count)
            data = json.loads(chart_json).get("top10", [])
            
            if data and len(data) >= 5:
                db_data = [{"category": cat, "rank": i['rank'], "title": i['title'], "meta_info": i['info'], "score": 100} for i in data]
                db.save_rankings(db_data)
                print(f"✅ {cat} Saved successfully.")
            else:
                # 메인 + 백업 모두 실패 시 자가 수정 로직 가동
                print(f"🚨 {cat} all sources failed. Triggering Groq AI Analysis...")
                analyze_with_groq(api_key, cat)

    # Phase 2: 기사 작성은 매시간 실행 (구조 대기)
    print(f"📝 News generation phase with Key #{key_idx}...")

    update_run_count(run_count)

if __name__ == "__main__":
    asyncio.run(run_automation())
