export interface Post {
  id: string;
  author: string;
  author_display_name?: string;
  content: string;
  timestamp: string;
  likes: number;
  retweets: number;
  replies: number;
  quotes: number;
  bookmarks: number;
  views: number;
  post_url?: string;
  post_type: string;
  content_type: string;
  hashtags: string[];
  mentions: string[];
  media_urls: any[];
  link_urls: any[];
  grok_description?: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
  offset?: number;
  author?: string;
  content_type?: string;
  sort_by?: string;
  use_grok_enhancement?: boolean;
  include_summary?: boolean;
}

export interface SearchResponse {
  results: Post[];
  total: number;
  limit: number;
  offset: number;
  query: string;
  enhanced_query?: {
    intent?: string;
    keywords?: string[];
    expanded_terms?: string[];
    query_type?: string;
  };
  summary?: string;
}
