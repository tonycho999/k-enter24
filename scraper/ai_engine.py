import os
import json
import time
import requests
from groq import Groq
from scraper.config import CATEGORIES, EXCLUDE_KEYWORDS

# ---------------------------------------------------------
# 1. 각 서비스별 모델 조회 및 클라이언트 설정
# ---------------------------------------------------------

def get_groq_models():
    """Groq에서 사용 가능한 텍스트 모델 목록 조회 (최신순)"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key: return []
    try:
        client = Groq(api_key=api_key)
        all_models = client.models.list()
        # 텍스트 전용 모델 필터링 및 정렬
        models = [m.id for m in all_models.data if any(x in m.id for x in ['llama', 'mixtral', 'gemma'])]
        models.sort(reverse=True)
        return models
    except: return []

def get_openrouter_models():
    """OpenRouter에서 사용 가능한 무료/주요 모델 목록 조회 (최신순)"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key: return []
    try:
        # 무료 모델 및 주요 모델 위주로 가져오기
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code == 200:
            data = response.json().get('data', [])
            # llama, mistral 등 성능 좋은 모델 위주 필터링
            models = [m['id'] for m in data if any(x in m['id'] for x in ['llama-3.1', 'llama-3.3', 'mistral-7b'])]
            models.sort(reverse=True)
            return models
    except: pass
    return ["meta-llama/llama-3.1-8b-instruct:free", "mistralai/mistral-7b-instruct:free"]

def get_hf_models():
    """Hugging Face에서 신뢰도 높은 추론 모델 목록 (정적 리스트 최신순)"""
    # HF는 서버리스 API 특성상 모든 모델 조회가 비효율적이므로 검증된 최신 모델 리스트를 사용합니다.
    return [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "meta-llama/Llama-3.2-3B-Instruct",
        "microsoft/Phi-3-mini-4k-instruct",
        "google/gemma-2-2b-it"
    ]

# ---------------------------------------------------------
# 2. 마스터 AI 실행 엔진 (3단계 계단식 로직)
# ---------------------------------------------------------

def ask_ai_master(system_prompt, user_input):
    """
    [규칙 준수]
    1. Groq (모든 모델 최신순) -> 실패 시
    2. OpenRouter (모든 모델 최신순) -> 실패 시
    3. Hugging Face (순차 시도)
    """
    
    # --- 1단계: Groq 시도 ---
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        groq_models = get_groq_models()
        client = Groq(api_key=groq_api_key)
        for model_id in groq_models:
            try:
                completion = client.chat.completions.create(
                    model=model_id,
                    messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                    temperature=0.3
                )
                return completion.choices[0].message.content.strip()
            except: continue

    # --- 2단계: OpenRouter 시도 ---
    or_api_key = os.getenv("OPENROUTER_API_KEY")
    if or_api_key:
        print("      🚨 Groq 실패 -> OpenRouter 백업 가동")
        or_models = get_openrouter_models()
        for model_id in or_models:
            try:
                res = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {or_api_key}"},
                    json={
                        "model": model_id,
                        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_input}],
                        "temperature": 0.3
                    },
                    timeout=20
                )
                if res.status_code == 200:
                    return res.json()['choices'][0]['message']['content']
            except: continue

    # --- 3단계: Hugging Face 시도 ---
    hf_token = os.getenv("HF_API_TOKEN")
    if hf_token:
        print("      💀 OpenRouter 실패 -> Hugging Face 최후의 보루 가동")
        hf_models = get_hf_models()
        for model_id in hf_models:
            try:
                url = f"https://api-inference.huggingface.co/models/{model_id}"
                headers = {"Authorization": f"Bearer {hf_token}"}
                # HF 특화 프롬프트 형식
                payload = {"inputs": f"<s>[INST] {system_prompt}\n\n{user_input} [/INST]"}
                res = requests.post(url, headers=headers, json=payload, timeout=20)
                
                if res.status_code == 200:
                    data = res.json()
                    return data[0]['generated_text'] if isinstance(data, list) else data.get('generated_text', "")
                elif res.status_code == 503: # 모델 로딩 중
                    time.sleep(5)
            except: continue

    return ""

# ---------------------------------------------------------
# 3. 실무 함수 (분류 및 요약)
# ---------------------------------------------------------

def ai_filter_and_rank_keywords(raw_keywords):
    """구글 트렌드 키워드 필터링"""
    system_prompt = f"""
    You are the Chief Editor of 'K-Enter24'. 
    Filter keywords for: {json.dumps(CATEGORIES, indent=2)}.
    Exclude: {', '.join(EXCLUDE_KEYWORDS)}.
    Return JSON only: {{"k-pop": ["keyword1", ...], ...}}
    """
    
    raw_result = ask_ai_master(system_prompt, json.dumps(raw_keywords, ensure_ascii=False))
    return parse_json_result(raw_result)

def ai_category_editor(category, news_list):
    """뉴스 기사 요약 및 평점 부여 (3단계 구조화)"""
    system_prompt = f"""
    You are an expert K-Content News Editor for '{category}'.
    [STRUCTURE] 1. Context & Background 2. Core Development 3. Impact & Outlook.
    Score 0.0-10.0. Return JSON array ONLY.
    """
    
    input_data = []
    for i, n in enumerate(news_list):
        input_data.append({
            "index": i, "title": n['title'], "body": n.get('full_content', '')[:1500]
        })

    raw_result = ask_ai_master(system_prompt, json.dumps(input_data, ensure_ascii=False))
    return parse_json_result(raw_result)

def parse_json_result(text):
    """AI 응답에서 JSON만 추출하여 파싱"""
    if not text: return []
    try:
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            text = text.split("```")[1].split("```")[0]
        return json.loads(text.strip())
    except:
        return []
