// src/app/[category]/page.tsx
import Link from 'next/link';
// 절대 경로 적용
import { getPosts } from '@/lib/blogger';

export default async function CategoryPage({ params }: { params: { category: string } }) {
  // 1. URL에서 카테고리 이름 가져오기 (예: 'k-pop')
  const rawCategory = params.category;
  
  // URL의 'k-pop'을 Blogger 라벨 형태인 'K-POP'으로 변환
  const categoryLabel = rawCategory.toUpperCase();

  // 2. 해당 카테고리(라벨)의 글만 가져오기
  const posts = await getPosts(categoryLabel);

  // 🚀 Blogger 본문 내의 JSON-LD에서 description 추출
  const extractDescription = (html: string) => {
    if (!html) return '';

    try {
      const scriptMatch = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
      if (scriptMatch && scriptMatch[1]) {
        const jsonData = JSON.parse(scriptMatch[1]);
        if (jsonData && jsonData.description) {
          return jsonData.description; 
        }
      }
    } catch (e) {
      console.error("JSON parsing error in extractDescription", e);
    }

    // JSON-LD가 없을 때의 방어 코드
    let text = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');
    text = text.replace(/<[^>]*>?/gm, '');
    text = text.replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    text = text.trim();
    
    return text.length > 150 ? text.substring(0, 150) + '...' : text;
  };

  return (
    <div>
      <div className="page-header">
        {/* 현재 보고 있는 카테고리 이름을 타이틀로 출력 */}
        <h2 className="page-title">🔥 {categoryLabel} NEWS</h2>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>해당 카테고리에 아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            
            // 새로 만든 함수로 description 추출
            const description = extractDescription(post.content);

            return (
              <Link href={`/${rawCategory}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                
                <div className="list-content">
                  <div className="list-category">{categoryLabel}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">{description}</p>
  <div className="list-date">
    {/* timeZone: 'Asia/Seoul' 옵션을 추가하여 한국 시간으로 계산하여 표시합니다 */}
    {new Date(post.publishedAt).toLocaleDateString('en-US', { 
      timeZone: 'Asia/Seoul', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    })}
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
