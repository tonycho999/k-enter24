'use client';

import { useEffect, useState } from 'react';
import { supabase } from '@/lib/supabase';
import { 
  User, LogOut, Settings, ChevronDown, 
  ShieldCheck, Sun, Moon, Languages 
} from 'lucide-react';

export default function Header() {
  const [user, setUser] = useState<any>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [langCode, setLangCode] = useState('EN'); // 기본값 EN

  useEffect(() => {
    const getUser = async () => {
      const { data: { user } } = await supabase.auth.getUser();
      setUser(user);
    };
    getUser();

    // 다크모드 설정
    if (localStorage.getItem('theme') === 'dark' || 
        (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      setIsDark(true);
      document.documentElement.classList.add('dark');
    }

    // [추가] 브라우저 언어 감지 (KO는 EN으로 고정)
    const browserLang = navigator.language.split('-')[0].toUpperCase();
    setLangCode(browserLang === 'KO' ? 'EN' : browserLang);

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });
    return () => subscription.unsubscribe();
  }, []);

  const toggleDarkMode = () => {
    if (isDark) {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    }
    setIsDark(!isDark);
  };

  // [수정] AI 번역 핸들러: 이벤트를 발생시켜 page.tsx에서 처리하게 함
  const handleAiTranslate = () => {
    if (langCode === 'EN') {
      alert("System is already in Global Standard (EN).");
      return;
    }
    window.dispatchEvent(new CustomEvent('ai-translate', { detail: langCode }));
  };

  const handleLogin = async () => {
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo: `${location.origin}/auth/callback` },
    });
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setMenuOpen(false);
  };

  return (
    <header className="flex justify-between items-center mb-6 py-2 border-b border-slate-100 dark:border-slate-800 transition-colors">
      <div className="flex items-center gap-4">
        <div className="w-[128px] h-[60px] flex items-center justify-center overflow-hidden">
          <img src="/logo.png" alt="Logo" className="w-full h-full object-contain" />
        </div>
        <div className="flex flex-col ml-2 border-l border-slate-200 dark:border-slate-700 pl-3">
             <div className="flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                </span>
                <span className="text-[10px] font-black text-cyan-500 uppercase tracking-tighter">Live</span>
             </div>
             <span className="text-[11px] font-bold text-slate-400 dark:text-slate-500 leading-none mt-0.5 uppercase">
               Global AI Monitoring
             </span>
        </div>
      </div>

      <div className="flex items-center gap-2 relative">
        <button onClick={toggleDarkMode} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-500 dark:text-slate-400">
          {isDark ? <Sun size={20} /> : <Moon size={20} />}
        </button>

        {/* [수정] 언어 설정 버튼: 현재 브라우저 언어 표시 */}
        <button 
          onClick={handleAiTranslate}
          className="px-3 py-1.5 bg-cyan-50 dark:bg-cyan-900/30 text-cyan-600 dark:text-cyan-400 rounded-full flex items-center gap-2 border border-cyan-100 dark:border-cyan-800 transition-all hover:scale-105"
        >
          <Languages size={18} />
          <span className="text-[11px] font-black uppercase">{langCode}</span>
        </button>

        <div className="h-4 w-[1px] bg-slate-200 dark:bg-slate-700 mx-1" />

        {user ? (
          <div className="relative">
            <button onClick={() => setMenuOpen(!menuOpen)} className="flex items-center gap-2 px-3 py-1.5 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-full">
              <div className="w-7 h-7 rounded-full bg-slate-100 overflow-hidden">
                {user.user_metadata?.avatar_url ? <img src={user.user_metadata.avatar_url} alt="profile" /> : <User size={16} />}
              </div>
              <span className="text-xs font-bold text-slate-700 dark:text-slate-300 truncate max-w-[80px]">
                {user.email?.split('@')[0]}
              </span>
              <ChevronDown size={14} />
            </button>
            {menuOpen && (
              <div className="absolute right-0 mt-3 w-56 bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-[24px] shadow-xl z-[100] p-2">
                <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800/50 rounded-2xl mb-1">
                  <ShieldCheck size={14} className="text-cyan-500 mb-1" />
                  <p className="text-sm font-black text-slate-800 dark:text-slate-200">Standard Member</p>
                </div>
                <button className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded-xl">
                  <Settings size={18} /> Settings
                </button>
                <button onClick={handleLogout} className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-bold text-red-500 hover:bg-red-50 rounded-xl">
                  <LogOut size={18} /> Log Out
                </button>
              </div>
            )}
          </div>
        ) : (
          <button onClick={handleLogin} className="px-6 py-2 text-sm font-black text-white bg-slate-900 dark:bg-cyan-600 rounded-full">
            Sign In
          </button>
        )}
      </div>
    </header>
  );
}
