# scripts/AI.py
import os
import json
import re
from groq import Groq
import google.generativeai as genai

def get_best_groq_models(client):
    models = client.models.list().data
    valid_models = []
    
    for m in models:
        mid = m.id.lower()
        # 🚀 [추가된 부분] 뼈대 있는 1티어 모델(Llama, Mixtral, Gemma)만 허용!
        if 'llama' in mid or 'mixtral' in mid or 'gemma' in mid:
            if 'whisper' not in mid and 'vision' not in mid and 'guard' not in mid:
                valid_models.append(m)
                
    def sort_key(m):
        created_time = getattr(m, 'created', 0)
        param_size = 0
        import re
        match_multi = re.search(r'(\d+)x(\d+)b', m.id.lower())
        if match_multi:
            param_size = int(match_multi.group(1)) * int(match_multi.group(2))
        else:
            match_single = re.search(r'(\d+)b', m.id.lower())
            if match_single:
                param_size = int(match_single.group(1))
        return (created_time, param_size)
        
    valid_models.sort(key=sort_key, reverse=True)
    return [m.id for m in valid_models]
        
    # 출시일과 파라미터 크기 기준으로 내림차순(가장 좋고 최신인 것부터) 정렬
    valid_models.sort(key=sort_key, reverse=True)
    return [m.id for m in valid_models]

def get_cheapest_gemini_model():
    """
    브랜드 버전 하드코딩 X:
    구글에서 현재 서비스 중인 텍스트 모델 리스트를 실시간으로 가져와서,
    가장 저렴한 라인업인 'flash' 키워드가 들어간 최신 모델을 자동 선택합니다.
    """
    # 1. 실시간 사용 가능한 전체 제미나이 모델 리스트 가져오기
    models = genai.list_models()
    text_models = [m.name for m in models if 'generateContent' in m.supported_generation_methods and 'vision' not in m.name.lower()]
    
    # 2. 구글의 저가형 라인업 공식 명칭인 'flash'가 포함된 모델만 추출
    flash_models = [name for name in text_models if 'flash' in name.lower()]
    
    if flash_models:
        # 이름순으로 역순 정렬하면 자연스럽게 최신 버전(예: flash-2.0 > flash-1.5)이 맨 위로 올라옵니다.
        flash_models.sort(reverse=True)
        return flash_models[0]
    
    # flash가 아예 없어지면 그냥 사용 가능한 첫 번째 텍스트 모델 반환
    return text_models[0] if text_models else "gemini-pro"

def get_ai_response(system_prompt, user_content):
    # 길이 제한 규칙 강력 적용 (500 ~ 1500자)
    strict_length_prompt = system_prompt + "\n\n[CRITICAL RULE]: The 'content' strictly MUST be between 500 and 1500 characters in length. Do not make it too short."

    # 1. 등록된 Groq 키 1~8번 모두 불러오기
    groq_keys = [os.environ.get(f"GROQ_API_KEY{i}") for i in range(1, 9)]
    groq_keys = [k for k in groq_keys if k]
    gemini_key = os.environ.get("GEMINI_API_KEY")

    # 2. 폭포수 라우팅: Groq 키 순회
    for key in groq_keys:
        try:
            client = Groq(api_key=key)
            # 실시간으로 API를 찔러서 가장 좋은 모델 리스트를 받아옴!
            best_groq_models = get_best_groq_models(client)
            
            for model in best_groq_models:
                try:
                    print(f"🤖 시도 중: Groq ({model}) - Key: ...{key[-4:]}")
                    response = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": strict_length_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.7,
                        max_tokens=3000
                    )
                    return json.loads(response.choices[0].message.content)
                except Exception as e:
                    print(f"⚠️ Groq 모델({model}) 실패: {e}")
                    continue 
        except Exception as e:
            print(f"⚠️ Groq 키 연결 실패: {e}")
            continue

    # 3. 최후의 보루: 구글 Gemini 호출
    if gemini_key:
        try:
            genai.configure(api_key=gemini_key)
            # 실시간으로 가장 저렴한 제미나이 모델을 찾아옴!
            cheapest_gemini = get_cheapest_gemini_model()
            print(f"🆘 Groq 전체 한도 초과. 가장 저렴한 {cheapest_gemini} 모델로 전환합니다...")
            
            # 모델 이름에서 'models/' 접두사가 있으면 제거
            model_name_clean = cheapest_gemini.replace('models/', '')
            model = genai.GenerativeModel(model_name_clean, generation_config={"response_mime_type": "application/json"})
            full_prompt = f"{strict_length_prompt}\n\nUser Input:\n{user_content}"
            response = model.generate_content(full_prompt)
            return json.loads(response.text)
        except Exception as e:
            print(f"❌ Gemini마저 실패했습니다: {e}")
    
    raise Exception("모든 AI API 호출에 실패했습니다.")

# scripts/AI.py 파일 맨 아래에 추가

def verify_category_fit(category_name, entity, article_contents):
    """
    AI에게 이 기사 내용이 해당 카테고리의 '본질'에 맞는지 검증받습니다.
    """
    # 카테고리별 엄격한 판단 기준
    criteria = {
        "K-POP": "음악, 앨범 발매, 콘서트, 무대, 차트 성적, 음악 방송 등 순수 음악 활동",
        "K-DRAMA": "드라마 캐스팅, 방영 소식, 시청률, 줄거리, 작품 속 연기",
        "K-MOVIE": "영화 개봉, 박스오피스, 영화제, 무대인사, 영화 촬영",
        "K-ENTERTAINMENT": "예능 프로그램 출연, 관찰 예능, 토크쇼, 유튜버/BJ 방송 활동",
        "K-CULTURE": "뷰티, 패션, 식품, 팝업스토어, 여행지, 라이프스타일 트렌드"
    }
    
    criterion = criteria.get(category_name, "해당 카테고리")
    
    system_prompt = f"""너는 K-Culture 매거진의 깐깐한 편집장이야. 
    기자가 [{entity}]에 대한 기사를 [{category_name}] 카테고리에 올리려고 해.
    [{category_name}] 카테고리의 올바른 기준은 오직 [{criterion}]와 관련된 이슈여야 해.
    
    만약 기사 내용이 이 기준과 안 맞고, 단순히 예능 출연, 가십, 열애설, 타 분야 활동(가수가 연기함) 등이라면 가차 없이 반려(False)해야 해.
    기사 요약을 읽어보고, 이 기사가 [{category_name}]에 완벽하게 부합하면 "true", 조금이라도 성격이 다르면 "false"로만 대답해.
    반드시 JSON 형식으로 답변: {{"is_valid": true 또는 false}}
    """
    
    try:
        response_data = get_ai_response(system_prompt, article_contents)
        return response_data.get('is_valid', False)
    except Exception as e:
        print(f"카테고리 검증 중 에러: {e}")
        return False # 에러 나면 안전하게 버림
