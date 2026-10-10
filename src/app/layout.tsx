// src/app/layout.tsx
import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

// 🚀 절대 경로(@/) 적용 (경로 에러 방지)
import AdTop from '@/components/AdTop';
import AdLeft from '@/components/AdLeft';
import AdRight from '@/components/AdRight';
import SearchBar from '@/components/SearchBar';
import Footer from '@/components/Footer'; 

export const metadata: Metadata = {
  // 🚀 metadataBase 필수 추가: Next.js가 이미지 주소를 절대 경로로 만들 때 필요합니다.
  metadataBase: new URL('https://k-enter24.com'),
  
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
  
  verification: {
    google: 'K7nILRoN2qJRl9Cfvp6tkRkddR_Q9YWz7GSd56MY05Y',
  },
  
  // 🚀 방금 만든 og-image.png를 사이트 '기본' 썸네일로 지정 (카톡, 페북 공유용)
  openGraph: {
    title: 'K-ENTER 24 | Global K-Culture Blog',
    description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
    url: 'https://k-enter24.com',
    siteName: 'K-ENTER 24',
    images: ['/og-image.png'],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'K-ENTER 24 | Global K-Culture Blog',
    description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
    images: ['/og-image.png'],
  },

  robots: {
    index: true,     
    follow: true,    
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large', 
      'max-snippet': -1,            
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  // 🚀 구글 봇에게 우리 웹사이트의 '공식 로고'가 무엇인지 알려주는 구조화 데이터
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "K-ENTER 24",
    "url": "https://k-enter24.com",
    "publisher": {
      "@type": "Organization",
      "name": "K-ENTER 24",
      "logo": {
        "@type": "ImageObject",
        "url": "https://k-enter24.com/logo.png" // 방금 만드신 로고 연결!
      }
    }
  };

  return (
    <html lang="en">
      <body>
        {/* 🚀 JSON-LD 스크립트를 화면에 보이지 않게 삽입 */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />

        <div className="magazine-layout">
          
          {/* 상단 1: 로고 & 검색바 */}
          <header className="header-top">
            
            {/* 만약 화면 상단 글씨(K-ENTER 24)도 이미지 로고로 바꾸고 싶다면, 
                아래 <Link> 안의 글씨를 지우고 <img src="/logo.png" alt="logo" height="40" /> 로 바꾸셔도 됩니다. */}
            <Link href="/" className="logo">K-ENTER 24</Link>
            
            {/* 🚀 검색창 부품 장착! */}
            <SearchBar />
            
          </header>

          {/* 상단 2: 메인 카테고리 메뉴 */}
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

          <Footer />
        </div>
      </body>
    </html>
  );
}
