import type { Metadata } from 'next';
import './globals.css';
import Sidebar from '../components/Sidebar';

export const metadata: Metadata = {
  title: 'K-ENTER 24 | Global K-Culture Blog',
  description: 'Your daily source for K-Pop, K-Drama, and K-Culture.',
};

export default function RootLayout({ children }: { children: React.ReactNode; }) {
  return (
    <html lang="en">
      <body>
        <div className="layout-container">
          <Sidebar />
          <main className="main-content">
            <div className="content-wrapper">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  );
}
