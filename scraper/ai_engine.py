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
    
    # 1. 사용 가능한 모델 동적 조회 (수정 금지)
    dynamic_models = get_latest_models(client)
    
    # 2. 프롬프트: 요약 길이(40~50%) 및 3단계 구조화 요약 명시
    system_prompt = f"""
    You are an expert K-Content News Editor for '{category}'.
    
    [GOAL]
    Provide a rich and informative summary of the provided text. 
    The summary must be approximately 40-50% of the input text length to ensure depth.

    [3-STAGE SUMMARY STRUCTURE]
    Every summary MUST consist of these three parts:
    1. **Context & Background**: Why did this happen? Provide historical context or previous situations.
    2. **Core Development**: What happened? Detail the main facts (Who, When, What, How) using the provided rich data.
    3. **Impact & Outlook**: What's next? Include industry impact, fan reactions, stock trends, or future schedules.

    [SCORING CRITERIA]
    - Score (0.0 - 10.0) based on newsworthiness.
    - Score >= 7.0: Major breaking news or high-quality deep dives.
    - Score < 5.0: Minor updates or spam.

    [OUTPUT FORMAT]
    Return a JSON array ONLY:
    [
        {{
            "original_index": (int) index,
            "eng_title": "Attractive Translated Title",
            "summary": "Full 3-stage summary (Background / Core / Impact)",
            "score": (float) 0.0-10.0
        }}
    ]
    """

    # 3. 입력 데이터 준비 (본문 1500자 제한)
    # news_list의 각 아이템에 'full_content' 키가 있다고 가정합니다.
    # 만약 'full_content'가 없다면 'link'를 대신 사용하지만, 
    # 스크래퍼에서 본문을 채워주는 것이 중요합니다.
    input_data = []
    for i, n in enumerate(news_list):
        body_text = n.get('full_content', '')
        if not body_text:
             # full_content가 없으면 링크라도 넣어서 뭐라도 하게 함 (예외처리)
             body_text = n.get('originallink', n['link'])
             
        input_data.append({
            "index": i, 
            "title": n['title'], 
            "body": body_text[:1500] # 1,500자까지 전달
        })

    # 4. 모델 순차 시도 (수정 금지)
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
