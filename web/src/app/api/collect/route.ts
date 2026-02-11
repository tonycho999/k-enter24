import { NextResponse } from 'next/server';
import { createClient } from '@supabase/supabase-js';
import Groq from 'groq-sdk';
import { google } from 'googleapis';

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_KEY!);
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
const customsearch = google.customsearch('v1');

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
    // PHASE 1-1: 지능형 가수 발견 (1시간차 01분 ~ 05분)
    // ---------------------------------------------------------
    if (cycleHour === 0 && mins >= 1 && mins <= 5) {
      // 1. 구글 커스텀 검색으로 광범위한 K-POP 트렌드 키워드 검색
      const googleRes = await customsearch.cse.list({
        auth: process.env.GOOGLE_SEARCH_API_KEY,
        cx: process.env.GOOGLE_SEARCH_ENGINE_ID,
        q: "K-POP (comeback OR debut OR world tour OR new album) news",
        dateRestrict: 'd1',
        num: 10
      });

      const titles = googleRes.data.items?.map(i => i.title).join("\n") || "";

      // 2. AI에게 뉴스 제목에서 가수(그룹/솔로) 이름을 모두 추출하도록 요청
      const discoveryChat = await groq.chat.completions.create({
        messages: [{ 
          role: "user", 
          content: `Identify all K-pop artists (groups or soloists) mentioned in these headlines. Include new or rising artists. 
          Headlines:
          ${titles}
          
          Return ONLY a JSON object: { "found_artists": ["Name1", "Name2"] }` 
        }],
        model: "llama3-8b-8192",
        response_format: { type: "json_object" }
      });

      const { found_artists } = JSON.parse(discoveryChat.choices[0]?.message?.content || '{"found_artists":[]}');

      // 3. 기존 대기열 비우고 새로운 발견 리스트로 채우기
      if (found_artists.length > 0) {
        await supabase.from('scraping_queue').delete().neq('id', 0);
        const insertData = found_artists.map((name: string) => ({ artist_name: name }));
        await supabase.from('scraping_queue').insert(insertData);
      }

      return NextResponse.json({ step: 'Discovery Done', artists_count: found_artists.length });
    }

    // ---------------------------------------------------------
    // PHASE 1-2: 타겟 정밀 수집 (1시간차 06분 ~ 50분, 5분 간격)
    // ---------------------------------------------------------
    if (cycleHour === 0 && mins >= 6 && mins <= 50) {
      const { data: queue } = await supabase
        .from('scraping_queue')
        .select('*')
        .limit(5)
        .order('created_at', { ascending: true });

      if (!queue || queue.length === 0) return NextResponse.json({ status: 'Queue Empty' });

      const query = queue.map(a => a.artist_name).join(' OR ');
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

      for (const item of naverData.items || []) {
        await supabase.from('raw_news').upsert({
          link: item.link, 
          title: item.title.replace(/<[^>]*>?/gm, ''),
          snippet: item.description.replace(/<[^>]*>?/gm, ''),
          source: 'Naver'
        }, { onConflict: 'link' });
      }
      
      const idsToRemove = queue.map(q => q.id);
      await supabase.from('scraping_queue').delete().in('id', idsToRemove);

      return NextResponse.json({ step: 'Targeted Scrape Done', artists: queue.map(a => a.artist_name) });
    }

    // ---------------------------------------------------------
    // PHASE 2: AI 심층 분석 및 요약 (1시간차 51분 ~ 2시간차 55분)
    // ---------------------------------------------------------
    if ((cycleHour === 0 && mins >= 51) || cycleHour === 1) {
      const { data: rawData } = await supabase
        .from('raw_news')
        .select('*')
        .limit(3)
        .order('created_at', { ascending: false });

      if (!rawData || rawData.length === 0) return NextResponse.json({ status: 'Analysis Complete' });

      for (const article of rawData) {
        const analysisChat = await groq.chat.completions.create({
          messages: [{ 
            role: "user", 
            content: `Analyze this K-pop news and provide a cyberpunk-style summary.
            Title: ${article.title}
            Snippet: ${article.snippet}
            
            Return ONLY a JSON object: 
            { 
              "artist": "string", 
              "summary": "1 sentence neon-vibed summary", 
              "vibe": { "excitement": 0-100, "shock": 0-100, "sadness": 0-100 } 
            }` 
          }],
          model: "llama3-8b-8192",
          response_format: { type: "json_object" }
        });
        
        const result = JSON.parse(analysisChat.choices[0]?.message?.content || "{}");
        
        await supabase.from('live_news').insert({
          artist: result.artist, 
          title: article.title, 
          summary: result.summary,
          reactions: result.vibe, 
          is_published: false
        });
        
        // 처리된 원본 데이터 삭제하여 중복 방지
        await supabase.from('raw_news').delete().eq('id', article.id);
      }
      return NextResponse.json({ step: 'AI Analysis Batch Done' });
    }

    // ---------------------------------------------------------
    // PHASE 3: 최종 배포 (2시간 주기의 정각)
    // ---------------------------------------------------------
    if (cycleHour === 0 && mins === 0) {
      await supabase.from('live_news').update({ 
        is_published: true, 
        published_at: new Date().toISOString() 
      }).eq('is_published', false);
      
      return NextResponse.json({ step: 'Cycle Complete - Released' });
    }

    return NextResponse.json({ status: 'System Standby' });
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
