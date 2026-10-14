// src/app/layout.tsx
import type { Metadata } from 'next';
import Link from 'next/link';
import './globals.css';

import AdTop from '@/components/AdTop';
import AdLeft from '@/components/AdLeft';
import AdRight from '@/components/AdRight';
import SearchBar from '@/components/SearchBar';
import Footer from '@/components/Footer';

const SITE_TITLE = 'K-ENTER 24 | Korea Travel & Trend Guide';
const SITE_DESC = "Your guide to Korea's best attractions, food, shopping, beauty, and local trends, written for international travelers.";

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
    images: ['/og-image.png'],
    locale: 'en_US',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: SITE_TITLE,
    description: SITE_DESC,
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

// 🚀 메뉴 목록 (라벨을 바꾸고 싶으면 여기만 고치면 됩니다)
const MENU = [
  { href: '/attractions', label: 'ATTRACTIONS' },
  { href: '/food', label: 'FOOD' },
  { href: '/shopping', label: 'SHOPPING' },
  { href: '/beauty', label: 'BEAUTY' },
  { href: '/culture', label: 'CULTURE & TIPS' },
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
      logo: { '@type': 'ImageObject', url: 'https://k-enter24.com/logo.png' },
    },
  };

  return (
    <html lang="en">
      <body>
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />

        <div className="magazine-layout">
          <header className="header-top">
            <Link href="/" className="logo">K-ENTER 24</Link>
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
