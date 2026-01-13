import type { Post } from "../types";

interface PostCardProps {
  post: Post;
}

export default function PostCard({ post }: PostCardProps) {
  const formatDate = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return "just now";
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;

      return date.toLocaleDateString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-black rounded-full flex items-center justify-center text-white font-semibold">
            {post.author[0].toUpperCase()}
          </div>
          <div>
            <div className="font-semibold text-gray-900">
              {post.author_display_name || `@${post.author}`}
            </div>
            <div className="text-sm text-gray-500">@{post.author}</div>
          </div>
        </div>
        <div className="text-sm text-gray-500">
          {formatDate(post.timestamp)}
        </div>
      </div>

      <p className="text-gray-800 mb-4 whitespace-pre-wrap">{post.content}</p>

      {post.hashtags && post.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {post.hashtags.map((tag, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
            >
              #{tag}
            </span>
          ))}
        </div>
      )}

      {post.mentions && post.mentions.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {post.mentions.map((mention, idx) => (
            <span
              key={idx}
              className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-sm"
            >
              @{mention}
            </span>
          ))}
        </div>
      )}

      <div className="flex items-center gap-6 text-sm text-gray-600 pt-3 border-t border-gray-100">
        <div className="flex items-center gap-1">
          <span className="text-red-500">❤️</span>
          <span>{post.likes.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-green-500">🔄</span>
          <span>{post.retweets.toLocaleString()}</span>
        </div>
        <div className="flex items-center gap-1">
          <span className="text-blue-500">💬</span>
          <span>{post.replies.toLocaleString()}</span>
        </div>
        {post.views > 0 && (
          <div className="flex items-center gap-1">
            <span className="text-gray-500">👁️</span>
            <span>{post.views.toLocaleString()}</span>
          </div>
        )}
      </div>

      {post.post_url && (
        <a
          href={post.post_url}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-block text-black hover:underline text-sm"
        >
          View on X →
        </a>
      )}
    </div>
  );
}
