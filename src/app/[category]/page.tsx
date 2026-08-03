// src/app/[category]/page.tsx
import Link from 'next/link';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
// 🚀 캐싱을 적용해 1분마다 새로고침되도록 하여 속도 극대화!
export const revalidate = 60;

export default async function CategoryPage({ params }: { params: { category: string } }) {
  // URL에서 넘어온 영어 소문자(k-pop)를 대문자(K-POP)로 변환
  const currentCategory = params.category.toUpperCase();

  // DB에서 '현재 클릭한 카테고리'와 일치하는 글만 최신순으로 가져옵니다.
  const posts = await prisma.post.findMany({
    where: { 
      category: {
        equals: currentCategory,
        mode: 'insensitive' // 대소문자 구분 없이 검색
      }
    },
    orderBy: { createdAt: 'desc' },
  });

  return (
    <div>
      {/* 🚀 상단 타이틀 영역 (가로 리스트형 CSS 적용 완료) */}
      <div className="page-header">
        <h2 className="page-title">📂 {currentCategory}</h2>
        <span style={{ color: '#64748b', fontWeight: 'bold' }}>{posts.length} articles</span>
      </div>
      
      {/* 글이 없을 때 */}
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>{currentCategory} 카테고리에 아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        /* 🚀 가로 리스트형 뼈대(article-list, list-card 등)로 완벽 교체! */
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.images.length > 0 ? post.images[0] : 'https://k-enter24.com/og-image.png';

            return (
              <Link href={`/${params.category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                
                {/* 왼쪽: 썸네일 (강제 고정 크기 240x160) */}
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
