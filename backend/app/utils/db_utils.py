"""Database utility functions"""
import json
from sqlalchemy.orm import Session
from app.models.database import Post, SessionLocal
from typing import List, Optional, Dict, Any
from datetime import datetime

def normalize_media(media: Any) -> List[Dict[str, Any]]:
    """Normalize media input to structured format"""
    if not media:
        return []
    
    # If it's already a list of dicts, validate and return
    if isinstance(media, list):
        normalized = []
        for item in media:
            if isinstance(item, dict):
                # Ensure required fields
                normalized.append({
                    "url": item.get("url", ""),
                    "type": item.get("type", "image"),  # image, video, gif
                    "thumbnail": item.get("thumbnail"),
                    "duration": item.get("duration"),  # For videos
                    "width": item.get("width"),
                    "height": item.get("height")
                })
            elif isinstance(item, str):
                # Simple string URL, infer type from extension
                media_type = "image"
                if any(ext in item.lower() for ext in [".mp4", ".mov", ".webm"]):
                    media_type = "video"
                elif ".gif" in item.lower():
                    media_type = "gif"
                normalized.append({"url": item, "type": media_type})
        return normalized
    
    # Single string URL
    if isinstance(media, str):
        media_type = "image"
        if any(ext in media.lower() for ext in [".mp4", ".mov", ".webm"]):
            media_type = "video"
        elif ".gif" in media.lower():
            media_type = "gif"
        return [{"url": media, "type": media_type}]
    
    return []

def normalize_links(links: Any) -> List[Dict[str, Any]]:
    """Normalize link input to structured format"""
    if not links:
        return []
    
    # If it's already a list of dicts, validate and return
    if isinstance(links, list):
        normalized = []
        for item in links:
            if isinstance(item, dict):
                normalized.append({
                    "url": item.get("url", ""),
                    "title": item.get("title"),
                    "description": item.get("description"),
                    "image": item.get("image")
                })
            elif isinstance(item, str):
                normalized.append({"url": item})
        return normalized
    
    # Single string URL
    if isinstance(links, str):
        return [{"url": links}]
    
    return []

def detect_content_type(content: str, media: List[Dict], links: List[Dict]) -> str:
    """Detect content type based on content, media, and links"""
    has_media = bool(media)
    has_links = bool(links)
    has_text = bool(content and content.strip())
    
    if has_media and has_links and has_text:
        return "text_media_link"
    elif has_media and has_text:
        return "text_media"
    elif has_media and not has_text:
        return "media_only"
    elif has_links and has_text:
        return "text_link"
    elif has_links and not has_text:
        return "link_only"
    else:
        return "text"

def create_post(
    db: Session,
    post_id: str,
    author: str,
    content: str,
    timestamp: datetime,
    # Engagement metrics
    likes: int = 0,
    retweets: int = 0,
    replies: int = 0,
    quotes: int = 0,
    bookmarks: int = 0,
    views: int = 0,
    # Post metadata
    author_display_name: Optional[str] = None,
    post_url: Optional[str] = None,
    post_type: str = "tweet",
    content_type: Optional[str] = None,  # Auto-detected if not provided
    in_reply_to_id: Optional[str] = None,
    retweeted_from_id: Optional[str] = None,
    # Content metadata (can be simple strings or structured objects)
    hashtags: Optional[List[str]] = None,
    mentions: Optional[List[str]] = None,
    media_urls: Optional[Any] = None,  # Can be List[str], List[Dict], or single string
    link_urls: Optional[Any] = None,  # Can be List[str], List[Dict], or single string
    # AI metadata
    grok_description: Optional[str] = None,
    is_processed: bool = False
) -> Post:
    """Create a new post in the database with comprehensive metadata"""
    # Normalize media and links
    normalized_media = normalize_media(media_urls)
    normalized_links = normalize_links(link_urls)
    
    # Auto-detect content type if not provided
    if not content_type:
        content_type = detect_content_type(content, normalized_media, normalized_links)
    
    post = Post(
        id=post_id,
        author=author,
        author_display_name=author_display_name,
        content=content,
        timestamp=timestamp,
        # Engagement metrics
        likes=likes,
        retweets=retweets,
        replies=replies,
        quotes=quotes,
        bookmarks=bookmarks,
        views=views,
        # Post metadata
        post_url=post_url,
        post_type=post_type,
        content_type=content_type,
        in_reply_to_id=in_reply_to_id,
        retweeted_from_id=retweeted_from_id,
        # Content metadata (stored as JSON strings)
        hashtags=json.dumps(hashtags) if hashtags else None,
        mentions=json.dumps(mentions) if mentions else None,
        media_urls=json.dumps(normalized_media) if normalized_media else None,
        link_urls=json.dumps(normalized_links) if normalized_links else None,
        # AI metadata
        grok_description=grok_description,
        is_processed=is_processed
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post

def create_post_from_dict(db: Session, post_data: Dict[str, Any]) -> Post:
    """Create a post from a dictionary"""
    return create_post(
        db=db,
        post_id=post_data.get("id"),
        author=post_data.get("author"),
        content=post_data.get("content"),
        timestamp=post_data.get("timestamp"),
        likes=post_data.get("likes", 0),
        retweets=post_data.get("retweets", 0),
        replies=post_data.get("replies", 0),
        quotes=post_data.get("quotes", 0),
        bookmarks=post_data.get("bookmarks", 0),
        views=post_data.get("views", 0),
        author_display_name=post_data.get("author_display_name"),
        post_url=post_data.get("post_url"),
        post_type=post_data.get("post_type", "tweet"),
        in_reply_to_id=post_data.get("in_reply_to_id"),
        retweeted_from_id=post_data.get("retweeted_from_id"),
        hashtags=post_data.get("hashtags"),
        mentions=post_data.get("mentions"),
        media_urls=post_data.get("media_urls"),
        link_urls=post_data.get("link_urls"),
        grok_description=post_data.get("grok_description"),
        is_processed=post_data.get("is_processed", False)
    )

def get_post_by_id(db: Session, post_id: str) -> Optional[Post]:
    """Get a post by its ID"""
    return db.query(Post).filter(Post.id == post_id).first()

def get_posts_by_author(db: Session, author: str, limit: int = 100) -> List[Post]:
    """Get posts by a specific author"""
    return db.query(Post).filter(Post.author == author).order_by(Post.timestamp.desc()).limit(limit).all()

def get_all_posts(db: Session, limit: int = 100, offset: int = 0) -> List[Post]:
    """Get all posts with pagination"""
    return db.query(Post).order_by(Post.timestamp.desc()).offset(offset).limit(limit).all()

def update_post_description(db: Session, post_id: str, grok_description: str) -> Optional[Post]:
    """Update the Grok description for a post and mark as processed"""
    post = get_post_by_id(db, post_id)
    if post:
        post.grok_description = grok_description
        post.is_processed = True
        post.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(post)
    return post

def get_unprocessed_posts(db: Session, limit: int = 100) -> List[Post]:
    """Get posts that haven't been processed by Grok yet"""
    return db.query(Post).filter(Post.is_processed == False).order_by(Post.timestamp.desc()).limit(limit).all()

def get_top_posts_by_engagement(db: Session, limit: int = 100, metric: str = "likes") -> List[Post]:
    """Get top posts by engagement metric (likes, retweets, etc.)"""
    if metric == "likes":
        return db.query(Post).order_by(Post.likes.desc()).limit(limit).all()
    elif metric == "retweets":
        return db.query(Post).order_by(Post.retweets.desc()).limit(limit).all()
    elif metric == "replies":
        return db.query(Post).order_by(Post.replies.desc()).limit(limit).all()
    else:
        return db.query(Post).order_by(Post.likes.desc()).limit(limit).all()

def get_posts_by_content_type(db: Session, content_type: str, limit: int = 100) -> List[Post]:
    """Get posts filtered by content type"""
    return db.query(Post).filter(Post.content_type == content_type).order_by(Post.timestamp.desc()).limit(limit).all()

def get_posts_with_media(db: Session, limit: int = 100) -> List[Post]:
    """Get posts that contain media"""
    return db.query(Post).filter(
        Post.content_type.in_(["text_media", "media_only", "text_media_link"])
    ).order_by(Post.timestamp.desc()).limit(limit).all()

def get_posts_by_media_type(db: Session, media_type: str, limit: int = 100) -> List[Post]:
    """Get posts containing specific media type (image, video, gif)"""
    all_posts = db.query(Post).filter(
        Post.content_type.in_(["text_media", "media_only", "text_media_link"])
    ).all()
    
    # Filter by media type in Python (since we need to parse JSON)
    filtered = []
    for post in all_posts:
        if post.has_media_type(media_type):
            filtered.append(post)
            if len(filtered) >= limit:
                break
    
    return filtered

def post_exists(db: Session, post_id: str) -> bool:
    """Check if a post already exists in the database"""
    return db.query(Post).filter(Post.id == post_id).first() is not None

def get_post_count(db: Session) -> int:
    """Get total number of posts in database"""
    return db.query(Post).count()

