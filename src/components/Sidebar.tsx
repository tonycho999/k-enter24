'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const CATEGORIES = [
  { name: 'K-Pop', path: '/k-pop' },
  { name: 'K-Drama & Movie', path: '/k-drama-movie' },
  { name: 'K-Entertain', path: '/k-entertain' },
  { name: 'K-Culture', path: '/k-culture' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-screen fixed left-0 top-0 bg-slate-900 text-white p-6 hidden md:flex flex-col">
      <Link href="/" className="text-2xl font-bold mb-10 text-pink-500">
        K-ENTER 24
      </Link>
      
      <nav className="flex flex-col gap-4">
        {CATEGORIES.map((cat) => {
          const isActive = pathname.startsWith(cat.path);
          return (
            <Link 
              key={cat.path} 
              href={cat.path}
              className={`text-lg font-medium p-3 rounded-lg transition-colors ${
                isActive ? 'bg-pink-500 text-white' : 'text-slate-300 hover:bg-slate-800'
              }`}
            >
              {cat.name}
            </Link>
          );
        })}
      </nav>
      
      {/* 하단 여백 또는 추가 메뉴(광고, About) */}
      <div className="mt-auto text-sm text-slate-500">
        © 2026 K-ENTER24.
      </div>
    </aside>
  );
}
