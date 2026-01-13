import type { SearchResponse } from "../types";

interface PaginationProps {
  data: SearchResponse;
  onPageChange: (offset: number) => void;
}

export default function Pagination({ data, onPageChange }: PaginationProps) {
  const { total, limit = 20, offset = 0 } = data;

  // Calculate pagination values
  const currentPage = Math.floor(offset / limit) + 1;
  const totalPages = Math.ceil(total / limit);
  const startResult = offset + 1;
  const endResult = Math.min(offset + limit, total);

  // Only show pagination if there are multiple pages
  if (!total || totalPages <= 1) {
    return null;
  }

  const handlePrevious = () => {
    if (offset > 0) {
      onPageChange(Math.max(0, offset - limit));
    }
  };

  const handleNext = () => {
    if (offset + limit < total) {
      onPageChange(offset + limit);
    }
  };

  const handlePageClick = (page: number) => {
    onPageChange((page - 1) * limit);
  };

  const getPageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxVisible = 7;

    if (totalPages <= maxVisible) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      pages.push(1);

      if (currentPage > 3) {
        pages.push("...");
      }

      const start = Math.max(2, currentPage - 1);
      const end = Math.min(totalPages - 1, currentPage + 1);

      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      if (currentPage < totalPages - 2) {
        pages.push("...");
      }

      pages.push(totalPages);
    }

    return pages;
  };

  return (
    <div className="mt-6 pb-12 flex flex-col items-center gap-3">
      <div className="text-xs text-gray-500">
        Showing {startResult.toLocaleString()} - {endResult.toLocaleString()} of{" "}
        {total.toLocaleString()} results
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={handlePrevious}
          disabled={offset === 0}
          className="px-3 py-1.5 rounded-full text-sm text-black hover:bg-gray-100 disabled:text-gray-300 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
          aria-label="Previous page"
        >
          ←
        </button>

        <div className="flex items-center gap-0.5">
          {getPageNumbers().map((page, index) => {
            if (page === "...") {
              return (
                <span
                  key={`ellipsis-${index}`}
                  className="px-2 text-gray-400 text-sm"
                >
                  ...
                </span>
              );
            }

            const pageNum = page as number;
            const isActive = pageNum === currentPage;

            return (
              <button
                key={pageNum}
                onClick={() => handlePageClick(pageNum)}
                className={`min-w-[32px] px-2 py-1.5 rounded-full text-sm transition-colors ${
                  isActive
                    ? "bg-black text-white font-semibold"
                    : "text-gray-700 hover:bg-gray-100"
                }`}
              >
                {pageNum}
              </button>
            );
          })}
        </div>

        <button
          onClick={handleNext}
          disabled={offset + limit >= total}
          className="px-3 py-1.5 rounded-full text-sm text-black hover:bg-gray-100 disabled:text-gray-300 disabled:cursor-not-allowed disabled:hover:bg-transparent transition-colors"
          aria-label="Next page"
        >
          →
        </button>
      </div>
    </div>
  );
}
