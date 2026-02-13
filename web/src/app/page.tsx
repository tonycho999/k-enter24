import { supabase } from '@/lib/supabase';
import HomeClient from '@/components/HomeClient';

// 👇 [핵심] 60초마다 서버에서 데이터를 새로 가져오도록 설정 (ISR)
export const revalidate = 60;

export default async function Page() {
  // 1. 서버 사이드에서 뉴스 데이터 가져오기
  const { data: news, error } = await supabase
    .from('live_news')
    .select('*')
    .order('score', { ascending: false });

  if (error) {
    console.error('Failed to fetch news:', error);
  }

  // 2. 가져온 데이터를 클라이언트 컴포넌트에 넘겨줌 (초기 로딩 속도 향상)
  return <HomeClient initialNews={news || []} />;
}
