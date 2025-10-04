import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key exists: {bool(api_key)}")

try:
    print("Initializing Groq client...")
    client = Groq(api_key=api_key)
    print("✅ Groq client initialized successfully")
    
    print("Sending test request...")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Hello, world!",
            }
        ],
        model="llama-3.1-8b-instant",
    )
    print(f"✅ Response received: {chat_completion.choices[0].message.content[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()