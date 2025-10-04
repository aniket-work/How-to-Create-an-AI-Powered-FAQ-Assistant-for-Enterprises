# main.py - Enterprise FAQ Assistant Platform
from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules (we'll create these next)
from ingestion import ingest_document_with_retry as ingest_document
from retriever import query_docs_with_retry as query_docs
from hybrid_retriever import query_hybrid_with_retry as query_hybrid
from streaming import stream_sse_with_memory
from models import IngestResponse, QueryRequest, QueryResponse, FeedbackRequest
from feedback import add_feedback
from mem import router as mem_router, reset_session

# Initialize FastAPI app
app = FastAPI(
    title="Enterprise FAQ Assistant API",
    description="A professional RAG platform for enterprise FAQ management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include memory router
app.include_router(mem_router)

@app.get("/")
def read_root():
    return {"message": "Enterprise FAQ Assistant API is running"}

@app.post("/ingest/", response_model=IngestResponse)
async def ingest(file: UploadFile):
    """Ingest a document for FAQ assistance"""
    content = await file.read()
    result = ingest_document(content, file.filename)
    return {"status": "success", "file": file.filename, "result": result}

@app.post("/query/", response_model=QueryResponse)
async def query(req: QueryRequest):
    """Query documents for FAQ answers"""
    answer, sources = query_docs(req.query)
    return {"answer": answer, "sources": sources}

@app.post("/query_hybrid/", response_model=QueryResponse)
async def query_hybrid_endpoint(req: QueryRequest):
    """Query documents using hybrid search"""
    answer, sources = query_hybrid(req.query)
    return {"answer": answer, "sources": sources}

@app.post("/feedback/")
async def feedback(req: FeedbackRequest):
    """Submit feedback on FAQ answers"""
    result = add_feedback(
        query=req.query,
        answer=req.answer,
        is_helpful=req.is_helpful,
        sources=str(req.sources)
    )
    return result

@app.post("/reset_memory/")
async def reset_memory(session_id: str):
    """Reset conversation memory"""
    reset_session(session_id)
    return {"status": "memory cleared"}

@app.post("/query_sse_memory/")
async def query_sse_memory(request: Request):
    """Query with streaming SSE response"""
    data = await request.json()
    question = data.get("query", "")
    session_id = data.get("session_id", "default_session")
    k = data.get("k", 3)

    return stream_sse_with_memory(session_id=session_id, question=question, k=k)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)