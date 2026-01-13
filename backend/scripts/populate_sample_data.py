"""Populate database with realistic sample tweets"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db, SessionLocal
from app.utils.db_utils import create_post, post_exists
from app.services.grok_client import GrokClient
from datetime import datetime, timedelta
import random

# Popular accounts to simulate
POPULAR_ACCOUNTS = [
    {"username": "elonmusk", "display_name": "Elon Musk"},
    {"username": "OpenAI", "display_name": "OpenAI"},
    {"username": "xai", "display_name": "xAI"},
    {"username": "sama", "display_name": "Sam Altman"},
    {"username": "BillGates", "display_name": "Bill Gates"},
    {"username": "tim_cook", "display_name": "Tim Cook"},
    {"username": "satyanadella", "display_name": "Satya Nadella"},
    {"username": "verge", "display_name": "The Verge"},
    {"username": "techcrunch", "display_name": "TechCrunch"},
    {"username": "wired", "display_name": "WIRED"},
]

# Sample tweet templates with realistic content
SAMPLE_TWEETS = [
    # AI-related tweets
    {
        "content": "AI will fundamentally change how we work, learn, and create. The future is exciting!",
        "hashtags": ["AI", "Future", "Technology"],
        "mentions": [],
        "likes_range": (5000, 50000),
        "retweets_range": (1000, 10000),
    },
    {
        "content": "Just launched our new AI model. It's 10x faster and more accurate than previous versions. Check it out!",
        "hashtags": ["AI", "MachineLearning", "Tech"],
        "mentions": [],
        "likes_range": (3000, 30000),
        "retweets_range": (500, 5000),
    },
    {
        "content": "The intersection of AI and space exploration will unlock possibilities we can't even imagine yet.",
        "hashtags": ["AI", "Space", "Innovation"],
        "mentions": ["SpaceX"],
        "likes_range": (8000, 80000),
        "retweets_range": (2000, 20000),
    },
    {
        "content": "Building safe AI systems is our top priority. We're committed to responsible AI development.",
        "hashtags": ["AI", "Safety", "Ethics"],
        "mentions": [],
        "likes_range": (2000, 20000),
        "retweets_range": (400, 4000),
    },
    {
        "content": "Grok is now available for everyone! Try it out and let us know what you think.",
        "hashtags": ["Grok", "AI", "xAI"],
        "mentions": ["xai"],
        "likes_range": (10000, 100000),
        "retweets_range": (3000, 30000),
    },
    # Technology tweets
    {
        "content": "Quantum computing breakthrough: We've achieved a new milestone in quantum error correction.",
        "hashtags": ["Quantum", "Computing", "Science"],
        "mentions": [],
        "likes_range": (1500, 15000),
        "retweets_range": (300, 3000),
    },
    {
        "content": "The future of computing is here. Our new chip architecture delivers unprecedented performance.",
        "hashtags": ["Technology", "Innovation", "Hardware"],
        "mentions": [],
        "likes_range": (4000, 40000),
        "retweets_range": (800, 8000),
    },
    {
        "content": "Excited to announce our latest product launch! This will revolutionize how people interact with technology.",
        "hashtags": ["ProductLaunch", "Innovation", "Tech"],
        "mentions": [],
        "likes_range": (6000, 60000),
        "retweets_range": (1200, 12000),
    },
    # Space/Science tweets
    {
        "content": "Mars mission update: We're on track for our next launch window. Humanity's future is multi-planetary.",
        "hashtags": ["SpaceX", "Mars", "Space"],
        "mentions": ["SpaceX"],
        "likes_range": (20000, 200000),
        "retweets_range": (5000, 50000),
    },
    {
        "content": "The James Webb Space Telescope continues to amaze us with new discoveries about our universe.",
        "hashtags": ["Space", "Science", "JWST"],
        "mentions": [],
        "likes_range": (5000, 50000),
        "retweets_range": (1000, 10000),
    },
    # General tech news
    {
        "content": "Breaking: Major tech company announces new AI partnership. This could change everything.",
        "hashtags": ["TechNews", "AI", "Partnership"],
        "mentions": [],
        "likes_range": (1000, 10000),
        "retweets_range": (200, 2000),
    },
    {
        "content": "The pace of innovation in AI is accelerating. We're seeing breakthroughs almost weekly now.",
        "hashtags": ["AI", "Innovation", "Technology"],
        "mentions": [],
        "likes_range": (3000, 30000),
        "retweets_range": (600, 6000),
    },
    {
        "content": "Privacy and security in the age of AI: How we're building systems that protect user data.",
        "hashtags": ["Privacy", "Security", "AI"],
        "mentions": [],
        "likes_range": (2500, 25000),
        "retweets_range": (500, 5000),
    },
    # Media tweets (with links)
    {
        "content": "Check out this amazing article about the future of AI: https://example.com/ai-future",
        "hashtags": ["AI", "Article", "Read"],
        "mentions": [],
        "link_urls": [{"url": "https://example.com/ai-future", "title": "The Future of AI", "description": "An in-depth look at AI developments"}],
        "likes_range": (800, 8000),
        "retweets_range": (150, 1500),
    },
    {
        "content": "New video: Watch how we're training our AI models. Fascinating process! https://example.com/video",
        "hashtags": ["AI", "Video", "MachineLearning"],
        "mentions": [],
        "link_urls": [{"url": "https://example.com/video", "title": "AI Training Process"}],
        "likes_range": (2000, 20000),
        "retweets_range": (400, 4000),
    },
    # Media tweets (with images)
    {
        "content": "Here's a visualization of our latest AI model architecture. Pretty cool, right?",
        "hashtags": ["AI", "Architecture", "Visualization"],
        "mentions": [],
        "media_urls": [{"url": "https://example.com/image1.jpg", "type": "image", "thumbnail": "https://example.com/thumb1.jpg"}],
        "likes_range": (4000, 40000),
        "retweets_range": (800, 8000),
    },
    {
        "content": "Sneak peek at our upcoming product! Can't wait to share more details soon.",
        "hashtags": ["Product", "SneakPeek", "Tech"],
        "mentions": [],
        "media_urls": [
            {"url": "https://example.com/product1.jpg", "type": "image"},
            {"url": "https://example.com/product2.jpg", "type": "image"}
        ],
        "likes_range": (6000, 60000),
        "retweets_range": (1200, 12000),
    },
    # Complex tweets (text + media + links)
    {
        "content": "Exciting announcement! We're launching something big. Check out the details: https://example.com/launch",
        "hashtags": ["Launch", "Announcement", "Tech"],
        "mentions": [],
        "media_urls": [{"url": "https://example.com/launch.jpg", "type": "image"}],
        "link_urls": [{"url": "https://example.com/launch", "title": "Product Launch Details"}],
        "likes_range": (10000, 100000),
        "retweets_range": (2000, 20000),
    },
]

async def generate_sample_tweets(count: int = 50):
    """Generate and store sample tweets in the database with Grok descriptions"""
    print(f"Generating {count} sample tweets with Grok descriptions...")
    print("=" * 60)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    # Initialize Grok client
    grok_client = GrokClient()
    
    created_count = 0
    skipped_count = 0
    description_failures = 0
    
    try:
        # Generate tweets over the past 30 days
        base_time = datetime.now()
        
        for i in range(count):
            # Pick random account
            account = random.choice(POPULAR_ACCOUNTS)
            
            # Pick random tweet template
            template = random.choice(SAMPLE_TWEETS)
            
            # Generate unique post ID (simulate Twitter ID format)
            post_id = str(random.randint(1000000000000000000, 9999999999999999999))
            
            # Check if already exists
            if post_exists(db, post_id):
                skipped_count += 1
                continue
            
            # Generate random timestamp (within last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = base_time - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
            
            # Generate engagement metrics
            likes = random.randint(*template.get("likes_range", (100, 1000)))
            retweets = random.randint(*template.get("retweets_range", (20, 200)))
            replies = random.randint(int(likes * 0.1), int(likes * 0.3))
            quotes = random.randint(int(retweets * 0.1), int(retweets * 0.5))
            bookmarks = random.randint(int(likes * 0.05), int(likes * 0.15))
            views = random.randint(likes * 10, likes * 100)
            
            # Generate Grok description
            grok_description = None
            is_processed = False
            try:
                grok_description = await grok_client.describe_post(
                    template["content"],
                    account["username"]
                )
                is_processed = True
            except Exception as e:
                print(f"⚠️  Failed to generate Grok description for post {i+1}: {e}")
                description_failures += 1
                # Continue without description - post will still be created
            
            # Create post
            create_post(
                db=db,
                post_id=post_id,
                author=account["username"],
                author_display_name=account["display_name"],
                content=template["content"],
                timestamp=timestamp,
                likes=likes,
                retweets=retweets,
                replies=replies,
                quotes=quotes,
                bookmarks=bookmarks,
                views=views,
                post_url=f"https://x.com/{account['username']}/status/{post_id}",
                post_type="tweet",
                hashtags=template.get("hashtags", []),
                mentions=template.get("mentions", []),
                media_urls=template.get("media_urls"),
                link_urls=template.get("link_urls"),
                grok_description=grok_description,
                is_processed=is_processed
            )
            
            created_count += 1
            
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1}/{count} tweets...")
        
        db.commit()
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully created {created_count} sample tweets")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} duplicate tweets")
        if description_failures > 0:
            print(f"⚠️  Failed to generate {description_failures} Grok descriptions")
        else:
            print(f"✅ All tweets have Grok descriptions")
        print(f"📊 Database now contains posts from {len(POPULAR_ACCOUNTS)} accounts")
        
    except Exception as e:
        print(f"\n❌ Error generating sample tweets: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        await grok_client.close()
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate database with sample tweets")
    parser.add_argument("--count", type=int, default=50, help="Number of tweets to generate (default: 50)")
    args = parser.parse_args()
    
    asyncio.run(generate_sample_tweets(args.count))

