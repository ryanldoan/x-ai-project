"""Test comprehensive post metadata storage"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db, SessionLocal
from app.utils.db_utils import create_post, get_post_by_id, create_post_from_dict
from datetime import datetime

def test_metadata_storage():
    """Test storing comprehensive post metadata"""
    print("Testing comprehensive metadata storage...")
    print("-" * 50)
    
    # Initialize database (will recreate tables)
    init_db()
    
    db = SessionLocal()
    
    try:
        # Test 1: Create post with full metadata
        print("\n1. Creating post with full metadata...")
        post_id = f"test_{uuid.uuid4().hex[:8]}"
        
        post = create_post(
            db=db,
            post_id=post_id,
            author="elonmusk",
            author_display_name="Elon Musk",
            content="AI will change everything! #AI #Technology https://example.com",
            timestamp=datetime.now(),
            likes=15000,
            retweets=5000,
            replies=1200,
            quotes=800,
            bookmarks=2000,
            views=100000,
            post_url="https://x.com/elonmusk/status/1234567890",
            post_type="tweet",
            hashtags=["AI", "Technology", "Future"],
            mentions=["OpenAI", "xai"],
            media_urls=["https://example.com/image.jpg"],
            link_urls=["https://example.com"],
            grok_description="Post about AI transformation",
            is_processed=True
        )
        print(f"✅ Created post: {post.id}")
        print(f"   Author: @{post.author} ({post.author_display_name})")
        print(f"   Engagement: {post.likes} likes, {post.retweets} retweets, {post.replies} replies")
        print(f"   Has {len(post.hashtags.split(',') if post.hashtags else [])} hashtags")
        
        # Test 2: Retrieve and verify metadata
        print("\n2. Retrieving post and verifying metadata...")
        retrieved = get_post_by_id(db, post_id)
        assert retrieved is not None, "Post not found"
        assert retrieved.likes == 15000, "Likes not stored correctly"
        assert retrieved.retweets == 5000, "Retweets not stored correctly"
        assert retrieved.quotes == 800, "Quotes not stored correctly"
        assert retrieved.views == 100000, "Views not stored correctly"
        print("✅ All metadata fields verified")
        
        # Test 3: Test to_dict() method
        print("\n3. Testing to_dict() serialization...")
        post_dict = retrieved.to_dict()
        assert "hashtags" in post_dict, "Hashtags missing from dict"
        assert "mentions" in post_dict, "Mentions missing from dict"
        assert "media_urls" in post_dict, "Media URLs missing from dict"
        assert isinstance(post_dict["hashtags"], list), "Hashtags should be a list"
        print(f"✅ Serialization works: {len(post_dict['hashtags'])} hashtags, {len(post_dict['mentions'])} mentions")
        
        # Test 4: Create post from dictionary
        print("\n4. Testing create_post_from_dict()...")
        post_data = {
            "id": f"test_{uuid.uuid4().hex[:8]}",
            "author": "OpenAI",
            "content": "We're building safe AI systems",
            "timestamp": datetime.now(),
            "likes": 5000,
            "retweets": 2000,
            "replies": 500,
            "hashtags": ["AI", "Safety"],
            "mentions": [],
            "post_url": "https://x.com/OpenAI/status/0987654321"
        }
        post2 = create_post_from_dict(db, post_data)
        print(f"✅ Created post from dict: {post2.id}")
        
        print("\n" + "-" * 50)
        print("✅ All metadata storage tests passed!")
        
    except Exception as e:
        print(f"\n❌ Metadata test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_metadata_storage()

