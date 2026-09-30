// src/app/rss.xml/route.ts
// 절대 경로 적용
import { getPosts } from '@/lib/blogger';

export async function GET() {
  // Blogger에서 최신글 20개를 가져옵니다. 
  const posts = await getPosts(undefined, 20);

  const siteUrl = 'https://k-enter24.com';

  // 🚀 Blogger 본문 내의 JSON-LD에서 description 추출
  const extractDescription = (html: string) => {
    if (!html) return '';

    try {
      const scriptMatch = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
      if (scriptMatch && scriptMatch[1]) {
        const jsonData = JSON.parse(scriptMatch[1]);
        if (jsonData && jsonData.description) {
          return jsonData.description; 
        }
      }
    } catch (e) {
      console.error("JSON parsing error in extractDescription", e);
    }

    // JSON-LD가 없을 때의 방어 코드
    let text = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');
    text = text.replace(/<[^>]*>?/gm, '');
    text = text.replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    text = text.trim();
    
    return text.length > 200 ? text.substring(0, 200) + '...' : text;
  };

  // RSS 2.0 표준 양식 생성
  const rssItemsXml = posts.map(post => {
    // 카테고리가 비어있을 경우 대비
    const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
    
    // 새로 만든 함수로 description 추출 (RSS용)
    const description = extractDescription(post.content);
    
    return `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/${category.toLowerCase()}/${post.id}</link>
      <description><![CDATA[${description}]]></description>
      <category>${category}</category>
      <pubDate>${new Date(post.publishedAt).toUTCString()}</pubDate>
    </item>
  `}).join('');

  const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
      <channel>
        <title>K-ENTER 24 | Global K-Culture Blog</title>
        <link>${siteUrl}</link>
        <description>Your daily source for K-Pop, K-Drama, and K-Culture.</description>
        <language>en</language>
        <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
        ${rssItemsXml}
      </channel>
    </rss>`;

  // 브라우저와 구글 봇이 XML 파일로 인식하도록 헤더(Header) 설정
  return new Response(rssXml, {
    headers: { 'Content-Type': 'text/xml; charset=utf-8' },
  });
}
