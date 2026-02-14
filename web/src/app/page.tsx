import { supabase } from '@/lib/supabase';
import HomeClient from '@/components/HomeClient';

// 👇 60초마다 ISR (데이터 갱신)
export const revalidate = 60;

export default async function Page() {
  // 1. 서버 사이드에서 뉴스 데이터 가져오기
  // ✅ [수정] 초기 화면(All) 기준이므로 'rank'가 아니라 'score' 높은 순으로 변경
  const { data: news, error } = await supabase
    .from('live_news')
    .select('*')
    .order('score', { ascending: false }) // 점수 높은 순 (트렌드순)
    .limit(30); // 클라이언트 로직과 동일하게 30개만 가져오기

  if (error) {
    console.error('Failed to fetch news:', error);
  }

  // 2. 가져온 데이터를 클라이언트 컴포넌트에 전달
  return <HomeClient initialNews={news || []} />;
}
