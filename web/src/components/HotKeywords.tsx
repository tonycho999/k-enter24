'use client';

const KEYWORDS = [
  { rank: 1, text: "BTS Jin Comeback", percent: 85 },
  { rank: 2, text: "NewJeans How Sweet", percent: 70 },
  { rank: 3, text: "IVE World Tour", percent: 60 },
  { rank: 4, text: "SEVENTEEN Maestro", percent: 50 },
  { rank: 5, text: "AESPA Supernova", percent: 45 },
];

export default function HotKeywords() {
  return (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 h-full">
      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
        🔥 Hot Keywords <span className="text-xs text-gray-500 font-normal">(Live)</span>
      </h3>
      <div className="space-y-4">
        {KEYWORDS.map((item, idx) => (
          <div key={idx} className="group">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-300 font-medium">
                <span className="text-cyan-400 mr-2">{item.rank}.</span>
                {item.text}
              </span>
              <span className="text-gray-500 text-xs">{item.percent}%</span>
            </div>
            {/* 게이지 바 배경 */}
            <div className="w-full bg-gray-800 rounded-full h-2.5 overflow-hidden">
              {/* 실제 게이지 (그라데이션 효과) */}
              <div 
                className="bg-gradient-to-r from-cyan-500 to-blue-500 h-2.5 rounded-full transition-all duration-1000 ease-out group-hover:from-pink-500 group-hover:to-purple-500" 
                style={{ width: `${item.percent}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
