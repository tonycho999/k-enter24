// src/lib/blogger.tsx

const BLOG_URL = process.env.BLOGGER_URL;

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishedAt: string;
  thumbnail: string;
  categories: string[];
}

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

      // 🚀 썸네일 해상도 완벽 해결 로직 (리스트용)
      let thumbnail = entry.media$thumbnail?.url || '';
      if (thumbnail) {
        if (thumbnail.includes('/s72-c/')) {
          thumbnail = thumbnail.replace('/s72-c/', '/w480-h320-c/'); 
        } else if (thumbnail.includes('blogger.googleusercontent.com')) {
          thumbnail = thumbnail.split('=')[0] + '=w480-h320-c';
        }
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
    console.error('Blogger API Error (getPosts):', error);
    return [];
  }
}

export async function getPostById(id: string): Promise<BlogPost | null> {
  const url = `${BLOG_URL}/feeds/posts/default/${id}?alt=json`;

  try {
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    const data = await res.json();
    const entry = data.entry;
    
    if (!entry) return null;

    // 🚀 썸네일 해상도 완벽 해결 로직 (상세 페이지용 더 큰 사이즈)
    let thumbnail = entry.media$thumbnail?.url || '';
    if (thumbnail) {
      if (thumbnail.includes('/s72-c/')) {
        thumbnail = thumbnail.replace('/s72-c/', '/w800-h600-c/'); 
      } else if (thumbnail.includes('blogger.googleusercontent.com')) {
        thumbnail = thumbnail.split('=')[0] + '=w800-h600-c';
      }
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

      // 🚀 썸네일 해상도 완벽 해결 로직 (검색 리스트용)
      let thumbnail = entry.media$thumbnail?.url || '';
      if (thumbnail) {
        if (thumbnail.includes('/s72-c/')) {
          thumbnail = thumbnail.replace('/s72-c/', '/w480-h320-c/'); 
        } else if (thumbnail.includes('blogger.googleusercontent.com')) {
          thumbnail = thumbnail.split('=')[0] + '=w480-h320-c';
        }
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
