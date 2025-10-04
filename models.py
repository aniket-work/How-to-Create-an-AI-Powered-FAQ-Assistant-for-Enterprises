# models.py - Data models for the Enterprise FAQ Assistant
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IngestResponse(BaseModel):
    status: str
    file: str
    result: Optional[str] = None

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None

class Source(BaseModel):
    filename: str
    preview: str
    score: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]

class FeedbackRequest(BaseModel):
    query: str
    answer: str
    is_helpful: bool
    sources: List[Dict[str, Any]]
    session_id: Optional[str] = None

class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    created_at: str
    chunk_count: int

class FAQEntry(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    category: Optional[str] = None
    confidence: Optional[float] = None