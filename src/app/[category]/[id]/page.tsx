// src/app/[category]/[id]/page.tsx
import { PrismaClient } from '@prisma/client';
import { notFound } from 'next/navigation';

const prisma = new PrismaClient();

export const revalidate = 3600;

export default async function PostDetail({ params }: { params: { category: string, id: string } }) {
  const postId = parseInt(params.id, 10);

  if (isNaN(postId)) { notFound(); }

  const post = await prisma.post.findUnique({
    where: { id: postId },
  });

  if (!post) { notFound(); }

  // 💡 [수정] 실제 줄바꿈(\n)뿐만 아니라 텍스트로 들어간 리터럴 '\n'도 함께 분리하도록 정규식 개선
  const paragraphs = post.content.split(/(?:\r?\n|\\n)+/).filter(p => p.trim() !== '');

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

        {paragraphs.map((paragraph, index) => {
          // 🚀 [수정] 아마존 링크가 포함된 문단 처리
          if (paragraph.toLowerCase().includes('amazon.com')) {
            const urlMatch = paragraph.match(/(https?:\/\/[^\s]+)/);
            const url = urlMatch ? urlMatch[0] : '#';
            
            // URL과 🛒 기호를 제거한 나머지 문장 (일반 텍스트용)
            const remainingText = paragraph
              .replace(/(https?:\/\/[^\s]+)/, '')
              .replace(/🛒/g, '')
              .trim();

            return (
              <div key={index}>
                {/* 만약 링크 외에 다른 텍스트(설명글)가 있다면 버튼 위에 일반 문단으로 먼저 출력 */}
                {remainingText && (
                  <p>{remainingText}</p>
                )}
                
                {/* 아마존 버튼은 독립된 영역으로만 출력 */}
                <div className="amazon-banner-wrapper">
                  <a href={url} target="_blank" rel="noopener noreferrer" className="amazon-banner-btn">
                    <span className="amazon-icon">🛒</span>
                    <span className="amazon-text">Buy on Amazon</span>
                  </a>
                </div>
              </div>
            );
          }

          return (
            <div key={index}>
              {/* 일반 문단은 그대로 출력 */}
              <p>{paragraph}</p>
              
              {/* 문단 사이에 서브 이미지 삽입 */}
              {index === 1 && post.images && post.images.length > 1 && (
                <div className="post-main-image">
                  <img src={post.images[1]} alt="Sub Image 1" />
                </div>
              )}
              
              {index === 3 && post.images && post.images.length > 2 && (
                <div className="post-main-image">
                  <img src={post.images[2]} alt="Sub Image 2" />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </article>
  );
}
