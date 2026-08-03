// src/app/[category]/[id]/page.tsx
import { PrismaClient } from '@prisma/client';
import { notFound } from 'next/navigation';

const prisma = new PrismaClient();
export const revalidate = 3600; // 1시간 캐시

export default async function PostDetail({ params }: { params: { category: string, id: string } }) {
  const postId = parseInt(params.id, 10);
  if (isNaN(postId)) { notFound(); }

  const post = await prisma.post.findUnique({
    where: { id: postId },
  });

  if (!post) { notFound(); }

  // 🚀 AI가 준 본문을 엔터(\n) 기준으로 완벽하게 쪼개서 배열로 만듭니다.
  const paragraphs = post.content.split(/\n+/).filter(p => p.trim() !== '');

  return (
    <article className="post-detail-container">
      <div className="post-category-label">
        {post.category.toUpperCase()}
      </div>

      <h1 className="post-title">
        {post.title}
      </h1>

      <div className="post-meta">
        <span>By K-ENTER 24 Editor</span>
        <span className="dot">•</span>
        <span>{post.createdAt.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
        <span className="dot">•</span>
        <span>👁️ {post.views} Views</span>
      </div>

      <div className="post-body">
        {/* 메인 이미지 */}
        {post.images && post.images.length > 0 && (
          <div className="post-main-image">
            <img src={post.images[0]} alt="Article Main Image" />
          </div>
        )}

        {/* 문단을 순서대로 뿌려주고, 중간에 이미지를 끼워 넣습니다 */}
        {paragraphs.map((paragraph, index) => (
          <div key={index}>
            <p>{paragraph}</p>
            
            {/* 문단 2개가 끝난 지점에 두 번째 사진 삽입 */}
            {index === 1 && post.images && post.images.length > 1 && (
              <div className="post-main-image">
                <img src={post.images[1]} alt="Sub Image 1" />
              </div>
            )}
            
            {/* 문단 4개가 끝난 지점에 세 번째 사진 삽입 */}
            {index === 3 && post.images && post.images.length > 2 && (
              <div className="post-main-image">
                <img src={post.images[2]} alt="Sub Image 2" />
              </div>
            )}
          </div>
        ))}
      </div>
    </article>
  );
}
