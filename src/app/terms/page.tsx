// src/app/terms/page.tsx
export default function Terms() {
  const lastUpdated = "August 10, 2026";

  return (
    <div className="post-detail-container">
      <div className="post-category-label">LEGAL</div>
      <h1 className="post-title">Terms of Service</h1>
      
      <div className="post-meta">
        <span>Last Updated: {lastUpdated}</span>
      </div>

      <div className="post-body">
        <p>
          Welcome to <strong>K-ENTER 24</strong>. These Terms of Service ("Terms") govern your access to and use of our website (https://k-enter24.com). By accessing or using the website, you agree to be bound by these Terms.
        </p>
        <p>
          If you disagree with any part of these Terms, you may not access our website.
        </p>

        <hr style={{ margin: '40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px' }}>
          1. Intellectual Property Rights
        </h2>
        <p>
          Unless otherwise stated, K-ENTER 24 and/or its licensors own the intellectual property rights for all material on this website. All intellectual property rights are reserved. You may access this from K-ENTER 24 for your own personal use subjected to restrictions set in these terms and conditions.
        </p>
        <p>
          You must not:
        </p>
        <ul style={{ paddingLeft: '24px', marginBottom: '32px' }}>
          <li>Republish material from K-ENTER 24 without proper attribution.</li>
          <li>Sell, rent, or sub-license material from K-ENTER 24.</li>
          <li>Reproduce, duplicate, or copy material from K-ENTER 24 for commercial purposes.</li>
        </ul>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          2. Disclaimer of Warranties
        </h2>
        <p>
          All the information on this website is published in good faith and for general information purpose only. K-ENTER 24 does not make any warranties about the completeness, reliability, and accuracy of this information. Any action you take upon the information you find on this website is strictly at your own risk.
        </p>
        <p>
          K-ENTER 24 will not be liable for any losses and/or damages in connection with the use of our website.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          3. Affiliate Links & Advertising
        </h2>
        <p>
          Some of the links on this website may be affiliate links. This means that if you click on the link and make a purchase, we may receive a small commission at no extra cost to you. We only recommend products or services we believe will add value to our readers.
        </p>
        <p>
          We also use third-party advertising companies to serve ads when you visit our website. We are not responsible for the content of these external advertisements.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          4. User Comments & Conduct
        </h2>
        <p>
          Parts of this website may offer an opportunity for users to post and exchange opinions and information. K-ENTER 24 reserves the right to monitor all Comments and to remove any Comments which can be considered inappropriate, offensive, or causes breach of these Terms of Service.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          5. Modifications to Terms
        </h2>
        <p>
          We reserve the right, at our sole discretion, to modify or replace these Terms at any time. By continuing to access or use our website after those revisions become effective, you agree to be bound by the revised terms.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          6. Contact Information
        </h2>
        <p>
          If you have any questions about these Terms, please contact us at: <strong>contact@k-enter24.com</strong>
        </p>
      </div>
    </div>
  );
}
