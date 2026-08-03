// src/components/SearchBar.tsx
'use client'; // 이 부품은 사용자의 입력을 받아야 하므로 클라이언트 컴포넌트로 선언합니다.

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function SearchBar() {
  const [keyword, setKeyword] = useState('');
  const router = useRouter();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault(); // 엔터 쳤을 때 새로고침 방지
    if (keyword.trim()) {
      // 검색어가 있으면 /search 페이지로 이동시킵니다!
      router.push(`/search?q=${encodeURIComponent(keyword.trim())}`);
    }
  };

  return (
    <form onSubmit={handleSearch} className="search-bar">
      <input
        type="text"
        placeholder="Search news, idols, drama..."
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
      />
      <button type="submit" style={{ background: 'none', border: 'none', cursor: 'pointer' }}>
        🔍
      </button>
    </form>
  );
}
