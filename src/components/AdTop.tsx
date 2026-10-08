// src/components/AdTop.tsx
'use client';
import Link from 'next/link';

export default function AdTop() {
  return (
    <div style={{
      width: '100%',
      maxWidth: '1200px', // 전체 매거진 레이아웃 너비에 맞춤
      margin: '0 auto 30px auto', // 배너 아래쪽 여백 추가
      padding: '0 20px', // 모바일에서 양옆 여백
      boxSizing: 'border-box'
    }}>
      {/* 🚀 target="_blank"를 추가해서 배너 클릭 시 새 창으로 열리도록 설정 */}
      <Link href="https://invl.me/clo2vf4" target="_blank" rel="noopener noreferrer" style={{ display: 'block', textDecoration: 'none' }}>
        <div style={{
          backgroundColor: '#06b6d4', // 여행 느낌의 청량한 시안 블루 컬러
          backgroundImage: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)', // 블루 그라데이션
          borderRadius: '12px',
          padding: '24px',
          color: '#ffffff',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
          transition: 'transform 0.2s ease, box-shadow 0.2s ease',
          cursor: 'pointer'
        }}
        // 마우스 올렸을 때 살짝 떠오르는 애니메이션 효과
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'translateY(-2px)';
          e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'translateY(0)';
          e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.1)';
        }}
        >
          {/* 배너 타이틀 */}
          <div style={{ fontSize: '20px', fontWeight: '800', letterSpacing: '0.5px', marginBottom: '8px', textAlign: 'center' }}>
            ✈️ Explore Korea with KKday
          </div>
          
          {/* 배너 서브 텍스트 */}
          <div style={{ fontSize: '14px', fontWeight: '500', opacity: '0.9', textAlign: 'center', marginBottom: '16px' }}>
            Book the best tours, activities, and tickets for your K-Culture journey!
          </div>
          
          {/* 배너 버튼 */}
          <div style={{
            backgroundColor: '#ffffff',
            color: '#3b82f6',
            padding: '10px 24px',
            borderRadius: '30px',
            fontSize: '14px',
            fontWeight: '700',
            textTransform: 'uppercase'
          }}>
            Book Now
          </div>
        </div>
      </Link>
    </div>
  );
}
