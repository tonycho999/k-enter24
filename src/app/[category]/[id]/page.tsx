// src/app/[category]/[id]/page.tsx
import { notFound } from 'next/navigation';
import { getPostById } from '../../../lib/blogger';
import { Metadata } from 'next';

// 🚀 기사별 동적 SEO 메타데이터 생성 (공유 시 썸네일, 제목 자동 지정)
export async function generateMetadata({ params }: { params: { id: string, category: string } }): Promise<Metadata> {
  const post = await getPostById(params.id);
  
  if (!post) {
    return { title: 'Post Not Found | K-ENTER 24' };
  }

  const plainTextContent = post.content.replace(/<[^>]*>?/gm, '').substring(0, 160);

  return {
    title: `${post.title} | K-ENTER 24`,
    description: plainTextContent,
    openGraph: {
      title: post.title,
      description: plainTextContent,
      images: [post.thumbnail || 'https://k-enter24.com/og-image.png'],
    },
  };
}

export default async function PostDetailPage({ params }: { params: { id: string, category: string } }) {
  // 1. Blogger에서 해당 ID의 글 불러오기
  const post = await getPostById(params.id);

  // 글이 없으면 404 Not Found 페이지로 이동
  if (!post) {
    notFound();
  }

  return (
    <article className="post-detail-container">
      {/* 🚀 상단 헤더: 대형 제목, 카테고리, 날짜 */}
      <header className="post-header" style={{ marginBottom: '30px', borderBottom: '2px solid #000', paddingBottom: '20px' }}>
        <div style={{ color: '#ef4444', fontWeight: 'bold', marginBottom: '10px', textTransform: 'uppercase' }}>
          {params.category.replace('-', ' ')}
        </div>
        <h1 style={{ fontSize: '2.5rem', fontWeight: '900', lineHeight: '1.2', marginBottom: '15px' }}>
          {post.title}
        </h1>
        <time style={{ color: '#64748b', fontSize: '0.95rem' }}>
          {new Date(post.publishedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
        </time>
      </header>

      {/* 🚀 본문 영역: Blogger에서 작성한 HTML이 그대로 렌더링 됩니다. */}
      {/* 기획하신 '18px 폰트 및 1.9 줄간격의 가독성 높은 매거진 스타일'을 인라인 스타일로 적용 */}
      <div 
        className="post-content"
        style={{ 
          fontSize: '18px', 
          lineHeight: '1.9', 
          color: '#333',
          wordBreak: 'keep-all'
        }}
        dangerouslySetInnerHTML={{ __html: post.content }} 
      />
      
    </article>
  );
}
