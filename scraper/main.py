# scraper/main.py
import sys
import time
from datetime import datetime
import config
import processor

def main():
    print(f"🤖 GitHub Action Scraper Started at {datetime.now()} (UTC)")
    
    # [수정됨] 시간 계산 없이 모든 카테고리를 순서대로 다 실행
    results = {"success": 0, "failed": 0}

    for category in config.CATEGORY_ORDER:
        try:
            print(f"\n==================================================")
            print(f"🏃 Starting Category: {category}")
            
            # 로직 실행
            processor.run_category_process(category)
            
            print(f"✅ Finished: {category}")
            results["success"] += 1
            
            # 카테고리 사이에 5초 휴식 (API 과부하 방지)
            time.sleep(5)
            
        except Exception as e:
            print(f"🚨 Error in {category}: {e}")
            results["failed"] += 1
            # 에러가 나도 다음 카테고리는 계속 진행 (continue)
            continue

    print(f"\n🎉 Batch Job Completed. Success: {results['success']}, Failed: {results['failed']}")
    
    # 하나라도 실패했으면 깃허브에 경고 표시 (선택사항, 지금은 그냥 성공 처리)
    sys.exit(0)

if __name__ == "__main__":
    main()
