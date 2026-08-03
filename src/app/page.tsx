import Link from 'next/link';

// 임시 데이터 (나중에는 DB에서 불러옵니다)
const recentPosts = [
  { id: 1, category: 'k-pop', title: 'BTS Jin Returns: What to Expect in 2026', image: '/mock1.jpg', date: 'Aug 3, 2026' },
  { id: 2, category: 'k-drama-movie', title: 'Top 5 K-Dramas to Binge Watch This Weekend', image: '/mock2.jpg', date: 'Aug 2, 2026' },
];

export default function Home() {
  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Latest Updates</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {recentPosts.map(post => (
          <Link key={post.id} href={`/${post.category}/${post.id}`} className="group block bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition">
            <div className="h-48 bg-slate-200 relative">
              {/* Image 태그로 교체 필요 */}
              <div className="absolute inset-0 flex items-center justify-center text-slate-400">Image Area</div>
            </div>
            <div className="p-4">
              <span className="text-xs font-bold text-pink-500 uppercase tracking-wider">{post.category.replace('-', ' ')}</span>
              <h2 className="text-lg font-bold mt-2 group-hover:text-pink-600 line-clamp-2">{post.title}</h2>
              <p className="text-sm text-slate-500 mt-2">{post.date}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
