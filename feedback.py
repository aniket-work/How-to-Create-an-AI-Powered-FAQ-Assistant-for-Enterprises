# feedback.py - Feedback collection for Enterprise FAQ Assistant
import sqlite3
import os
from datetime import datetime
from models import FeedbackRequest

# Initialize database
def init_db():
    """Initialize the feedback database"""
    conn = sqlite3.connect('feedback.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  query TEXT,
                  answer TEXT,
                  is_helpful BOOLEAN,
                  sources TEXT,
                  session_id TEXT)''')
    conn.commit()
    conn.close()

def add_feedback(query: str, answer: str, is_helpful: bool, sources: str, session_id: str = None):
    """Add feedback to the database"""
    try:
        init_db()
        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute("""INSERT INTO feedback 
                     (timestamp, query, answer, is_helpful, sources, session_id)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (datetime.now().isoformat(), query, answer, is_helpful, sources, session_id))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Feedback recorded"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_feedback_stats():
    """Get feedback statistics"""
    try:
        init_db()
        conn = sqlite3.connect('feedback.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) as total, SUM(is_helpful) as helpful FROM feedback")
        result = c.fetchone()
        conn.close()
        
        total = result[0] if result[0] else 0
        helpful = result[1] if result[1] else 0
        
        return {
            "total_feedback": total,
            "helpful_feedback": helpful,
            "helpfulness_rate": helpful/total if total > 0 else 0
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}