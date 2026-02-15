import sys
import time
import os
import random 
from datetime import datetime
import processor

def main():
    print(f"🤖 GitHub Action Scraper Started at {datetime.now()} (UTC)")
    
    try:
        run_count = int(os.getenv("RUN_COUNT", "0"))
    except (ValueError, TypeError):
        run_count = 0

    # 2. 카테고리 설정
    categories = ["K-Pop", "K-Drama", "K-Movie", "K-Entertain", "K-Culture"]
    results = {"success": 0, "failed": 0}

    print(f"📊 Current Cycle Index: {run_count % 6} (Total Runs: {run_count})")
    print(f"💡 Perplexity Paid Tier Mode: Optimized waiting times.")

    for idx, category in enumerate(categories):
        try:
            print(f"\n" + "="*50)
            # ✅ [보완 1] 현재 처리 중인 카테고리를 명확히 출력하여 추적성을 높입니다.
            print(f"🏃 [{idx + 1}/{len(categories)}] Processing: {category}")
            
            # [핵심] 해당 카테고리 프로세스 실행
            # 내부 로직에서 AI 응답의 카테고리 태그보다 이 'category' 변수를 우선하도록 
            # processor.run_category_process가 설계되어 있어야 합니다.
            processor.run_category_process(category, run_count)
            
            print(f"✅ Success: {category}")
            results["success"] += 1
            
            if idx < len(categories) - 1:
                # 유료 계정 안정권인 10~20초 유지
                wait_sec = random.uniform(10, 20)
                print(f"💤 [Safe Interval] Waiting {wait_sec:.2f}s for next category...")
                time.sleep(wait_sec)
            
        except Exception as e:
            # ✅ [보완 2] 에러 발생 시 어느 카테고리에서 났는지 더 상세히 출력합니다.
            print(f"🚨 CRITICAL ERROR in {category}: {str(e)}")
            results["failed"] += 1
            # 하나가 실패해도 다음 카테고리는 계속 진행합니다.
            continue

    print(f"\n" + "="*50)
    print(f"🎉 Batch Processing Completed.")
    print(f"📊 Summary | Success: {results['success']} | Failed: {results['failed']}")
    print(f"⏰ Finished at: {datetime.now()} (UTC)")
    print(f"="*50)
    
    # 실패가 하나라도 있으면 Action 결과에 경고를 남기기 위해 0이 아닌 값으로 종료할 수 있으나,
    # 여기서는 전체 흐름을 위해 0으로 종료합니다.
    sys.exit(0)

if __name__ == "__main__":
    main()
