// src/app/page.tsx
import Link from 'next/link';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
export const revalidate = 60; 

export default async function Home() {
  const posts = await prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    take: 20, // 일단 최신 20개만 가져옵니다.
  });

  // 현재 연도를 구해서 필터 버튼에 사용 (나중에 2027이 되면 자동으로 추가되도록 응용 가능합니다)
  const currentYear = new Date().getFullYear();

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        {/* 🚀 연도별 필터 버튼 (현재 연도만 활성화된 상태로 표시) */}
        <div className="year-filter">
          <button className="year-btn active">{currentYear}</button>
          {/* <button className="year-btn">2025</button> 나중에 데이터가 쌓이면 이렇게 추가 가능합니다 */}
        </div>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        /* 🚀 가로형 리스트 컨테이너로 변경 */
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.images.length > 0 ? post.images[0] : 'https://k-enter24.com/og-image.png';

            return (
              <Link href={`/${post.category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                {/* 왼쪽: 썸네일 (원본 비율 유지하면서 꽉 차게) */}
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                
                {/* 오른쪽: 텍스트 정보 */}
                <div className="list-content">
                  <div className="list-category">{post.category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">
                    {post.content.length > 150 ? post.content.substring(0, 150) + '...' : post.content}
                  </p>
                  <div className="list-date">
                    {post.createdAt.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
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
