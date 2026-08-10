// src/components/Footer.tsx
import Link from 'next/link';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer style={{
      marginTop: '60px',
      padding: '40px 20px',
      borderTop: '1px solid #e2e8f0',
      backgroundColor: '#f8fafc',
      color: '#64748b',
      fontSize: '14px',
      textAlign: 'center'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* 필수 정책 링크들 (hover 에러 해결 완료) */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', flexWrap: 'wrap' }}>
          <Link href="/about" className="footer-link">About Us</Link>
          <Link href="/privacy" className="footer-link">Privacy Policy</Link>
          <Link href="/terms" className="footer-link">Terms of Service</Link>
          <Link href="/contact" className="footer-link">Contact</Link>
        </div>

        {/* 저작권 명시 */}
        <div>
          &copy; {currentYear} K-ENTER 24. All rights reserved.
        </div>
        
        {/* 면책 조항 (제휴 마케팅 시 필수!) */}
        <div style={{ fontSize: '12px', color: '#94a3b8', marginTop: '8px' }}>
          Disclaimer: This site may contain affiliate links to products. We may receive a commission for purchases made through these links at no additional cost to you.
        </div>
        
      </div>
    </footer>
  );
}
