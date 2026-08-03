# scripts/run_next.py
import os
import psycopg2
import subprocess

DATABASE_URL = os.environ.get("DATABASE_URL")

# 카테고리 순서와 그에 맞는 파이썬 파일들
CATEGORIES = ["K-POP", "K-DRAMA", "K-MOVIE", "K-ENTERTAINMENT", "K-CULTURE"]
SCRIPTS = ["auto_pop.py", "auto_drama.py", "auto_movie.py", "auto_entertainment.py", "auto_culture.py"]

def get_last_successful_category():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        # DB에서 가장 마지막으로 성공해서 저장된 글의 카테고리 딱 1개를 가져옵니다.
        cur.execute('SELECT category FROM "Post" ORDER BY "createdAt" DESC LIMIT 1')
        row = cur.fetchone()
        cur.close()
        conn.close()
        if row:
            return row[0]
    except Exception as e:
        print(f"DB 확인 중 에러 발생: {e}")
    return None

def main():
    last_category = get_last_successful_category()
    print(f"📌 마지막으로 성공한 카테고리: {last_category}")
    
    next_index = 0
    # 마지막 카테고리가 목록에 있다면, 그 다음 인덱스를 찾습니다.
    if last_category in CATEGORIES:
        current_index = CATEGORIES.index(last_category)
        # 마지막이 K-CULTURE(4)였다면 다시 K-POP(0)으로 돌아갑니다.
        next_index = (current_index + 1) % len(CATEGORIES)
        
    next_category = CATEGORIES[next_index]
    next_script = SCRIPTS[next_index]
    
    print(f"👉 이번에 실행할 타겟: {next_category} (스크립트: {next_script})")
    
    # 해당 스크립트 딱 1개만 실행합니다.
    script_path = os.path.join(os.path.dirname(__file__), next_script)
    result = subprocess.run(["python", script_path])
    
    if result.returncode != 0:
        print(f"❌ {next_script} 실행 실패! (다음 턴에 다시 재시도합니다)")
        exit(1)
    else:
        print(f"✅ {next_script} 실행 완벽하게 성공!")

if __name__ == "__main__":
    main()
