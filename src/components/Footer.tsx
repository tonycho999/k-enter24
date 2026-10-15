import Link from 'next/link';

const CATEGORIES = [
  { href: '/sights', label: 'Sights' },
  { href: '/food', label: 'Food' },
  { href: '/style', label: 'Style' },
  { href: '/tips', label: 'Tips' },
];

const POLICIES = [
  { href: '/about', label: 'About Us' },
  { href: '/privacy', label: 'Privacy Policy' },
  { href: '/terms', label: 'Terms of Service' },
  { href: '/contact', label: 'Contact' },
];

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer
      style={{
        marginTop: '60px',
        padding: '40px 20px',
        borderTop: '1px solid #e2e8f0',
        backgroundColor: '#f8fafc',
        color: '#64748b',
        fontSize: '14px',
        textAlign: 'center',
      }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {/* 사이트 소개 */}
        <div>
          <div style={{ fontWeight: 800, color: '#0f172a', fontSize: '16px' }}>K-ENTER 24</div>
          <div style={{ marginTop: '4px' }}>Korea Travel &amp; Trend Guide for International Visitors</div>
        </div>

        {/* 카테고리 링크 (내부 링크 → 검색 노출에 도움) */}
        <nav aria-label="Guide categories" style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
          {CATEGORIES.map((item) => (
            <Link key={item.href} href={item.href} className="footer-link">{item.label}</Link>
          ))}
        </nav>

        {/* 정책 링크 */}
        <nav aria-label="Site information" style={{ display: 'flex', justifyContent: 'center', gap: '24px', flexWrap: 'wrap' }}>
          {POLICIES.map((item) => (
            <Link key={item.href} href={item.href} className="footer-link">{item.label}</Link>
          ))}
          <a href="/rss.xml" className="footer-link">RSS</a>
        </nav>

        {/* 저작권 */}
        <div>&copy; {currentYear} K-ENTER 24. All rights reserved.</div>

        {/* 고지 문구 */}
        <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px', lineHeight: 1.6 }}>
          Disclosure: Some links on this site are affiliate links to travel services such as tours, tickets, and hotels. We may earn a commission at no extra cost to you.
          <br />
          Travel details such as prices and opening hours may change. Please check official sources before you visit.
          <br />
          Some images are provided by the Korea Tourism Organization and other public sources, credited where required.
        </div>
      </div>
    </footer>
  );
}
