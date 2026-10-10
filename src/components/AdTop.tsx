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
      <Link href="https://invl.me/clo2vf4" target="_blank" rel="sponsored nofollow noopener noreferrer"  style={{ display: 'block', textDecoration: 'none' }}>
        <div style={{
          position: 'relative',
          borderRadius: '12px', // 모서리 둥글기 살짝 축소
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between', // 텍스트는 왼쪽, 버튼은 오른쪽으로 가로 배치
          padding: '20px 30px', // 위아래 여백을 40px에서 20px로 절반 축소
          color: '#ffffff',
          boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          flexWrap: 'wrap', // 모바일에서는 자연스럽게 줄바꿈 되도록 설정
          gap: '16px'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-3px)';
          e.currentTarget.style.boxShadow = '0 12px 30px rgba(0,0,0,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.1)';
        }}
        >
          {/* 1. 배경 이미지 */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            backgroundImage: 'url("https://images.unsplash.com/photo-1520356417937-23b9d0339ab3?auto=format&fit=crop&w=1200&q=80")',
            backgroundSize: 'cover',
            backgroundPosition: 'center 30%', // 이미지가 잘릴 때 약간 윗부분이 보이도록 조정
            zIndex: 0
          }} />
          
          {/* 2. 다크 그라데이션 마스크 (오른쪽으로 갈수록 투명해짐) */}
          <div style={{
            position: 'absolute',
            top: 0, left: 0, right: 0, bottom: 0,
            background: 'linear-gradient(to right, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.75) 60%, rgba(15, 23, 42, 0.3) 100%)',
            zIndex: 1
          }} />

          {/* 3. 왼쪽 텍스트 영역 */}
          <div style={{ position: 'relative', zIndex: 2, flex: '1 1 auto', maxWidth: '750px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
              <span style={{ 
                backgroundColor: '#0ea5e9', 
                color: 'white', 
                padding: '3px 8px', 
                borderRadius: '4px', 
                fontSize: '11px', 
                fontWeight: '700', 
                letterSpacing: '0.5px',
                textTransform: 'uppercase'
              }}>
                ✈️ TRAVEL DEAL
              </span>
              <h3 style={{ fontSize: '20px', fontWeight: '800', margin: 0, lineHeight: '1.2' }}>
                Discover the Best of Korea with KKday
              </h3>
            </div>
            <p style={{ fontSize: '14px', color: '#e2e8f0', margin: 0, lineHeight: '1.4' }}>
              Exclusive deals on K-Pop tours, hanbok rentals, theme parks, and authentic cultural experiences.
            </p>
          </div>

          {/* 4. 오른쪽 버튼 영역 */}
          <div style={{ position: 'relative', zIndex: 2, flexShrink: 0 }}>
            <div style={{
              display: 'inline-block',
              backgroundColor: '#f59e0b',
              color: '#ffffff',
              padding: '10px 24px', // 버튼 크기 살짝 축소
              borderRadius: '30px',
              fontSize: '14px',
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
