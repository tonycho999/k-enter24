import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';
import AdTop from '@/components/AdTop';
import AdLeft from '@/components/AdLeft';
import AdRight from '@/components/AdRight';
import SearchBar from '@/components/SearchBar';
import Footer from '@/components/Footer';

const SITE_TITLE = 'K-ENTER 24 | Korea Travel & Trend Guide';
const SITE_DESC = "Your guide to Korea's best sights, local food, style, beauty, and travel tips, written for international travelers.";

// 🖼️ 이미지 정보 (og-image 표준 비율인 1200x630으로 수정 반영)
const LOGO = { url: 'https://k-enter24.com/logo.png', width: 600, height: 230 };
const OG_IMAGE = { url: '/og-image.png', width: 1200, height: 630, alt: 'K-ENTER 24 | Korea Travel & Trend Guide' };

export const metadata: Metadata = {
  metadataBase: new URL('https://k-enter24.com'),
  title: SITE_TITLE,
  description: SITE_DESC,
  verification: {
    google: 'K7nILRoN2qJRl9Cfvp6tkRkddR_Q9YWz7GSd56MY05Y',
  },
  openGraph: {
    title: SITE_TITLE,
    description: SITE_DESC,
    url: 'https://k-enter24.com',
    siteName: 'K-ENTER 24',
    images: [OG_IMAGE], // 🚀 크기와 alt를 함께 넘겨서 SNS가 더 빨리, 정확하게 표시
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: SITE_TITLE,
    description: SITE_DESC,
    images: [OG_IMAGE.url],
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

// 🗺️ 새롭게 정의된 4대 카테고리 메뉴 구조
const MENU = [
  { href: '/sights', label: 'SIGHTS' },
  { href: '/food', label: 'FOOD' },
  { href: '/style', label: 'STYLE' },
  { href: '/tips', label: 'TIPS' },
];

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'K-ENTER 24',
    alternateName: 'K-ENTER 24 Korea Travel Guide',
    description: SITE_DESC,
    url: 'https://k-enter24.com',
    publisher: {
      '@type': 'Organization',
      name: 'K-ENTER 24',
      url: 'https://k-enter24.com',
      logo: {
        '@type': 'ImageObject',
        url: LOGO.url,
        width: LOGO.width,   // 🚀 로고 실제 크기 명시
        height: LOGO.height,
      },
    },
  };

  return (
    <html lang="en">
      <body>
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
        <div className="magazine-layout">
          <header className="header-top">
            {/* 🚀 텍스트 로고 → logo.png 이미지 로고 */}
            <Link href="/" className="logo" aria-label="K-ENTER 24 Home" style={{ display: 'flex', alignItems: 'center' }}>
              <img
                src="/logo.png"
                alt="K-ENTER 24"
                width={120}   // 600×230 비율 유지 (120×46)
                height={46}
                style={{ height: '46px', width: 'auto', display: 'block' }}
              />
            </Link>
            <SearchBar />
          </header>
          <nav className="nav-menu">
            {MENU.map((item) => (
              <Link key={item.href} href={item.href} prefetch={true} className="nav-link">
                {item.label}
              </Link>
            ))}
          </nav>
          <AdTop />
          <div className="content-area-with-ads">
            <AdLeft />
            <main className="main-content">{children}</main>
            <AdRight />
          </div>
          <Footer />
        </div>
      </body>
    </html>
  );
}
