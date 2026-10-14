// src/components/SearchBar.tsx
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SearchBar() {
  const [keyword, setKeyword] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (keyword.trim()) {
      router.push(`/search?q=${encodeURIComponent(keyword.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="search-bar" role="search">
      <input
        type="search"
        placeholder="Search places, food, tips..."
        aria-label="Search Korea travel guides"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
      <button
        type="submit"
        aria-label="Search"
        style={{ background: 'none', border: 'none', cursor: 'pointer' }}
      >
        🔍
      </button>
    </form>
  );
}
