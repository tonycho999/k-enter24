// src/app/search/page.tsx
import Link from 'next/link';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();
// 검색 결과는 검색어마다 다르므로 캐시하지 않고 무조건 실시간으로 DB에서 찾습니다.
export const dynamic = 'force-dynamic'; 

export default async function SearchPage({ searchParams }: { searchParams: { q: string } }) {
  // 주소창에서 '?q=검색어' 의 '검색어'를 빼냅니다.
  const keyword = searchParams.q || '';

  // DB에서 제목이나 본문에 검색어가 포함된 기사를 최신순으로 가져옵니다.
  const posts = await prisma.post.findMany({
    where: {
      OR: [
        { title: { contains: keyword, mode: 'insensitive' } },
        { content: { contains: keyword, mode: 'insensitive' } },
      ],
    },
    orderBy: { createdAt: 'desc' },
  });

  return (
    <div>
      <div className="page-header">
        {/* 화면 제목에 검색어와 검색 결과 개수를 띄워줍니다 */}
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
        /* 검색 결과를 예쁜 가로 리스트로 출력합니다! */
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.images.length > 0 ? post.images[0] : 'https://k-enter24.com/og-image.png';

            return (
              <Link href={`/${post.category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
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
