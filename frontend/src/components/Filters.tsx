import { useState } from "react";

interface FiltersProps {
  author: string;
  contentType: string;
  sortBy: string;
  onAuthorChange: (value: string) => void;
  onContentTypeChange: (value: string) => void;
  onSortByChange: (value: string) => void;
}

const CONTENT_TYPES = [
  { value: "", label: "All Types" },
  { value: "text", label: "Text Only" },
  { value: "text_link", label: "Text + Link" },
  { value: "text_media", label: "Text + Media" },
  { value: "text_media_link", label: "Text + Media + Link" },
  { value: "media_only", label: "Media Only" },
  { value: "link_only", label: "Link Only" },
];

const SORT_OPTIONS = [
  { value: "relevance", label: "Relevance" },
  { value: "date", label: "Most Recent" },
  { value: "likes", label: "Most Liked" },
  { value: "retweets", label: "Most Retweeted" },
];

export default function Filters({
  author,
  contentType,
  sortBy,
  onAuthorChange,
  onContentTypeChange,
  onSortByChange,
}: FiltersProps) {
  const [showAuthorInput, setShowAuthorInput] = useState(false);
  const [authorInput, setAuthorInput] = useState("");

  const handleAuthorClick = () => {
    if (!showAuthorInput) {
      setShowAuthorInput(true);
      setAuthorInput(author);
    } else {
      onAuthorChange(authorInput);
      setShowAuthorInput(false);
    }
  };

  return (
    <div className="flex flex-wrap items-center justify-center gap-4 mt-4">
      {/* Author Filter Tab */}
      <div className="relative">
        {!showAuthorInput ? (
          <button
            onClick={handleAuthorClick}
            className={`px-6 py-2.5 rounded-full text-sm font-medium transition-all ${
              author
                ? "bg-black text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {author ? `Author: ${author}` : "Filter by Author"}
          </button>
        ) : (
          <div className="flex items-center gap-2 bg-white border-2 border-black rounded-full px-4 py-2.5">
            <input
              type="text"
              value={authorInput}
              onChange={(e) => setAuthorInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  handleAuthorClick();
                } else if (e.key === "Escape") {
                  setShowAuthorInput(false);
                  setAuthorInput(author);
                }
              }}
              placeholder="Enter author..."
              className="outline-none text-sm w-32"
              autoFocus
            />
            <button
              onClick={handleAuthorClick}
              className="text-black hover:opacity-70"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Content Type Filter Tab */}
      <div className="relative">
        <div className="relative">
          <select
            value={contentType}
            onChange={(e) => onContentTypeChange(e.target.value)}
            className={`appearance-none px-6 py-2.5 rounded-full text-sm font-medium transition-all cursor-pointer ${
              contentType
                ? "bg-black text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {CONTENT_TYPES.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg
              className={`w-4 h-4 ${
                contentType ? "text-white" : "text-gray-500"
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Sort By Filter Tab */}
      <div className="relative">
        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => onSortByChange(e.target.value)}
            className={`appearance-none px-6 py-2.5 rounded-full text-sm font-medium transition-all cursor-pointer ${
              sortBy !== "relevance"
                ? "bg-black text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {SORT_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg
              className={`w-4 h-4 ${
                sortBy !== "relevance" ? "text-white" : "text-gray-500"
              }`}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 9l-7 7-7-7"
              />
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
