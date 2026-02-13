'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase'; // 경로는 프로젝트 설정에 맞게
import { Lock, Zap } from 'lucide-react';

import Header from '@/components/Header';
import CategoryNav from '@/components/CategoryNav';
import InsightBanner from '@/components/InsightBanner';
import NewsFeed from '@/components/NewsFeed';
import Sidebar from '@/components/Sidebar';
import ArticleModal from '@/components/ArticleModal'; // 파일명 확인 (NewsModal인지 ArticleModal인지)
import MobileFloatingBtn from '@/components/MobileFloatingBtn';
import AdBanner from '@/components/AdBanner';
import { LiveNewsItem } from '@/types'; // [New] 타입 import

interface HomeClientProps {
  initialNews: LiveNewsItem[];
}

export default function HomeClient({ initialNews }: HomeClientProps) {
  // 1. 상태 관리
  const [news, setNews] = useState<LiveNewsItem[]>(initialNews);
  const [category, setCategory] = useState('All');
  const [selectedArticle, setSelectedArticle] = useState<LiveNewsItem | null>(null);
  
  const [loading, setLoading] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const [user, setUser] = useState<any>(null);
  
  const [showWelcome, setShowWelcome] = useState(false);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  // 2. 초기화 및 인증 체크
  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => setUser(data.user));
    
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome_v1');
    if (!hasSeenWelcome) setTimeout(() => setShowWelcome(true), 1000);

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  // 3. [핵심] 카테고리 변경 시 DB에서 데이터 새로 가져오기
  const handleCategoryChange = async (newCategory: string) => {
    setCategory(newCategory);
    setLoading(true);

    try {
      let query = supabase
        .from('live_news')
        .select('*')
        .order('rank', { ascending: true }) // 랭킹 순 정렬
        .limit(30);

      if (newCategory !== 'All') {
        query = query.eq('category', newCategory);
      }

      const { data, error } = await query;

      if (!error && data) {
        setNews(data as LiveNewsItem[]);
      }
    } catch (error) {
      console.error("Fetch Error:", error);
    } finally {
      setLoading(false);
    }
  };

  // 4. [핵심] 좋아요 핸들러 (SQL 함수 increment_vote에 맞춤)
  const handleVote = async (id: string, type: 'likes' | 'dislikes') => {
    if (!user) {
      alert("Please sign in to vote!");
      return;
    }

    // 싫어요 기능은 현재 DB 함수에 없으므로 좋아요만 처리 (필요시 DB 함수 수정 필요)
    if (type === 'dislikes') {
       alert("Dislike feature is coming soon!");
       return;
    }

    // 낙관적 UI 업데이트 (서버 응답 기다리지 않고 즉시 숫자 올림)
    setNews(prev => prev.map(item => item.id === id ? { ...item, likes: item.likes + 1 } : item));
    if (selectedArticle?.id === id) {
      setSelectedArticle((prev: any) => ({ ...prev, likes: prev.likes + 1 }));
    }

    // 서버 요청
    await supabase.rpc('increment_vote', { row_id: id });
  };

  // 5. 로그인 여부에 따른 뉴스 필터링 (Freemium 모델)
  // 로그인이 안 되어 있으면 1개만 보여줌
  const displayNews = user ? news : news.slice(0, 1);

  // 6. 기타 이벤트 핸들러 (모달, 번역 등)
  useEffect(() => {
    const handleSearchModalOpen = (e: any) => {
      if (e.detail) setSelectedArticle(e.detail);
    };
    window.addEventListener('open-news-modal', handleSearchModalOpen);
    return () => window.removeEventListener('open-news-modal', handleSearchModalOpen);
  }, []);

  const closeWelcome = () => {
    if (dontShowAgain) localStorage.setItem('hasSeenWelcome_v1', 'true');
    setShowWelcome(false);
  };

  // 7. 로그인 핸들러
  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${window.location.origin}/auth/callback` },
    });
  };

  return (
    <main className="min-h-screen bg-[#f8fafc] text-slate-800 font-sans dark:bg-slate-950 dark:text-slate-200 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-0">
        <Header />
        
        <div className="flex flex-col gap-0">
          <div className="mb-1">
             {/* 카테고리 변경 시 handleCategoryChange 호출 */}
             <CategoryNav active={category} setCategory={handleCategoryChange} />
          </div>
          
          <div className="mt-0"> 
             {/* 상단 배너에는 현재 리스트의 1위 뉴스 요약 표시 */}
             <InsightBanner insight={news.length > 0 ? news[0].summary : undefined} />
          </div>
          
          <div className="mt-2">
             <AdBanner />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mt-6">
          <div className="col-span-1 md:col-span-3 relative">
            {/* NewsFeed에 displayNews 전달 */}
            <NewsFeed 
              news={displayNews} 
              loading={loading || isTranslating} 
              onOpen={setSelectedArticle} 
            />
            
            {/* 로그인 안 했을 때 블러 처리 및 유도 */}
            {!user && !loading && news.length > 0 && (
              <div className="mt-6 relative">
                 <div className="space-y-6 opacity-40 blur-sm select-none pointer-events-none grayscale">
                    <div className="h-40 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200" />
                    <div className="h-40 bg-white dark:bg-slate-900 rounded-3xl border border-slate-200" />
                 </div>
                 
                 <div className="absolute inset-0 flex flex-col items-center justify-start pt-4">
                    <div className="bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl p-8 rounded-[32px] shadow-2xl border border-slate-100 dark:border-slate-800 text-center max-w-sm mx-auto">
                        <div className="w-14 h-14 bg-gradient-to-br from-cyan-400 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg shadow-cyan-200">
                           <Lock className="text-white" size={24} />
                        </div>
                        <h3 className="text-xl font-black text-slate-900 dark:text-white mb-2">Want to see more?</h3>
                        <p className="text-sm text-slate-500 dark:text-slate-400 mb-6 leading-relaxed">
                           Sign in to unlock <span className="font-bold text-cyan-600">Real-time K-Trends</span> & <span className="font-bold text-cyan-600">AI Analysis</span>.
                        </p>
                        <button onClick={handleLogin} className="w-full py-3.5 bg-slate-900 dark:bg-cyan-600 text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-xl">
                          Sign in with Google
                        </button>
                    </div>
                 </div>
              </div>
            )}
          </div>
          
          <div className="hidden md:block col-span-1">
            {/* Sidebar에는 전체 news 데이터와 현재 카테고리 전달 */}
            <Sidebar news={news} category={category} />
          </div>
        </div>
      </div>

      {selectedArticle && (
        <ArticleModal 
          article={selectedArticle} 
          onClose={() => setSelectedArticle(null)} 
          // @ts-ignore: ArticleModal의 타입 정의가 아직 안 되어 있다면 무시
          onVote={handleVote} 
        />
      )}
      
      <MobileFloatingBtn />
      
      {showWelcome && !user && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-300">
          {/* ... (Welcome 모달 내용은 그대로 유지) ... */}
           <div className="bg-white dark:bg-slate-900 w-full max-w-md rounded-[32px] p-1 shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
              <div className="bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-600 p-8 rounded-[28px] text-center relative overflow-hidden">
                 <div className="absolute top-0 left-0 w-full h-full opacity-20 bg-[url('https://grainy-gradients.vercel.app/noise.svg')]"></div>
                 <div className="relative z-10">
                    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-white/20 backdrop-blur-md mb-4 border border-white/30 shadow-lg">
                       <Zap className="text-yellow-300 fill-yellow-300" size={24} />
                    </div>
                    <h2 className="text-2xl font-black text-white mb-3 tracking-tight leading-tight">⚡️ Real-time K-News Radar</h2>
                    <div className="text-white/95 font-medium text-sm mb-8 leading-relaxed space-y-2 opacity-90">
                       <p>Stop waiting for late translations.</p>
                       <p>Access breaking <span className="text-yellow-300 font-bold">K-Pop & Drama</span> articles the second they are published in Korea.</p>
                       <p>Experience the world's fastest K-Trend source.</p>
                    </div>
                    <button onClick={closeWelcome} className="w-full py-4 bg-white text-slate-900 font-black text-lg rounded-2xl hover:bg-slate-50 hover:scale-[1.02] transition-all shadow-xl">
                       Start Monitoring Now
                    </button>
                 </div>
              </div>
              <div className="p-4 bg-white dark:bg-slate-900 text-center">
                 <label className="flex items-center justify-center gap-2 cursor-pointer group select-none">
                    <input type="checkbox" className="w-4 h-4 rounded border-slate-300 text-cyan-600 focus:ring-cyan-500 transition-all" checked={dontShowAgain} onChange={(e) => setDontShowAgain(e.target.checked)} />
                    <span className="text-xs font-bold text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors">Don't show this again</span>
                 </label>
              </div>
           </div>
        </div>
      )}
    </main>
  );
}
