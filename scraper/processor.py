import gemini_api
import database
import naver_api
import re
import json
from datetime import datetime

# 카테고리 6단계 질문 (요청하신 대로 수정 없이 유지)
PROMPT_VERSIONS = {
    "K-Pop": [
        "최근 24시간 내 언급량이 가장 압도적인 K-pop 가수(그룹)를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘.",
        "현재 차트 역주행이나 급상승으로 화제인 K-pop 가수를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘.",
        "비하인드 뉴스나 독점 인터뷰로 화제인 K-pop 가수 리스트를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘.",
        "글로벌 팬덤 및 SNS 반응이 폭발적인 K-pop 가수를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘.",
        "업계 내 뜨거운 논쟁이나 반전 이슈의 주인공인 K-pop 가수를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘.",
        "컴백 예고나 대형 프로젝트를 시작한 K-pop 가수를 선정해 심층 기사 1개를 쓰고 Top 10 곡 순위를 알려줘."
    ],
    "K-Drama": [
        "화제성 1위 드라마의 주연 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘.",
        "드라마 한 편으로 인생이 바뀐 라이징 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘.",
        "촬영 현장 비화나 캐스팅 소식으로 화제인 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘.",
        "글로벌 OTT 차트를 휩쓴 드라마의 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘.",
        "결말 논란이나 인터뷰로 화제인 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘.",
        "차기작이 기대되는 '믿보배' 배우를 선정해 심층 기사 1개를 쓰고 드라마 순위 1~10위를 알려줘."
    ],
    "K-Movie": [
        "박스오피스 1위 영화의 핵심 배우나 감독을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘.",
        "독립영화나 저예산 영화에서 발굴된 천재 영화인을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘.",
        "독특한 연출이나 제작 비화로 화제인 영화인을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘.",
        "해외 시상식 수상이나 해외 진출로 화제인 영화인을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘.",
        "영화계 이슈나 논쟁의 중심인 영화인을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘.",
        "대작 개봉을 앞두고 홍보 중인 핫한 영화인을 선정해 심층 기사 1개를 쓰고 영화 순위 1~10위를 알려줘."
    ],
    "K-Entertain": [
        "시청률 1위 예능의 메인 출연진을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘.",
        "유튜브나 OTT 예능에서 제2의 전성기를 맞은 예능인을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘.",
        "출연진 간의 케미로 화제인 예능인을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘.",
        "해외 팬덤이 강력한 글로벌 예능인을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘.",
        "태도 논란이나 섭외 이슈로 화제인 예능인을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘.",
        "새 시즌 복귀나 컴백으로 화제인 예능인을 선정해 심층 기사 1개를 쓰고 예능 순위 1~10위를 알려줘."
    ],
    "K-Culture": [
        "가장 핫한 전시나 팝업스토어를 기획한 문화인을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘.",
        "MZ세대 트렌드를 선도하는 예술가나 인물을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘.",
        "전통을 힙하게 재해석한 장인이나 인물을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘.",
        "K-푸드나 한국 문화를 세계에 알린 인물을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘.",
        "공익적 문화 활동이나 지역 살리기로 화제인 인물을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘.",
        "랜드마크 건립이나 대형 축제를 이끄는 인물을 선정해 심층 기사 1개를 쓰고 문화 핫픽 1~10위를 알려줘."
    ]
}

def parse_rankings(raw_rankings_text):
    """
    텍스트 형태의 랭킹을 리스트 객체로 변환
    예: "1. Song (곡명) - 95" 형태를 파싱
    """
    parsed = []
    lines = raw_rankings_text.strip().split('\n')
    for i, line in enumerate(lines[:10]):
        try:
            # 주석 제거 및 기본 클리닝
            line = re.sub(r'\[\d+\]', '', line).strip()
            # 정규표현식으로 제목 추출 시도 (숫자. 제목 형태)
            title_match = re.search(r'\d+[\.\)\s]+(.*)', line)
            title = title_match.group(1) if title_match else line
            
            parsed.append({
                "rank": i + 1,
                "title_en": title,
                "title_kr": title, # 텍스트 방식에서는 우선 동일하게 처리
                "score": 100 - (i * 2)
            })
        except:
            continue
    return parsed

def run_category_process(category, run_count):
    print(f"\n🚀 [Autonomous Mode] {category} (Run #{run_count})")

    v_idx = run_count % 6
    task = PROMPT_VERSIONS[category][v_idx]

    # [프로그래머의 설계] JSON 대신 태그 방식을 AI에게 요구
    final_prompt = f"""
    실시간 뉴스 검색을 사용하여 다음 과제를 수행하라: {task}
    
    [작성 가이드]
    1. 인물/그룹을 선정하고 심층적인 영문 기사를 작성하세요.
    2. 모든 결과물은 아래의 태그 형식을 반드시 사용하여 구분하세요.
    3. 구글 검색 출처 번호(예: [1])는 절대 적지 마세요.
    4. 기사 제목과 본문은 반드시 영어(English)로 작성하세요.

    [형식]
    ##TARGET_KR## 인물명(한국어)
    ##TARGET_EN## Person Name(English)
    ##HEADLINE## English Article Headline
    ##CONTENT## English Article Content (Deep analysis)
    ##RANKINGS##
    1. Title 1 (제목 1)
    2. Title 2 (제목 2)
    ... 10위까지 작성
    """

    # AI 호출 (gemini_api에서 딕셔너리로 반환함)
    data = gemini_api.ask_gemini_with_search(final_prompt)

    if not data or 'headline' not in data or 'content' not in data:
        print(f"❌ {category} 데이터 추출 실패: 필수 태그가 누락되었습니다.")
        return

    # 1. 랭킹 데이터 처리
    raw_rankings = data.get('raw_rankings', '')
    clean_rankings = parse_rankings(raw_rankings)
    if clean_rankings:
        database.save_rankings_to_db(clean_rankings)

    # 2. 이미지 수집
    target_kr = data.get("target_kr", "K-Pop Star").strip()
    target_en = data.get("target_en", "K-Pop Star").strip()
    print(f"📸 '{target_kr}' 관련 최적 이미지 수집 중...")
    final_image = naver_api.get_target_image(target_kr)

    # 3. 기사 저장
    news_items = [{
        "category": category,
        "keyword": target_en,
        "title": data.get("headline", "Breaking News"),
        "summary": data.get("content", ""),
        "image_url": final_image,
        "score": 100,
        "created_at": datetime.now().isoformat(),
        "likes": 0
    }]
    
    database.save_news_to_live(news_items)
    print(f"🎉 성공: '{target_en}' 관련 기사 및 랭킹 발행 완료.")
