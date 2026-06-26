'use client';

import Image from 'next/image';
import Link from 'next/link';
import { useEffect, useState } from 'react';

// 💡 3개의 광고 링크와 각각에 맞는 이미지 데이터를 배열로 관리합니다.
const ADS = [
  {
    id: 1,
    link: "https://invl.me/clnkyyb",
    imgPc: "https://k-enter24.com/ad1_1000.png",    // 👈 1번 광고 PC용 이미지 주소 (수정 필요)
    imgMobile: "https://k-enter24.com/ad1_600.png", // 👈 1번 광고 모바일용 이미지 주소 (수정 필요)
  },
  {
    id: 2,
    link: "https://invl.app/clnkyyd",
    imgPc: "https://k-enter24.com/ad2_1000.png",    // 👈 2번 광고 PC용 이미지 주소 (수정 필요)
    imgMobile: "https://k-enter24.com/ad2_600.png", // 👈 2번 광고 모바일용 이미지 주소 (수정 필요)
  },
  {
    id: 3,
    link: "https://invl.me/clnkyyh",
    imgPc: "https://k-enter24.com/ad3_1000.png",    // 👈 3번 광고 PC용 이미지 주소 (수정 필요)
    imgMobile: "https://k-enter24.com/ad3_600.png", // 👈 3번 광고 모바일용 이미지 주소 (수정 필요)
  }
];

export default function AdBanner() {
  const [mounted, setMounted] = useState(false);
  const [currentAd, setCurrentAd] = useState(ADS[0]);

  useEffect(() => {
    // 클라이언트 마운트 후 랜덤으로 광고 1개 선택 (Next.js Hydration 에러 방지)
    const randomAd = ADS[Math.floor(Math.random() * ADS.length)];
    setCurrentAd(randomAd);
    setMounted(true);
  }, []);

  // 배너 활성화 (강제로 빈 공간으로 만들고 싶을 때만 true로 변경)
  const isPlaceholder = false; 

  if (isPlaceholder) {
    return (
      <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-2xl flex items-center justify-center p-4 border border-slate-200 dark:border-slate-700 min-h-[90px] lg:min-h-[120px]">
         <span className="text-slate-400 text-sm font-bold tracking-widest uppercase">Advertisement Space</span>
      </div>
    );
  }

  // 브라우저 렌더링 전(마운트 전)에는 화면이 덜컹거리지 않게 빈 투명 영역만 잡아둡니다.
  if (!mounted) {
    return <div className="w-full rounded-2xl min-h-[70px] sm:min-h-[90px] lg:min-h-[120px]" />;
  }

  return (
    <div className="w-full relative rounded-2xl overflow-hidden shadow-sm hover:shadow-md transition-shadow group border border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900">
      <Link href={currentAd.link} target="_blank" rel="noopener noreferrer" className="block w-full">
        
        {/* 우측 상단 AD 뱃지 (광고임을 명시) */}
        <div className="absolute top-2 right-2 bg-black/30 backdrop-blur-md text-white text-[9px] px-1.5 py-0.5 rounded z-10 font-bold tracking-wider">
          AD
        </div>
        
        {/* 💻 PC용 배너 (md 이상 화면에서 노출) */}
        <div className="hidden md:block relative w-full h-[90px] lg:h-[120px]">
          <Image 
            src={currentAd.imgPc} 
            alt={`Sponsored Advertisement ${currentAd.id}`} 
            fill 
            className="object-cover group-hover:scale-[1.02] transition-transform duration-500" 
            unoptimized 
          />
        </div>
        
        {/* 📱 모바일용 배너 (md 미만 화면에서 노출) */}
        <div className="block md:hidden relative w-full h-[70px] sm:h-[90px]">
          <Image 
            src={currentAd.imgMobile} 
            alt={`Sponsored Advertisement ${currentAd.id}`} 
            fill 
            className="object-cover group-hover:scale-[1.02] transition-transform duration-500" 
            unoptimized 
          />
        </div>
        
      </Link>
    </div>
  );
}
