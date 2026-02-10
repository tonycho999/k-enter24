'use client';

import { useState, useEffect } from 'react';
import HotKeywords from '@/components/HotKeywords';
import GlobalReactions from '@/components/GlobalReactions';

// --- 타입 정의 ---
type Article = {
  id: number;
  title: string;
  summary: string;
  artist: string;
  date: string;
  image: string;
  source: string; // 언론사
};

// --- 더미 데이터 (이미지 & 소스 포함) ---
const MOCK_NEWS: Article[] = [
  {
    id: 1,
    artist: "BTS",
    title: "BTS Jin Discharge: Global Fans Celebrate",
    summary: "Jin completed his military service today. Thousands of fans gathered...",
    date: "2024-06-12",
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Jin_for_Dispatch_%22Boy_With_Luv%22_MV_behind_the_scene_shooting%2C_15_March_2019_03.jpg/440px-Jin_for_Dispatch_%22Boy_With_Luv%22_MV_behind_the_scene_shooting%2C_15_March_2019_03.jpg",
    source: "Dispatch"
  },
  {
    id: 2,
    artist: "NewJeans",
    title: "NewJeans 'How Sweet' Breaks Records",
    summary: "NewJeans' latest single has topped the Billboard Global charts...",
    date: "2024-06-12",
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/NewJeans_X_OLENS_1.jpg/640px-NewJeans_X_OLENS_1.jpg",
    source: "Billboard"
  },
  {
    id: 3,
    artist: "IVE",
    title: "IVE World Tour Sold Out in Europe",
    summary: "IVE proves global popularity with sold-out shows in London and Paris...",
    date: "2024-06-11",
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Ive_on_October_13%2C_2023.jpg/640px-Ive_on_October_13%2C_2023.jpg",
    source: "AllKpop"
  },
  {
    id: 4,
    artist: "Lisa",
    title: "BLACKPINK Lisa's New Solo Announcement",
    summary: "Lisa teases new solo project with a mysterious Instagram post...",
    date: "2024-06-10",
    image: "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ed/Lisa_for_Bulgari_Aurora_Awards_2022_01.jpg/460px-Lisa_for_Bulgari_Aurora_Awards_2022_01.jpg",
    source: "Vogue"
  }
];

export default function Home() {
  const [articles, setArticles] = useState<Article[]>(MOCK_NEWS);
  const [clickedCount, setClickedCount] = useState(0);
  const [isSubscribed, setIsSubscribed] = useState(false); // DB 연동 예정

  // 1. 로컬 스토리지에서 오늘 클릭 횟수 확인 및 초기화
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const today = new Date().toISOString().slice(0, 10);
      const storedDate = localStorage.getItem('lastClickDate');
      const storedCount = localStorage.getItem('clickCount');

      if (storedDate === today && storedCount) {
        setClickedCount(parseInt(storedCount));
      } else {
        // 날짜가 바뀌었으면 리셋
        localStorage.setItem('lastClickDate', today);
        localStorage.setItem('clickCount', '0');
        setClickedCount(0);
      }
    }
  }, []);

  // 2. 카드 클릭 핸들러 (구독 제한 로직)
  const handleCardClick = (id: number) => {
    // 구독자가 아니고, 무료 횟수(1회)를 넘었을 때
    if (!isSubscribed && clickedCount >= 1) {
      alert("🔒 Free limit reached! Subscribe to read more K-POP news.");
      return;
    }

    // 클릭 카운트 증가
    const newCount = clickedCount + 1;
    setClickedCount(newCount);
    localStorage.setItem('clickCount', newCount.toString());
    
    alert(`📢 Opening Article #${id} details...`);
    // 추후 router.push(`/article/${id}`) 등으로 이동
  };

  return (
    <main className="min-h-screen bg-black text-white p-4 md:p-8 font-sans selection:bg-pink-500 selection:text-white">
      
      {/* --- 1. 헤더 영역 (로고 적용) --- */}
      <header className="flex justify-between items-center mb-8 max-w-7xl mx-auto">
        {/* 텍스트 대신 로고 이미지 사용 */}
        <div className="flex items-center gap-2">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src="/logo.png" 
              alt="K-POP 24 Logo" 
              className="h-14 md:h-16 w-auto object-contain drop-shadow-[0_0_15px_rgba(34,211,238,0.6)]" 
            />
        </div>

        <button 
          onClick={() => setIsSubscribed(!isSubscribed)} // 테스트용 토글
          className={`px-4 py-1.5 rounded-full text-sm font-bold transition-all shadow-[0_0_10px_rgba(34,211,238,0.2)] border 
            ${isSubscribed 
              ? 'bg-cyan-500 text-black border-cyan-500 hover:bg-cyan-400' 
              : 'bg-transparent text-cyan-400 border-cyan-500/50 hover:bg-cyan-500/10'
            }`}
        >
          {isSubscribed ? 'SUBSCRIBED (VIP)' : 'LOG IN ($15/yr)'}
        </button>
      </header>

      {/* --- 2. 상단 뉴스 섹션 (카드형) --- */}
      <section className="mb-8 max-w-7xl mx-auto">
        <h2 className="text-xl font-bold mb-4 text-gray-200 flex items-center gap-2">
          Today&apos;s Top News 
          {!isSubscribed && <span className="text-xs font-normal text-gray-500">(Free limit: {Math.max(0, 1 - clickedCount)}/1)</span>}
        </h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {articles.map((news) => (
            <div 
              key={news.id} 
              onClick={() => handleCardClick(news.id)}
              className={`group relative h-72 rounded-xl overflow-hidden border transition-all duration-300 cursor-pointer
                ${!isSubscribed && clickedCount >= 1 
                  ? 'border-gray-800 opacity-60' // 잠김 상태: 어둡게
                  : 'border-gray-800 hover:border-pink-500 hover:shadow-[0_0_15px_rgba(236,72,153,0.3)]' // 활성 상태
                }`}
            >
              {/* 배경 이미지 */}
              <div className="absolute inset-0 bg-gray-900">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img 
                  src={news.image} 
                  alt={news.title} 
                  className="w-full h-full object-cover opacity-60 group-hover:opacity-40 group-hover:scale-110 transition-transform duration-700"
                />
              </div>
              
              {/* 그라데이션 오버레이 */}
              <div className="absolute inset-0 bg-gradient-to-t from-black via-black/40 to-transparent" />

              {/* 텍스트 내용 */}
              <div className="absolute bottom-0 left-0 p-5 w-full">
                 <div className="flex justify-between items-end mb-1">
                    <span className="text-xs text-cyan-300 font-bold bg-cyan-900/30 px-2 py-0.5 rounded border border-cyan-500/30 backdrop-blur-sm">
                      {news.artist}
                    </span>
                    <span className="text-[10px] text-gray-400">{news.source}</span>
                 </div>
                 <h3 className="text-white font-bold text-lg leading-snug line-clamp-2 group-hover:text-pink-200 transition-colors">
                   {news.title}
                 </h3>
              </div>

              {/* 잠금 오버레이 (무료 유저 클릭 소진 시 Hover 효과) */}
              {!isSubscribed && clickedCount >= 1 && (
                <div className="absolute inset-0 bg-black/70 backdrop-blur-[2px] flex flex-col items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div className="text-3xl mb-2">🔒</div>
                  <span className="text-xs font-bold text-pink-500 border border-pink-500 px-3 py-1 rounded-full">
                    SUBSCRIBE TO UNLOCK
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* --- 3. 하단 데이터 섹션 (좌: 키워드 / 우: 글로벌 반응) --- */}
      <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-7xl mx-auto h-full pb-10">
        {/* KeywordTicker 대신 새로운 그래프 컴포넌트 사용 */}
        <HotKeywords />
        <GlobalReactions />
      </section>

    </main>
  );
}
