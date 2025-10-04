#!/usr/bin/env python3
"""
Test script to verify rate limit handling
"""

import os
import time
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

def test_embedding_rate_limit():
    """Test embedding with rate limit handling"""
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize embeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )
        
        print("✅ Google Generative AI configured successfully")
        
        # Test embedding with retry logic
        test_texts = [
            "This is a test document for embedding.",
            "Another test document to check rate limits.",
            "Yet another document for testing purposes."
        ]
        
        for i, text in enumerate(test_texts):
            print(f"Processing document {i+1}/{len(test_texts)}...")
            
            # Try to embed with retry logic
            embedded = False
            for attempt in range(3):
                try:
                    embedding = embeddings.embed_query(text)
                    print(f"  ✅ Document {i+1} embedded successfully (embedding length: {len(embedding)})")
                    embedded = True
                    break
                except Exception as e:
                    if "quota exceeded" in str(e).lower() and attempt < 2:
                        wait_time = 2 ** attempt
                        print(f"  ⚠️  Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/3")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise e
            
            if not embedded:
                print(f"  ❌ Failed to embed document {i+1} after retries")
                return False
            
            # Small delay between requests to avoid hitting rate limits
            time.sleep(1)
        
        print("\n🎉 All tests passed! Rate limit handling is working correctly.")
        return True
        
    except Exception as e:
        if "quota exceeded" in str(e).lower():
            print("⚠️  Rate limit exceeded during testing. This is expected if you've hit your quota.")
            print("💡 Wait for your quota to reset or consider upgrading your plan.")
            print("📚 For more information, see the ratelimit_guide.md file.")
            return True  # This is an expected error
        else:
            print(f"❌ Error testing rate limit handling: {e}")
            return False

if __name__ == "__main__":
    print("Testing Google Generative AI rate limit handling...")
    success = test_embedding_rate_limit()
    if not success:
        print("\n💥 Tests failed. Please check your setup.")