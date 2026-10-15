import { getPosts } from '@/lib/blogger';

export async function GET() {
  const posts = await getPosts(undefined, 20);
  const siteUrl = 'https://k-enter24.com';

  // Blogger 본문 JSON-LD에서 description 추출 (없으면 본문 텍스트 200자)
  const extractDescription = (html: string) => {
    if (!html) return '';
    try {
      const scriptMatch = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
      if (scriptMatch && scriptMatch[1]) {
        const jsonData = JSON.parse(scriptMatch[1]);
        if (jsonData && jsonData.description) return jsonData.description;
      }
    } catch (e) {
      console.error('JSON parsing error in extractDescription', e);
    }
    let text = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');
    text = text.replace(/<[^>]*>?/gm, '');
    text = text.replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    text = text.trim();
    return text.length > 200 ? text.substring(0, 200) + '...' : text;
  };

  // 한국 시간(+0900) RFC 822 형식
  const getKSTDateString = (dateString: string) => {
    const date = new Date(dateString);
    date.setHours(date.getHours() + 9);
    const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${days[date.getUTCDay()]}, ${pad(date.getUTCDate())} ${months[date.getUTCMonth()]} ${date.getUTCFullYear()} ${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}:${pad(date.getUTCSeconds())} +0900`;
  };

  // 🚀 CDATA 안전 처리 (본문에 "]]>"가 있어도 XML이 깨지지 않게)
  const cdata = (text: string) => `<![CDATA[${String(text).replace(/]]>/g, ']]]]><![CDATA[>')}]]>`;

  const rssItemsXml = posts.map((post) => {
    const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'TIPS';
    const link = `${siteUrl}/${category.toLowerCase()}/${post.id}`;
    return `
    <item>
      <title>${cdata(post.title)}</title>
      <link>${link}</link>
      <guid isPermaLink="true">${link}</guid>
      <description>${cdata(extractDescription(post.content))}</description>
      <category>${cdata(category)}</category>
      <pubDate>${getKSTDateString(post.publishedAt)}</pubDate>
    </item>`;
  }).join('');

  const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>K-ENTER 24 | Korea Travel &amp; Trend Guide</title>
    <link>${siteUrl}</link>
    <description>Your guide to Korea's best sights, food, style, and travel tips.</description>
    <language>en</language>
    <atom:link href="${siteUrl}/rss.xml" rel="self" type="application/rss+xml"/>
    ${rssItemsXml}
  </channel>
</rss>`;

  return new Response(rssXml, {
    headers: { 'Content-Type': 'application/rss+xml; charset=utf-8' },
  });
}
