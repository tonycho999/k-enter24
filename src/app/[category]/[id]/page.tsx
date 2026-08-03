// src/app/[category]/[id]/page.tsx
import { PrismaClient } from '@prisma/client';
import { notFound } from 'next/navigation';

const prisma = new PrismaClient();
export const dynamic = 'force-dynamic';

export default async function PostDetail({ params }: { params: { category: string, id: string } }) {
  // 1. URL에서 전달받은 id(문자열)를 숫자(Int)로 변환합니다.
  const postId = parseInt(params.id, 10);

  // 숫자가 아니면 404 에러 페이지로 보냅니다.
  if (isNaN(postId)) {
    notFound();
  }

  // 2. Prisma를 통해 Supabase DB에서 해당 id의 진짜 글을 가져옵니다.
  const post = await prisma.post.findUnique({
    where: { id: postId },
  });

  // DB에 해당 글이 없으면 404 에러 페이지로 보냅니다.
  if (!post) {
    notFound();
  }

  // 본문 내용을 줄바꿈(\n) 기준으로 배열로 나누어 문단(p 태그) 단위로 보여주기 위한 준비
  const paragraphs = post.content.split('\n').filter(p => p.trim() !== '');

  return (
    <article className="post-detail-container">
      {/* 카테고리 라벨 */}
      <div className="post-category-label">
        {post.category.toUpperCase()}
      </div>

      {/* 진짜 기사 제목 */}
      <h1 className="post-title">
        {post.title}
      </h1>

      {/* 날짜 정보 (DB에 저장된 createdAt 시간 표시) */}
      <div className="post-meta">
        <span>By K-ENTER 24</span>
        <span className="dot">·</span>
        <span>{post.createdAt.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
        <span className="dot">·</span>
        <span>👁️ {post.views} Views</span>
      </div>

      {/* 3. 진짜 본문과 이미지 배치 (영구 보존 블로그의 핵심 로직) */}
      <div className="post-body">
        
        {/* 메인 썸네일 이미지 (배열의 0번째 이미지) */}
        {post.images.length > 0 && (
          <div className="post-main-image">
            <img src={post.images[0]} alt="Main Article Image" />
          </div>
        )}

        {/* 본문을 문단(paragraph)별로 뿌려주고, 중간중간 남은 이미지를 섞어줍니다 */}
        {paragraphs.map((paragraph, index) => (
          <div key={index}>
            <p>{paragraph}</p>
            
            {/* 문단이 2개 지날 때마다 남아있는 이미지가 있다면 하나씩 꺼내어 보여줍니다 */}
            {index === 1 && post.images.length > 1 && (
              <div className="post-main-image" style={{ marginTop: '32px', marginBottom: '32px' }}>
                <img src={post.images[1]} alt="Sub Image 1" />
              </div>
            )}
            
            {/* 추가 이미지 (3번째 사진이 있다면) */}
            {index === 4 && post.images.length > 2 && (
              <div className="post-main-image" style={{ marginTop: '32px', marginBottom: '32px' }}>
                <img src={post.images[2]} alt="Sub Image 2" />
              </div>
            )}
          </div>
        ))}

      </div>
    </article>
  );
}
