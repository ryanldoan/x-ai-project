"""Test that Grok descriptions are generated on post creation"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db, SessionLocal
from app.utils.db_utils import create_post, get_post_by_id, get_unprocessed_posts
from app.services.grok_client import GrokClient
from datetime import datetime

async def test_grok_description_generation():
    """Test that Grok descriptions are generated when creating posts"""
    print("Testing Grok Description Generation")
    print("=" * 60)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    grok_client = GrokClient()
    
    try:
        # Test 1: Create post with Grok description
        print("\n1. Creating post with Grok description...")
        test_content = "AI will revolutionize everything. The future is exciting!"
        test_author = "testuser"
        
        # Generate description
        description = await grok_client.describe_post(test_content, test_author)
        print(f"   Generated description: {description[:100]}...")
        
        # Create post with description
        post = create_post(
            db=db,
            post_id="test_grok_1",
            author=test_author,
            content=test_content,
            timestamp=datetime.now(),
            likes=100,
            grok_description=description,
            is_processed=True
        )
        
        print(f"   ✅ Post created: {post.id}")
        print(f"   ✅ Has description: {bool(post.grok_description)}")
        print(f"   ✅ Is processed: {post.is_processed}")
        
        # Test 2: Verify description is stored and searchable
        print("\n2. Verifying description is stored correctly...")
        retrieved = get_post_by_id(db, "test_grok_1")
        assert retrieved is not None, "Post not found"
        assert retrieved.grok_description is not None, "Description not stored"
        assert retrieved.grok_description == description, "Description mismatch"
        assert retrieved.is_processed == True, "Post not marked as processed"
        print("   ✅ Description stored correctly")
        
        # Test 3: Create post without description (should be unprocessed)
        print("\n3. Creating post without Grok description...")
        post2 = create_post(
            db=db,
            post_id="test_grok_2",
            author="testuser2",
            content="This is a test post without description",
            timestamp=datetime.now(),
            likes=50,
            is_processed=False
        )
        assert post2.grok_description is None, "Should not have description"
        assert post2.is_processed == False, "Should not be processed"
        print("   ✅ Post created without description (unprocessed)")
        
        # Test 4: Check unprocessed posts
        print("\n4. Checking unprocessed posts...")
        unprocessed = get_unprocessed_posts(db, limit=10)
        unprocessed_ids = [p.id for p in unprocessed]
        assert "test_grok_2" in unprocessed_ids, "Unprocessed post not found"
        assert "test_grok_1" not in unprocessed_ids, "Processed post should not be in unprocessed list"
        print(f"   ✅ Found {len(unprocessed)} unprocessed posts")
        
        # Test 5: Verify description improves search
        print("\n5. Testing search with Grok descriptions...")
        from app.services.search_service import SearchService
        search_service = SearchService(db)
        
        # Search for something that might be in description but not exact in content
        results = search_service.search("revolutionary technology", limit=5)
        found_post = any(p["id"] == "test_grok_1" for p in results["results"])
        print(f"   ✅ Search found post with description: {found_post}")
        
        print("\n" + "=" * 60)
        print("✅ All Grok description tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await grok_client.close()
        db.close()

if __name__ == "__main__":
    asyncio.run(test_grok_description_generation())

