import { MetadataRoute } from 'next';
import { getPosts } from '@/lib/blogger';

const BASE_URL = 'https://k-enter24.com';
const CATEGORIES = ['sights', 'food', 'style', 'tips'];
const INFO_PAGES = ['/about', '/contact', '/privacy', '/terms'];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const posts = await getPosts(undefined, 150);

  // 기사별 카테고리와 날짜 정리
  const articles = posts.map((post) => {
    const category = (post.categories?.[0] || 'tips').toLowerCase();
    return { category, id: post.id, date: new Date(post.publishedAt) };
  });

  // 카테고리별 최신 글 날짜 (글이 없으면 undefined)
  const latestOf = (cat?: string) => {
    const list = cat ? articles.filter((a) => a.category === cat) : articles;
    return list.length ? new Date(Math.max(...list.map((a) => a.date.getTime()))) : undefined;
  };

  // 1. 홈
  const home: MetadataRoute.Sitemap = [{ url: BASE_URL, lastModified: latestOf() }];

  // 2. 카테고리
  const categoryRoutes: MetadataRoute.Sitemap = CATEGORIES.map((cat) => ({
    url: \\\`${BASE_URL}/${cat}\\\`,
    lastModified: latestOf(cat),
  }));

  // 3. 정보 페이지 (날짜 생략: 자주 바뀌지 않음)
  const infoRoutes: MetadataRoute.Sitemap = INFO_PAGES.map((path) => ({ url: \\\`${BASE_URL}${path}\\\` }));

  // 4. 기사
  const articleRoutes: MetadataRoute.Sitemap = articles.map((a) => ({
    url: \\\`${BASE_URL}/${a.category}/${a.id}\\\`,
    lastModified: a.date,
  }));

  return [...home, ...categoryRoutes, ...articleRoutes, ...infoRoutes];
}
