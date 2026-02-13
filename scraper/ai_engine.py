import os
import json
import re
import requests
from groq import Groq

# =========================================================
# 1. 모델 선택 로직 (Guard 모델 제외 및 하드코딩 추가)
# =========================================================

def get_groq_text_models():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return []
    try:
        client = Groq(api_key=api_key)
        all_models = client.models.list()
        valid_models = []
        for m in all_models.data:
            mid = m.id.lower()
            # [수정] guard, audio, vision, whisper 등 대화용 아닌거 다 뺌
            if any(x in mid for x in ['vision', 'whisper', 'audio', 'guard', 'safe']): continue
            valid_models.append(m.id)
        # 8b, 70b 등 큰 모델 우선
        valid_models.sort(key=lambda x: '70b' in x, reverse=True) 
        return valid_models
    except: return []

def get_openrouter_text_models():
    # [수정] API 호출 실패 대비해서, 확실한 무료/저가 모델 하드코딩 리스트 준비
    fallback_models = [
        "google/gemini-2.0-flash-lite-preview-02-05:free",
        "google/gemini-2.0-flash-exp:free",
        "mistralai/mistral-7b-instruct:free",
        "meta-llama/llama-3-8b-instruct:free",
        "microsoft/phi-3-medium-128k-instruct:free"
    ]
    
    try:
        res = requests.get("https://openrouter.ai/api/v1/models", timeout=3)
        if res.status_code == 200:
            data = res.json().get('data', [])
            valid_models = []
            for m in data:
                mid = m['id'].lower()
                # 무료이면서 채팅 가능한거
                if ':free' in mid and not any(x in mid for x in ['vision', 'image', '3d', 'diffusion']):
                    valid_models.append(m['id'])
            
            if valid_models:
                return valid_models
    except:
        pass
    
    # API 실패시 하드코딩 리스트 반환 (무조건 실행되게)
    return fallback_models

# =========================================================
# 2. AI 답변 정제기
# =========================================================

def clean_ai_response(text):
    if not text: return ""
    cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()
    if "```" in cleaned:
        parts = cleaned.split("```")
        for part in parts:
            if "{" in part or "[" in part:
                cleaned = part.replace("json", "").strip()
                break
    return cleaned

def ask_ai_master(system_prompt, user_input):
    raw_response = ""
    
    # 1. Groq 시도
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        models = get_groq_text_models()
        client = Groq(api_key=groq_key)
        for model_id in models:
            try:
                # print(f"   [DEBUG] Groq 시도: {model_id}")
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                    temperature=0.3
                )
                raw_response = completion.choices[0].message.content.strip()
                if raw_response: break
            except Exception as e:
                # Rate Limit(429)이면 그냥 조용히 다음 모델/오픈라우터로 넘어감
                continue

    # 2. OpenRouter 시도 (Groq 실패 시 무조건 실행)
    if not raw_response:
        or_key = os.getenv("OPENROUTER_API_KEY")
        if or_key:
            # print("   [DEBUG] 🔄 Groq 실패 -> OpenRouter 전환 시도")
            models = get_openrouter_text_models()
            
            for model_id in models:
                try:
                    # print(f"   [DEBUG] OpenRouter 시도: {model_id}")
                    res = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {or_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://k-enter-trend.com" 
                        },
                        json={
                            "model": model_id,
                            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                            "temperature": 0.3
                        },
                        timeout=30 # 타임아웃 넉넉하게
                    )
                    
                    if res.status_code == 200:
                        raw_response = res.json()['choices'][0]['message']['content']
                        if raw_response: break
                    # else:
                        # print(f"   [DEBUG] OpenRouter 응답 실패: {res.status_code}")
                        
                except Exception as e:
                    continue
        else:
            print("   [DEBUG] ⚠️ OPENROUTER_API_KEY가 없습니다.")

    return clean_ai_response(raw_response)

# =========================================================
# 3. JSON 파서
# =========================================================

def parse_json_result(text):
    if not text: return []
    text = clean_ai_response(text)
    try: return json.loads(text)
    except: pass
    try:
        match = re.search(r'(\[.*\]|\{.*\})', text, re.DOTALL)
        if match: return json.loads(match.group(0))
    except: pass
    return []

# =========================================================
# 4. 키워드 추출
# =========================================================

def extract_top_entities(category, news_text_data):
    system_prompt = f"""
    You are a K-Content Trend Analyst for '{category}'. 
    
    [TASK]
    1. Analyze the provided news titles and summaries.
    2. Extract the most frequently mentioned keywords.
    3. CLASSIFY each keyword into 'person' or 'content'.
    
    [CLASSIFICATION RULES]
    - 'person': Groups (BTS), Singers, Actors, Entertainers.
    - 'content': Song Titles, Drama Titles, Movie Titles, Shows, Places.
    
    [OUTPUT FORMAT]
    - JSON LIST of objects. Example: [{{"keyword": "BTS", "type": "person"}}]
    - Max 40 items.
    """
    
    user_input = news_text_data[:12000] # 길이 제한 (토큰 절약)
    raw_result = ask_ai_master(system_prompt, user_input)
    parsed = parse_json_result(raw_result)
    
    if isinstance(parsed, list):
        seen = set()
        unique_list = []
        for item in parsed:
            if isinstance(item, dict) and 'keyword' in item:
                if item['keyword'] not in seen:
                    seen.add(item['keyword'])
                    unique_list.append(item)
        return unique_list
    return []

# =========================================================
# 5. 브리핑
# =========================================================

def synthesize_briefing(keyword, news_contents):
    system_prompt = f"""
    You are a Professional News Editor. Topic: {keyword}
    [TASK] Write a comprehensive news briefing in ENGLISH (5-20 lines).
    [CRITICAL] NO <think> tags. If data is invalid, output "INVALID_DATA".
    """
    
    user_input = "\n\n".join(news_contents)[:6000] 
    result = ask_ai_master(system_prompt, user_input)
    
    if not result or "INVALID_DATA" in result or len(result) < 50:
        return None
        
    return result
