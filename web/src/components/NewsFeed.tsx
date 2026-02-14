'use client';

import { LiveNewsItem } from '@/types';
import { Clock, ThumbsUp, ArrowRight, ExternalLink, PlayCircle } from 'lucide-react';
import Image from 'next/image';

interface NewsFeedProps {
  news: LiveNewsItem[];
  loading: boolean;
  onOpen: (item: LiveNewsItem) => void;
}

export default function NewsFeed({ news, loading, onOpen }: NewsFeedProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6 animate-pulse">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-64 bg-slate-200 dark:bg-slate-800 rounded-[32px]" />
        ))}
      </div>
    );
  }

  if (news.length === 0) {
    return (
      <div className="text-center py-20 bg-white dark:bg-slate-900 rounded-[32px] border border-dashed border-slate-200 dark:border-slate-800">
        <p className="text-slate-400 font-medium">No news updates yet.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-6 gap-6">
      {news.map((item, index) => {
        // ✅ [수정] DB에 rank가 없으므로, 배열의 순서(index)를 랭킹으로 사용
        const displayRank = index + 1;
        
        // 레이아웃 결정 로직 (1~2위: 대형, 3~6위: 중형, 7위~: 리스트형)
        const isHero = displayRank <= 2;
        const isMedium = displayRank > 2 && displayRank <= 6;

        return (
          <div 
            key={item.id}
            onClick={() => onOpen(item)}
            className={`
              group relative overflow-hidden rounded-[32px] bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer
              ${isHero ? 'md:col-span-3 h-[420px]' : isMedium ? 'md:col-span-2 h-[340px]' : 'md:col-span-6 h-[140px] flex gap-6 items-center pr-6'}
            `}
          >
            {/* 이미지 영역 */}
            <div className={`
              relative overflow-hidden bg-slate-100 dark:bg-slate-800
              ${isHero ? 'h-3/5 w-full' : isMedium ? 'h-1/2 w-full' : 'h-full w-1/3 min-w-[140px]'}
            `}>
              {item.image_url ? (
                <Image
                  src={item.image_url}
                  alt={item.title}
                  fill
                  className="object-cover group-hover:scale-105 transition-transform duration-700"
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-slate-300">
                  <span className="text-xs font-bold uppercase tracking-widest">No Image</span>
                </div>
              )}
              
              {/* 랭킹 뱃지 */}
              <div className="absolute top-4 left-4 bg-white/90 dark:bg-black/80 backdrop-blur-md px-3 py-1 rounded-full text-xs font-black shadow-lg z-10">
                <span className="text-cyan-600 dark:text-cyan-400">#{displayRank}</span>
              </div>
            </div>

            {/* 텍스트 영역 */}
            <div className={`
              flex flex-col justify-between
              ${isHero ? 'p-6 h-2/5' : isMedium ? 'p-5 h-1/2' : 'flex-1 py-4'}
            `}>
              <div>
                <div className="flex items-center gap-2 mb-2 text-[10px] font-bold uppercase tracking-widest text-slate-400">
                   <span className="text-cyan-600 dark:text-cyan-500">{item.category}</span>
                   <span>•</span>
                   <span className="flex items-center gap-1">
                      <Clock size={10} />
                      NEW
                   </span>
                </div>
                
                <h3 className={`
                  font-bold text-slate-800 dark:text-slate-100 leading-tight group-hover:text-cyan-600 transition-colors
                  ${isHero ? 'text-2xl mb-3 line-clamp-2' : isMedium ? 'text-lg mb-2 line-clamp-2' : 'text-lg mb-1 line-clamp-1'}
                `}>
                  {item.title}
                </h3>

                {(isHero || !isMedium) && (
                   <p className="text-sm text-slate-500 dark:text-slate-400 line-clamp-2 leading-relaxed">
                     {item.summary}
                   </p>
                )}
              </div>

              <div className="flex items-center justify-between mt-auto pt-4">
                 <div className="flex items-center gap-4 text-xs font-bold text-slate-400">
                    <span className="flex items-center gap-1.5 group-hover:text-cyan-500 transition-colors">
                       <ThumbsUp size={14} />
                       {item.likes || 0}
                    </span>
                    {item.score && (
                        <span className="bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[10px]">
                           Sc: {item.score.toFixed(0)}
                        </span>
                    )}
                 </div>
                 
                 <div className="w-8 h-8 rounded-full bg-slate-50 dark:bg-slate-800 flex items-center justify-center group-hover:bg-cyan-500 group-hover:text-white transition-colors">
                    <ArrowRight size={14} />
                 </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
