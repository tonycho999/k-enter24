// src/lib/blogger.tsx
const BLOG_URL = process.env.BLOGGER_URL || 'https://본인블로그주소.blogspot.com'; // 🚀 본인 블로그 주소로 변경하세요!

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishedAt: string;
  thumbnail: string;
  categories: string[];
}

// 1. 전체 글 또는 특정 카테고리(라벨) 글 가져오기 (Sitemap, RSS를 위해 maxResults 추가)
export async function getPosts(category?: string, maxResults: number = 20): Promise<BlogPost[]> {
  const categoryPath = category ? `/-/${encodeURIComponent(category)}` : '';
  const url = `${BLOG_URL}/feeds/posts/default${categoryPath}?alt=json&max-results=${maxResults}`;

  try {
    // Vercel에서 60초마다 최신화(ISR)하도록 설정
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch posts');
    const data = await res.json();

    // 글이 없을 경우를 대비한 안전한 접근
    const entries = data.feed?.entry || [];

    return entries.map((entry: any) => {
      // ID 추출
      const rawId = entry.id.$t;
      const id = rawId.split('post-')[1];

      // 썸네일 해상도 최적화 (240x160)
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
    console.error('Blogger API Error (getPosts):', error);
    return [];
  }
}

// 2. 특정 상세 글 하나만 가져오기
export async function getPostById(id: string): Promise<BlogPost | null> {
  const url = `${BLOG_URL}/feeds/posts/default/${id}?alt=json`;

  try {
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    const data = await res.json();
    const entry = data.entry;
    
    if (!entry) return null;

    // 상세페이지용 큰 이미지 최적화
    let thumbnail = entry.media$thumbnail?.url || '';
    if (thumbnail) {
      thumbnail = thumbnail.replace('/s72-c/', '/w800-h600-c/'); 
    }

    return {
      id,
      title: entry.title.$t,
      content: entry.content?.$t || '',
      publishedAt: entry.published.$t,
      thumbnail,
      categories: entry.category ? entry.category.map((cat: any) => cat.term) : [],
    };
  } catch (error) {
    console.error('Blogger API Error (getPostById):', error);
    return null;
  }
}

// 3. 검색어로 글 찾기
export async function searchPosts(keyword: string): Promise<BlogPost[]> {
  const url = `${BLOG_URL}/feeds/posts/default?q=${encodeURIComponent(keyword)}&alt=json&max-results=20`;

  try {
    // 검색 결과는 실시간성이 중요하므로 캐시하지 않음
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('Search API failed');
    
    const data = await res.json();
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
        content: entry.content?.$t || '', 
        publishedAt: entry.published.$t,
        thumbnail,
        categories,
      };
    });
  } catch (error) {
    console.error('Blogger Search Error:', error);
    return [];
  }
}
