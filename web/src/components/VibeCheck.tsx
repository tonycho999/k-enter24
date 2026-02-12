'use client';

import { Activity } from 'lucide-react';
import { motion } from 'framer-motion';

export default function VibeCheck() {
  // 실전에서는 뉴스들의 summary를 분석한 결과를 넣으면 좋습니다.
  const stats = [
    { label: 'Excitement', val: 78, color: 'bg-cyan-400', icon: '⚡' },
    { label: 'Expectation', val: 12, color: 'bg-orange-400', icon: '🔥' },
    { label: 'Shock', val: 10, color: 'bg-yellow-400', icon: '😲' }
  ];

  return (
    <section className="bg-white rounded-[32px] p-8 border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-center gap-2 mb-6">
        <Activity size={18} className="text-cyan-500" />
        <h3 className="font-black text-slate-800 uppercase tracking-wider text-sm">AI Vibe Check</h3>
      </div>
      
      <div className="space-y-6">
        {stats.map(stat => (
          <div key={stat.label}>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-bold text-slate-500 flex items-center gap-1.5">
                <span className="text-sm">{stat.icon}</span> {stat.label}
              </span>
              <span className="text-sm font-black text-slate-800">{stat.val}%</span>
            </div>
            <div className="h-2 bg-slate-50 rounded-full overflow-hidden">
              <motion.div 
                initial={{ width: 0 }} 
                animate={{ width: `${stat.val}%` }} 
                transition={{ duration: 1, ease: "circOut" }}
                className={`h-full ${stat.color} rounded-full`} 
              />
            </div>
          </div>
        ))}
      </div>
      
      <p className="mt-6 text-[10px] text-slate-400 font-medium leading-relaxed">
        * Analysis based on global social media reactions and news sentiment.
      </p>
    </section>
  );
}
