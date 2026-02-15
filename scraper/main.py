import sys
import time
import os
from datetime import datetime
import processor

def main():
    print(f"🤖 GitHub Action Scraper Started at {datetime.now()} (UTC)")
    
    # 1. GitHub Actions에서 실행 횟수(RUN_COUNT)를 가져옵니다. (없으면 0)
    try:
        run_count = int(os.getenv("RUN_COUNT", "0"))
    except (ValueError, TypeError):
        run_count = 0

    # 2. 고정된 카테고리 순서 (config.py 의존성 제거)
    categories = ["K-Pop", "K-Drama", "K-Movie", "K-Entertain", "K-Culture"]
    
    results = {"success": 0, "failed": 0}

    print(f"📊 Current Cycle Index: {run_count % 6} (Total Runs: {run_count})")

    for category in categories:
        try:
            print(f"\n==================================================")
            print(f"🏃 Starting Category: {category}")
            
            # [핵심] processor에 category와 run_count를 함께 전달합니다.
            processor.run_category_process(category, run_count)
            
            print(f"✅ Finished: {category}")
            results["success"] += 1
            
            # API 과부하 방지 (5초 휴식)
            time.sleep(5)
            
        except Exception as e:
            print(f"🚨 Error in {category}: {e}")
            results["failed"] += 1
            continue

    print(f"\n🎉 Batch Job Completed. Success: {results['success']}, Failed: {results['failed']}")
    
    # 종료
    sys.exit(0)

if __name__ == "__main__":
    main()
