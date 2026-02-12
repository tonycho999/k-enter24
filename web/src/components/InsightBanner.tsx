'use client';
import { Zap } from 'lucide-react';

export default function InsightBanner({ insight }: { insight?: string }) {
  return (
    <div className="mb-8 px-6 py-3 bg-cyan-50 border border-cyan-100 rounded-2xl flex items-center gap-3">
      <Zap className="text-yellow-500 w-5 h-5 flex-shrink-0" />
      <p className="text-sm font-bold text-slate-700 italic leading-none">
        <span className="text-cyan-600 uppercase mr-2 font-black tracking-wider">AI Insight:</span>
        {insight || "Analyzing global K-Entertainment trends in real-time..."}
      </p>
    </div>
  );
}
