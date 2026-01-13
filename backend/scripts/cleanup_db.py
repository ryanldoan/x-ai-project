"""Utility script to clean up the database"""
import sys
import argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import SessionLocal
from app.utils.db_utils import get_all_posts, get_post_count
from sqlalchemy import delete
from app.models.database import Post

def cleanup_sample_data():
    """Remove sample data (posts with very long numeric IDs that look generated)"""
    db = SessionLocal()
    try:
        # Sample data IDs are typically 19-digit numbers
        # Real tweet IDs are also 19 digits, but we can identify sample data by:
        # 1. Very high random numbers (sample generator creates large random IDs)
        # 2. Or we can delete by author if we know which accounts were sample
        
        # Option: Delete all posts (nuclear option)
        count = get_post_count(db)
        print(f"⚠️  Current posts in database: {count}")
        
        response = input("Delete ALL posts? (yes/no): ")
        if response.lower() == 'yes':
            db.execute(delete(Post))
            db.commit()
            print(f"✅ Deleted all {count} posts")
        else:
            print("❌ Cancelled")
            
    finally:
        db.close()

def cleanup_by_author(authors: list):
    """Remove posts from specific authors"""
    db = SessionLocal()
    try:
        for author in authors:
            count = db.query(Post).filter(Post.author == author).count()
            if count > 0:
                db.query(Post).filter(Post.author == author).delete()
                db.commit()
                print(f"✅ Deleted {count} posts from @{author}")
            else:
                print(f"⚠️  No posts found for @{author}")
    finally:
        db.close()

def show_stats():
    """Show database statistics"""
    db = SessionLocal()
    try:
        total = get_post_count(db)
        print(f"\n📊 Database Statistics")
        print(f"{'='*50}")
        print(f"Total posts: {total}")
        
        # Group by author
        posts = get_all_posts(db, limit=1000)
        authors = {}
        for post in posts:
            authors[post.author] = authors.get(post.author, 0) + 1
        
        print(f"\nPosts by author:")
        for author, count in sorted(authors.items(), key=lambda x: x[1], reverse=True):
            print(f"  @{author}: {count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database cleanup utility")
    parser.add_argument("--clean-all", action="store_true", help="Delete all posts")
    parser.add_argument("--clean-authors", nargs="+", help="Delete posts from specific authors")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    args = parser.parse_args()
    
    if args.stats:
        show_stats()
    elif args.clean_all:
        cleanup_sample_data()
    elif args.clean_authors:
        cleanup_by_author(args.clean_authors)
    else:
        print("Use --stats to view database, --clean-all to delete all, or --clean-authors to delete by author")
        show_stats()

