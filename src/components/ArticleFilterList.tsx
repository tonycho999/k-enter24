// src/components/ArticleFilterList.tsx
'use client'; 

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { BlogPost } from '@/lib/blogger';

export default function ArticleFilterList({ initialPosts }: { initialPosts: BlogPost[] }) {
  const currentYear = new Date().getFullYear();
  const [selectedYear, setSelectedYear] = useState<number>(currentYear);
  const [selectedMonth, setSelectedMonth] = useState<number | null>(null); 

  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

  const getPostYearMonth = (dateString: string) => {
    const dateObj = new Date(dateString);
    const kstYear = dateObj.toLocaleDateString('en-US', { timeZone: 'Asia/Seoul', year: 'numeric' });
    const kstMonth = dateObj.toLocaleDateString('en-US', { timeZone: 'Asia/Seoul', month: 'numeric' });
    return { year: Number(kstYear), month: Number(kstMonth) };
  };

  const availableMonths = Array.from(new Set(
    initialPosts
      .filter(post => getPostYearMonth(post.publishedAt).year === selectedYear)
      .map(post => getPostYearMonth(post.publishedAt).month)
  )).sort((a, b) => b - a);

  // 컴포넌트가 로드되면 최신 달로 자동 세팅
  useEffect(() => {
    if (initialPosts.length > 0 && selectedMonth === null && availableMonths.length > 0) {
      setSelectedMonth(availableMonths[0]);
    }
  }, [initialPosts, selectedMonth, availableMonths]);

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
    return text.trim().length > 150 ? text.trim().substring(0, 150) + '...' : text.trim();
  };

  const filteredPosts = initialPosts.filter(post => {
    if (selectedMonth === null) return false; 
    const postDate = getPostYearMonth(post.publishedAt);
    return postDate.year === selectedYear && postDate.month === selectedMonth;
  });

  return (
    <div>
      <div className="page-header">
        <h2 className="page-title">🔥 Trending K-Culture</h2>
        
        <div style={{ marginBottom: '20px' }}>
          <div className="year-filter" style={{ marginBottom: '10px' }}>
            <button 
              className={`year-btn ${selectedYear === currentYear ? 'active' : ''}`}
              onClick={() => {
                setSelectedYear(currentYear);
                setSelectedMonth(null); 
              }}
            >
              {currentYear}
            </button>
          </div>

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
                  {monthNames[monthNum - 1]}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {filteredPosts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '100px 0', color: '#64748b' }}>
          <h3>기사가 존재하지 않습니다.</h3>
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
