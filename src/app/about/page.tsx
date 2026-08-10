// src/app/about/page.tsx
export default function About() {
  return (
    <div className="post-detail-container">
      <div className="post-category-label">ABOUT US</div>
      <h1 className="post-title">Welcome to K-ENTER 24</h1>
      
      <div className="post-body">
        {/* 멋진 대표 이미지 1장 삽입 (고정) */}
        <div className="post-main-image" style={{ marginBottom: '40px' }}>
          <img 
            src="https://images.unsplash.com/photo-1514525253161-7a46d19cd819?q=80&w=1200&auto=format&fit=crop" 
            alt="K-ENTER 24 Team" 
          />
        </div>

        <p style={{ fontSize: '22px', fontWeight: 'bold', color: '#1e293b', marginBottom: '32px' }}>
          Your ultimate daily source for everything related to Korean Entertainment, Pop Culture, and Lifestyle trends.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '40px' }}>
          Our Mission
        </h2>
        <p>
          At K-ENTER 24, our mission is simple: to bridge the gap between South Korea and the rest of the world. The Korean wave (Hallyu) has taken the globe by storm, and we are here to ensure that global fans never miss a beat. 
        </p>
        <p>
          Whether it's the latest comeback of your favorite K-Pop idol, the soaring ratings of a new K-Drama, or the trendiest K-Beauty items hitting the streets of Seoul, we deliver fast, accurate, and engaging content directly to your screen.
        </p>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '40px' }}>
          What We Cover
        </h2>
        <ul style={{ paddingLeft: '24px', marginBottom: '32px', lineHeight: '1.8' }}>
          <li><strong>🎶 K-POP:</strong> Breaking news, album releases, concert updates, and idol fashion.</li>
          <li><strong>📺 K-DRAMA & MOVIE:</strong> In-depth reviews, casting news, and box office hits.</li>
          <li><strong>🎭 K-ENTERTAINMENT:</strong> Highlights from popular Korean variety shows and celebrity issues.</li>
          <li><strong>🛒 K-CULTURE:</strong> The hottest trends in K-Beauty, K-Food, travel spots, and street style.</li>
        </ul>

        <h2 style={{ fontSize: '24px', fontWeight: '800', color: '#1e293b', marginBottom: '16px', marginTop: '40px' }}>
          Why Choose Us?
        </h2>
        <p>
          We know how passionate K-Culture fans are. That’s why our dedicated team works around the clock to curate the most relevant and high-quality news. We utilize cutting-edge technology and trend-tracking algorithms to bring you the hottest topics exactly when they happen.
        </p>
        <p>
          Join our global community and immerse yourself in the dynamic world of Korean entertainment.
        </p>

        <hr style={{ margin: '60px 0 40px 0', border: 'none', borderTop: '1px solid #e2e8f0' }} />
        
        <p style={{ textAlign: 'center', fontWeight: 'bold', color: '#2563eb' }}>
          Stay Connected. Stay Trendy. <br/>
          — The K-ENTER 24 Team
        </p>
      </div>
    </div>
  );
}
