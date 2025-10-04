# streaming.py - Streaming responses for Enterprise FAQ Assistant
import json
import time
import os
from dotenv import load_dotenv
from fastapi.responses import StreamingResponse
from langchain_groq import ChatGroq
from langchain.callbacks.base import BaseCallbackHandler
from retriever import query_docs
from typing import Callable

# Load environment variables
load_dotenv()

# Get API key from environment
groq_api_key = os.getenv("GROQ_API_KEY")

class TokenStreamCallbackHandler(BaseCallbackHandler):
    """Callback handler for streaming LLM tokens"""
    def __init__(self, send_function: Callable):
        self.send_function = send_function

    def on_llm_new_token(self, token: str, **kwargs):
        self.send_function(token)

def stream_sse_with_memory(session_id: str, question: str, k: int = 3):
    """Stream SSE response with memory integration"""
    def generate():
        try:
            # Send initial event
            yield f"data: {json.dumps({'type': 'status', 'value': 'processing'})}\n\n"
            
            # Get answer and sources
            answer, sources = query_docs(question, k)
            
            # Stream tokens
            yield f"data: {json.dumps({'type': 'status', 'value': 'generating'})}\n\n"
            
            # Stream answer word by word for better UX
            words = answer.split()
            for i, word in enumerate(words):
                yield f"data: {json.dumps({'type': 'token', 'value': word + ('' if i == len(words)-1 else ' ')})}\n\n"
                # Small delay for better streaming effect
                time.sleep(0.05)
            
            # Send sources
            yield f"data: {json.dumps({'type': 'sources', 'value': sources})}\n\n"
            
            # Send completion signal
            yield f"data: {json.dumps({'type': 'done', 'value': 'completed'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'value': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")