// src/app/rss.xml/route.ts
import { getPosts } from '../../lib/blogger';

export async function GET() {
  // Prisma 대신 Blogger에서 최신글 20개를 가져옵니다. 
  // (lib/blogger.tsx에서 getPosts에 maxResults 파라미터를 추가하셨다면 undefined, 20 으로 넘깁니다)
  const posts = await getPosts(undefined, 20);

  const siteUrl = 'https://k-enter24.com';

  // 본문에서 HTML 태그를 제거하는 함수 (RSS 요약본을 깔끔하게 만들기 위함)
  const stripHtml = (html: string) => {
    return html.replace(/<[^>]*>?/gm, '');
  };

  // RSS 2.0 표준 양식 생성
  const rssItemsXml = posts.map(post => {
    // 카테고리가 비어있을 경우 대비
    const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
    const plainTextContent = stripHtml(post.content);
    
    return `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/${category.toLowerCase()}/${post.id}</link>
      <description><![CDATA[${plainTextContent.length > 200 ? plainTextContent.substring(0, 200) + '...' : plainTextContent}]]></description>
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
