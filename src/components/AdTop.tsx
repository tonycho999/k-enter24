// src/components/AdTop.tsx
'use client'; 

import Link from 'next/link';

export default function AdTop() {
  return (
    <div style={{
      width: '100%',
      maxWidth: '1200px',
      margin: '0 auto 30px auto',
      padding: '0 20px',
      boxSizing: 'border-box'
    }}>
      <Link href="https://invl.me/clo2vf4" target="_blank" rel="noopener noreferrer" style={{ display: 'block', textDecoration: 'none' }}>
        <div style={{
          position: 'relative',
          borderRadius: '16px',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          padding: '40px 30px',
          color: '#ffffff',
          boxShadow: '0 10px 30px rgba(0,0,0,0.12)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          minHeight: '180px',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-4px)';
          e.currentTarget.style.boxShadow = '0 15px 35px rgba(0,0,0,0.2)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 10px 30px rgba(0,0,0,0.12)';
        }}
        >
          {/* 1. 고화질 배경 이미지 (Unsplash 무료 이미지 활용) */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundImage: 'url("https://images.unsplash.com/photo-1520356417937-23b9d0339ab3?auto=format&fit=crop&w=1200&q=80")',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            zIndex: 0
          }} />
          
          {/* 2. 글씨가 잘 보이도록 깔아주는 다크 그라데이션 마스크 */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'linear-gradient(to right, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.7) 50%, rgba(15, 23, 42, 0.1) 100%)',
            zIndex: 1
          }} />

          {/* 3. 텍스트 및 버튼 콘텐츠 영역 */}
          <div style={{ position: 'relative', zIndex: 2, maxWidth: '600px' }}>
            
            {/* 프로모션 태그 배지 */}
            <span style={{ 
              display: 'inline-block', 
              backgroundColor: '#0ea5e9', 
              color: 'white', 
              padding: '4px 10px', 
              borderRadius: '4px', 
              fontSize: '12px', 
              fontWeight: '700', 
              letterSpacing: '1px', 
              marginBottom: '12px',
              textTransform: 'uppercase'
            }}>
              ✈️ TRAVEL DEAL
            </span>
            
            <h3 style={{ fontSize: '26px', fontWeight: '800', margin: '0 0 10px 0', lineHeight: '1.3' }}>
              Discover the Best of Korea with KKday
            </h3>
            
            <p style={{ fontSize: '15px', color: '#e2e8f0', margin: '0 0 24px 0', lineHeight: '1.6' }}>
              Exclusive deals on K-Pop tours, hanbok rentals, theme parks, and authentic cultural experiences.
            </p>
            
            {/* 클릭을 유도하는 강렬한 오렌지색 CTA 버튼 */}
            <div style={{
              display: 'inline-block',
              backgroundColor: '#f59e0b',
              color: '#ffffff',
              padding: '12px 26px',
              borderRadius: '30px',
              fontSize: '15px',
              fontWeight: '800',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              boxShadow: '0 4px 10px rgba(245, 158, 11, 0.4)',
            }}>
              Explore Offers &rarr;
            </div>
            
          </div>
        </div>
      </Link>
    </div>
  );
}
