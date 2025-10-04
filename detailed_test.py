import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv("GROQ_API_KEY")
print(f"API Key: {api_key[:10]}...{api_key[-5:] if api_key else 'None'}")

try:
    print("Initializing Groq client...")
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=api_key
    )
    print("✅ Groq client initialized successfully")
    
    print("Sending test request...")
    response = llm.invoke("Hello, world!")
    print(f"✅ Response received: {response.content[:100]}...")
    
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()