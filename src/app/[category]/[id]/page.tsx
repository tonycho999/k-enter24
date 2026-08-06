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
        {post.images && post.images.length > 0 && (
          <div className="post-main-image">
            <img src={post.images[0]} alt="Article Main Image" />
          </div>
        )}

        {paragraphs.map((paragraph, index) => {
          // 🚀 [핵심 추가] 아마존 링크가 포함된 문단인지 감지합니다!
          if (paragraph.toLowerCase().includes('amazon.com')) {
            // 정규식으로 'https://...' 주소만 쏙 뽑아냅니다.
            const urlMatch = paragraph.match(/(https?:\/\/[^\s]+)/);
            const url = urlMatch ? urlMatch[0] : '#';
            
            // 주소와 🛒 기호를 제외한 나머지 안내 문구만 뽑아냅니다.
            const btnText = paragraph.replace(/(https?:\/\/[^\s]+)/, '').replace('🛒', '').trim() || 'Buy on Amazon';

            return (
              <div key={index} className="amazon-banner-wrapper">
                <a href={url} target="_blank" rel="noopener noreferrer" className="amazon-banner-btn">
                  <span className="amazon-icon">🛒</span>
                  <span className="amazon-text">{btnText}</span>
                </a>
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
