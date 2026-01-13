import { useState } from "react";
import type { SearchResponse } from "./types";
import { searchPosts } from "./services/api";
import SearchResults from "./components/SearchResults";
import Filters from "./components/Filters";

function App() {
  const [query, setQuery] = useState("");
  const [searchData, setSearchData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [author, setAuthor] = useState("");
  const [contentType, setContentType] = useState("");
  const [sortBy, setSortBy] = useState("relevance");
  const [offset, setOffset] = useState(0);
  const [limit] = useState(20);

  // Cache for query summary and enhanced query (keyed by query signature)
  const [queryCache, setQueryCache] = useState<
    Map<string, { summary?: string; enhanced_query?: any }>
  >(new Map());

  const getQuerySignature = (
    query: string,
    author: string,
    contentType: string,
    sortBy: string
  ): string => {
    return `${query}|${author}|${contentType}|${sortBy}`;
  };

  const handleSubmit = async (
    e?: React.FormEvent,
    overrideFilters?: {
      author?: string;
      contentType?: string;
      sortBy?: string;
      offset?: number;
    },
    isPaginationOnly: boolean = false
  ) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    // Use override values if provided, otherwise use current state
    const searchAuthor =
      overrideFilters?.author !== undefined ? overrideFilters.author : author;
    const searchContentType =
      overrideFilters?.contentType !== undefined
        ? overrideFilters.contentType
        : contentType;
    const searchSortBy =
      overrideFilters?.sortBy !== undefined ? overrideFilters.sortBy : sortBy;
    const searchOffset =
      overrideFilters?.offset !== undefined ? overrideFilters.offset : offset;

    // Create query signature for caching
    const querySig = getQuerySignature(
      query.trim(),
      searchAuthor,
      searchContentType,
      searchSortBy
    );

    // Check if we have cached summary/enhanced query for this query
    const cached = queryCache.get(querySig);
    const shouldSkipSummary = isPaginationOnly && cached;

    // Determine the offset to use
    const finalOffset = isPaginationOnly ? searchOffset : 0;

    // Reset offset state if this is a new search (not pagination)
    if (!isPaginationOnly) {
      setOffset(0);
    }

    try {
      const response = await searchPosts({
        query: query.trim(),
        author: searchAuthor.trim() || undefined,
        content_type: searchContentType || undefined,
        sort_by: searchSortBy,
        limit: limit,
        offset: finalOffset,
        include_summary: !shouldSkipSummary, // Skip summary if we have cached one
        use_grok_enhancement: !shouldSkipSummary, // Skip query enhancement if we have cached one
      });

      // If we skipped summary generation, use cached values
      if (shouldSkipSummary && cached) {
        response.summary = cached.summary;
        response.enhanced_query = cached.enhanced_query;
      } else if (response.summary || response.enhanced_query) {
        // Cache the summary and enhanced query for future pagination
        setQueryCache((prev) => {
          const newCache = new Map(prev);
          newCache.set(querySig, {
            summary: response.summary,
            enhanced_query: response.enhanced_query,
          });
          return newCache;
        });
      }

      setSearchData(response);
      setOffset(finalOffset);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setSearchData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTrendingClick = (trendingQuery: string) => {
    setQuery(trendingQuery);
    setTimeout(() => {
      handleSubmit();
    }, 100);
  };

  const handleLogoClick = () => {
    setQuery("");
    setSearchData(null);
    setError(null);
    setAuthor("");
    setContentType("");
    setSortBy("relevance");
    setOffset(0);
    setQueryCache(new Map());
  };

  const handlePageChange = (newOffset: number) => {
    setOffset(newOffset);
    handleSubmit(undefined, { offset: newOffset }, true);
  };

  const showCompactLayout = loading || searchData !== null;

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <main
        className={`flex-1 ${
          showCompactLayout ? "pt-6" : "flex items-center justify-center"
        } px-4`}
      >
        <div className="w-full max-w-3xl mx-auto">
          {showCompactLayout ? (
            <div className="mb-6">
              <h1
                className="text-3xl font-bold text-black mb-2 tracking-tight cursor-pointer hover:opacity-70 transition-opacity"
                onClick={handleLogoClick}
              >
                Groktor-X
              </h1>
            </div>
          ) : (
            <div className="text-center mb-4">
              <h1 className="text-7xl sm:text-8xl font-bold text-black mb-4 tracking-tight">
                Groktor-X
              </h1>
              <p className="text-lg text-gray-600">
                AI-enhanced queries, semantic matching, and intelligent
                summaries.
              </p>
            </div>
          )}

          <form
            onSubmit={handleSubmit}
            className={showCompactLayout ? "mb-6" : "mb-8"}
          >
            <div className="relative group">
              <div className="relative">
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search posts..."
                  className="w-full px-6 py-4 pl-14 pr-16 text-lg rounded-full border-2 border-gray-300 focus:border-black focus:outline-none shadow-sm hover:shadow-md transition-all duration-200 bg-white text-black placeholder-gray-500"
                  autoFocus
                />

                <div className="absolute left-5 top-1/2 -translate-y-1/2 text-gray-500">
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                  </svg>
                </div>

                <button
                  type="submit"
                  disabled={!query.trim()}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-black text-white rounded-full hover:bg-gray-800 disabled:bg-gray-200 disabled:text-gray-400 disabled:cursor-not-allowed transition-all hover:scale-110 disabled:hover:scale-100"
                  title="Search"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 7l5 5m0 0l-5 5m5-5H6"
                    />
                  </svg>
                </button>
              </div>

              {!showCompactLayout && (
                <Filters
                  author={author}
                  contentType={contentType}
                  sortBy={sortBy}
                  onAuthorChange={setAuthor}
                  onContentTypeChange={setContentType}
                  onSortByChange={setSortBy}
                />
              )}

              {!showCompactLayout && (
                <div className="mt-4 text-center">
                  <p className="text-sm text-gray-500 mb-2">
                    Trending:{" "}
                    <span
                      className="text-black font-medium hover:underline cursor-pointer"
                      onClick={() => handleTrendingClick("AI")}
                    >
                      AI
                    </span>{" "}
                    •{" "}
                    <span
                      className="text-black font-medium hover:underline cursor-pointer"
                      onClick={() => handleTrendingClick("Crypto")}
                    >
                      Crypto
                    </span>{" "}
                    •{" "}
                    <span
                      className="text-black font-medium hover:underline cursor-pointer"
                      onClick={() => handleTrendingClick("Healthcare")}
                    >
                      Healthcare
                    </span>
                  </p>
                </div>
              )}
            </div>
          </form>

          {showCompactLayout && (
            <Filters
              author={author}
              contentType={contentType}
              sortBy={sortBy}
              onAuthorChange={(value: string) => {
                setAuthor(value);
                // Trigger new search with updated author filter (pass new value directly)
                if (query.trim()) {
                  handleSubmit(undefined, {
                    author: value,
                    contentType,
                    sortBy,
                  });
                }
              }}
              onContentTypeChange={(value: string) => {
                setContentType(value);
                // Trigger new search with updated content type filter (pass new value directly)
                if (query.trim()) {
                  handleSubmit(undefined, {
                    author,
                    contentType: value,
                    sortBy,
                  });
                }
              }}
              onSortByChange={(value: string) => {
                setSortBy(value);
                // Trigger new search with updated sort (pass new value directly)
                if (query.trim()) {
                  handleSubmit(undefined, {
                    author,
                    contentType,
                    sortBy: value,
                  });
                }
              }}
            />
          )}

          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-center">
              {error}
            </div>
          )}

          <SearchResults
            data={searchData}
            loading={loading}
            onPageChange={handlePageChange}
          />
        </div>
      </main>
    </div>
  );
}

export default App;
