// 3. 검색어로 글 찾기
export async function searchPosts(keyword: string): Promise<BlogPost[]> {
  // 상단에 선언해둔 BLOG_URL 상수를 깔끔하게 재사용합니다.
  const url = `${BLOG_URL}/feeds/posts/default?q=${encodeURIComponent(keyword)}&alt=json&max-results=20`;

  try {
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('Search API failed');
    
    const data = await res.json();
    
    // 검색 결과가 아예 없을 경우 에러가 나지 않도록 feed?.entry 로 안전하게 접근합니다.
    const entries = data.feed?.entry || []; 

    return entries.map((entry: any) => {
      const rawId = entry.id.$t;
      const id = rawId.split('post-')[1];

      let thumbnail = entry.media$thumbnail?.url || '';
      if (thumbnail) {
        thumbnail = thumbnail.replace('/s72-c/', '/w240-h160-c/'); 
      }

      const categories = entry.category ? entry.category.map((cat: any) => cat.term) : [];

      return {
        id,
        title: entry.title.$t,
        content: entry.content?.$t || '', // 내용이 비어있는 글 방어코드
        publishedAt: entry.published.$t,
        thumbnail,
        categories,
      };
    });
  } catch (error) {
    console.error('Blogger Search Error:', error);
    return []; // 에러가 나면 사이트가 터지지 않고 그냥 '결과 없음' 화면을 띄워줍니다.
  }
}
