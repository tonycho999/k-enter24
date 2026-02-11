'use client';

export default function VibeCheck({ data }: { data?: any }) {
  // DB 스키마에 맞춰 'reactions' 필드에서 에너지를 추출합니다.
  const vibe = data || { excitement: 33, shock: 33, sadness: 34 };

  const bars = [
    { label: "🤩 Excitement", val: vibe.excitement, color: "from-pink-500 to-purple-600" },
    { label: "⚡ Shock / Buzz", val: vibe.shock, color: "from-yellow-400 to-orange-500" },
    { label: "💧 Sadness / Serious", val: vibe.sadness, color: "from-cyan-400 to-blue-600" }
  ];

  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 h-full flex flex-col justify-center">
      <h3 className="text-lg font-bold text-white mb-6 flex items-center gap-2">
        🔮 AI Vibe Check <span className="text-xs text-gray-500 font-normal">(Sentiment Analysis)</span>
      </h3>
      <div className="space-y-6">
        {bars.map((bar) => (
          <div key={bar.label}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300 font-bold">{bar.label}</span>
              <span className="text-white">{bar.val}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-3 overflow-hidden shadow-inner">
              <div 
                className={`bg-gradient-to-r ${bar.color} h-full transition-all duration-1000`} 
                style={{ width: `${bar.val}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
