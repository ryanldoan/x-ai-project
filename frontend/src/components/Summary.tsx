import { useState } from "react";

interface SummaryProps {
  summary?: string;
  enhancedQuery?: {
    intent?: string;
    keywords?: string[];
    expanded_terms?: string[];
    query_type?: string;
  };
}

export default function Summary({ summary, enhancedQuery }: SummaryProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!summary && !enhancedQuery) return null;

  const wordCount = summary
    ? summary.split(/\s+/).filter((word) => word.length > 0).length
    : 0;
  const shouldTruncate = wordCount > 80;

  let displaySummary = summary || "";
  if (shouldTruncate && !isExpanded && summary) {
    const words = summary.split(/\s+/);
    displaySummary = words.slice(0, 80).join(" ") + "...";
  }

  return (
    <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
      {enhancedQuery?.keywords && enhancedQuery.keywords.length > 0 && (
        <div className="mb-3 pb-3 border-b border-gray-200">
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-gray-500 font-medium">Keywords:</span>
            {enhancedQuery.keywords.slice(0, 8).map((keyword, idx) => (
              <span
                key={idx}
                className="px-2 py-1 bg-white border border-gray-300 rounded-md text-xs text-gray-700 font-medium"
              >
                {keyword}
              </span>
            ))}
            {enhancedQuery.keywords.length > 8 && (
              <span className="text-xs text-gray-500">
                +{enhancedQuery.keywords.length - 8} more
              </span>
            )}
          </div>
        </div>
      )}

      {summary && (
        <div>
          <h3 className="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
            Summary
          </h3>
          <p className="text-sm text-gray-700 leading-relaxed">
            {displaySummary}
          </p>
          {shouldTruncate && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="mt-2 text-sm text-black hover:underline font-medium"
            >
              {isExpanded ? "View Less" : "View More"}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
