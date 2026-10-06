// src/app/page.tsx
'use client'; 

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getPosts, BlogPost } from '@/lib/blogger';

export default function Home() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null); // 처음에는 최신 기사가 있는 달로 자동 설정되게 만듦

  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  useEffect(() => {
    async function fetchPosts() {
      const data = await getPosts(undefined, 100);
      setPosts(data);
      
      // 🚀 데이터가 로드되면, 가장 '최근 기사가 있는 달'을 찾아서 기본 선택 달로 설정합니다.
      if (data.length > 0) {
        // 첫 번째 기사(가장 최신 기사)의 달을 찾음
        const firstPostDate = new Date(data[0].publishedAt);
        // getMonth()는 0부터 시작하므로 +1 안하고 문자열 매칭용으로 씁니다 (안전한 파싱)
        const latestMonth = Number(firstPostDate.toLocaleDateString('en-US', { timeZone: 'Asia/Seoul', month: 'numeric' }));
        setSelectedMonth(latestMonth);
      }
      setLoading(false);
    }
    fetchPosts();
  }, []);

  const extractDescription = (html: string) => {
    if (!html) return '';
    try {
      const scriptMatch = html.match(/<script[^>]*type="application\/ld\+json"[^>]*>([\s\S]*?)<\/script>/i);
      if (scriptMatch && scriptMatch[1]) {
        const jsonData = JSON.parse(scriptMatch[1]);
        if (jsonData && jsonData.description) return jsonData.description; 
      }
    } catch (e) {}

    let text = html.replace(/<(script|style)[^>]*>[\s\S]*?<\/\1>/gi, '');
    text = text.replace(/<[^>]*>?/gm, '');
    text = text.replace(/&nbsp;/g, ' ').replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>');
    text = text.trim();
    return text.length > 150 ? text.substring(0, 150) + '...' : text;
  };

  // 🚀 핵심: 기사에서 한국 시간(KST) 기준의 연/월을 안전하게 추출하는 헬퍼 함수
  const getPostYearMonth = (dateString: string) => {
    // toLocaleDateString을 이용해 강제로 한국 시간 기준의 숫자를 뽑아냅니다. (오류 제로)
    const kstYear = new Date(dateString).toLocaleDateString('en-US', { timeZone: 'Asia/Seoul', year: 'numeric' });
    const kstMonth = new Date(dateString).toLocaleDateString('en-US', { timeZone: 'Asia/Seoul', month: 'numeric' });
    return { year: Number(kstYear), month: Number(kstMonth) };
  };

  // 1. 우리가 불러온 모든 기사를 쭉 스캔해서 "기사가 존재하는 달" 목록만 뽑아냅니다. (중복 제거)
  const availableMonths = Array.from(new Set(
    posts
      .filter(post => getPostYearMonth(post.publishedAt).year === selectedYear) // 현재 선택된 연도에 해당하는 글만 대상
      .map(post => getPostYearMonth(post.publishedAt).month)
  )).sort((a, b) => b - a); // 최신 달(12월)부터 역순으로 보여주도록 정렬

  // 2. 현재 선택된 연도와 월에 해당하는 기사만 솎아냅니다.
  const filteredPosts = posts.filter(post => {
    const postDate = getPostYearMonth(post.publishedAt);
    return postDate.year === selectedYear && postDate.month === selectedMonth;
  });

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        <div style={{ marginBottom: '20px' }}>
          {/* 연도 버튼 */}
          <div className="year-filter" style={{ marginBottom: '10px' }}>
            <button 
              className={`year-btn ${selectedYear === currentYear ? 'active' : ''}`}
              onClick={() => {
                setSelectedYear(currentYear);
                // 연도를 바꿨을 때 그 연도의 기사가 없으면 에러가 날 수 있으니 방어
                setSelectedMonth(null); 
              }}
            >
              {currentYear}
            </button>
          </div>

          {/* 🚀 기사가 있는 월(Month)만 렌더링하는 버튼 영역 */}
          {availableMonths.length > 0 && (
            <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px', whiteSpace: 'nowrap' }}>
              {availableMonths.map((monthNum) => (
                <button
                  key={monthNum}
                  onClick={() => setSelectedMonth(monthNum)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    border: '1px solid #cbd5e1',
                    background: selectedMonth === monthNum ? '#0f172a' : '#ffffff',
                    color: selectedMonth === monthNum ? '#ffffff' : '#475569',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: selectedMonth === monthNum ? 'bold' : 'normal'
                  }}
                >
                  {/* monthNames 배열은 0부터 시작하므로 monthNum - 1을 씁니다 */}
                  {monthNames[monthNum - 1]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <p>Loading K-Culture trends...</p>
        </div>
      ) : filteredPosts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>기사가 존재하지 않습니다. 다른 탭을 클릭해 보세요.</h3>
        </div>
      ) : (
        <div className="article-list">
          {filteredPosts.map((post) => {
            const thumbnailUrl = post.thumbnail || 'https://k-enter24.com/og-image.png';
            const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
            const description = extractDescription(post.content);

            return (
              <Link href={`/${category.toLowerCase()}/${post.id}`} key={post.id} className="list-card">
                <div className="list-image">
                  <img src={thumbnailUrl} alt={post.title} />
                </div>
                <div className="list-content">
                  <div className="list-category">{category.toUpperCase()}</div>
                  <h3 className="list-title">{post.title}</h3>
                  <p className="list-desc">{description}</p>
                  <div className="list-date">
                    {new Date(post.publishedAt).toLocaleDateString('en-US', { 
                      timeZone: 'Asia/Seoul', year: 'numeric', month: 'long', day: 'numeric' 
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
