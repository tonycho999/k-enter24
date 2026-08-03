import Link from 'next/link';

export default function Sidebar() {
  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-screen hidden md:block">
      <div className="p-6">
        <Link href="/">
          <h1 className="text-2xl font-black text-blue-600 mb-8 cursor-pointer">K-ENTER 24</h1>
        </Link>
        <nav className="flex flex-col gap-4">
          <Link href="/k-pop" className="text-slate-600 hover:text-blue-600 font-semibold transition-colors">
            K-Pop
          </Link>
          <Link href="/k-drama" className="text-slate-600 hover:text-blue-600 font-semibold transition-colors">
            K-Drama
          </Link>
          <Link href="/k-culture" className="text-slate-600 hover:text-blue-600 font-semibold transition-colors">
            K-Culture
          </Link>
        </nav>
      </div>
    </aside>
  );
}
