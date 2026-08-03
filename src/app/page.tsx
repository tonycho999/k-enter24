// src/app/page.tsx
import Link from 'next/link';

// 가상의 테스트 데이터 (나중에 봇이 크롤링해서 DB에 넣을 데이터의 형태입니다)
const mockPosts = [
  { id: 1, category: 'K-POP', title: 'BTS Jin, First Solo Album Release Post-Military Service... Global Fans Cheer', desc: 'BTS oldest member Jin is working on his first solo album aiming for a release in the second half of the year after completing his military service.', image: 'https://images.unsplash.com/photo-1549834125-82d3c48159a3?q=80&w=800&auto=format&fit=crop' },
  { id: 2, category: 'K-DRAMA', title: 'Queen of Tears Kim Soo-hyun & Kim Ji-won, The Secret Behind Record Ratings?', desc: 'The tvN drama Queen of Tears is creating a syndrome, breaking its own highest viewership ratings every episode. The perfect chemistry between the two lead actors stands out.', image: 'https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?q=80&w=800&auto=format&fit=crop' },
  { id: 3, category: 'K-MOVIE', title: 'The Roundup 4 Surpasses 10 Million Viewers in First Week... Ma Dong-seok Power', desc: 'The fourth installment of Korea\'s representative action series, The Roundup, has taken over theaters, showing an incredible box office pace right upon release.', image: 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?q=80&w=800&auto=format&fit=crop' },
  { id: 4, category: 'K-CULTURE', title: 'Korean Street Food Pop-up in New York, Locals Wait for 2 Hours', desc: 'The popularity of K-food is burning hot. A tteokbokki and hot dog pop-up store opened in Manhattan, New York, is a huge success with locals flocking to it.', image: 'https://images.unsplash.com/photo-1583224964978-225ddb3ea386?q=80&w=800&auto=format&fit=crop' },
  { id: 5, category: 'K-ENTERTAINMENT', title: 'Running Man Special Episode: The Return of the Legends', desc: 'The beloved variety show brings back iconic guests for its anniversary special, promising non-stop laughter and nostalgia for long-time fans.', image: 'https://images.unsplash.com/photo-1601004890684-d8cbf643f5f2?q=80&w=800&auto=format&fit=crop' },
];

export default function Home() {
  return (
    <div>
      <h2 className="page-title">🔥 Trending Now</h2>
      
      <div className="article-grid">
        {mockPosts.map((post) => (
          {/* 각 카드를 클릭하면 해당 카테고리와 글 번호로 이동하게 됩니다 */}
          <Link href={`/${post.category.toLowerCase()}/${post.id}`} key={post.id} className="article-card">
            <div className="image-wrapper">
              <img src={post.image} alt={post.title} />
            </div>
            <div className="card-content">
              <div className="card-category">{post.category}</div>
              <h3 className="card-title">{post.title}</h3>
              <p className="card-desc">{post.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
