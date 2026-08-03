import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

export const metadata: Metadata = {
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
};

export default function RootLayout({ children }: { children: React.ReactNode; }) {
  return (
    <html lang="en">
      <body>
        <div className="magazine-layout">
          
          {/* 상단 1: 로고 & 검색바 */}
          <header className="header-top">
            <Link href="/" className="logo">K-ENTER 24</Link>
            <div className="search-bar">
              <input type="text" placeholder="Search news, idols, drama..." />
              🔍
            </div>
          </header>

          {/* 상단 2: 메인 카테고리 메뉴 (확실한 링크) */}
          <nav className="nav-menu">
            <Link href="/k-pop" className="nav-link">K-POP</Link>
            <Link href="/k-drama" className="nav-link">K-DRAMA</Link>
            <Link href="/k-movie" className="nav-link">K-MOVIE</Link>
            <Link href="/k-entertainment" className="nav-link">K-ENTERTAINMENT</Link>
            <Link href="/k-culture" className="nav-link">K-CULTURE</Link>
          </nav>

          {/* 상단 3: 상단 메인 광고 배너 (나중에 AdBannerTop 컴포넌트로 교체) */}
          <div className="ad-banner-top">
            Google AdSense Top Banner (728x90)
          </div>

          {/* 하단 본문 영역 (좌우 광고 + 중앙 콘텐츠) */}
          <div className="content-area-with-ads">
            {/* 좌측 광고 배너 공간 */}
            <aside className="ad-sidebar">Left Ad (160x600)</aside>

            {/* 중앙 메인 콘텐츠 (page.tsx 가 들어오는 곳) */}
            <main className="main-content">
              {children}
            </main>

            {/* 우측 광고 배너 공간 */}
            <aside className="ad-sidebar">Right Ad (160x600)</aside>
          </div>

        </div>
      </body>
    </html>
  );
}
