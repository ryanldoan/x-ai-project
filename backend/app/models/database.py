from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config import settings

Base = declarative_base()

class Post(Base):
    __tablename__ = "posts"
    
    # Core identifiers
    id = Column(String, primary_key=True)  # Tweet ID
    author = Column(String, index=True, nullable=False)
    author_display_name = Column(String)  # Display name (if different from username)
    
    # Content
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    
    # Engagement metrics
    likes = Column(Integer, default=0, index=True)
    retweets = Column(Integer, default=0, index=True)
    replies = Column(Integer, default=0)
    quotes = Column(Integer, default=0)  # Quote tweets
    bookmarks = Column(Integer, default=0)  # Bookmark count
    views = Column(Integer, default=0)  # View count (if available)
    
    # Post metadata
    post_url = Column(String)  # URL to the post on X.com
    post_type = Column(String, default="tweet", index=True)  # tweet, reply, retweet, quote
    content_type = Column(String, default="text")  # text, text_link, text_media, media_only, link_only
    in_reply_to_id = Column(String)  # If this is a reply, the parent tweet ID
    retweeted_from_id = Column(String)  # If this is a retweet, original tweet ID
    
    # Content metadata
    hashtags = Column(Text)  # JSON array of hashtags
    mentions = Column(Text)  # JSON array of mentioned users
    media_urls = Column(Text)  # JSON array of media objects: [{"url": "...", "type": "image|video|gif", "thumbnail": "..."}]
    link_urls = Column(Text)  # JSON array of external links: [{"url": "...", "title": "...", "description": "..."}]
    
    # AI-generated metadata
    grok_description = Column(Text)  # AI-generated description for searchability
    
    # System metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_processed = Column(Boolean, default=False)  # Whether Grok description has been generated
    
    # Full-text search index on content and grok_description
    __table_args__ = (
        Index('idx_content_fts', 'content'),
        Index('idx_timestamp', 'timestamp'),
        Index('idx_author_timestamp', 'author', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Post {self.id} by @{self.author} ({self.content_type})>"
    
    def get_content_type(self) -> str:
        """Determine content type based on content, media, and links"""
        import json
        
        has_media = bool(self.media_urls and json.loads(self.media_urls))
        has_links = bool(self.link_urls and json.loads(self.link_urls))
        has_text = bool(self.content and self.content.strip())
        
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
    
    def get_media_types(self) -> list:
        """Get list of media types in this post"""
        import json
        
        if not self.media_urls:
            return []
        
        try:
            media_list = json.loads(self.media_urls)
            if isinstance(media_list, list):
                return [media.get("type", "unknown") for media in media_list if isinstance(media, dict)]
        except:
            pass
        return []
    
    def has_media_type(self, media_type: str) -> bool:
        """Check if post contains specific media type (image, video, gif)"""
        return media_type in self.get_media_types()
    
    def to_dict(self):
        """Convert post to dictionary for API responses"""
        import json
        
        return {
            "id": self.id,
            "author": self.author,
            "author_display_name": self.author_display_name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "post_url": self.post_url,
            "post_type": self.post_type,
            "content_type": self.content_type or self.get_content_type(),
            # Engagement metrics
            "likes": self.likes,
            "retweets": self.retweets,
            "replies": self.replies,
            "quotes": self.quotes,
            "bookmarks": self.bookmarks,
            "views": self.views,
            # Content metadata
            "hashtags": json.loads(self.hashtags) if self.hashtags else [],
            "mentions": json.loads(self.mentions) if self.mentions else [],
            "media_urls": json.loads(self.media_urls) if self.media_urls else [],
            "link_urls": json.loads(self.link_urls) if self.link_urls else [],
            # AI metadata
            "grok_description": self.grok_description,
            # System metadata
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_processed": self.is_processed
        }

# Create engine and session
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL debugging
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Database initialized successfully")

def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

