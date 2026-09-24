// src/app/[category]/page.tsx
import Link from 'next/link';
import { getPosts } from '../../lib/blogger';

export default async function CategoryPage({ params }: { params: { category: string } }) {
  // 1. URL에서 카테고리 이름 가져오기 (예: 'k-pop')
  const rawCategory = params.category;
  
  // URL의 'k-pop'을 Blogger 라벨 형태인 'K-POP'으로 변환 (필요에 따라 대소문자 매칭)
  const categoryLabel = rawCategory.toUpperCase();

  // 2. 해당 카테고리(라벨)의 글만 가져오기
  const posts = await getPosts(categoryLabel);

  const stripHtml = (html: string) => {
    return html.replace(/<[^>]*>?/gm, '');
  };

  return (
    <div>
      <div className="page-header">
        {/* 현재 보고 있는 카테고리 이름을 타이틀로 출력 */}
        <h2 className="page-title">🔥 {categoryLabel} NEWS</h2>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>해당 카테고리에 아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            const plainTextContent = stripHtml(post.content);

            return (
              <Link href={`/${rawCategory}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                
                <div className="list-content">
                  <div className="list-category">{categoryLabel}</div>
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
