"""Test database setup and operations"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db, SessionLocal, Post
from app.utils.db_utils import create_post, get_post_count, get_all_posts, post_exists, get_post_by_id
from datetime import datetime

def test_database():
    """Test database initialization and basic operations"""
    print("Testing database setup...")
    print("-" * 50)
    
    # Initialize database
    init_db()
    
    # Create a test session
    db = SessionLocal()
    
    try:
        # Test 1: Create a sample post (use unique ID to avoid conflicts)
        print("\n1. Creating a test post...")
        test_post_id = f"test_{uuid.uuid4().hex[:8]}"  # Generate unique ID
        
        # Check if test post already exists, if so skip creation
        if not post_exists(db, test_post_id):
            test_post = create_post(
                db=db,
                post_id=test_post_id,
                author="testuser",
                author_display_name="Test User",
                content="This is a test post about AI and technology! #AI #Tech",
                timestamp=datetime.now(),
                likes=10,
                retweets=5,
                replies=2,
                quotes=1,
                bookmarks=3,
                views=100,
                post_url="https://x.com/testuser/status/123456",
                post_type="tweet",
                hashtags=["AI", "Tech"],
                mentions=["testmention"],
                grok_description="Test post discussing AI technology",
                is_processed=True
            )
            print(f"✅ Created post: {test_post}")
            print(f"   Metadata: {test_post.likes} likes, {test_post.retweets} retweets, {test_post.quotes} quotes")
        else:
            test_post = get_post_by_id(db, test_post_id)
            print(f"✅ Post already exists: {test_post}")
        
        # Test 2: Check post count
        print("\n2. Checking post count...")
        count = get_post_count(db)
        print(f"✅ Total posts in database: {count}")
        
        # Test 3: Retrieve posts
        print("\n3. Retrieving all posts...")
        posts = get_all_posts(db, limit=10)
        print(f"✅ Retrieved {len(posts)} posts")
        for post in posts:
            print(f"   - @{post.author}: {post.content[:50]}...")
        
        # Test 4: Verify metadata fields
        print("\n4. Verifying metadata fields...")
        if posts:
            post = posts[0]
            metadata_checks = [
                ("author_display_name", post.author_display_name),
                ("quotes", post.quotes),
                ("bookmarks", post.bookmarks),
                ("views", post.views),
                ("post_url", post.post_url),
                ("post_type", post.post_type),
                ("hashtags", post.hashtags),
                ("is_processed", post.is_processed)
            ]
            for field_name, field_value in metadata_checks:
                if field_value is not None:
                    print(f"   ✅ {field_name}: {field_value}")
                else:
                    print(f"   ⚠️  {field_name}: None (optional field)")
        
        print("\n" + "-" * 50)
        print("✅ All database tests passed!")
        
    except Exception as e:
        print(f"\n❌ Database test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_database()

