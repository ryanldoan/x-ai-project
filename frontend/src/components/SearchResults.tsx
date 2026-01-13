import type { Post, SearchResponse } from "../types";
import PostCard from "./PostCard";
import Summary from "./Summary";
import Pagination from "./Pagination";

interface SearchResultsProps {
  data: SearchResponse | null;
  loading: boolean;
  onPageChange: (offset: number) => void;
}

export default function SearchResults({
  data,
  loading,
  onPageChange,
}: SearchResultsProps) {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-black"></div>
      </div>
    );
  }

  if (!data) {
    return null;
  }

  if (data.results.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-lg text-gray-600">
          No results found for "{data.query}"
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Try a different search term
        </p>
      </div>
    );
  }

  return (
    <div className="mt-8">
      <Summary summary={data.summary} enhancedQuery={data.enhanced_query} />

      <div className="mb-4 text-sm text-gray-500">
        Found {data.total.toLocaleString()} result{data.total !== 1 ? "s" : ""}{" "}
        for "{data.query}"
      </div>

      <div className="space-y-2">
        {data.results.map((post: Post) => (
          <PostCard key={post.id} post={post} />
        ))}
      </div>

      <Pagination data={data} onPageChange={onPageChange} />
    </div>
  );
}
