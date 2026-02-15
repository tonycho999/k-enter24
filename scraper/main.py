import sys
import time
import os
import random  # 랜덤 시간 생성을 위해 추가
from datetime import datetime
import processor

def main():
    print(f"🤖 GitHub Action Scraper Started at {datetime.now()} (UTC)")
    
    # 1. GitHub Actions에서 실행 횟수(RUN_COUNT)를 가져옵니다.
    try:
        run_count = int(os.getenv("RUN_COUNT", "0"))
    except (ValueError, TypeError):
        run_count = 0

    # 2. 카테고리 설정
    categories = ["K-Pop", "K-Drama", "K-Movie", "K-Entertain", "K-Culture"]
    results = {"success": 0, "failed": 0}

    print(f"📊 Current Cycle Index: {run_count % 6} (Total Runs: {run_count})")

    for idx, category in enumerate(categories):
        try:
            print(f"\n==================================================")
            print(f"🏃 Starting Category: {category}")
            
            # [핵심] 해당 카테고리 프로세스 실행
            processor.run_category_process(category, run_count)
            
            print(f"✅ Finished: {category}")
            results["success"] += 1
            
            # [전문가 팁] 마지막 카테고리가 아닐 때만 랜덤 휴식 실행
            if idx < len(categories) - 1:
                # 60,000ms ~ 180,000ms 사이의 랜덤한 밀리초 생성
                wait_ms = random.randint(60000, 180000)
                wait_sec = wait_ms / 1000.0
                
                print(f"💤 [API 할당량 보호] 다음 카테고리 시작 전 랜덤 휴식...")
                print(f"💤 대기 시간: {wait_ms}ms ({wait_sec:.2f}초)")
                
                time.sleep(wait_sec)
            
        except Exception as e:
            print(f"🚨 Error in {category}: {e}")
            results["failed"] += 1
            continue

    print(f"\n" + "="*50)
    print(f"🎉 Batch Job Completed.")
    print(f"📊 Success: {results['success']}, Failed: {results['failed']}")
    print(f"="*50)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
