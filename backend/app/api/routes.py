"""FastAPI routes for search API"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel, Field

from app.models.database import get_db, Post
from app.services.search_service import SearchService
from app.services.grok_client import GrokClient
from app.utils.db_utils import get_post_by_id, get_post_count

router = APIRouter()

# Request/Response models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query (supports AND, OR, NOT operators)")
    limit: int = Field(20, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Pagination offset")
    author: Optional[str] = Field(None, description="Filter by author username")
    content_type: Optional[str] = Field(None, description="Filter by content type")
    sort_by: str = Field("relevance", description="Sort by: relevance, date, likes, retweets")
    use_grok_enhancement: bool = Field(True, description="Use Grok to enhance query")
    include_summary: bool = Field(True, description="Include Grok-generated summary")

class SearchResponse(BaseModel):
    results: List[dict]
    total: int
    limit: int
    offset: int
    query: str
    enhanced_query: Optional[dict] = None
    summary: Optional[str] = None

class PostResponse(BaseModel):
    id: str
    author: str
    author_display_name: Optional[str]
    content: str
    timestamp: str
    likes: int
    retweets: int
    replies: int
    quotes: int
    bookmarks: int
    views: int
    post_url: Optional[str]
    post_type: str
    content_type: str
    hashtags: List[str]
    mentions: List[str]
    media_urls: List[dict]
    link_urls: List[dict]
    grok_description: Optional[str]


@router.post("/api/search", response_model=SearchResponse)
async def search_posts(
    request: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search posts with Grok-enhanced query understanding
    
    Supports:
    - Natural language queries
    - Boolean operators (AND, OR, NOT)
    - Author filtering
    - Content type filtering
    - Multiple sort options
    - Grok query enhancement
    - Result summarization
    """
    try:
        search_service = SearchService(db)
        grok_client = GrokClient()
        
        # Enhance query with Grok if enabled
        enhanced_query_data = None
        search_query = request.query
        
        if request.use_grok_enhancement:
            try:
                enhanced_query_data = await grok_client.enhance_query(request.query)
                # Use expanded terms from Grok if available
                if enhanced_query_data.get("expanded_terms"):
                    # Combine original query with expanded terms
                    expanded = " ".join(enhanced_query_data["expanded_terms"])
                    search_query = f"{request.query} {expanded}"
            except Exception as e:
                print(f"⚠️  Grok query enhancement failed: {e}")
                # Fall back to original query
        
        # Perform search
        results = search_service.search(
            query=search_query,
            limit=request.limit,
            offset=request.offset,
            author=request.author,
            content_type=request.content_type,
            sort_by=request.sort_by
        )
        
        # Generate summary with Grok if enabled
        summary = None
        if request.include_summary and results["results"]:
            try:
                # Prepare posts for summarization
                posts_for_summary = [
                    {
                        "author": post["author"],
                        "content": post["content"][:200]  # Truncate for efficiency
                    }
                    for post in results["results"][:10]
                ]
                summary = await grok_client.summarize_results(request.query, posts_for_summary)
            except Exception as e:
                print(f"⚠️  Grok summarization failed: {e}")
        
        try:
            await grok_client.close()
        except:
            pass
        
        return SearchResponse(
            results=results["results"],
            total=results["total"],
            limit=results["limit"],
            offset=results["offset"],
            query=request.query,
            enhanced_query=enhanced_query_data,
            summary=summary
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")

@router.get("/api/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: Session = Depends(get_db)
):
    """Get a specific post by ID"""
    post = get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return post.to_dict()

@router.get("/api/posts")
async def list_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    author: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """List posts with optional filtering"""
    from app.utils.db_utils import get_all_posts, get_posts_by_author
    
    if author:
        posts = get_posts_by_author(db, author, limit=limit)
    else:
        posts = get_all_posts(db, limit=limit, offset=offset)
    
    return {
        "results": [post.to_dict() for post in posts],
        "total": get_post_count(db),
        "limit": limit,
        "offset": offset
    }


