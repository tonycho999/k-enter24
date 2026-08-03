import Link from 'next/link';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <Link href="/" className="logo">K-ENTER 24</Link>
      <nav>
        <Link href="/k-pop" className="nav-link">K-POP</Link>
        <Link href="/k-drama" className="nav-link">K-DRAMA</Link>
        <Link href="/k-movie" className="nav-link">K-MOVIE</Link>
        <Link href="/k-entertainment" className="nav-link">K-ENTERTAINMENT</Link>
        <Link href="/k-culture" className="nav-link">K-CULTURE</Link>
      </nav>
    </aside>
  );
}
