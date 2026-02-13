'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { supabase } from '@/lib/supabase';

export default function AuthCallback() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState('Processing login...');

  useEffect(() => {
    const handleAuth = async () => {
      // 1. URL에 'code'가 있는지 확인 (PKCE 방식 - 최신 Supabase 기본값)
      const code = searchParams.get('code');
      
      if (code) {
        setStatus('Verifying security code...');
        // 코드를 이용해 세션 교환 요청
        const { error } = await supabase.auth.exchangeCodeForSession(code);
        if (!error) {
          router.push('/'); // 성공 시 메인으로 이동
          return;
        }
      }

      // 2. URL에 'access_token'이 있는지 확인 (Implicit 방식 - 구형)
      const hash = window.location.hash;
      if (hash && hash.includes('access_token')) {
        setStatus('Verifying token...');
        // Supabase가 자동으로 해시를 감지하여 세션 설정함
      }

      // 3. 이미 세션이 잡혀있는지 최종 확인
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        router.push('/');
      } else {
        // 세션 변화 감지 리스너 등록
        const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
          if (event === 'SIGNED_IN' || session) {
            router.push('/');
          }
        });
        return () => subscription.unsubscribe();
      }
    };

    handleAuth();
  }, [router, searchParams]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-white dark:bg-slate-950">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-4 border-slate-200 border-t-cyan-500 rounded-full animate-spin"></div>
        <p className="text-slate-500 font-bold text-sm animate-pulse">{status}</p>
      </div>
    </div>
  );
}
