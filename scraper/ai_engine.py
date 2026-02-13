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
    [완전 동적 방식]
    API에서 받아온 모델들을 버전이 높은 순서대로 자동 정렬하여 반환
    (예: llama-3.3 -> llama-3.1 -> ... 순서)
    """
    try:
        all_models = client.models.list()
        # 텍스트 생성용 모델만 필터링 (Whisper, Vision 제외)
        text_models = [m.id for m in all_models.data if "whisper" not in m.id and "vision" not in m.id]
        
        # 문자열 역순 정렬 (3.3이 3.1보다 위로 오도록)
        text_models.sort(reverse=True)
        return text_models
    except Exception as e:
        print(f"      ⚠️ 모델 목록 조회 실패: {e}")
        return ["llama-3.3-70b-versatile", "llama-3.1-70b-versatile"]

def ai_category_editor(category, news_list):
    client = get_groq_client()
    if not client: return []
    
    # 1. 사용 가능한 모델 동적 조회
    dynamic_models = get_latest_models(client)
    
    # 2. 프롬프트: 요약 길이(40~50%) 및 평점 기준 명시
    system_prompt = f"""
    You are an expert K-Content News Editor for '{category}'.
    
    [TASK]
    1. Analyze the provided news articles.
    2. **Summary Requirement:** The summary length must be **40% to 50% of the original text length**. 
       - Keep enough details to understand the full context.
       - Do NOT make it too short.
    3. **Scoring:** Assign a score (0.0 - 10.0) based on newsworthiness.
       - Score >= 7.0: Major news (will be archived).
       - Score >= 5.0: Standard news.
       - Score < 5.0: Minor/Spam.
    
    [OUTPUT FORMAT]
    Return a JSON array ONLY:
    [
        {{
            "original_index": (int) index,
            "eng_title": "Translated Title",
            "summary": "Detailed summary (40-50% length)",
            "score": (float) 0.0-10.0
        }}
    ]
    """

    # 3. 입력 데이터 준비 (토큰 절약 위해 본문 500자 제한)
    input_data = [
        {"index": i, "title": n['title'], "body": n.get('originallink', n['link'])[:500]} 
        for i, n in enumerate(news_list)
    ]

    # 4. 모델 순차 시도
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
            # print(f"      ⚠️ {model_id} 실패. 다음 모델 시도.")
            continue
            
    print("      ❌ 모든 Groq 모델 시도 실패.")
    return []
