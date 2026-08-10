// src/app/privacy/page.tsx
export default function PrivacyPolicy() {
  const lastUpdated = "August 10, 2026"; // 현재 날짜로 변경 가능

  return (
    <div className="post-detail-container">
      <div className="post-category-label">LEGAL</div>
      <h1 className="post-title">Privacy Policy</h1>
      
      <div className="post-meta">
        <span>Last Updated: {lastUpdated}</span>
      </div>

      <div className="post-body">
        <p>
          Welcome to <strong>K-ENTER 24</strong> ("we," "our," or "us"). We respect your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, and safeguard your information when you visit our website (https://k-enter24.com).
        </p>
        <p>
          Please read this privacy policy carefully. If you do not agree with the terms of this privacy policy, please do not access the site.
        </p>

        <hr style={{ margin: '40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px' }}>
          1. Information We Collect
        </h2>
        <p>
          We automatically collect certain information when you visit, use, or navigate our website. This information does not reveal your specific identity (like your name or contact information) but may include device and usage information, such as your IP address, browser and device characteristics, operating system, language preferences, referring URLs, country, location, and information about how and when you use our website.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          2. Log Files and Analytics
        </h2>
        <p>
          Like many other websites, K-ENTER 24 makes use of log files and analytics tools (such as Google Analytics). The information inside the log files includes internet protocol (IP) addresses, type of browser, Internet Service Provider (ISP), date/time stamp, referring/exit pages, and possibly the number of clicks. This information is used to analyze trends, administer the site, track user's movement around the site, and gather demographic information.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          3. Cookies and Web Beacons
        </h2>
        <p>
          We use cookies to store information about visitors' preferences, to record user-specific information on which pages the site visitor accesses or visits, and to personalize or customize our web page content based upon visitors' browser type or other information that the visitor sends via their browser.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          4. Google AdSense & DoubleClick DART Cookie
        </h2>
        <p>
          Google, as a third-party vendor, uses cookies to serve ads on K-ENTER 24. Google's use of the DART cookie enables it to serve ads to our site's visitors based upon their visit to our site and other sites on the Internet.
        </p>
        <p>
          Users may opt-out of the use of the DART cookie by visiting the Google ad and content network privacy policy at the following URL: <br/>
          <a href="https://policies.google.com/technologies/ads" target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'underline' }}>
            https://policies.google.com/technologies/ads
          </a>
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          5. Affiliate Disclosure (Amazon Associates)
        </h2>
        <p>
          K-ENTER 24 is a participant in the Amazon Services LLC Associates Program, an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.com. As an Amazon Associate, we earn from qualifying purchases at no additional cost to you.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          6. External Links
        </h2>
        <p>
          Our website may contain links to other websites that are not operated by us. If you click on a third-party link, you will be directed to that third party's site. We strongly advise you to review the Privacy Policy of every site you visit. We have no control over and assume no responsibility for the content, privacy policies, or practices of any third-party sites or services.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '32px' }}>
          7. Contact Us
        </h2>
        <p>
          If you have any questions or suggestions about our Privacy Policy, do not hesitate to contact us at: <strong>contact@k-enter24.com</strong>
        </p>
      </div>
    </div>
  );
}
