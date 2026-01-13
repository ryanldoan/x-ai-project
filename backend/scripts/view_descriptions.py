"""View Grok descriptions for posts in the database"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal, Post
from app.utils.db_utils import get_all_posts, get_post_count
import argparse

def view_descriptions(limit: int = 10, author: str = None):
    """View Grok descriptions for posts"""
    db = SessionLocal()
    
    try:
        total = get_post_count(db)
        processed = db.query(Post).filter(Post.is_processed == True).count()
        with_desc = db.query(Post).filter(Post.grok_description.isnot(None)).count()
        
        print("=" * 70)
        print(f"Database Statistics:")
        print(f"  Total posts: {total}")
        print(f"  Processed: {processed}")
        print(f"  With descriptions: {with_desc}")
        print("=" * 70)
        print()
        
        # Get posts
        if author:
            posts = db.query(Post).filter(Post.author == author).order_by(Post.timestamp.desc()).limit(limit).all()
            print(f"Posts by @{author}:\n")
        else:
            posts = get_all_posts(db, limit=limit)
            print(f"Recent posts:\n")
        
        for i, post in enumerate(posts, 1):
            print(f"{i}. @{post.author} ({post.author_display_name or post.author})")
            print(f"   Content: {post.content[:80]}...")
            if post.grok_description:
                print(f"   ✅ Description: {post.grok_description[:150]}...")
                print(f"   Status: Processed")
            else:
                print(f"   ❌ No description")
                print(f"   Status: Unprocessed")
            print(f"   Likes: {post.likes}, Retweets: {post.retweets}")
            print()
        
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="View Grok descriptions for posts")
    parser.add_argument("--limit", type=int, default=10, help="Number of posts to show (default: 10)")
    parser.add_argument("--author", type=str, help="Filter by author username")
    args = parser.parse_args()
    
    view_descriptions(limit=args.limit, author=args.author)

