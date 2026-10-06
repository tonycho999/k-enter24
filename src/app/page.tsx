// src/app/page.tsx
// 🚀 'use client' 를 삭제했습니다! 이제 다시 안전한 서버 컴포넌트입니다.

import { getPosts } from '@/lib/blogger';
import ArticleFilterList from '@/components/ArticleFilterList'; // 방금 만든 필터 부품

export default async function Home() {
  // 1. 서버에서 안전하게 Blogger API 주소를 읽어서 100개의 데이터를 가져옵니다.
  const posts = await getPosts(undefined, 100);

  // 2. 가져온 100개의 데이터를 클라이언트 부품(ArticleFilterList)에 넘겨줍니다.
  return (
    <div>
      <ArticleFilterList initialPosts={posts} />
    </div>
  );
}
