'use client';
import { Zap } from 'lucide-react';

export default function InsightBanner({ insight }: { insight?: string }) {
  // 데이터가 없으면 기본 문구 표시
  const content = insight || "Analyzing global K-Entertainment trends in real-time...";

  return (
    // [수정 요청 반영] 여백 및 높이 조정 (mt-1, mb-2, py-2)
    <div className="mt-1 mb-2 px-4 sm:px-6 py-2 bg-cyan-50 dark:bg-cyan-900/20 border border-cyan-100 dark:border-cyan-800 rounded-2xl flex items-center gap-3 overflow-hidden shadow-sm">
      
      {/* 아이콘: 깜빡이는 애니메이션 추가 */}
      <Zap className="text-yellow-500 w-5 h-5 flex-shrink-0 animate-pulse" fill="currentColor" />
      
      {/* 텍스트 영역: 넘치는 텍스트 처리 */}
      <div className="flex-1 overflow-hidden relative flex items-center h-5">
        <p className="text-sm font-bold text-slate-700 dark:text-slate-300 italic leading-none whitespace-nowrap truncate">
          <span className="text-cyan-600 dark:text-cyan-400 uppercase mr-2 font-black tracking-wider">AI Insight:</span>
          <span className="text-slate-600 dark:text-slate-400 font-medium not-italic">
            {content}
          </span>
        </p>
      </div>
    </div>
  );
}
