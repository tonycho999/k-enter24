// web/src/app/api/collect/route.ts
import { NextResponse } from 'next/server';
import Groq from 'groq-sdk';
import { google } from 'googleapis';

const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
const customSearch = google.customsearch('v1');

export async function GET() {
  try {
    const targetArtist = "NewJeans"; // 나중엔 요청에서 받아오게 수정
    const query = `${targetArtist} k-pop news`;

    // 1. 구글 검색 (이미지 포함)
    const googleRes = await customSearch.cse.list({
      auth: process.env.GOOGLE_SEARCH_API_KEY,
      cx: process.env.GOOGLE_SEARCH_ENGINE_ID,
      q: query,
      num: 4, // 디자인에 맞춰 4개 수집
      dateRestrict: 'd1',
    });

    const items = googleRes.data.items || [];
    if (items.length === 0) return NextResponse.json({ message: "No news found." });

    // 2. 데이터 가공 (이미지 추출 로직 추가 🔥)
    const articles = items.map((item: any) => {
        // 구글 검색 결과에서 썸네일 찾기 (pagemap > cse_image)
        const imgUrl = item.pagemap?.cse_image?.[0]?.src 
                    || item.pagemap?.cse_thumbnail?.[0]?.src 
                    || null;
        
        return {
            title: item.title,
            link: item.link,
            snippet: item.snippet,
            image: imgUrl // 이미지 주소 저장
        };
    });

    // 3. AI 요약 (생략 가능하나, 기사 정제를 위해 유지)
    // 빠른 응답을 위해 이번 코드에서는 AI 단계를 건너뛰고 바로 데이터를 리턴해봅니다.
    // (실제 서비스에선 여기서 AI 요약 로직을 태우세요)
    
    return NextResponse.json({
      success: true,
      artist: targetArtist,
      data: articles // 프론트엔드로 기사 목록 전송
    });

  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
