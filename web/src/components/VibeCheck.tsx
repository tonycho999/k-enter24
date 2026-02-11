'use client';

import { useState, useEffect } from 'react';
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs';

export default function VibeCheck() {
  const [vibe, setVibe] = useState({ excitement: 0, shock: 0, sadness: 0 });
  const supabase = createClientComponentClient();

  useEffect(() => {
    const fetchVibe = async () => {
      const { data } = await supabase
        .from('live_news')
        .select('vibe')
        .eq('is_published', true)
        .order('created_at', { ascending: false })
        .limit(1)
        .single();
      
      if (data?.vibe) setVibe(data.vibe);
    };
    fetchVibe();
  }, [supabase]);

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 h-full flex flex-col justify-center">
      <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
        🔮 AI Vibe Check <span className="text-xs text-gray-500 font-normal">(Sentiment Analysis)</span>
      </h3>
      <div className="space-y-6">
        {Object.entries({
          "🤩 Excitement": { val: vibe.excitement, color: "from-pink-500 to-purple-600" },
          "⚡ Shock / Buzz": { val: vibe.shock, color: "from-yellow-400 to-orange-500" },
          "💧 Sadness / Serious": { val: vibe.sadness, color: "from-cyan-400 to-blue-600" }
        }).map(([label, { val, color }]) => (
          <div key={label}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300 font-bold">{label}</span>
              <span className="text-white">{val}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden">
              <div className={`bg-gradient-to-r ${color} h-full transition-all duration-1000`} style={{ width: `${val}%` }}></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
