// src/app/page.tsx
import Link from 'next/link';
// 절대 경로를 사용하여 에러를 방지합니다.
import { getPosts } from '@/lib/blogger';

export default async function Home() {
  // Blogger API에서 최신 글(최대 20개)을 가져옵니다.
  const posts = await getPosts();
  const currentYear = new Date().getFullYear();

  // 🚀 Blogger 본문 내의 JSON-LD에서 description 추출 (가장 깔끔한 방법)
  const extractDescription = (html: string) => {
    if (!html) return '';

    try {
      const scriptMatch = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
      if (scriptMatch && scriptMatch[1]) {
        const jsonData = JSON.parse(scriptMatch[1]);
        if (jsonData && jsonData.description) {
          // JSON 안에 description이 있으면 바로 반환
          return jsonData.description; 
        }
      }
    } catch (e) {
      console.error("JSON parsing error in extractDescription", e);
    }

    // JSON-LD가 없거나 파싱에 실패했을 경우를 위한 방어 코드 (순수 텍스트 150자 추출)
    let text = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');
    text = text.replace(/<[^>]*>?/gm, '');
    text = text.replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    text = text.trim();
    
    return text.length > 150 ? text.substring(0, 150) + '...' : text;
  };

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        {/* 연도별 필터 버튼 */}
        <div className="year-filter">
          <button className="year-btn active">{currentYear}</button>
        </div>
      </div>
      
      {posts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>아직 등록된 기사가 없습니다.</h3>
        </div>
      ) : (
        <div className="article-list">
          {posts.map((post) => {
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
            
            // 우리가 새로 만든 함수를 사용하여 완벽한 요약본을 가져옵니다!
            const description = extractDescription(post.content);

            return (
              <Link href={`/${category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                {/* 왼쪽: 썸네일 */}
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                
                {/* 오른쪽: 텍스트 정보 */}
                <div className="list-content">
                  <div className="list-category">{category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  {/* 추출한 description을 그대로 출력합니다 */}
                  <p className="list-desc">{description}</p>
                  <div className="list-date">
                    {new Date(post.publishedAt).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })}
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
