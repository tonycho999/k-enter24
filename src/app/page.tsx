// src/app/page.tsx
import Link from 'next/link';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
export const dynamic = 'force-dynamic';
export const revalidate = 60; 

export default async function Home() {
  // 1. Supabase DB에서 최신 글 목록을 가져옵니다. (최신순 정렬)
  const posts = await prisma.post.findMany({
    orderBy: { createdAt: 'desc' },
    // 일단 화면이 꽉 차 보이도록 최근 12개만 가져옵니다.
    take: 12, 
  });

  return (
    <div>
      {/* 2. DB에 글이 아직 하나도 없을 때 보여줄 안내 화면 */}
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        /* 3. DB에서 가져온 글이 있다면 예쁜 카드로 반복해서 그려줍니다! */
        <div className="article-grid">
          {posts.map((post) => {
            // DB의 images 배열에서 첫 번째 이미지를 썸네일로 사용! (이미지가 없으면 기본 회색 배경)
            const thumbnailUrl = post.images.length > 0 ? post.images[0] : 'https://via.placeholder.com/800x500.png?text=No+Image';

            return (
              <Link href={`/${post.category.toLowerCase()}/${post.id}`} key={post.id} className="article-card">
                <div className="image-wrapper">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                <div className="card-content">
                  <div className="card-category">{post.category.toUpperCase()}</div>
                  <h3 className="card-title">{post.title}</h3>
                  {/* content 본문이 너무 길 수 있으니 앞에서부터 100글자만 잘라서 미리보기로 보여줍니다 */}
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
