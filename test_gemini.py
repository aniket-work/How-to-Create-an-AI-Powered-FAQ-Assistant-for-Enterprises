#!/usr/bin/env python3
"""
Test script to verify Google Generative AI setup
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_gemini_setup():
    """Test if Google Generative AI is properly configured"""
    # Get API key
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GOOGLE_GEMINI_API_KEY not found in environment variables")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # List available models
        print("✅ Google Generative AI configured successfully")
        print("Available models:")
        for model in genai.list_models():
            if "generateContent" in model.supported_generation_methods:
                print(f"  - {model.name}")
        
        # Test a simple prompt
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Say hello in 3 different languages")
        print(f"\n✅ Test response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing Google Generative AI: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google Generative AI setup...")
    success = test_gemini_setup()
    if success:
        print("\n🎉 All tests passed! Google Generative AI is ready to use.")
    else:
        print("\n💥 Tests failed. Please check your setup.")