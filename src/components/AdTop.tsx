'use client';

import { useEffect, useState } from 'react';

type Banner = {
  url: string;
  badge: string;
  title: string;
  desc: string;
  button: string;
  image: string;
  badgeColor: string;
  weight: number; // 노출 비율
};

const BANNERS: Banner[] = [
  {
    url: 'https://invl.me/clo41he',
    badge: '✈️ FLIGHT DEAL',
    title: 'Find Cheap Flights to Korea with Kiwi.com',
    desc: 'Compare flights to Seoul and Busan, mix airlines, and find smarter routes for your trip.',
    button: 'Search Flights',
    image: 'https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1200&q=80',
    badgeColor: '#00a991',
    weight: 70,
  },
  {
    url: 'https://invl.me/clo2vf4',
    badge: '✈️ TRAVEL DEAL',
    title: 'Discover the Best of Korea with KKday',
    desc: 'Tours, attraction tickets, eSIMs, and airport transfers for your Korea trip.',
    button: 'Explore Offers',
    image: 'https://images.unsplash.com/photo-1520356417937-23b9d0339ab3?auto=format&fit=crop&w=1200&q=80',
    badgeColor: '#0ea5e9',
    weight: 30,
  },
];

// 비율(weight)에 따라 배너 하나 선택
function pickBanner(): Banner {
  const total = BANNERS.reduce((sum, b) => sum + b.weight, 0);
  let r = Math.random() * total;
  for (const b of BANNERS) {
    if (r < b.weight) return b;
    r -= b.weight;
  }
  return BANNERS[0];
}

export default function AdTop() {
  const [banner, setBanner] = useState<Banner | null>(null);

  // 브라우저에서만 선택 (hydration 오류 방지)
  useEffect(() => {
    setBanner(pickBanner());
  }, []);

  return (
    <div style={{ width: '100%', maxWidth: '1200px', margin: '0 auto 30px auto', padding: '0 20px', boxSizing: 'border-box' }}>
      {/* 배너 선택 전: 같은 높이의 빈칸으로 레이아웃 흔들림 방지 */}
      {!banner ? (
        <div style={{ minHeight: '90px', borderRadius: '12px', backgroundColor: '#f1f5f9' }} />
      ) : (
        <a href={banner.url} target="_blank" rel="sponsored nofollow noopener noreferrer" style={{ display: 'block', textDecoration: 'none' }}>
          <div
            style={{
              position: 'relative',
              borderRadius: '12px',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '20px 30px',
              minHeight: '90px',
              color: '#ffffff',
              boxShadow: '0 8px 25px rgba(0,0,0,0.1)',
              transition: 'transform 0.3s ease, box-shadow 0.3s ease',
              flexWrap: 'wrap',
              gap: '16px',
              boxSizing: 'border-box',
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
            <div
              style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                backgroundImage: `url("${banner.image}")`,
                backgroundSize: 'cover',
                backgroundPosition: 'center 30%',
                zIndex: 0,
              }}
            />

            {/* 2. 다크 그라데이션 마스크 */}
            <div
              style={{
                position: 'absolute',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'linear-gradient(to right, rgba(15, 23, 42, 0.9) 0%, rgba(15, 23, 42, 0.75) 60%, rgba(15, 23, 42, 0.3) 100%)',
                zIndex: 1,
              }}
            />

            {/* 3. 왼쪽 텍스트 영역 */}
            <div style={{ position: 'relative', zIndex: 2, flex: '1 1 auto', maxWidth: '750px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
                <span
                  style={{
                    backgroundColor: banner.badgeColor,
                    color: 'white',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    fontSize: '11px',
                    fontWeight: 700,
                    letterSpacing: '0.5px',
                    textTransform: 'uppercase',
                  }}
                >
                  {banner.badge}
                </span>
                <div style={{ fontSize: '20px', fontWeight: 800, margin: 0, lineHeight: 1.2 }}>{banner.title}</div>
              </div>
              <p style={{ fontSize: '14px', color: '#e2e8f0', margin: 0, lineHeight: 1.4 }}>{banner.desc}</p>
            </div>

            {/* 4. 오른쪽 버튼 영역 */}
            <div style={{ position: 'relative', zIndex: 2, flexShrink: 0 }}>
              <div
                style={{
                  display: 'inline-block',
                  backgroundColor: '#f59e0b',
                  color: '#ffffff',
                  padding: '10px 24px',
                  borderRadius: '30px',
                  fontSize: '14px',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                  boxShadow: '0 4px 10px rgba(245, 158, 11, 0.4)',
                }}
              >
                {banner.button} &rarr;
              </div>
            </div>
          </div>
        </a>
      )}
    </div>
  );
}
