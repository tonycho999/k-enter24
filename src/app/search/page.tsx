// src/app/search/page.tsx
import Link from 'next/link';
// Prisma 대신 Blogger 검색 함수를 가져옵니다.
import { searchPosts } from '../../lib/blogger';

export const dynamic = 'force-dynamic'; 

export default async function SearchPage({ searchParams }: { searchParams: { q: string } }) {
  const keyword = searchParams.q || '';

  // Blogger에서 검색어로 글을 가져옵니다. (검색어가 없으면 빈 배열 반환)
  const posts = keyword ? await searchPosts(keyword) : [];

  const stripHtml = (html: string) => {
    return html.replace(/<[^>]*>?/gm, '');
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
            const plainTextContent = stripHtml(post.content);

            return (
              <Link href={`/${category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                <div className="list-content">
                  <div className="list-category">{category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">
                    {plainTextContent.length > 150 ? plainTextContent.substring(0, 150) + '...' : plainTextContent}
                  </p>
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
