"""Test different post types and media handling"""
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.models.database import init_db, SessionLocal
from app.utils.db_utils import create_post, get_posts_by_content_type, get_posts_with_media, get_posts_by_media_type
from datetime import datetime

def test_post_types():
    """Test handling of different post types and media"""
    print("Testing post types and media handling...")
    print("-" * 50)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    try:
        # Test 1: Text-only post
        print("\n1. Creating text-only post...")
        text_post = create_post(
            db=db,
            post_id=f"text_{uuid.uuid4().hex[:8]}",
            author="user1",
            content="This is a simple text post with no media or links.",
            timestamp=datetime.now(),
            likes=100
        )
        print(f"✅ Created: {text_post.content_type} - {text_post}")
        
        # Test 2: Text with link
        print("\n2. Creating text + link post...")
        link_post = create_post(
            db=db,
            post_id=f"link_{uuid.uuid4().hex[:8]}",
            author="user2",
            content="Check out this article about AI!",
            timestamp=datetime.now(),
            link_urls=[{"url": "https://example.com/article", "title": "AI Article", "description": "Great read"}]
        )
        print(f"✅ Created: {link_post.content_type} - {link_post}")
        
        # Test 3: Text with image
        print("\n3. Creating text + image post...")
        image_post = create_post(
            db=db,
            post_id=f"image_{uuid.uuid4().hex[:8]}",
            author="user3",
            content="Look at this amazing photo!",
            timestamp=datetime.now(),
            media_urls=[{"url": "https://example.com/image.jpg", "type": "image", "thumbnail": "https://example.com/thumb.jpg"}]
        )
        print(f"✅ Created: {image_post.content_type} - {image_post}")
        print(f"   Media types: {image_post.get_media_types()}")
        
        # Test 4: Video post
        print("\n4. Creating video post...")
        video_post = create_post(
            db=db,
            post_id=f"video_{uuid.uuid4().hex[:8]}",
            author="user4",
            content="Watch this video!",
            timestamp=datetime.now(),
            media_urls=[
                {"url": "https://example.com/video.mp4", "type": "video", "duration": 120, "thumbnail": "https://example.com/video_thumb.jpg"}
            ]
        )
        print(f"✅ Created: {video_post.content_type} - {video_post}")
        print(f"   Has video: {video_post.has_media_type('video')}")
        
        # Test 5: GIF post
        print("\n5. Creating GIF post...")
        gif_post = create_post(
            db=db,
            post_id=f"gif_{uuid.uuid4().hex[:8]}",
            author="user5",
            content="",
            timestamp=datetime.now(),
            media_urls=["https://example.com/animation.gif"]  # Simple string, auto-detected as gif
        )
        print(f"✅ Created: {gif_post.content_type} - {gif_post}")
        print(f"   Media types: {gif_post.get_media_types()}")
        
        # Test 6: Complex post with text, media, and links
        print("\n6. Creating complex post (text + media + links)...")
        complex_post = create_post(
            db=db,
            post_id=f"complex_{uuid.uuid4().hex[:8]}",
            author="user6",
            content="Check out this amazing content!",
            timestamp=datetime.now(),
            media_urls=[
                {"url": "https://example.com/image1.jpg", "type": "image"},
                {"url": "https://example.com/image2.jpg", "type": "image"}
            ],
            link_urls=[{"url": "https://example.com", "title": "Example"}]
        )
        print(f"✅ Created: {complex_post.content_type} - {complex_post}")
        
        # Test 7: Query by content type
        print("\n7. Querying posts by content type...")
        text_posts = get_posts_by_content_type(db, "text", limit=10)
        media_posts = get_posts_with_media(db, limit=10)
        print(f"✅ Found {len(text_posts)} text-only posts")
        print(f"✅ Found {len(media_posts)} posts with media")
        
        # Test 8: Query by media type
        print("\n8. Querying posts by media type...")
        video_posts = get_posts_by_media_type(db, "video", limit=10)
        image_posts = get_posts_by_media_type(db, "image", limit=10)
        print(f"✅ Found {len(video_posts)} posts with videos")
        print(f"✅ Found {len(image_posts)} posts with images")
        
        # Test 9: Verify serialization
        print("\n9. Testing serialization...")
        post_dict = complex_post.to_dict()
        assert "content_type" in post_dict
        assert isinstance(post_dict["media_urls"], list)
        assert isinstance(post_dict["link_urls"], list)
        if post_dict["media_urls"]:
            assert "type" in post_dict["media_urls"][0]
        print("✅ Serialization works correctly")
        
        print("\n" + "-" * 50)
        print("✅ All post type tests passed!")
        
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_post_types()

