import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Sidebar from '@/components/Sidebar';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 text-slate-900`}>
        <div className="flex min-h-screen">
          {/* PC 환경: 고정 사이드바 */}
          <Sidebar />
          
          {/* 우측 메인 콘텐츠 영역 (사이드바 너비인 64(16rem)만큼 마진을 줌) */}
          <main className="flex-1 md:ml-64 p-6 lg:p-12">
            <div className="max-w-5xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
