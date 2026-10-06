// src/app/page.tsx
'use client'; // 필터 버튼 클릭 상태를 관리하기 위해 클라이언트 컴포넌트로 변경

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { getPosts, BlogPost } from '@/lib/blogger';

export default function Home() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  
  // 현재 연도와 월을 기본값으로 설정 (월은 1~12 숫자)
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth() + 1; 
  
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);
  const [selectedMonth, setSelectedMonth] = useState<number>(currentMonth);

  // 영어 월 이름 매핑 (버튼 텍스트용)
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  useEffect(() => {
    async function fetchPosts() {
      // 넉넉하게 100개를 가져와서 클라이언트에서 필터링합니다.
      const data = await getPosts(undefined, 100);
      setPosts(data);
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

  // 🚀 선택된 연도와 월에 맞는 기사만 걸러내기 (필터링)
  const filteredPosts = posts.filter(post => {
    // 기사 발행 시간을 한국 시간(KST)으로 맞춰서 연/월을 뽑아냅니다.
    const date = new Date(post.publishedAt);
    date.setHours(date.getHours() + 9); 
    
    const postYear = date.getFullYear();
    const postMonth = date.getMonth() + 1;

    return postYear === selectedYear && postMonth === selectedMonth;
  });

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        {/* 🚀 연도별 & 월별 필터 UI 영역 */}
        <div style={{ marginBottom: '20px' }}>
          
          {/* 1. 연도 버튼들 (필요시 2025, 2024 추가 가능) */}
          <div className="year-filter" style={{ marginBottom: '10px' }}>
            <button 
              className={`year-btn ${selectedYear === currentYear ? 'active' : ''}`}
              onClick={() => setSelectedYear(currentYear)}
            >
              {currentYear}
            </button>
            {/* 예시: 작년 버튼 <button className={`year-btn ${selectedYear === 2025 ? 'active' : ''}`} onClick={() => setSelectedYear(2025)}>2025</button> */}
          </div>

          {/* 2. 월별 버튼들 (가로 스크롤 가능하게 flex로 나열) */}
          <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '10px', whiteSpace: 'nowrap' }}>
            {monthNames.map((month, index) => {
              const monthNumber = index + 1;
              return (
                <button
                  key={month}
                  onClick={() => setSelectedMonth(monthNumber)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '20px',
                    border: '1px solid #cbd5e1',
                    background: selectedMonth === monthNumber ? '#0f172a' : '#ffffff',
                    color: selectedMonth === monthNumber ? '#ffffff' : '#475569',
                    cursor: 'pointer',
                    fontSize: '14px',
                    fontWeight: selectedMonth === monthNumber ? 'bold' : 'normal'
                  }}
                >
                  {month}
                </button>
              );
            })}
          </div>

        </div>
      </div>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <p>Loading K-Culture trends...</p>
        </div>
      ) : filteredPosts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>{monthNames[selectedMonth - 1]} {selectedYear}에 등록된 기사가 없습니다.</h3>
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
