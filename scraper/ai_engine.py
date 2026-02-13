import os
import json
from groq import Groq

def get_groq_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️ GROQ_API_KEY가 없습니다.")
        return None
    return Groq(api_key=api_key)

def get_latest_models(client):
    """
    [완전 동적 방식] - 수정하지 않음
    API에서 받아온 모델들을 버전이 높은 순서대로 자동 정렬하여 반환
    """
    try:
        all_models = client.models.list()
        # 텍스트 생성용 모델만 필터링
        text_models = [m.id for m in all_models.data if "whisper" not in m.id and "vision" not in m.id]
        
        # 최신 모델이 먼저 오도록 역순 정렬
        text_models.sort(reverse=True)
        return text_models
    except Exception as e:
        print(f"      ⚠️ 모델 목록 조회 실패: {e}")
        return ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"]

def ai_category_editor(category, news_list):
    client = get_groq_client()
    if not client: return []
    
    # 1. 사용 가능한 모델 동적 조회 (기존 로직 유지)
    dynamic_models = get_latest_models(client)
    
    # 2. [강화된 프롬프트] 3단계 구조화 요약 + 50% 분량 확보
    system_prompt = f"""
    You are an expert K-Content News Editor for '{category}'.
    
    [GOAL]
    Provide a rich, detailed summary of the provided text. 
    The summary length must be approximately **40% to 50%** of the original text.
    Do NOT summarize too briefly. Use the full context provided.

    [3-STAGE SUMMARY STRUCTURE (MANDATORY)]
    Every summary MUST strictly follow this structure:
    
    1. **Context & Background**: 
       - Explain WHY this happened.
       - Provide historical context or the situation before this event.
       
    2. **Core Development**: 
       - Explain WHAT happened in detail.
       - Include specific facts (Who, When, What, How) from the text.
       
    3. **Impact & Outlook**: 
       - Explain WHAT comes next.
       - Include industry impact, fan reactions, or future schedules.

    [SCORING CRITERIA]
    - Score (0.0 - 10.0) based on newsworthiness.
    - Score >= 7.0: Major breaking news or high-quality deep dives (Will be Archived).
    - Score < 5.0: Minor updates or spam (Will be Deleted).

    [OUTPUT FORMAT]
    Return a JSON array ONLY:
    [
        {{
            "original_index": (int) index,
            "eng_title": "Attractive Translated Title",
            "summary": "Full 3-stage summary text...",
            "score": (float) 0.0-10.0
        }}
    ]
    """

    # 3. 입력 데이터 준비 (본문 1,500자 전달)
    input_data = []
    for i, n in enumerate(news_list):
        # crawler.get_article_data에서 가져온 'full_content' 사용
        body_text = n.get('full_content', '')
        if not body_text:
             body_text = n.get('originallink', n['link'])
             
        input_data.append({
            "index": i, 
            "title": n['title'], 
            "body": body_text[:1500] # 1,500자까지 AI에게 전달
        })

    # 4. 모델 순차 시도 (기존 로직 유지)
    for model_id in dynamic_models:
        try:
            # print(f"      🤖 시도 중: {model_id}...")
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)}
                ],
                temperature=0.3
            )
            
            result = completion.choices[0].message.content.strip()
            
            # JSON 파싱 전처리
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            return json.loads(result)

        except Exception as e:
            continue
            
    print("      ❌ 모든 Groq 모델 시도 실패.")
    return []
