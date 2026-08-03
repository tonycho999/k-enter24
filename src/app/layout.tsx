// src/app/layout.tsx
import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

// 🚀 방금 만든 광고 컴포넌트 3개를 불러옵니다!
import AdTop from '../components/AdTop';
import AdLeft from '../components/AdLeft';
import AdRight from '../components/AdRight';

export const metadata: Metadata = {
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
};

export default function RootLayout({ children }: { children: React.ReactNode; }) {
  return (
    <html lang="en">
      <body>
        <div className="magazine-layout">
          
          <header className="header-top">
            <Link href="/" className="logo">K-ENTER 24</Link>
            <div className="search-bar">
              <input type="text" placeholder="Search news, idols, drama..." />
              🔍
            </div>
          </header>

          <nav className="nav-menu">
            <Link href="/k-pop" className="nav-link">K-POP</Link>
            <Link href="/k-drama" className="nav-link">K-DRAMA</Link>
            <Link href="/k-movie" className="nav-link">K-MOVIE</Link>
            <Link href="/k-entertainment" className="nav-link">K-ENTERTAINMENT</Link>
            <Link href="/k-culture" className="nav-link">K-CULTURE</Link>
          </nav>

          {/* 💰 불러온 상단 광고 부착! */}
          <AdTop />

          <div className="content-area-with-ads">
            {/* 💰 불러온 좌측 광고 부착! */}
            <AdLeft />

            <main className="main-content">
              {children}
            </main>

            {/* 💰 불러온 우측 광고 부착! */}
            <AdRight />
          </div>

        </div>
      </body>
    </html>
  );
}
