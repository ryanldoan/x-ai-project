"""Token-based search service with boolean operators and fast indexing"""
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, text
from app.models.database import Post
from app.utils.db_utils import get_all_posts
import json


class SearchService:
    """Token-based search service with boolean operators"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _tokenize_query(self, query: str) -> List[str]:
        """Tokenize search query into individual terms"""
        # Remove special characters but keep spaces
        query = re.sub(r'[^\w\s]', ' ', query)
        # Split on whitespace and filter empty strings
        tokens = [token.lower().strip() for token in query.split() if token.strip()]
        return tokens
    
    def _parse_boolean_query(self, query: str) -> Dict[str, Any]:
        """
        Parse query for boolean operators (AND, OR, NOT)
        Returns: {
            'must_include': [terms that must be present],
            'should_include': [terms that should be present],
            'must_not_include': [terms that must not be present],
            'raw_tokens': [all tokens]
        }
        """
        # Normalize query
        query = query.strip()
        
        # Simple boolean parsing
        must_include = []
        should_include = []
        must_not_include = []
        raw_tokens = []
        
        # Split by boolean operators (case insensitive)
        parts = re.split(r'\s+(AND|OR|NOT)\s+', query, flags=re.IGNORECASE)
        
        current_operator = 'OR'  # Default is OR
        i = 0
        
        while i < len(parts):
            part = parts[i].strip()
            
            if part.upper() in ['AND', 'OR', 'NOT']:
                current_operator = part.upper()
                i += 1
                continue
            
            if not part:
                i += 1
                continue
            
            # Tokenize this part
            tokens = self._tokenize_query(part)
            raw_tokens.extend(tokens)
            
            if current_operator == 'AND':
                must_include.extend(tokens)
            elif current_operator == 'OR':
                should_include.extend(tokens)
            elif current_operator == 'NOT':
                must_not_include.extend(tokens)
            
            i += 1
        
        # If no operators found, treat all as OR (should_include)
        if not must_include and not must_not_include:
            should_include = raw_tokens if raw_tokens else self._tokenize_query(query)
        
        return {
            'must_include': list(set(must_include)),
            'should_include': list(set(should_include)),
            'must_not_include': list(set(must_not_include)),
            'raw_tokens': list(set(raw_tokens)) if raw_tokens else self._tokenize_query(query)
        }
    
    def _build_search_filters(self, parsed_query: Dict[str, Any], 
                              author: Optional[str] = None,
                              content_type: Optional[str] = None) -> List:
        """Build SQLAlchemy filters based on parsed query"""
        filters = []
        
        # Search in content and grok_description
        search_fields = [Post.content, Post.grok_description]
        
        # Must include terms (AND)
        if parsed_query['must_include']:
            must_filters = []
            for term in parsed_query['must_include']:
                term_filter = or_(
                    Post.content.ilike(f'%{term}%'),
                    Post.grok_description.ilike(f'%{term}%')
                )
                must_filters.append(term_filter)
            filters.append(and_(*must_filters))
        
        # Should include terms (OR)
        if parsed_query['should_include']:
            should_filters = []
            for term in parsed_query['should_include']:
                term_filter = or_(
                    Post.content.ilike(f'%{term}%'),
                    Post.grok_description.ilike(f'%{term}%')
                )
                should_filters.append(term_filter)
            if should_filters:
                filters.append(or_(*should_filters))
        
        # Must NOT include terms
        if parsed_query['must_not_include']:
            for term in parsed_query['must_not_include']:
                filters.append(
                    ~and_(
                        Post.content.ilike(f'%{term}%'),
                        Post.grok_description.ilike(f'%{term}%')
                    )
                )
        
        # Additional filters
        if author:
            filters.append(Post.author.ilike(f'%{author}%'))
        
        if content_type:
            filters.append(Post.content_type == content_type)
        
        return filters
    
    def _calculate_relevance_score(self, post: Post, parsed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for a post"""
        score = 0.0
        content_lower = (post.content or '').lower()
        description_lower = (post.grok_description or '').lower()
        combined_text = f"{content_lower} {description_lower}"
        
        # Count matches in content (higher weight)
        for term in parsed_query['raw_tokens']:
            # Exact matches in content
            score += content_lower.count(term) * 2.0
            # Matches in description
            score += description_lower.count(term) * 1.0
        
        # Boost for must_include terms
        for term in parsed_query['must_include']:
            if term in combined_text:
                score += 5.0
        
        # Boost for hashtag matches
        if post.hashtags:
            try:
                hashtags = json.loads(post.hashtags)
                for term in parsed_query['raw_tokens']:
                    if any(term in tag.lower() for tag in hashtags):
                        score += 3.0
            except:
                pass
        
        # Boost for mention matches
        if post.mentions:
            try:
                mentions = json.loads(post.mentions)
                for term in parsed_query['raw_tokens']:
                    if any(term in mention.lower() for mention in mentions):
                        score += 2.0
            except:
                pass
        
        # Engagement boost (popular posts get slight boost)
        engagement_score = (post.likes * 0.0001) + (post.retweets * 0.0002)
        score += min(engagement_score, 5.0)  # Cap engagement boost
        
        return score
    
    def search(self, 
               query: str,
               limit: int = 20,
               offset: int = 0,
               author: Optional[str] = None,
               content_type: Optional[str] = None,
               sort_by: str = "relevance") -> Dict[str, Any]:
        """
        Perform token-based search with boolean operators
        
        Args:
            query: Search query (supports AND, OR, NOT operators)
            limit: Maximum number of results
            offset: Pagination offset
            author: Filter by author (optional)
            content_type: Filter by content type (optional)
            sort_by: Sort by "relevance", "date", "likes", "retweets"
        
        Returns:
            Dictionary with results and metadata
        """
        if not query or not query.strip():
            return {
                "results": [],
                "total": 0,
                "limit": limit,
                "offset": offset,
                "query": query
            }
        
        # Parse query for boolean operators
        parsed_query = self._parse_boolean_query(query)
        
        # Build filters
        filters = self._build_search_filters(parsed_query, author, content_type)
        
        # Base query
        if filters:
            base_query = self.db.query(Post).filter(and_(*filters))
        else:
            base_query = self.db.query(Post)
        
        # Get total count
        total = base_query.count()
        
        # Apply sorting
        if sort_by == "date":
            base_query = base_query.order_by(Post.timestamp.desc())
        elif sort_by == "likes":
            base_query = base_query.order_by(Post.likes.desc())
        elif sort_by == "retweets":
            base_query = base_query.order_by(Post.retweets.desc())
        else:  # relevance (default)
            # For relevance, we'll fetch and sort in Python
            base_query = base_query.order_by(Post.timestamp.desc())
        
        # Get results
        posts = base_query.offset(offset).limit(limit * 2 if sort_by == "relevance" else limit).all()
        
        # If sorting by relevance, calculate scores and re-sort
        if sort_by == "relevance":
            scored_posts = []
            for post in posts:
                score = self._calculate_relevance_score(post, parsed_query)
                scored_posts.append((score, post))
            
            # Sort by score (descending)
            scored_posts.sort(key=lambda x: x[0], reverse=True)
            posts = [post for score, post in scored_posts[:limit]]
        
        # Convert to dictionaries
        results = [post.to_dict() for post in posts]
        
        return {
            "results": results,
            "total": total,
            "limit": limit,
            "offset": offset,
            "query": query,
            "parsed_query": parsed_query
        }
    
    def search_by_hashtag(self, hashtag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts by hashtag"""
        hashtag = hashtag.lstrip('#').lower()
        
        posts = self.db.query(Post).filter(
            Post.hashtags.ilike(f'%{hashtag}%')
        ).order_by(Post.timestamp.desc()).limit(limit).all()
        
        return [post.to_dict() for post in posts]
    
    def search_by_mention(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search posts mentioning a specific user"""
        username = username.lstrip('@').lower()
        
        posts = self.db.query(Post).filter(
            or_(
                Post.mentions.ilike(f'%{username}%'),
                Post.content.ilike(f'%@{username}%')
            )
        ).order_by(Post.timestamp.desc()).limit(limit).all()
        
        return [post.to_dict() for post in posts]

