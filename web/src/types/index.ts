export interface LiveNewsItem {
  id: string;
  category: string;
  keyword: string; // DB에 추가됨
  title: string;
  summary: string;
  link: string;
  image_url?: string | null;
  created_at: string;
  score?: number;   // 트렌드 점수 (옵션)
  likes: number;    // 좋아요 수 (필수)
}

export interface RankingItemData {
  id: string;
  category: string;
  rank: number;
  title: string;
  meta_info?: string; // 가수 이름, 방송사 등 부가정보
  score?: number;
  updated_at?: string;
}

export interface InsightData {
  summary: string;
  generated_at: string;
}
