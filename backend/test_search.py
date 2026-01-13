"""Test token-based search functionality"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import init_db, SessionLocal
from app.services.search_service import SearchService
from app.utils.db_utils import create_post
from datetime import datetime, timedelta
import random

def create_test_posts():
    """Create test posts for search testing"""
    db = SessionLocal()
    
    test_posts = [
        {
            "post_id": "test_ai_1",
            "author": "elonmusk",
            "content": "AI will revolutionize everything. The future is exciting!",
            "timestamp": datetime.now() - timedelta(days=1),
            "likes": 1000,
            "retweets": 200,
            "hashtags": ["AI", "Technology", "Future"],
            "grok_description": "Discussion about AI revolution and future technology"
        },
        {
            "post_id": "test_ai_2",
            "author": "OpenAI",
            "content": "We're building safe AI systems for everyone.",
            "timestamp": datetime.now() - timedelta(days=2),
            "likes": 5000,
            "retweets": 1000,
            "hashtags": ["AI", "Safety"],
            "grok_description": "Announcement about safe AI development"
        },
        {
            "post_id": "test_space_1",
            "author": "elonmusk",
            "content": "SpaceX is launching to Mars next year!",
            "timestamp": datetime.now() - timedelta(days=3),
            "likes": 2000,
            "retweets": 500,
            "hashtags": ["SpaceX", "Mars"],
            "grok_description": "SpaceX Mars mission announcement"
        },
        {
            "post_id": "test_tech_1",
            "author": "technews",
            "content": "New technology breakthrough in quantum computing",
            "timestamp": datetime.now() - timedelta(days=4),
            "likes": 800,
            "retweets": 150,
            "hashtags": ["Technology", "Quantum"],
            "grok_description": "News about quantum computing advances"
        },
        {
            "post_id": "test_ai_space",
            "author": "elonmusk",
            "content": "AI and space exploration will change humanity forever",
            "timestamp": datetime.now() - timedelta(days=5),
            "likes": 3000,
            "retweets": 800,
            "hashtags": ["AI", "Space", "Future"],
            "grok_description": "Discussion connecting AI and space exploration"
        }
    ]
    
    try:
        for post_data in test_posts:
            create_post(db=db, **post_data)
        db.commit()
        print(f"✅ Created {len(test_posts)} test posts")
    except Exception as e:
        print(f"⚠️  Error creating test posts: {e}")
        db.rollback()
    finally:
        db.close()

def test_search():
    """Test search functionality"""
    print("Testing Token-Based Search Service")
    print("=" * 60)
    
    # Initialize database
    init_db()
    
    # Create test posts
    print("\n1. Creating test posts...")
    create_test_posts()
    
    db = SessionLocal()
    search_service = SearchService(db)
    
    try:
        # Test 1: Simple search
        print("\n2. Testing simple search (AI)...")
        results = search_service.search("AI", limit=10)
        print(f"   Found {results['total']} results")
        for i, post in enumerate(results['results'][:3], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        # Test 2: Boolean AND
        print("\n3. Testing boolean AND (AI AND space)...")
        results = search_service.search("AI AND space", limit=10)
        print(f"   Found {results['total']} results")
        for i, post in enumerate(results['results'], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        # Test 3: Boolean OR
        print("\n4. Testing boolean OR (AI OR quantum)...")
        results = search_service.search("AI OR quantum", limit=10)
        print(f"   Found {results['total']} results")
        for i, post in enumerate(results['results'][:3], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        # Test 4: Boolean NOT
        print("\n5. Testing boolean NOT (AI NOT space)...")
        results = search_service.search("AI NOT space", limit=10)
        print(f"   Found {results['total']} results")
        for i, post in enumerate(results['results'][:3], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        # Test 5: Sort by likes
        print("\n6. Testing sort by likes...")
        results = search_service.search("AI", limit=5, sort_by="likes")
        print(f"   Top posts by likes:")
        for i, post in enumerate(results['results'], 1):
            print(f"   {i}. @{post['author']}: {post['likes']} likes - {post['content'][:40]}...")
        
        # Test 6: Search by hashtag
        print("\n7. Testing hashtag search (#AI)...")
        results = search_service.search_by_hashtag("AI", limit=5)
        print(f"   Found {len(results)} posts with #AI")
        for i, post in enumerate(results[:3], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        # Test 7: Filter by author
        print("\n8. Testing author filter...")
        results = search_service.search("AI", limit=10, author="elonmusk")
        print(f"   Found {results['total']} AI posts by elonmusk")
        for i, post in enumerate(results['results'], 1):
            print(f"   {i}. @{post['author']}: {post['content'][:50]}...")
        
        print("\n" + "=" * 60)
        print("✅ All search tests completed!")
        
    except Exception as e:
        print(f"\n❌ Search test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_search()

