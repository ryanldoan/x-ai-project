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
        prompt = f"""Analyze this search query and provide concise information:

Query: {user_query}

Respond in JSON format:
{{
    "intent": "brief one-sentence description of search intent (max 30 words)",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "expanded_terms": ["term1", "term2"],
    "query_type": "factual|opinion|recent|general"
}}

Keep intent brief and keywords limited to 5 most important terms."""
        
        messages = [
            {"role": "system", "content": "You are a search query analysis expert. Always respond with valid JSON only, no additional text. Keep responses concise."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages)
        
        # Try to parse JSON from response
        enhanced_data = {
            "original_query": user_query,
            "intent": "general search",
            "keywords": user_query.split()[:5],  # Limit to 5 keywords
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
                
                # Format and limit the data
                if "intent" in parsed:
                    # Truncate intent to 40 words max
                    intent_words = parsed["intent"].split()
                    if len(intent_words) > 40:
                        parsed["intent"] = " ".join(intent_words[:40]) + "..."
                
                if "keywords" in parsed and isinstance(parsed["keywords"], list):
                    # Limit to 5 keywords
                    parsed["keywords"] = parsed["keywords"][:5]
                
                if "expanded_terms" in parsed and isinstance(parsed["expanded_terms"], list):
                    # Limit to 5 expanded terms
                    parsed["expanded_terms"] = parsed["expanded_terms"][:5]
                
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

Provide a concise summary (maximum 280 words) of what these posts discuss. Focus on the main themes and key insights. Do not use markdown formatting, bullet points, or section headers. Write in plain text only. Keep it under 280 words."""
        
        messages = [
            {"role": "system", "content": "You are a search results summarization expert. Provide clear, concise summaries in plain text only. Maximum 280 words. No markdown, no bullet points, no section headers."},
            {"role": "user", "content": prompt}
        ]
        
        result = await self.chat_completion(messages)
        
        # Clean up the result - remove markdown if present
        if result:
            # Remove markdown headers, bold, etc.
            result = result.replace("**", "").replace("##", "").replace("#", "")
            # Remove common markdown patterns
            result = result.replace("###", "").replace("####", "")
        
        return result or f"Found {len(posts)} posts related to '{query}'."
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

