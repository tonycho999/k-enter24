// src/app/[category]/[id]/page.tsx
import { notFound } from 'next/navigation';
// 🚀 피드백 반영: 절대 경로 사용
import { getPostById } from '@/lib/blogger';
import { Metadata } from 'next';

export async function generateMetadata({ params }: { params: { id: string, category: string } }): Promise<Metadata> {
  const post = await getPostById(params.id);
  
  if (!post) {
    return { title: 'Post Not Found | K-ENTER 24' };
  }

  // 🚀 피드백 반영: Description 똑똑하게 추출하기 (JSON-LD 우선, 없으면 텍스트 추출)
  let description = '';
  try {
    const scriptMatch = post.content.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
    if (scriptMatch && scriptMatch[1]) {
      const jsonData = JSON.parse(scriptMatch[1]);
      if (jsonData && jsonData.description) {
        description = jsonData.description; 
      }
    }
  } catch (e) {}

  // JSON에 description이 없었을 경우를 위한 백업 (텍스트 추출 후 155자에서 깔끔하게 ... 처리)
  if (!description) {
    let plainText = post.content.replace(/<(style|script)[^>]*>[\s\S]*?<\/\1>/gi, '');
    plainText = plainText.replace(/<[^>]*>?/gm, '');
    plainText = plainText.replace(/\s+/g, ' ').trim();
    description = plainText.length > 155 ? plainText.substring(0, 155) + '...' : plainText;
  }

  // 🚀 기사의 최종 주소 (Canonical URL용)
  const postUrl = `https://k-enter24.com/${params.category.toLowerCase()}/${post.id}`;

  return {
    title: `${post.title} | K-ENTER 24`,
    description: description,
    
    // 🚀 피드백 1: Canonical URL 추가 (구글에게 이 주소가 진짜 원본이라고 알려줌)
    alternates: {
      canonical: postUrl,
    },
    
    openGraph: {
      title: post.title,
      description: description,
      images: [post.thumbnail || 'https://k-enter24.com/og-image.png'],
      // 🚀 피드백 2: OG 누락 속성 추가
      url: postUrl,
      siteName: 'K-ENTER 24',
      type: 'article',
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: description,
      images: [post.thumbnail || 'https://k-enter24.com/og-image.png'],
    }
  };
}

export default async function PostDetailPage({ params }: { params: { id: string, category: string } }) {
  const post = await getPostById(params.id);

  if (!post) {
    notFound();
  }

  return (
    <article className="post-detail-container">
      <header className="post-header" style={{ marginBottom: '30px', borderBottom: '2px solid #000', paddingBottom: '20px' }}>
        <div style={{ color: '#ef4444', fontWeight: 'bold', marginBottom: '10px', textTransform: 'uppercase' }}>
          {params.category.replace('-', ' ')}
        </div>
        
        <h1 style={{ fontSize: '2.5rem', fontWeight: '900', lineHeight: '1.2', marginBottom: '15px' }}>
          {post.title}
        </h1>
        
        <time 
          dateTime={new Date(post.publishedAt).toISOString()} // 🚀 피드백 반영: 구글 봇이 읽기 좋은 표준 포맷
          style={{ color: '#64748b', fontSize: '0.95rem' }}
        >
          {new Date(post.publishedAt).toLocaleDateString('en-US', { 
            timeZone: 'Asia/Seoul', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </time>
      </header>

      {/* 🚀 본문 영역 */}
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
