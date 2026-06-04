import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Footer from '@/components/Footer';
import Script from 'next/script'; 
import SEO from '@/components/SEO'; 

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'K-ENTER 24 | Real-time K-Pop & K-Drama News',
  description: 'The world\'s fastest source for K-Entertainment news. Monitoring 1,200+ articles daily in real-time. BTS, BLACKPINK, NewJeans updates instantly.',
  keywords: [
    'K-Pop', 'K-Drama', 'Korean News', 'Real-time News', 'BTS', 'BLACKPINK', 'NewJeans',
    'Kpop','Kdrama', 'Hallyu','Idol', 'Trainee','Comeback', 'Debut', 'Bias', 'Maknae',
    'Hyung', 'Noona', 'Oppa', 'Unnie', 'K-pop trainee', 'K-pop survival show', 'K-pop agency', 'K-pop fan meeting',
    'K-pop lightstick', 'K-pop tour', 'Fanclub', 'Scandal', 
    'K-drama', 'Korean drama','Korean actors','Korean actresses','K-drama cast', 'K-drama OST','K-drama 2026', 'Best K-drama',
    'Romantic K-drama','Historical K-drama', 'K-drama Netflix', 'Korean drama recommendations', 'Korean celebrity', 'Korean star',
    'Korean heartthrob', 'Korean actor Instagram', 'Korean actress profile', 'Korean drama awards','Korean drama list', 'New Korean drama',
  ],
  openGraph: {
    title: 'K-ENTER 24',
    description: 'Real-time K-News Radar. Stop waiting for translations.',
    url: 'https://k-enter24.com',
    siteName: 'K-ENTER 24',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
      },
    ],
    locale: 'en_US',
    type: 'website',
  },
  icons: {
    icon: '/favicon.png',
  },
  alternates: {
    types: {
      'application/rss+xml': 'https://k-enter24.com/rss.xml',
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <SEO />
      </head>
      <body className={inter.className}>
        {/* ✅ 구글 애드센스 스크립트 추가 */}
        <Script
          async
          src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7272957295128241"
          strategy="afterInteractive"
          crossOrigin="anonymous"
        />

        {/* ✅ 구글 애널리틱스 스크립트 */}
        <Script
          src="https://www.googletagmanager.com/gtag/js?id=G-1E4WN8MZ9N"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());

            gtag('config', 'G-1E4WN8MZ9N');
          `}
        </Script>
        
        <main className="min-h-screen">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
