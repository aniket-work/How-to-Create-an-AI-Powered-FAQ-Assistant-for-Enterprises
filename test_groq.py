#!/usr/bin/env python3
"""
Test script to verify Groq setup
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

def test_groq_setup():
    """Test if Groq is properly configured"""
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        return False
    
    try:
        # Initialize the LLM
        llm = ChatGroq(
            model_name="llama-3.1-8b-instant",
            groq_api_key=api_key,
            temperature=0.7
        )
        
        print("✅ Groq configured successfully")
        
        # Test a simple prompt
        response = llm.invoke("Say hello in 3 different languages")
        print(f"✅ Test response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Groq: {e}")
        return False

if __name__ == "__main__":
    print("Testing Groq setup...")
    success = test_groq_setup()
    if success:
        print("\n🎉 All tests passed! Groq is ready to use.")
    else:
        print("\n💥 Tests failed. Please check your setup.")