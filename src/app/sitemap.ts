// src/app/sitemap.ts
import { MetadataRoute } from 'next';
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://k-enter24.com';

  // 1. 고정된 기본 메뉴들
  const staticRoutes = ['', '/k-pop', '/k-drama', '/k-movie', '/k-entertainment', '/k-culture'].map((route) => ({
    url: `${baseUrl}${route}`,
    lastModified: new Date(),
    changeFrequency: 'hourly' as const,
    priority: route === '' ? 1.0 : 0.8,
  }));

  // 2. DB에서 모든 글을 가져와서 사이트맵에 자동 추가!
  const posts = await prisma.post.findMany({
    select: { id: true, category: true, updatedAt: true },
    orderBy: { createdAt: 'desc' },
  });

  const dynamicRoutes = posts.map((post) => ({
    url: `${baseUrl}/${post.category.toLowerCase()}/${post.id}`,
    lastModified: post.updatedAt,
    changeFrequency: 'daily' as const,
    priority: 0.6,
  }));

  return [...staticRoutes, ...dynamicRoutes];
}
