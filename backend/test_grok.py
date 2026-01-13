import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.grok_client import GrokClient

async def test_grok_connection():
    """Test Grok API connection with a sample query"""
    print("Testing Grok API connection...")
    print("-" * 50)
    
    client = GrokClient()
    
    try:
        # Test 1: Basic query enhancement
        print("\n1. Testing query enhancement...")
        query = "What did Elon Musk say about AI?"
        result = await client.enhance_query(query)
        print(f"Original query: {query}")
        print(f"Enhanced result: {json.dumps(result, indent=2)}")
        
        # Test 2: Post description
        print("\n2. Testing post description...")
        sample_post = "AI will change everything. The future is exciting!"
        description = await client.describe_post(sample_post, "elonmusk")
        print(f"Sample post: {sample_post}")
        print(f"Grok description: {description}")
        
        # Test 3: Summarization
        print("\n3. Testing result summarization...")
        sample_posts = [
            {"author": "elonmusk", "content": "AI is the future of technology"},
            {"author": "OpenAI", "content": "We're building safe AI systems"},
            {"author": "xai", "content": "Grok is now available for everyone"}
        ]
        summary = await client.summarize_results("AI technology", sample_posts)
        print(f"Summary: {summary}")
        
        print("\n" + "-" * 50)
        print("✅ All Grok API tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error testing Grok API: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_grok_connection())

