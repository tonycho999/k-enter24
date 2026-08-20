# scripts/run_next.py
import os
import subprocess
from datetime import datetime

# 실행할 카테고리 스크립트 5개 목록
SCRIPTS = [
    "auto_pop.py",
    "auto_drama.py",
    "auto_movie.py",
    "auto_entertainment.py",
    "auto_culture.py"
]

def main():
    # 🚀 [핵심] 현재 시간(UTC)을 구합니다.
    current_hour = datetime.utcnow().hour
    
    # 5개의 스크립트가 돌아가며 실행되도록 시간을 5로 나눈 나머지(0,1,2,3,4)를 구합니다.
    target_index = current_hour % 5
    
    next_script = SCRIPTS[target_index]
    
    print("======================================")
    print(f"⏰ 현재 시간(UTC): {current_hour}시")
    print(f"👉 이번 턴 타겟 인덱스: {target_index}")
    print(f"🎯 실행할 스크립트: {next_script}")
    print("======================================")
    
    script_path = os.path.join(os.path.dirname(__file__), next_script)
    
    # 해당 스크립트를 딱 1번만 실행합니다.
    result = subprocess.run(["python", script_path])
    
    # 결과가 어떻든(성공이든, 뉴스가 없어서 실패로 종료하든) 여기서 턴을 마칩니다.
    if result.returncode != 0:
        print(f"\n❌ [{next_script}] 실행 중 에러 또는 조건 미달(뉴스 없음 등)로 종료되었습니다.")
        print("⏭️ 상관없이 다음 시간에는 다음 카테고리 봇이 실행됩니다.")
        # Github Action이 자체적으로 실패(빨간불) 처리되지 않도록 0으로 정상 종료시킵니다.
        # (이렇게 해야 깃허브에서 에러 메일이 날아오지 않습니다.)
        exit(0) 
    else:
        print(f"\n✅ [{next_script}] 기사 발행 완벽하게 성공!")

if __name__ == "__main__":
    main()
