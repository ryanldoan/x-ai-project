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
      limit: 20,
      use_grok_enhancement: true,
      include_summary: true,
      ...request,
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
