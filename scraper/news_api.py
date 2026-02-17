import sqlite3
import datetime
import time
import random  # 시뮬레이션을 위한 임의 모듈

class NewsAutomationSystem:
    def __init__(self, db_path="news_history.db"):
        self.db_path = db_path
        self.cool_down_hours = 6  # 쿨타임: 6시간 (이 시간 내에는 다시 작성 안 함)
        self.target_count = 10    # 최종 목표 인원
        self.buffer_count = 30    # 1차 수집 인원
        self._init_db()

    def _init_db(self):
        """작성 기록을 저장할 DB 초기화"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 인물 이름과 마지막 작성 시간을 저장하는 테이블 생성
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_history (
                name TEXT PRIMARY KEY,
                category TEXT,
                last_written_at DATETIME
            )
        ''')
        conn.commit()
        conn.close()

    def get_trending_candidates(self, category):
        """
        [Step 1] 1차 수집: 목표치의 3배수(30명)를 가져옵니다.
        실제 환경에서는 크롤링이나 API를 통해 순위 데이터를 가져와야 합니다.
        여기서는 시뮬레이션을 위해 임의의 데이터를 생성합니다.
        """
        print(f"--- [{category}] 카테고리 후보 30명 수집 중... ---")
        
        # (예시 데이터) 실제로는 여기서 외부 데이터를 긁어옵니다.
        mock_names = [f"{category}_인물_{i}" for i in range(1, self.buffer_count + 1)]
        return mock_names

    def is_in_cooldown(self, name):
        """
        [Step 2] 쿨타임 체크: DB를 확인하여 최근에 작성했는지 검사
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT last_written_at FROM article_history WHERE name = ?', (name,))
        row = cursor.fetchone()
        conn.close()

        if row:
            last_time_str = row[0]
            last_time = datetime.datetime.strptime(last_time_str, "%Y-%m-%d %H:%M:%S")
            time_diff = datetime.datetime.now() - last_time
            
            # 쿨타임(6시간)이 지나지 않았으면 True 반환 (작성 금지)
            if time_diff.total_seconds() < (self.cool_down_hours * 3600):
                print(f"   [Pass] '{name}' - 쿨타임 적용 중 ({int(time_diff.total_seconds()/60)}분 전 작성됨)")
                return True
        
        return False

    def check_naver_news_exists(self, name):
        """
        [Step 3] 네이버 뉴스 유무 확인
        실제 코드에서는 네이버 검색 API나 크롤링 결과를 체크해야 합니다.
        """
        # --- [실제 구현 가이드] ---
        # url = f"https://search.naver.com/search.naver?where=news&query={name}"
        # response = requests.get(url)
        # if "검색결과가 없습니다" in response.text: return False
        # ------------------------
        
        # 시뮬레이션: 랜덤하게 20% 확률로 '뉴스 없음' 상황 연출
        has_news = random.choice([True, True, True, True, False]) 
        
        if not has_news:
            print(f"   [Skip] '{name}' - 네이버 뉴스 기사 없음 (작성 불가)")
        
        return has_news

    def write_article(self, name, category):
        """
        [Step 4] 기사 작성 (LLM 호출 부분)
        """
        print(f"   >> [작성 성공] '{name}'에 대한 기사를 생성했습니다.")
        
        # [Step 5] DB 업데이트 (작성 시간 기록)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 있으면 업데이트(UPDATE), 없으면 삽입(INSERT) - UPSERT 방식
        cursor.execute('''
            INSERT INTO article_history (name, category, last_written_at) 
            VALUES (?, ?, ?) 
            ON CONFLICT(name) DO UPDATE SET last_written_at = ?
        ''', (name, category, now, now))
        
        conn.commit()
        conn.close()

    def run_process(self, category):
        """전체 프로세스 실행"""
        candidates = self.get_trending_candidates(category)
        final_list = []

        print(f"\n[{category}] 필터링 시작...")
        
        for person in candidates:
            # 1. 10명이 꽉 찼으면 중단 (효율성)
            if len(final_list) >= self.target_count:
                break
            
            # 2. 쿨타임 체크 (DB 조회)
            if self.is_in_cooldown(person):
                continue
            
            # 3. 네이버 뉴스 존재 여부 체크
            if not self.check_naver_news_exists(person):
                continue

            # 4. 통과한 인물 리스트에 추가
            final_list.append(person)

        print(f"\n[{category}] 최종 선정된 {len(final_list)}명에 대해 기사 작성을 시작합니다.")
        print("-" * 50)
        
        if not final_list:
            print("작성 가능한 인물이 없습니다. (모두 쿨타임이거나 뉴스 없음)")
            return

        for person in final_list:
            self.write_article(person, category)

# --- 실행 예시 ---
if __name__ == "__main__":
    system = NewsAutomationSystem()
    
    # 1. 축구 선수 카테고리 실행
    system.run_process("축구선수")
    
    print("\n" + "="*50 + "\n")
    
    # 2. (테스트) 바로 다시 실행해보기 -> 쿨타임 작동 확인
    print(">>> 30분 뒤, 시스템 재가동 시뮬레이션 <<<")
    system.run_process("축구선수")
