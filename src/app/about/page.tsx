// src/app/about/page.tsx
import type { Metadata } from 'next';
import Link from 'next/link';

// 🚀 About 페이지 전용 SEO 설정
export const metadata: Metadata = {
  title: 'About Us | K-ENTER 24',
  description:
    'K-ENTER 24 is an independent Korea travel and trend guide for international visitors, covering attractions, food, shopping, beauty, and local culture.',
  alternates: { canonical: 'https://k-enter24.com/about' },
};

const h2Style = {
  fontSize: '24px',
  fontWeight: '800',
  color: '#1e293b',
  marginBottom: '16px',
  marginTop: '40px',
} as const;

export default function About() {
  return (
    <div className="post-detail-container">
      <div className="post-category-label">ABOUT US</div>
      <h1 className="post-title">Welcome to K-ENTER 24</h1>

      <div className="post-body">
        {/* 대표 이미지: public 폴더의 og-image.png 사용 (저작권 걱정 없음) */}
        <div className="post-main-image" style={{ marginBottom: '40px' }}>
          <img src="/og-image.png" alt="K-ENTER 24 Korea Travel and Trend Guide" width={1200} height={630} />
        </div>

        <p style={{ fontSize: '22px', fontWeight: 'bold', color: '#1e293b', marginBottom: '32px' }}>
          Your practical guide to exploring Korea, from must-see attractions and local food to shopping, beauty, and the latest trends.
        </p>

        <h2 style={h2Style}>Our Mission</h2>
        <p>
          Planning a trip to Korea can feel overwhelming. Transportation, reservations, and local customs are not always explained in English. K-ENTER 24 exists to make Korea easier to explore for international travelers.
        </p>
        <p>
          We focus on useful, up-to-date information: how to get there, when to go, what it costs, and the tips that save you time once you arrive.
        </p>

        <h2 style={h2Style}>What We Cover</h2>
        <ul style={{ paddingLeft: '24px', marginBottom: '32px', lineHeight: '1.8' }}>
          <li><strong>📍 ATTRACTIONS:</strong> Landmarks, palaces, night views, and neighborhoods worth visiting across Korea.</li>
          <li><strong>🍜 FOOD:</strong> Street food, traditional markets, local restaurants, and trending cafés and desserts.</li>
          <li><strong>🛍️ SHOPPING:</strong> Pop-up stores, duty-free tips, and the best shopping districts.</li>
          <li><strong>💄 BEAUTY:</strong> K-beauty best-sellers, Olive Young guides, and beauty experiences for visitors.</li>
          <li><strong>🧭 CULTURE &amp; TIPS:</strong> T-money cards, airport transfers, etiquette, festivals, and travel essentials.</li>
        </ul>

        <h2 style={h2Style}>How We Create Our Guides</h2>
        <p>
          Every guide is researched and written by our editorial team using official tourism sources, operator websites, and public information. We check details such as opening hours, prices, and directions before publishing and update guides when information changes.
        </p>
        <p>
          Our images come from official public sources such as the Korea Tourism Organization, royalty-free photo libraries, or our own photography. We credit image sources wherever required.
        </p>

        <h2 style={h2Style}>Affiliate Disclosure</h2>
        <p>
          Some links on K-ENTER 24 are affiliate links to travel services such as tours, tickets, and hotels. If you book through these links, we may earn a small commission at no extra cost to you. This helps keep our guides free. Our recommendations are based on what we believe is useful for travelers.
        </p>

        <h2 style={h2Style}>Get in Touch</h2>
        <p>
          Spotted outdated information or have a question about traveling in Korea? Visit our <Link href="/contact" style={{ color: '#2563eb', fontWeight: 'bold' }}>Contact page</Link>. We read every message.
        </p>

        <hr style={{ margin: '60px 0 40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <p style={{ textAlign: 'center', fontWeight: 'bold', color: '#2563eb' }}>
          Explore More. Travel Smarter. <br />
          — The K-ENTER 24 Team
        </p>
      </div>
    </div>
  );
}
