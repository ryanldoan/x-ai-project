import { useState } from "react";

function App() {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      console.log("Searching for:", query);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      <main className="flex-1 flex items-center justify-center px-4">
        <div className="w-full max-w-3xl">
          <div className="text-center mb-4">
            <h1 className="text-7xl sm:text-8xl font-bold text-black mb-4 tracking-tight">
              Groktor-X
            </h1>
            <p className="text-lg text-gray-600">
              AI-enhanced queries, semantic matching, and intelligent summaries.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="mb-8">
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

              <div className="mt-4 text-center">
                <p className="text-sm text-gray-500 mb-2">
                  Trending:{" "}
                  <span className="text-black font-medium hover:underline cursor-pointer">
                    AI
                  </span>{" "}
                  •{" "}
                  <span className="text-black font-medium hover:underline cursor-pointer">
                    AI AND space
                  </span>{" "}
                  •{" "}
                  <span className="text-black font-medium hover:underline cursor-pointer">
                    technology OR innovation
                  </span>
                </p>
              </div>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
