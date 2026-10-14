// src/app/terms/page.tsx
import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Terms of Service | K-ENTER 24',
  description: 'Terms of Service for K-ENTER 24, an independent Korea travel and trend guide for international visitors.',
  alternates: { canonical: 'https://k-enter24.com/terms' },
};

const h2Style = {
  fontSize: '24px',
  fontWeight: '800',
  color: '#1e293b',
  marginBottom: '16px',
  marginTop: '32px',
} as const;

export default function Terms() {
  const lastUpdated = 'October 14, 2026';

  return (
    <div className="post-detail-container">
      <div className="post-category-label">LEGAL</div>
      <h1 className="post-title">Terms of Service</h1>

      <div className="post-meta">
        <span>Last Updated: {lastUpdated}</span>
      </div>

      <div className="post-body">
        <p>
          Welcome to <strong>K-ENTER 24</strong>, an independent Korea travel and trend guide. These Terms of Service ("Terms") govern your use of https://k-enter24.com. By using the website, you agree to these Terms. If you do not agree, please do not use the website.
        </p>

        <hr style={{ margin: '40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <h2 style={{ ...h2Style, marginTop: 0 }}>1. Use of Our Content</h2>
        <p>
          The text, guides, and original materials on K-ENTER 24 are owned by K-ENTER 24 unless otherwise stated. You may read and share links to our guides for personal, non-commercial use.
        </p>
        <p>You must not:</p>
        <ul style={{ paddingLeft: '24px', marginBottom: '24px', lineHeight: '1.8' }}>
          <li>Copy or republish our guides in full without permission.</li>
          <li>Sell, rent, or sub-license material from K-ENTER 24.</li>
          <li>Use automated tools to scrape or copy content from the website.</li>
        </ul>

        <h2 style={h2Style}>2. Third-Party Content and Images</h2>
        <p>
          Some images and materials on this website are provided by third parties, such as the Korea Tourism Organization, public institutions, and royalty-free photo libraries. These materials remain the property of their respective owners and are used under their license terms. Credits are provided where required.
        </p>

        <h2 style={h2Style}>3. Travel Information Disclaimer</h2>
        <p>
          Our guides are for general information only. Opening hours, prices, transportation, entry requirements, and other travel details can change without notice. Please confirm important details with official sources, such as the attraction, operator, or government website, before you travel.
        </p>
        <p>
          K-ENTER 24 does not guarantee that all information is complete, accurate, or current, and is not responsible for any loss, inconvenience, or damage resulting from the use of information on this website.
        </p>

        <h2 style={h2Style}>4. Bookings and Third-Party Services</h2>
        <p>
          K-ENTER 24 is not a travel agency and does not sell tours, tickets, hotels, or flights. When you book through a link on our website, your booking is made directly with the third-party provider, such as KKday. Payments, cancellations, refunds, and customer service are handled by that provider under its own terms and policies.
        </p>

        <h2 style={h2Style}>5. Affiliate Links and Advertising</h2>
        <p>
          Some links on this website are affiliate links. If you make a booking or purchase through them, we may earn a commission at no extra cost to you. We also display ads from third-party advertising partners. We are not responsible for the content of external ads or websites. For details on cookies and data, see our{' '}
          <Link href="/privacy" style={{ color: '#2563eb', textDecoration: 'underline' }}>Privacy Policy</Link>.
        </p>

        <h2 style={h2Style}>6. Copyright Concerns</h2>
        <p>
          We respect the rights of creators. If you believe that any content on K-ENTER 24 infringes your copyright, please email us with the page URL, a description of the material, and proof of ownership. We will review your request and remove or correct the content promptly where appropriate.
        </p>

        <h2 style={h2Style}>7. Changes to These Terms</h2>
        <p>
          We may update these Terms from time to time. Changes will be posted on this page with an updated "Last Updated" date. Continued use of the website means you accept the revised Terms.
        </p>

        <h2 style={h2Style}>8. Contact Us</h2>
        <p>
          If you have questions about these Terms, contact us at: <strong>contact@k-enter24.com</strong>
        </p>
      </div>
    </div>
  );
}
