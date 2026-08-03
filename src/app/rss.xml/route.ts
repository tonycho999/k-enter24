// src/app/rss.xml/route.ts
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export async function GET() {
  const posts = await prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 20, // 최신글 20개만 RSS 피드로 전송
  });

  const siteUrl = 'https://k-enter24.com';

  // RSS 2.0 표준 양식 생성
  const rssItemsXml = posts.map(post => `
    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/${post.category.toLowerCase()}/${post.id}</link>
      <description><![CDATA[${post.content.substring(0, 200)}...]]></description>
      <category>${post.category}</category>
      <pubDate>${post.createdAt.toUTCString()}</pubDate>
    </item>
  `).join('');

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
