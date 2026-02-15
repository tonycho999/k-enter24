import sys
import time
import os
import random  # 랜덤 시간 생성을 위해 유지
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
    print(f"💡 Perplexity Paid Tier Mode: Optimized waiting times.")

    for idx, category in enumerate(categories):
        try:
            print(f"\n" + "="*50)
            print(f"🏃 Starting Category: {category}")
            
            # [핵심] 해당 카테고리 프로세스 실행
            # (내부에서 news_api.ask_news_ai를 호출하도록 processor.py가 수정되어 있어야 합니다)
            processor.run_category_process(category, run_count)
            
            print(f"✅ Finished: {category}")
            results["success"] += 1
            
            # [전문가 팁] 마지막 카테고리가 아닐 때만 짧은 랜덤 휴식 실행
            if idx < len(categories) - 1:
                # 유료 계정은 10초 ~ 20초(10,000ms ~ 20,000ms)면 충분합니다.
                # 너무 빠르면 검색 엔진 측에서 차단할 수 있으므로 최소한의 예의를 지킵니다.
                wait_ms = random.randint(10000, 20000)
                wait_sec = wait_ms / 1000.0
                
                print(f"💤 [안전 휴식] 다음 카테고리 준비 중...")
                print(f"💤 대기 시간: {wait_sec:.2f}초")
                
                time.sleep(wait_sec)
            
        except Exception as e:
            print(f"🚨 Error in {category}: {e}")
            results["failed"] += 1
            continue

    print(f"\n" + "="*50)
    print(f"🎉 All Categories Processed.")
    print(f"📊 Success: {results['success']}, Failed: {results['failed']}")
    print(f"⏰ End Time: {datetime.now()} (UTC)")
    print(f"="*50)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
