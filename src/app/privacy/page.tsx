// src/app/privacy/page.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy | K-ENTER 24',
  description: 'Learn how K-ENTER 24 collects, uses, and protects your information, including cookies, advertising, and affiliate links.',
  alternates: { canonical: 'https://k-enter24.com/privacy' },
};

const h2Style = {
  fontSize: '24px',
  fontWeight: '800',
  color: '#1e293b',
  marginBottom: '16px',
  marginTop: '32px',
} as const;

const linkStyle = { color: '#2563eb', textDecoration: 'underline' } as const;

export default function PrivacyPolicy() {
  const lastUpdated = 'October 14, 2026';

  return (
    <div className="post-detail-container">
      <div className="post-category-label">LEGAL</div>
      <h1 className="post-title">Privacy Policy</h1>

      <div className="post-meta">
        <span>Last Updated: {lastUpdated}</span>
      </div>

      <div className="post-body">
        <p>
          Welcome to <strong>K-ENTER 24</strong> ("we," "our," or "us"), a Korea travel and trend guide for international visitors. This Privacy Policy explains what information is collected when you visit https://k-enter24.com and how it is used.
        </p>
        <p>By using this website, you agree to the practices described in this policy.</p>

        <hr style={{ margin: '40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <h2 style={{ ...h2Style, marginTop: 0 }}>1. Information We Collect</h2>
        <p>
          We do not require you to create an account or provide your name to read our guides. When you visit, certain information is collected automatically, such as your IP address, browser type, device type, operating system, language settings, referring pages, approximate location (country or city), and the pages you view.
        </p>
        <p>
          If you contact us by email, we receive your email address and the contents of your message. We use this only to respond to you.
        </p>

        <h2 style={h2Style}>2. Hosting and Server Logs</h2>
        <p>
          Our website is hosted by Vercel. Like most hosting providers, Vercel processes technical log data (such as IP addresses and request times) to deliver the website securely and reliably.
        </p>

        <h2 style={h2Style}>3. Cookies</h2>
        <p>
          Cookies are small files stored on your device. We and our partners may use cookies to keep the website working, understand how visitors use our pages, serve advertising, and track bookings made through affiliate links. You can block or delete cookies in your browser settings, but some features may not work properly.
        </p>

        <h2 style={h2Style}>4. Advertising (Google AdSense)</h2>
        <p>
          We may display ads served by Google and other third-party vendors. These vendors, including Google, use cookies to serve ads based on your previous visits to this website and other websites.
        </p>
        <p>
          Google's use of advertising cookies enables it and its partners to serve ads to you based on your visits to our site and other sites on the Internet. You can opt out of personalized advertising by visiting{' '}
          <a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer" style={linkStyle}>Google Ads Settings</a>.
          You can also opt out of some third-party vendors' cookies at{' '}
          <a href="https://www.aboutads.info/choices" target="_blank" rel="noopener noreferrer" style={linkStyle}>www.aboutads.info</a>.
        </p>
        <p>
          To learn more, see{' '}
          <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener noreferrer" style={linkStyle}>How Google uses information from sites that use its services</a>.
        </p>

        <h2 style={h2Style}>5. Affiliate Links</h2>
        <p>
          Some links on K-ENTER 24 are affiliate links to travel services such as tours, attraction tickets, and hotels, including KKday. These links are managed through affiliate networks such as Involve Asia.
        </p>
        <p>
          When you click an affiliate link, the partner may place a cookie on your device to record that you came from our website. If you make a booking, we may earn a commission at no extra cost to you. Any booking you make is handled by the partner and is subject to their own privacy policy.
        </p>

        <h2 style={h2Style}>6. How We Use Information</h2>
        <ul style={{ paddingLeft: '24px', lineHeight: '1.8' }}>
          <li>To operate, maintain, and secure the website</li>
          <li>To understand which guides are useful and improve our content</li>
          <li>To display advertising and measure affiliate referrals</li>
          <li>To respond to messages you send us</li>
        </ul>
        <p>We do not sell your personal information.</p>

        <h2 style={h2Style}>7. Your Privacy Rights</h2>
        <p>
          Depending on where you live, including the European Economic Area, the United Kingdom, and California, you may have the right to access, correct, or delete personal information about you, or to object to certain processing. To make a request, contact us using the email below.
        </p>

        <h2 style={h2Style}>8. Children's Privacy</h2>
        <p>
          Our website is not directed at children under 13, and we do not knowingly collect personal information from children.
        </p>

        <h2 style={h2Style}>9. External Links</h2>
        <p>
          Our guides may link to official tourism sites, maps, booking platforms, and other third-party websites. We are not responsible for the content or privacy practices of those websites.
        </p>

        <h2 style={h2Style}>10. Changes to This Policy</h2>
        <p>
          We may update this Privacy Policy from time to time. Changes will be posted on this page with an updated "Last Updated" date.
        </p>

        <h2 style={h2Style}>11. Contact Us</h2>
        <p>
          If you have questions about this Privacy Policy, contact us at: <strong>contact@k-enter24.com</strong>
        </p>
      </div>
    </div>
  );
}
