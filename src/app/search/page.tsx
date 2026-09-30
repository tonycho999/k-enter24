// src/app/search/page.tsx
import Link from 'next/link';
// 절대 경로 적용
import { searchPosts } from '@/lib/blogger';

export const dynamic = 'force-dynamic'; 

export default async function SearchPage({ searchParams }: { searchParams: { q: string } }) {
  const keyword = searchParams.q || '';

  // Blogger에서 검색어로 글을 가져옵니다.
  const posts = keyword ? await searchPosts(keyword) : [];

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
    
    return text.length > 150 ? text.substring(0, 150) + '...' : text;
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">
          🔍 Search Results for: "<span style={{ color: '#2563eb' }}>{keyword}</span>"
        </h2>
        <span style={{ color: '#64748b', fontWeight: 'bold' }}>{posts.length} articles found</span>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>'{keyword}'에 대한 검색 결과가 없습니다.</h3>
          <p>다른 검색어로 다시 시도해 보세요.</p>
        </div>
      ) : (
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
            
            // 새로 만든 함수로 description 추출
            const description = extractDescription(post.content);

            return (
              <Link href={`/${category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                <div className="list-content">
                  <div className="list-category">{category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">{description}</p>
                  <div className="list-date">
                    {new Date(post.publishedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
