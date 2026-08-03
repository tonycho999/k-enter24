import Link from 'next/link';

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <Link href="/" className="logo">K-ENTER 24</Link>
      <nav>
        <Link href="/k-pop" className="nav-link">K-Pop</Link>
        <Link href="/k-drama" className="nav-link">K-Drama</Link>
        <Link href="/k-culture" className="nav-link">K-Culture</Link>
      </nav>
    </aside>
  );
}
