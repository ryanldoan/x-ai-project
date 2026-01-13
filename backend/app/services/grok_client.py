import httpx
import json
from typing import Optional, Dict, Any
from app.config import settings

class GrokClient:
    def __init__(self):
        self.api_key = settings.grok_api_key
        self.base_url = settings.grok_api_url
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def chat_completion(self, messages: list, model: str = "grok-3") -> Optional[str]:
        """Make a chat completion request to Grok"""
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": model,
                    "messages": messages
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            print(f"Grok API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            print(f"Grok API error: {e}")
            return None
    
    async def enhance_query(self, user_query: str) -> Dict[str, Any]:
        """Enhance and understand user search query"""
        prompt = f"""Analyze this search query and provide:
1. Main intent (what the user is looking for)
2. Key topics/keywords
3. Expanded query terms
4. Query type (factual, opinion, recent news, etc.)

Query: {user_query}

Respond in JSON format:
{{
    "intent": "...",
    "keywords": ["...", "..."],
    "expanded_terms": ["...", "..."],
    "query_type": "..."
}}"""
        
        messages = [
            {"role": "system", "content": "You are a search query analysis expert. Always respond with valid JSON only, no additional text."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages)
        
        # Try to parse JSON from response
        enhanced_data = {
            "original_query": user_query,
            "intent": "general search",
            "keywords": user_query.split(),
            "expanded_terms": user_query.split(),
            "query_type": "general"
        }
        
        if result:
            try:
                # Try to extract JSON from response (might have markdown code blocks)
                result = result.strip()
                if result.startswith("```"):
                    # Extract JSON from code block
                    result = result.split("```")[1]
                    if result.startswith("json"):
                        result = result[4:]
                    result = result.strip()
                elif result.startswith("```json"):
                    result = result[7:].split("```")[0].strip()
                
                parsed = json.loads(result)
                enhanced_data.update(parsed)
            except json.JSONDecodeError:
                print(f"Could not parse JSON from Grok response: {result}")
        
        return enhanced_data
    
    async def describe_post(self, post_content: str, author: str) -> str:
        """Generate rich description of a post for searchability"""
        prompt = f"""Analyze this X (Twitter) post and create a searchable description:
- Extract key topics and themes
- Identify entities (people, companies, concepts)
- Note sentiment and tone
- Highlight main message

Post by @{author}:
{post_content}

Provide a concise description (2-3 sentences) that would help match this post to relevant search queries."""
        
        messages = [
            {"role": "system", "content": "You are a content analysis expert. Provide clear, concise descriptions."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages)
        return result or f"Post by @{author} about {post_content[:50]}..."
    
    async def summarize_results(self, query: str, posts: list) -> str:
        """Generate intelligent summary of search results"""
        if not posts:
            return "No results found for your query."
        
        posts_text = "\n\n".join([
            f"Post {i+1} by @{p.get('author', 'unknown')}: {p.get('content', '')[:200]}"
            for i, p in enumerate(posts[:10])
        ])
        
        prompt = f"""Summarize these search results for the query: "{query}"

Results:
{posts_text}

Provide:
1. Overall summary of what these posts discuss
2. Key themes and insights
3. Most relevant posts highlighted
4. Any patterns or trends

Keep it concise (3-4 paragraphs)."""
        
        messages = [
            {"role": "system", "content": "You are a search results summarization expert. Provide clear, structured summaries."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages)
        return result or f"Found {len(posts)} results for '{query}'."
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

