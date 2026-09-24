// src/app/sitemap.ts
import { MetadataRoute } from 'next';
// Prisma 대신 Blogger에서 전체 글을 가져오는 함수 사용
import { getPosts } from '../lib/blogger';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://k-enter24.com'; // 실제 도메인으로 변경해 주세요.

  // 1. 고정된 기본 메뉴들
  const staticRoutes = ['', '/k-pop', '/k-drama', '/k-movie', '/k-entertainment', '/k-culture'].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'hourly' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  // 2. Blogger에서 전체 글 목록 가져오기
  // (참고: SEO를 위해 가능한 많은 글을 사이트맵에 등록해야 하므로 Blogger API 호출 시 
  // max-results 파라미터를 크게 잡는 것이 좋습니다. 이 부분은 뒤에 설명 추가했습니다.)
  const posts = await getPosts();

  const dynamicRoutes = posts.map((post) => {
    // 카테고리가 여러 개인 경우 첫 번째 사용, 없을 경우 'news' 기본값 처리
    const category = post.categories && post.categories.length > 0 ? post.categories[0] : 'news';
    
    return {
      url: `${baseUrl}/${category.toLowerCase()}/${post.id}`,
      // Blogger는 updatedAt을 명시적으로 주지 않아 publishedAt을 사용합니다.
      lastModified: new Date(post.publishedAt),
      changeFrequency: 'daily' as const,
      priority: 0.6,
    };
  });

  return [...staticRoutes, ...dynamicRoutes];
}
