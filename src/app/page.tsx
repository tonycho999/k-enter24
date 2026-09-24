// src/app/page.tsx
import Link from 'next/link';
// 1. Prisma 대신 우리가 만든 Blogger 유틸리티 함수를 불러옵니다.
import { getPosts } from '../lib/blogger';

export default async function Home() {
  // 2. Blogger API에서 최신 글(최대 20개)을 가져옵니다.
  const posts = await getPosts();

  const currentYear = new Date().getFullYear();

  // Blogger 본문(HTML)에서 순수 텍스트만 추출하는 함수 (요약 텍스트용)
  const stripHtml = (html: string) => {
    return html.replace(/<[^>]*>?/gm, '');
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        {/* 🚀 연도별 필터 버튼 (현재 연도만 활성화된 상태로 표시) */}
        <div className="year-filter">
          <button className="year-btn active">{currentYear}</button>
        </div>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        /* 🚀 가로형 리스트 컨테이너 */
        <div className="article-list">
          {posts.map((post) => {
            // 3. 썸네일, 카테고리, 텍스트 가공
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            
            // Blogger는 카테고리(라벨)가 여러 개일 수 있으므로 첫 번째 값을 메인으로 사용. 없을 경우 'news'
            const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
            
            const plainTextContent = stripHtml(post.content);

            return (
              <Link href={`/${category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                {/* 왼쪽: 썸네일 */}
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                
                {/* 오른쪽: 텍스트 정보 */}
                <div className="list-content">
                  <div className="list-category">{category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">
                    {plainTextContent.length > 150 ? plainTextContent.substring(0, 150) + '...' : plainTextContent}
                  </p>
                  <div className="list-date">
                    {/* Blogger의 날짜 데이터를 보기 좋게 변환 */}
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
