'use client';

import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';
import { Flame } from 'lucide-react';

export default function HotKeywords() {
  const [keywords, setKeywords] = useState<{ text: string; count: number }[]>([]);

  useEffect(() => {
    const fetchKeywords = async () => {
      const { data } = await supabase
        .from('live_news')
        .select('category')
        .order('created_at', { ascending: false });

      if (data) {
        const allTags = data.map(item => item.category);
        const counts = allTags.reduce((acc: any, tag: string) => {
          acc[tag] = (acc[tag] || 0) + 1;
          return acc;
        }, {});

        const sorted = Object.keys(counts)
          .map(tag => ({ text: tag, count: counts[tag] }))
          .sort((a, b) => b.count - a.count)
          .slice(0, 5);

        setKeywords(sorted);
      }
    };
    fetchKeywords();
  }, []);

  return (
    // [수정] h-full을 삭제하고 h-fit을 적용, p-8을 p-6으로 줄여 컴팩트하게 변경
    <div className="bg-white border border-slate-100 rounded-[32px] p-6 h-fit shadow-sm hover:shadow-md transition-shadow">
      <h3 className="text-xs font-black text-slate-800 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <Flame className="w-4 h-4 text-orange-500 fill-current" /> 
        Trending Keywords
      </h3>
      
      {/* [수정] space-y-6을 space-y-4로 줄여 아이템 간격 축소 */}
      <div className="space-y-4">
        {keywords.length > 0 ? (
          keywords.map((item, idx) => (
            <div key={idx} className="group">
              <div className="flex justify-between items-center text-[11px] mb-1.5">
                <span className="text-slate-700 font-bold">
                  <span className="text-cyan-500 mr-2 font-black">0{idx + 1}</span> 
                  {item.text.toUpperCase()}
                </span>
                <span className="text-slate-400 font-bold">Score {item.count * 10}</span>
              </div>
              
              <div className="w-full bg-slate-50 rounded-full h-1 overflow-hidden">
                <div 
                  className="bg-gradient-to-r from-cyan-400 to-blue-500 h-full rounded-full transition-all duration-1000 ease-out" 
                  style={{ width: `${Math.min(item.count * 20, 100)}%` }}
                ></div>
              </div>
            </div>
          ))
        ) : (
          <div className="flex flex-col gap-3">
            {[1, 2, 3].map((n) => (
              <div key={n} className="h-8 bg-slate-50 animate-pulse rounded-lg" />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
