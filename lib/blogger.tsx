// 3. 검색어로 글 찾기
export async function searchPosts(keyword: string): Promise<BlogPost[]> {
  // Blogger 주소에 ?q=검색어 를 붙이면 알아서 제목과 본문에서 검색해 줍니다.
  const url = `${process.env.BLOGGER_URL || 'https://본인블로그주소.blogspot.com'}/feeds/posts/default?q=${encodeURIComponent(keyword)}&alt=json&max-results=20`;

  try {
    // 검색 결과는 실시간성이 중요하므로 캐시하지 않음 (cache: 'no-store')
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) return [];
    const data = await res.json();

    const entries = data.feed.entry || [];

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
        content: entry.content.$t,
        publishedAt: entry.published.$t,
        thumbnail,
        categories,
      };
    });
  } catch (error) {
    return [];
  }
}
