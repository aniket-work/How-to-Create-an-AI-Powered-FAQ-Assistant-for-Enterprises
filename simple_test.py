from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test Groq
print("Testing Groq...")
try:
    llm = ChatGroq(
        model_name="llama-3.1-8b-instant",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    print("✅ Groq initialized successfully")
except Exception as e:
    print(f"❌ Error initializing Groq: {e}")

# Test embeddings
print("Testing embeddings...")
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("✅ Embeddings initialized successfully")
except Exception as e:
    print(f"❌ Error initializing embeddings: {e}")

print("Test completed.")