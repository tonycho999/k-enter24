# scraper/config.py

# 실행 순서
CATEGORY_ORDER = ["K-Pop", "K-Drama", "K-Movie", "K-Entertain", "K-Culture"]

# 카테고리별 초기 탐색 키워드 (네이버 검색용)
SEARCH_KEYWORDS = {
    # [K-Pop] 가수 이름 검색을 위해선 일단 차트나 음악방송 뉴스를 긁어야 함
    "K-Pop": "멜론차트 빌보드 뮤직뱅크 인기가요 컴백 쇼케이스 신곡발표",
    
    # [K-Drama] 배우 검색을 위해선 드라마 캐스팅, 시청률 기사를 긁어야 함
    "K-Drama": "드라마 시청률 넷플릭스 티빙 방영예정 제작발표회 주연 확정",
    
    # [K-Movie] 배우 검색을 위해선 개봉작, 무대인사 기사를 긁어야 함
    "K-Movie": "박스오피스 개봉영화 시사회 무대인사 크랭크인 천만관객",
    
    # [K-Entertain] 출연진 검색을 위해선 예능 시청률, 게스트 기사를 긁어야 함
    "K-Entertain": "예능 시청률 나혼자산다 유퀴즈 런닝맨 전지적참견시점 출연",
    
    # [K-Culture] 아이돌/연예인 관련 단어 싹 빼고 '장소/음식'만 남김
    "K-Culture": "한국관광공사 추천 여행지 서울 맛집 미슐랭 가이드 경복궁 야간개장 한식 문화유산 축제"
}

# DB 유지 개수
MAX_ITEMS_PER_CATEGORY = 30
