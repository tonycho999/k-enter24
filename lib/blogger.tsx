// lib/blogger.ts
const BLOG_URL = process.env.BLOGGER_URL || 'https://본인블로그주소.blogspot.com';

export interface BlogPost {
  id: string;
  title: string;
  content: string;
  publishedAt: string;
  thumbnail: string;
  categories: string[];
}

// 1. 전체 글 또는 특정 카테고리(라벨) 글 가져오기
export async function getPosts(category?: string): Promise<BlogPost[]> {
  // 카테고리가 있으면 해당 라벨의 글만, 없으면 전체 글
  const categoryPath = category ? `/-/${encodeURIComponent(category)}` : '';
  const url = `${BLOG_URL}/feeds/posts/default${categoryPath}?alt=json&max-results=20`;

  try {
    // Vercel에서 60초마다 최신화(ISR)하도록 설정
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) throw new Error('Failed to fetch posts');
    const data = await res.json();

    const entries = data.feed.entry || [];

    return entries.map((entry: any) => {
      // 1. ID 추출 (형태: tag:blogger.com,1999:blog-xxx.post-yyy -> yyy 추출)
      const rawId = entry.id.$t;
      const id = rawId.split('post-')[1];

      // 2. 썸네일 해상도 최적화 (Blogger 기본 썸네일은 72px로 매우 작음)
      // 기획하신 240x160 썸네일 크기에 맞춰 고해상도로 주소 치환
      let thumbnail = entry.media$thumbnail?.url || '';
      if (thumbnail) {
        thumbnail = thumbnail.replace('/s72-c/', '/w240-h160-c/'); 
      }

      // 3. 카테고리(라벨) 추출
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
    console.error('Blogger API Error:', error);
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

    let thumbnail = entry.media$thumbnail?.url || '';
    if (thumbnail) {
      thumbnail = thumbnail.replace('/s72-c/', '/w800-h600-c/'); // 상세페이지용 큰 이미지
    }

    return {
      id,
      title: entry.title.$t,
      content: entry.content.$t,
      publishedAt: entry.published.$t,
      thumbnail,
      categories: entry.category ? entry.category.map((cat: any) => cat.term) : [],
    };
  } catch (error) {
    return null;
  }
}
