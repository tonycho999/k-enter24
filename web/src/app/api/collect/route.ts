import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import Groq from 'groq-sdk';
import { google } from 'googleapis';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_KEY!);
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
const customSearch = google.customsearch('v1');

// 가수 그룹 데이터 (10개 그룹)
const ARTIST_GROUPS = [
  ["뉴진스", "아이브", "에스파", "르세라핌", "블랙핑크", "트와이스", "레드벨벳", "(여자)아이들", "있지", "스테이씨"],
  ["세븐틴", "스트레이키즈", "NCT 127", "NCT DREAM", "TXT", "엔하이픈", "에이티즈", "더보이즈", "트레저", "제베원"],
  ["라이즈", "투어스", "베이비몬스터", "엔믹스", "키스오브라이프", "아일릿", "케플러", "트리플에스", "유니스", "넥스지"],
  ["BTS", "엑소", "샤이니", "비투비", "마마무", "에이핑크", "소녀시대", "카라", "인피니트", "하이라이트"],
  ["몬스타엑스", "아스트로", "SF9", "골든차일드", "온앤오프", "원어스", "CIX", "크래비티", "피원하모니", "템페스트"],
  ["드림캐쳐", "오마이걸", "우주소녀", "위클리", "빌리", "우아", "퍼플키스", "하이키", "라이임라잇", "라잇썸"],
  ["아이유", "태연", "제니", "로제", "리사", "지수", "정국", "지민", "뷔", "슈가"],
  ["박재범", "지코", "제시", "비비", "크러쉬", "헤이즈", "자이언티", "이무진", "볼빨간사춘기", "악뮤"],
  ["보넥도", "올아워즈", "나우어데이즈", "비디유", "루네이트", "앰퍼샌드원", "영파씨", "배드빌런", "미야오", "메이딘"],
  ["플레이브", "이세계아이돌", "메이브", "스텔라이브", "시그니처", "블랙스완", "소디엑", "이븐", "루네이트", "파우"]
];

export async function GET(request: Request) {
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const now = new Date();
  const cycleHour = now.getHours() % 2; // 0 또는 1 (2시간 주기)
  const mins = now.getMinutes();

  try {
    // ---------------------------------------------------------
    // PHASE 1: 수집 (1시간차 01분 ~ 46분, 5분 간격, 총 10회)
    // ---------------------------------------------------------
    if (cycleHour === 0 && mins >= 1 && mins <= 46) {
      const groupIndex = Math.floor((mins - 1) / 5); // 0~9 인덱스 자동 계산
      const targetArtists = ARTIST_GROUPS[groupIndex] || ARTIST_GROUPS[0];
      
      // 네이버 검색 (작살 방식 - 여러 가수 한꺼번에)
      const query = targetArtists.join(' OR ');
      const naverRes = await fetch(
        `https://openapi.naver.com/v1/search/news.json?query=${encodeURIComponent(query)}&display=10&sort=sim`,
        {
          headers: {
            'X-Naver-Client-Id': process.env.NAVER_CLIENT_ID!,
            'X-Naver-Client-Secret': process.env.NAVER_CLIENT_SECRET!,
          }
        }
      );
      const naverData = await naverRes.json();

      // 구글 검색 (그물 방식 - 1회차에만 실행하여 할당량 절약)
      if (groupIndex === 0) {
        const googleRes = await customSearch.cse.list({
          auth: process.env.GOOGLE_SEARCH_API_KEY,
          cx: process.env.GOOGLE_SEARCH_ENGINE_ID,
          q: "K-POP comeback debut world tour",
          dateRestrict: 'd1',
          num: 5
        });
        // 구글 데이터 저장 로직...
      }

      // 네이버 데이터 저장
      for (const item of naverData.items || []) {
        await supabase.from('raw_news').upsert({
          link: item.link, title: item.title.replace(/<[^>]*>?/gm, ''),
          snippet: item.description.replace(/<[^>]*>?/gm, ''),
          source: 'Naver'
        }, { onConflict: 'link' });
      }

      return NextResponse.json({ step: `Scraping Group ${groupIndex}` });
    }

    // ---------------------------------------------------------
    // PHASE 2: AI 요약 (1시간차 51분 ~ 2시간차 51분, 5분 간격, 총 12회)
    // ---------------------------------------------------------
    if ((cycleHour === 0 && mins >= 51) || (cycleHour === 1 && mins <= 51)) {
      // 아직 요약 안 된 뉴스 3개만 가져오기 (10초 제한 방지)
      const { data: rawData } = await supabase
        .from('raw_news')
        .select('*')
        .limit(3)
        .order('created_at', { ascending: false });

      if (!rawData || rawData.length === 0) return NextResponse.json({ status: 'No news to summarize' });

      for (const article of rawData) {
        const chat = await groq.chat.completions.create({
          messages: [{ role: "user", content: `Analyze: ${article.title}. Return JSON {artist, summary, vibe: {excitement, shock, sadness}}` }],
          model: "llama3-8b-8192",
          response_format: { type: "json_object" }
        });
        const result = JSON.parse(chat.choices[0]?.message?.content || "{}");
        
        await supabase.from('live_news').insert({
          artist: result.artist, title: article.title, summary: result.summary,
          reactions: result.vibe, is_published: false
        });
        await supabase.from('raw_news').delete().eq('id', article.id);
      }
      return NextResponse.json({ step: 'Batch AI Summarizing' });
    }

    // ---------------------------------------------------------
    // PHASE 3: 배포 (2시간 주기의 시작 정각)
    // ---------------------------------------------------------
    if (cycleHour === 0 && mins === 0) {
      await supabase.from('live_news').update({ 
        is_published: true, 
        published_at: new Date().toISOString() 
      }).eq('is_published', false);
      
      return NextResponse.json({ step: 'Bi-Hourly Release Done' });
    }

    return NextResponse.json({ status: 'Standby' });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
