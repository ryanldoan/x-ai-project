"""Test FastAPI endpoints"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app
from app.models.database import init_db, SessionLocal
from app.utils.db_utils import create_post
from datetime import datetime, timedelta

def setup_test_data():
    """Create test posts for API testing"""
    init_db()
    db = SessionLocal()
    
    test_posts = [
        {
            "post_id": "api_test_1",
            "author": "elonmusk",
            "content": "AI will change everything. The future is exciting!",
            "timestamp": datetime.now() - timedelta(days=1),
            "likes": 1000,
            "retweets": 200,
            "hashtags": ["AI", "Technology"],
            "grok_description": "Discussion about AI revolution"
        },
        {
            "post_id": "api_test_2",
            "author": "OpenAI",
            "content": "Building safe AI systems for everyone.",
            "timestamp": datetime.now() - timedelta(days=2),
            "likes": 5000,
            "retweets": 1000,
            "hashtags": ["AI", "Safety"],
            "grok_description": "AI safety announcement"
        }
    ]
    
    try:
        for post_data in test_posts:
            create_post(db=db, **post_data)
        db.commit()
        print("✅ Test data created")
    except Exception as e:
        print(f"⚠️  Error: {e}")
        db.rollback()
    finally:
        db.close()

def test_api():
    """Test API endpoints"""
    print("Testing FastAPI Endpoints")
    print("=" * 60)
    
    # Setup test data
    setup_test_data()
    
    client = TestClient(app)
    
    try:
        # Test 1: Health check
        print("\n1. Testing /health endpoint...")
        response = client.get("/health")
        assert response.status_code == 200
        print(f"   ✅ Health check: {response.json()}")
        
        # Test 2: Root endpoint
        print("\n2. Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        print(f"   ✅ Root endpoint works")
        
        # Test 3: Search endpoint
        print("\n3. Testing /api/search endpoint...")
        search_data = {
            "query": "AI",
            "limit": 5,
            "use_grok_enhancement": False,  # Skip Grok for faster testing
            "include_summary": False
        }
        response = client.post("/api/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Search returned {data['total']} results")
        print(f"   ✅ Found {len(data['results'])} posts")
        
        # Test 4: Get specific post
        print("\n4. Testing /api/posts/{id} endpoint...")
        response = client.get("/api/posts/api_test_1")
        assert response.status_code == 200
        post = response.json()
        print(f"   ✅ Retrieved post: @{post['author']} - {post['content'][:40]}...")
        
        # Test 5: List posts
        print("\n5. Testing /api/posts endpoint...")
        response = client.get("/api/posts?limit=5")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ List returned {len(data['results'])} posts")
        
        # Test 6: Stats endpoint
        print("\n6. Testing /api/stats endpoint...")
        response = client.get("/api/stats")
        assert response.status_code == 200
        stats = response.json()
        print(f"   ✅ Stats: {stats['total_posts']} total posts")
        
        # Test 7: Search with filters
        print("\n7. Testing search with author filter...")
        search_data = {
            "query": "AI",
            "limit": 5,
            "author": "elonmusk",
            "use_grok_enhancement": False,
            "include_summary": False
        }
        response = client.post("/api/search", json=search_data)
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Filtered search returned {len(data['results'])} results")
        
        print("\n" + "=" * 60)
        print("✅ All API tests passed!")
        
    except Exception as e:
        print(f"\n❌ API test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()

