import type { SearchRequest, SearchResponse, Post } from "../types";

const API_BASE_URL =
  (import.meta.env.VITE_API_URL as string) || "http://localhost:8000";

export const searchPosts = async (
  request: SearchRequest
): Promise<SearchResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query: request.query,
      limit: request.limit || 20,
      offset: request.offset || 0,
      author: request.author,
      content_type: request.content_type,
      sort_by: request.sort_by || "relevance",
      use_grok_enhancement: request.use_grok_enhancement !== false,
      include_summary: request.include_summary !== false,
    }),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Search failed" }));
    throw new Error(error.detail || "Search failed");
  }

  return response.json();
};

export const getPost = async (postId: string): Promise<Post> => {
  const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`);
  if (!response.ok) throw new Error("Failed to fetch post");
  return response.json();
};

export const getStats = async () => {
  const response = await fetch(`${API_BASE_URL}/api/stats`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
};
