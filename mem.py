# mem.py - Memory management for Enterprise FAQ Assistant
from fastapi import APIRouter
from typing import List, Dict, Any
import json

router = APIRouter()

# In-memory session storage (in production, use Redis or database)
sessions = {}

def format_sources_for_frontend(sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Format sources for frontend display"""
    formatted_sources = []
    for source in sources:
        formatted_sources.append({
            "filename": source.get("filename", "unknown"),
            "preview": source.get("preview", "")[:300] + "..." if len(source.get("preview", "")) > 300 else source.get("preview", ""),
        })
    return formatted_sources

def get_session(session_id: str) -> Dict[str, Any]:
    """Get or create a session"""
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "sources": []
        }
    return sessions[session_id]

def add_to_history(session_id: str, role: str, content: str):
    """Add a message to session history"""
    session = get_session(session_id)
    session["history"].append({"role": role, "content": content})

def reset_session(session_id: str):
    """Reset a session"""
    if session_id in sessions:
        del sessions[session_id]

@router.post("/memory/add_message/")
async def add_message(session_id: str, role: str, content: str):
    """Add a message to the session memory"""
    add_to_history(session_id, role, content)
    return {"status": "success"}

@router.get("/memory/get_history/")
async def get_history(session_id: str):
    """Get conversation history"""
    session = get_session(session_id)
    return {"history": session["history"]}

@router.post("/memory/reset/")
async def reset_memory(session_id: str):
    """Reset session memory"""
    reset_session(session_id)
    return {"status": "memory cleared"}