'use client';

import { useEffect, useState, useMemo } from 'react';
import { supabase } from '@/lib/supabase';
import KeywordTicker from './KeywordTicker';
import VibeCheck from './VibeCheck';
import RankingItem from './RankingItem';
import { Trophy, Flame, Music, Film, Tv, MapPin, ThumbsUp, TrendingUp } from 'lucide-react'; // TrendingUp 아이콘 추가
import { LiveNewsItem, RankingItemData } from '@/types';

interface SidebarProps {
  news: LiveNewsItem[];
  category: string;
}

export default function Sidebar({ news, category }: SidebarProps) {
  const [rankings, setRankings] = useState<RankingItemData[]>([]);
  const [loading, setLoading] = useState(false);

  // 카테고리 변경 시 랭킹 데이터 새로고침
  useEffect(() => {
    const fetchRankings = async () => {
      setLoading(true);
      
      try {
        let data: RankingItemData[] | null = null;

        // ✅ All일 때는 '평점(score)' 높은 순으로 정렬
        if (category === 'All') {
          const { data: trendingData, error } = await supabase
            .from('trending_rankings')
            .select('*')
            .order('score', { ascending: false }) // 평점 높은 순
            .limit(10);
          
          if (error) throw error;

          if (trendingData) {
            // 화면에 보여줄 때만 1위~10위로 번호 매김 (DB 데이터 변경 X)
            data = trendingData.map((item, index) => ({
              ...item,
              rank: index + 1
            })) as RankingItemData[];
          }

        } else {
          // ✅ 개별 카테고리는 DB에 저장된 'rank' 순서대로 (기존 유지)
          const targetCategory = category.toLowerCase();
          
          const { data: categoryData, error } = await supabase
            .from('trending_rankings')
            .select('*')
            .eq('category', targetCategory)
            .order('rank', { ascending: true }) // 지정된 랭킹 순
            .limit(10);
            
          if (error) throw error;
            
          data = categoryData as RankingItemData[];
        }

        setRankings(data || []);

      } catch (error) {
        console.error("Sidebar Error:", error);
        setRankings([]);
      } finally {
        setLoading(false);
      }
    };

    fetchRankings();
  }, [category]);

  // 상단 헤더 아이콘/제목 설정 (useMemo 사용)
  const headerInfo = useMemo(() => {
    switch (category) {
      case 'K-Pop': return { title: 'Top 10 Music Chart', icon: <Music size={18} /> };
      case 'K-Drama': return { title: 'Drama Ranking', icon: <Tv size={18} /> }; 
      case 'K-Movie': return { title: 'Box Office Top 10', icon: <Film size={18} /> };
      case 'K-Entertain': return { title: 'Variety Show Trends', icon: <Flame size={18} /> };
      case 'K-Culture': return { title: "K-Culture Hot Picks", icon: <MapPin size={18} /> };
      default: return { title: 'Total Trend Ranking', icon: <TrendingUp size={18} /> }; // 아이콘 변경
    }
  }, [category]);

  
  // 좋아요 순 정렬 (Top 3)
  const topLiked = useMemo(() => {
      if (!news) return [];
      return [...news]
        .sort((a, b) => (b.likes || 0) - (a.likes || 0))
        .slice(0, 3);
  }, [news]);

  return (
    <aside className="lg:col-span-1 space-y-6"> {/* lg:col-span-4 -> lg:col-span-1 로 수정 (전체 레이아웃 고려) */}
      
      {/* 1. 실시간 랭킹 (All 포함 모든 카테고리에서 표시) */}
      <section className="bg-white dark:bg-slate-900 rounded-[32px] p-6 border border-slate-100 dark:border-slate-800 shadow-sm animate-in fade-in slide-in-from-right-4 duration-500">
        <div className="flex items-center gap-2 mb-4 text-cyan-600 dark:text-cyan-400 border-b border-slate-50 dark:border-slate-800 pb-3">
          {headerInfo.icon}
          <h3 className="font-black uppercase tracking-wider text-sm">
            {headerInfo.title}
          </h3>
        </div>
        
        <div className="space-y-1">
          {loading ? (
              <div className="text-center py-8 text-xs text-slate-400 animate-pulse">Update Charts...</div>
          ) : rankings.length > 0 ? (
              rankings.map((item, index) => (
                // key prop 수정: id가 없으면 index 활용
                <RankingItem 
                    key={item.id || `${item.category}-${item.rank}-${index}`} 
                    rank={item.rank} 
                    item={item} 
                />
              ))
          ) : (
              <div className="text-center py-6 text-xs text-slate-400 italic">
                Ranking data preparing...
              </div>
          )}
        </div>
      </section>

      {/* 2. Hot Keywords */}
      <KeywordTicker />

      {/* 3. AI Vibe Check */}
      <VibeCheck />
      
      {/* 4. Users' Choice (Top Voted) */}
      <section className="bg-white dark:bg-slate-900 rounded-[32px] p-6 border border-slate-100 dark:border-slate-800 shadow-sm">
        <div className="flex items-center gap-2 mb-6 text-cyan-500">
          <Trophy size={18} className="fill-current" />
          <h3 className="font-black text-slate-800 dark:text-slate-200 uppercase tracking-wider text-sm">
            Users' Choice
          </h3>
        </div>
        
        <div className="space-y-4">
          {topLiked.length > 0 ? (
            topLiked.map((m, idx) => (
              <div key={m.id} className="group cursor-pointer border-b border-slate-50 dark:border-slate-800 pb-3 last:border-0 last:pb-0 hover:pl-2 transition-all duration-300">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] font-black text-slate-300 uppercase">#{idx + 1}</span>
                  <span className="text-[10px] font-bold text-cyan-500 uppercase">{m.category}</span>
                </div>
                <p className="text-sm font-bold text-slate-700 dark:text-slate-300 line-clamp-2 group-hover:text-cyan-500 transition-colors mb-2">
                  {m.title}
                </p>
                <div className="flex items-center gap-3">
                    <span className="text-[10px] font-black text-cyan-600 bg-cyan-50 dark:bg-cyan-900/30 px-2 py-0.5 rounded-md flex items-center gap-1">
                      <ThumbsUp size={10} /> {m.likes || 0}
                    </span>
                </div>
              </div>
            ))
          ) : (
            <p className="text-xs text-slate-400 text-center py-4 italic">No votes yet.</p>
          )}
        </div>
      </section>
    </aside>
  );
}
