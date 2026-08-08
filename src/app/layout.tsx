// src/app/layout.tsx
import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';
import AdTop from '../components/AdTop';
import AdLeft from '../components/AdLeft';
import AdRight from '../components/AdRight';
import SearchBar from '../components/SearchBar';

// 🚀 구글 서치콘솔 소유권 확인 태그 (SEO 핵심)
export const metadata: Metadata = {
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
  verification: {
    google: 'K7nILRoN2qJRl9Cfvp6tkRkddR_Q9YWz7GSd56MY05Y',
  },
  robots: {
    index: true,     // 구글에 이 페이지를 등록해라
    follow: true,    // 이 페이지에 있는 링크(기사들)도 다 따라가서 수집해라
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large', // 사진을 고화질로 긁어가서 구글 이미지 검색에 크게 띄워라
      'max-snippet': -1,            // 글 내용도 제한 없이 다 긁어가라
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="magazine-layout">
          
          {/* 상단 1: 로고 & 검색바 */}
          <header className="header-top">
            <Link href="/" className="logo">K-ENTER 24</Link>
            
            {/* 🚀 검색창 부품 장착! */}
            <SearchBar />
            
          </header>

          {/* 상단 2: 메인 카테고리 메뉴 (미리 다운로드 기능 prefetch=true 장착) */}
          <nav className="nav-menu">
            <Link href="/k-pop" prefetch={true} className="nav-link">K-POP</Link>
            <Link href="/k-drama" prefetch={true} className="nav-link">K-DRAMA</Link>
            <Link href="/k-movie" prefetch={true} className="nav-link">K-MOVIE</Link>
            <Link href="/k-entertainment" prefetch={true} className="nav-link">K-ENTERTAINMENT</Link>
            <Link href="/k-culture" prefetch={true} className="nav-link">K-CULTURE</Link>
          </nav>

          {/* 상단 3: 상단 메인 광고 배너 */}
          <AdTop />

          {/* 하단 본문 영역 (좌우 광고 + 중앙 콘텐츠) */}
          <div className="content-area-with-ads">
            
            {/* 좌측 광고 */}
            <AdLeft />

            {/* 🚀 중앙 메인 콘텐츠 (page.tsx 들이 들어오는 진짜 본문 영역) */}
            <main className="main-content">
              {children}
            </main>

            {/* 우측 광고 */}
            <AdRight />
            
          </div>

        </div>
      </body>
    </html>
  );
}
