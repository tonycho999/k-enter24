// src/app/[category]/page.tsx
import Link from 'next/link';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
export const dynamic = 'force-dynamic';

export default async function CategoryPage({ params }: { params: { category: string } }) {
  // URL에서 넘어온 영어 소문자(k-pop)를 대문자(K-POP)로 변환하여 DB에서 찾기 쉽게 만듭니다.
  const currentCategory = params.category.toUpperCase();

  // 1. DB에서 '현재 클릭한 카테고리'와 일치하는 글만 최신순으로 가져옵니다!
  const posts = await prisma.post.findMany({
    where: { 
      category: {
        equals: currentCategory,
        mode: 'insensitive' // 대소문자 구분 없이 찰떡같이 찾아냅니다
      }
    },
    orderBy: { createdAt: 'desc' },
  });

  return (
    <div>
      {/* 화면 제목에 현재 카테고리 이름을 띄워줍니다 */}
      <h2 className="page-title">📂 {currentCategory}</h2>
      
      {/* 2. 해당 카테고리에 글이 없을 때 */}
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>{currentCategory} 카테고리에 아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        /* 3. 해당 카테고리의 글이 있으면 카드로 뿌려줍니다 */
        <div className="article-grid">
          {posts.map((post) => {
            const thumbnailUrl = post.images.length > 0 ? post.images[0] : 'https://via.placeholder.com/800x500.png?text=No+Image';

            return (
              <Link href={`/${params.category.toLowerCase()}/${post.id}`} key={post.id} className="article-card">
                <div className="image-wrapper">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                <div className="card-content">
                  <div className="card-category">{post.category.toUpperCase()}</div>
                  <h3 className="card-title">{post.title}</h3>
                  <p className="card-desc">
                    {post.content.length > 100 ? post.content.substring(0, 100) + '...' : post.content}
                  </p>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
}
