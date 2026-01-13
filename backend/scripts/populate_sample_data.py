"""Populate database with AI-generated tweets using Grok"""
import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.database import init_db, SessionLocal, Post
from app.utils.db_utils import create_post
from app.services.grok_client import GrokClient
from datetime import datetime, timedelta
import random
import re

# Accounts to generate tweets for
POPULAR_ACCOUNTS = [
    {"username": "elonmusk", "display_name": "Elon Musk"},
    {"username": "sama", "display_name": "Sam Altman"},
    {"username": "realDonaldTrump", "display_name": "Donald J. Trump"},
]

# Topics and themes for tweet generation
TWEET_TOPICS = [
    "AI and machine learning developments",
    "Space exploration and Mars missions",
    "Technology innovation and startups",
    "Electric vehicles and sustainable energy",
    "Artificial intelligence safety and ethics",
    "Quantum computing breakthroughs",
    "Product launches and announcements",
    "Science and research discoveries",
    "Business and entrepreneurship",
    "Future of technology",
    "Cryptocurrency and blockchain",
    "Climate change and environment",
    "Politics and current events",
    "Social media and digital culture",
    "Healthcare and biotechnology",
]

async def generate_tweet_with_grok(
    grok_client: GrokClient,
    account: dict,
    topic: str,
    attempt_number: int = 1
) -> dict:
    """Use Grok to generate a realistic tweet for a specific account and topic"""
    # Add variation to prompt to ensure uniqueness
    variation_prompt = ""
    if attempt_number > 1:
        variation_prompt = f" This is attempt {attempt_number}. Generate a DIFFERENT and UNIQUE tweet. Do not repeat previous content."
    
    prompt = f"""Generate a realistic tweet that @{account['username']} ({account['display_name']}) would post about: {topic}

Requirements:
- Write in their authentic voice and style
- Keep it under 280 characters
- Include 1-3 relevant hashtags
- Make it engaging and realistic
- Return ONLY the tweet text, nothing else
- Be creative and unique{variation_prompt}"""

    messages = [
        {
            "role": "system",
            "content": "You are a social media content generator. Generate realistic, authentic tweets in the style of the specified user. Each tweet must be completely unique and different from any previous tweets. Return only the tweet text."
        },
        {"role": "user", "content": prompt}
    ]
    
    try:
        tweet_content = await grok_client.chat_completion(messages)
        if not tweet_content:
            return None
        
        # Clean up the response (remove quotes, extra whitespace)
        tweet_content = tweet_content.strip().strip('"').strip("'")
        
        # Extract hashtags and mentions
        hashtags = [tag.lower() for tag in re.findall(r'#(\w+)', tweet_content)]
        mentions = [mention.lower() for mention in re.findall(r'@(\w+)', tweet_content)]
        links = [{"url": url, "title": "", "description": ""} for url in re.findall(r'https?://[^\s]+', tweet_content)]
        
        return {
            "content": tweet_content,
            "hashtags": hashtags,
            "mentions": mentions,
            "link_urls": links,
        }
    except Exception as e:
        print(f"   ⚠️  Failed to generate tweet: {e}")
        return None

def content_exists_in_db(db, content: str) -> bool:
    """Check if a tweet with this exact content already exists"""
    # Use exact match (case-insensitive) instead of partial match
    normalized_content = content.strip()
    existing = db.query(Post).filter(
        Post.content.ilike(normalized_content)
    ).first()
    return existing is not None

async def generate_sample_tweets(count: int = 50):
    """Generate and store AI-generated tweets using Grok, ensuring no duplicates"""
    print(f"Generating {count} unique AI-generated tweets using Grok...")
    print("=" * 60)
    
    # Initialize database
    init_db()
    db = SessionLocal()
    
    # Initialize Grok client
    grok_client = GrokClient()
    
    created_count = 0
    skipped_count = 0
    generation_failures = 0
    description_failures = 0
    duplicate_count = 0
    
    # Track generated content in this session to avoid duplicates
    generated_content_set = set()
    
    try:
        # Generate tweets over the past 30 days
        base_time = datetime.now()
        
        attempts = 0
        max_attempts = count * 3  # Allow up to 3x attempts to get unique tweets
        
        while created_count < count and attempts < max_attempts:
            attempts += 1
            
            # Show progress every 5 attempts
            if attempts % 5 == 0:
                print(f"  Progress: {created_count}/{count} created, {attempts} attempts...")
            
            # Pick random account
            account = random.choice(POPULAR_ACCOUNTS)
            
            # Pick random topic
            topic = random.choice(TWEET_TOPICS)
            
            # Generate tweet content using Grok
            attempt_num = 1
            tweet_data = None
            
            # Try up to 3 times to get a unique tweet
            for retry in range(3):
                try:
                    if retry == 0:
                        print(f"  Attempt {attempts}: Generating tweet for @{account['username']} about '{topic}'...")
                    
                    tweet_data = await generate_tweet_with_grok(
                        grok_client, account, topic, attempt_num
                    )
                    attempt_num += 1
                    
                    if not tweet_data:
                        if retry == 2:  # Last attempt
                            generation_failures += 1
                            print(f"   ❌ Failed to generate tweet after 3 attempts (Grok returned None)")
                        else:
                            print(f"   ⚠️  Grok returned None, retrying...")
                        break
                    
                    print(f"   ✓ Generated: {tweet_data['content'][:60]}...")
                    
                    # Check if content is unique
                    content_normalized = tweet_data["content"].strip().lower()
                    
                    # Check in-memory set first (faster)
                    if content_normalized in generated_content_set:
                        print(f"   ⚠️  Duplicate in memory set (attempt {retry + 1}), retrying...")
                        if retry < 2:  # Try again
                            continue
                        else:
                            print(f"   ⚠️  All 3 attempts resulted in duplicates, skipping")
                            skipped_count += 1
                            break
                    
                    # Check database
                    if content_exists_in_db(db, tweet_data["content"]):
                        duplicate_count += 1
                        print(f"   ⚠️  Duplicate in database (attempt {retry + 1}), retrying...")
                        if retry < 2:  # Try again
                            continue
                        else:
                            print(f"   ⚠️  All 3 attempts found database duplicates, skipping")
                            skipped_count += 1
                            break
                    
                    # Content is unique! Add to set and break out of retry loop
                    generated_content_set.add(content_normalized)
                    print(f"   ✓ Content is unique (normalized: {content_normalized[:50]}...)")
                    break
                except Exception as e:
                    print(f"   ❌ Error generating tweet (attempt {retry + 1}): {e}")
                    import traceback
                    traceback.print_exc()
                    if retry == 2:
                        generation_failures += 1
                    break
            
            if not tweet_data:
                print(f"   ⚠️  No tweet data generated, moving to next attempt")
                continue
            
            # Final check before creating - if we got here, content should be unique
            # (it was added to generated_content_set in the retry loop if unique)
            content_normalized = tweet_data["content"].strip().lower()
            
            # If it's NOT in the set, something went wrong - add it and continue
            if content_normalized not in generated_content_set:
                print(f"   ⚠️  WARNING: Content not in memory set after retry loop - adding it now")
                generated_content_set.add(content_normalized)
            
            # Double-check database one more time (shouldn't be needed, but safety check)
            if content_exists_in_db(db, tweet_data["content"]):
                print(f"   ⚠️  WARNING: Content found in database after validation - skipping")
                skipped_count += 1
                duplicate_count += 1
                continue
            
            print(f"   ✓ Content verified unique, proceeding to create post...")
            
            # Generate unique post ID (simulate Twitter ID format)
            post_id = str(random.randint(1000000000000000000, 9999999999999999999))
            
            # Ensure unique ID (very unlikely collision, but check anyway)
            from app.utils.db_utils import post_exists
            retry_id = 0
            while post_exists(db, post_id) and retry_id < 10:
                post_id = str(random.randint(1000000000000000000, 9999999999999999999))
                retry_id += 1
            
            if post_exists(db, post_id):
                skipped_count += 1
                continue
            
            # Generate random timestamp (within last 30 days)
            days_ago = random.randint(0, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            timestamp = base_time - timedelta(
                days=days_ago, hours=hours_ago, minutes=minutes_ago
            )
            
            # Generate realistic engagement metrics based on account
            if account["username"] == "elonmusk":
                likes = random.randint(10000, 200000)
                retweets = random.randint(2000, 50000)
            elif account["username"] == "realDonaldTrump":
                likes = random.randint(15000, 300000)
                retweets = random.randint(3000, 60000)
            else:  # sama and others
                likes = random.randint(5000, 100000)
                retweets = random.randint(1000, 20000)
            
            replies = random.randint(int(likes * 0.1), int(likes * 0.3))
            quotes = random.randint(int(retweets * 0.1), int(retweets * 0.5))
            bookmarks = random.randint(int(likes * 0.05), int(likes * 0.15))
            views = random.randint(likes * 10, likes * 100)
            
            # Generate Grok description for searchability
            grok_description = None
            is_processed = False
            try:
                grok_description = await grok_client.describe_post(
                    tweet_data["content"], account["username"]
                )
                is_processed = True
            except Exception as e:
                description_failures += 1
                # Continue without description - post will still be created
            
            # Create post
            print(f"   → Creating post in database (ID: {post_id})...")
            try:
                post = create_post(
                    db=db,
                    post_id=post_id,
                    author=account["username"],
                    author_display_name=account["display_name"],
                    content=tweet_data["content"],
                    timestamp=timestamp,
                    likes=likes,
                    retweets=retweets,
                    replies=replies,
                    quotes=quotes,
                    bookmarks=bookmarks,
                    views=views,
                    post_url=f"https://x.com/{account['username']}/status/{post_id}",
                    post_type="tweet",
                    hashtags=tweet_data.get("hashtags", []),
                    mentions=tweet_data.get("mentions", []),
                    link_urls=tweet_data.get("link_urls", []),
                    media_urls=[],
                    grok_description=grok_description,
                    is_processed=is_processed,
                )
                
                created_count += 1
                print(f"  ✅ Successfully created tweet {created_count}/{count} by @{account['username']} (ID: {post.id})")
            except Exception as e:
                print(f"   ❌ Error creating post: {e}")
                import traceback
                traceback.print_exc()
                skipped_count += 1
                # Rollback the failed transaction
                db.rollback()
        
        # Final commit (create_post already commits, but this ensures everything is saved)
        try:
            db.commit()
            print(f"\n  → Final database commit completed")
        except Exception as e:
            print(f"  ⚠️  Final commit warning: {e}")
        
        print("\n" + "=" * 60)
        print(f"✅ Successfully created {created_count} unique AI-generated tweets")
        if skipped_count > 0:
            print(f"⚠️  Skipped {skipped_count} duplicate/failed tweets")
        if duplicate_count > 0:
            print(f"⚠️  Found {duplicate_count} duplicate content attempts")
        if generation_failures > 0:
            print(f"⚠️  Failed to generate {generation_failures} tweets")
        if description_failures > 0:
            print(f"⚠️  Failed to generate {description_failures} Grok descriptions")
        else:
            print(f"✅ All tweets have Grok descriptions")
        print(f"📊 Database now contains posts from {len(POPULAR_ACCOUNTS)} accounts")
        print(f"📝 Total attempts: {attempts}")
        
    except Exception as e:
        print(f"\n❌ Error generating tweets: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        await grok_client.close()
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate database with AI-generated tweets")
    parser.add_argument(
        "--count", type=int, default=50, help="Number of tweets to generate (default: 50)"
    )
    args = parser.parse_args()
    
    asyncio.run(generate_sample_tweets(args.count))
