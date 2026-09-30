// src/lib/blogger.tsx

// 환경변수에 설정된 블로그 주소만 사용합니다.
const BLOG_URL = process.env.BLOGGER_URL;

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishedAt: string;
  thumbnail: string;
  categories: string[];
}

// 1. 전체 글 또는 특정 카테고리(라벨) 글 가져오기
export async function getPosts(category?: string, maxResults: number = 20): Promise<BlogPost[]> {
  const categoryPath = category ? `/-/${encodeURIComponent(category)}` : '';
  const url = `${BLOG_URL}/feeds/posts/default${categoryPath}?alt=json&max-results=${maxResults}`;

  try {
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch posts');
    const data = await res.json();

    const entries = data.feed?.entry || [];

    return entries.map((entry: any) => {
      const rawId = entry.id.$t;
      const id = rawId.split('post-')[1];

      // 🚀 썸네일 변환 없이 원본 URL 그대로 사용
      const thumbnail = entry.media$thumbnail?.url || '';

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

    // 🚀 썸네일 변환 없이 원본 URL 그대로 사용
    const thumbnail = entry.media$thumbnail?.url || '';

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
    const res = await fetch(url, { cache: 'no-store' });
    if (!res.ok) throw new Error('Search API failed');
    
    const data = await res.json();
    const entries = data.feed?.entry || []; 

    return entries.map((entry: any) => {
      const rawId = entry.id.$t;
      const id = rawId.split('post-')[1];

      // 🚀 썸네일 변환 없이 원본 URL 그대로 사용
      const thumbnail = entry.media$thumbnail?.url || '';

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
