# app.py - Enterprise FAQ Assistant Platform
import streamlit as st
import requests
import uuid
import json
import os
from dotenv import load_dotenv

# ---------- CONFIG ----------
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8001")
# ----------------------------

st.set_page_config(
    page_title="Enterprise FAQ Assistant", 
    layout="wide",
    page_icon="🏢"
)

# --- Custom CSS for professional UI ---
st.markdown("""
<style>
    /* Import professional fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Roboto+Slab:wght@300;400;500;600&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    /* Base styles */
    :root {
        --primary-color: #2563eb;
        --primary-hover: #1d4ed8;
        --secondary-color: #0f172a;
        --accent-color: #7c3aed;
        --background-color: #f8fafc;
        --card-background: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
    }
    
    body {
        font-family: 'Inter', sans-serif;
        background-color: var(--background-color);
        color: var(--text-primary);
        line-height: 1.5;
        font-size: 0.875rem;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Roboto Slab', serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    h1 { font-size: 1.5rem; }
    h2 { font-size: 1.25rem; }
    h3 { font-size: 1.125rem; }
    h4 { font-size: 1rem; }
    h5 { font-size: 0.875rem; }
    h6 { font-size: 0.875rem; }
    
    p { 
        font-size: 0.875rem;
        line-height: 1.5;
    }
    
    /* Header */
    .header-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 1.5rem 2rem;
        border-radius: 0;
        margin-bottom: 0;
        color: white;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
        position: relative;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .header-title {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .header-subtitle {
        font-size: 1rem;
        opacity: 0.85;
        font-weight: 400;
        max-width: 800px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Main layout */
    .main-content {
        display: flex;
        gap: 1.25rem;
        padding: 1.25rem;
        max-width: 100%;
    }
    
    .sidebar {
        flex: 0 0 300px;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .content {
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    /* Cards */
    .card {
        background: var(--card-background);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        transition: all 0.2s ease;
        margin-bottom: 0;
    }
    
    .card:hover {
        box-shadow: var(--shadow-md);
        border-color: #cbd5e1;
    }
    
    .card-title {
        font-size: 1.125rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: var(--secondary-color);
        display: flex;
        align-items: center;
        gap: 8px;
        padding-bottom: 0.625rem;
        border-bottom: 1px solid var(--border-color);
    }
    
    /* Chat container */
    .chat-container {
        background: var(--card-background);
        border-radius: var(--radius-md);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        height: 60vh;
        overflow-y: auto;
    }
    
    /* Messages */
    .message {
        padding: 0.875rem 1.125rem;
        border-radius: var(--radius-md);
        margin-bottom: 0.875rem;
        max-width: 90%;
        line-height: 1.5;
        position: relative;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        font-size: 0.875rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    
    .assistant-message {
        background-color: #f8fafc;
        color: var(--text-primary);
        border: 1px solid var(--border-color);
        margin-right: auto;
        border-bottom-left-radius: 4px;
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.875rem;
    }
    
    /* Source cards */
    .source-card {
        background-color: #f1f5f9;
        border-left: 3px solid var(--primary-color);
        padding: 12px;
        border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
        margin-top: 10px;
        font-size: 0.8125rem;
        transition: all 0.2s ease;
    }
    
    .source-card:hover {
        background-color: #e2e8f0;
        transform: translateX(2px);
    }
    
    .source-title {
        font-weight: 600;
        margin-bottom: 5px;
        color: var(--secondary-color);
        font-size: 0.875rem;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
        color: white;
        border: none;
        border-radius: var(--radius-sm);
        padding: 0.625rem 1.125rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        letter-spacing: 0.01em;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, var(--primary-hover) 0%, var(--primary-color) 100%);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    .stButton>button:active {
        transform: translateY(0);
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    
    .stButton>button:focus:not(:active) {
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.3);
    }
    
    /* Secondary button */
    .stButton>button.secondary {
        background: white;
        color: var(--primary-color);
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton>button.secondary:hover {
        background: #f8fafc;
        box-shadow: var(--shadow-md);
    }
    
    /* Input fields */
    .stTextInput>div>div>input {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-color);
        padding: 0.625rem 0.875rem;
        font-size: 0.875rem;
        transition: all 0.2s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2);
        outline: none;
    }
    
    .stFileUploader>div>div {
        border-radius: var(--radius-sm);
        border: 1px dashed var(--border-color);
        padding: 1.25rem;
        text-align: center;
        transition: all 0.2s ease;
        font-size: 0.875rem;
    }
    
    .stFileUploader>div>div:hover {
        border-color: var(--primary-color);
        background-color: #f8fafc;
    }
    
    /* Feedback buttons */
    .feedback-container {
        display: flex;
        gap: 8px;
        margin-top: 0.875rem;
    }
    
    .feedback-btn {
        flex: 1;
        text-align: center;
        padding: 0.5rem;
        border-radius: var(--radius-sm);
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 5px;
        font-size: 0.8125rem;
    }
    
    .feedback-positive {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #d1fae5;
    }
    
    .feedback-negative {
        background-color: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fee2e2;
    }
    
    .feedback-btn:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
    }
    
    .feedback-positive:hover {
        background-color: #d1fae5;
    }
    
    .feedback-negative:hover {
        background-color: #fee2e2;
    }
    
    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 6px;
    }
    
    .status-online {
        background-color: var(--success-color);
        box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.3);
    }
    
    .status-offline {
        background-color: var(--error-color);
    }
    
    /* Icons */
    .icon {
        font-size: 1rem;
        width: 18px;
        height: 18px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        padding: 0.625rem 0;
    }
    
    /* Divider */
    hr {
        border: 0;
        height: 1px;
        background: linear-gradient(to right, transparent, var(--border-color), transparent);
        margin: 1rem 0;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #94a3b8;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
    }
    
    /* Responsive adjustments */
    @media (max-width: 1024px) {
        .main-content {
            flex-direction: column;
        }
        
        .sidebar {
            flex: 0 0 auto;
        }
    }
    
    @media (max-width: 768px) {
        .header-container {
            padding: 1.25rem;
        }
        
        .header-title {
            font-size: 1.25rem;
        }
        
        .header-subtitle {
            font-size: 0.875rem;
        }
        
        .main-content {
            padding: 1rem;
        }
        
        .message {
            max-width: 95%;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- SSE Stream Helper ---
def sse_stream_post(url, json_data=None, timeout=60):
    """
    Minimal SSE client using POST + requests. 
    Yields parsed JSON payloads from lines that start with "data: ".
    """
    with requests.post(url, json=json_data, stream=True, timeout=timeout) as resp:
        resp.raise_for_status()
        buffer = ""
        for raw_line in resp.iter_lines(decode_unicode=True):
            if raw_line is None:
                continue
            line = raw_line.strip()
            if not line:
                if buffer:
                    for l in buffer.splitlines():
                        l = l.strip()
                        if l.startswith("data:"):
                            payload = l[len("data:"):].strip()
                            try:
                                yield json.loads(payload)
                            except Exception:
                                yield {"type": "raw", "value": payload}
                    buffer = ""
                continue
            buffer += line + "\n"
        if buffer:
            for l in buffer.splitlines():
                l = l.strip()
                if l.startswith("data:"):
                    payload = l[len("data:"):].strip()
                    try:
                        yield json.loads(payload)
                    except Exception:
                        yield {"type": "raw", "value": payload}

# --- Session state ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sources" not in st.session_state:
    st.session_state.sources = []
if "last_assistant" not in st.session_state:
    st.session_state.last_assistant = None
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False

# --- Header ---
st.markdown("""
<div class="header-container">
    <div class="header-title">
        <i class="fas fa-building icon"></i>
        Enterprise FAQ Assistant
    </div>
    <div class="header-subtitle">Intelligent answers to your company's most common questions, powered by advanced AI</div>
</div>
""", unsafe_allow_html=True)

# --- Layout: left pane upload + controls, right pane chat display ---
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Left sidebar
st.markdown('<div class="sidebar">', unsafe_allow_html=True)

# Document Management Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div class="card-title">
    <i class="fas fa-file-alt icon"></i>
    Document Management
</div>
''', unsafe_allow_html=True)

upload_file = st.file_uploader("Upload Company Documents", type=["pdf", "txt", "docx"], accept_multiple_files=False)

if st.button("Upload & Process Document"):
    if upload_file is None:
        st.warning("Please select a file first.")
    else:
        try:
            files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
            with st.spinner("Processing document..."):
                r = requests.post(f"{BACKEND_URL}/ingest/", files=files, timeout=120)
                r.raise_for_status()
            st.success("Document processed successfully")
            st.balloons()
        except Exception as e:
            error_msg = str(e)
            if "quota exceeded" in error_msg.lower():
                st.error("Rate limit exceeded during document processing. Please wait a moment and try again.")
            else:
                st.error(f"Upload failed: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# System Controls Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div class="card-title">
    <i class="fas fa-cog icon"></i>
    System Controls
</div>
''', unsafe_allow_html=True)

if st.button("Clear Conversation History"):
    try:
        resp = requests.post(
            f"{BACKEND_URL}/reset_memory/?session_id={st.session_state.session_id}",
            timeout=10
        )
        resp.raise_for_status()
        # Clear session state
        st.session_state.messages = []
        st.session_state.sources = []
        st.session_state.last_assistant = None
        st.session_state.session_id = str(uuid.uuid4())
        st.success("Conversation history cleared.")
    except Exception as e:
        st.error(f"Reset failed: {e}")

st.markdown("#### System Status")
st.markdown('<span class="status-indicator status-online"></span> API Connection: Online', unsafe_allow_html=True)
st.progress(len(st.session_state.messages) / 50 if len(st.session_state.messages) < 50 else 1.0)
st.write(f"Messages: {len(st.session_state.messages)}")
st.write(f"Sources: {len(st.session_state.sources)}")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Right content area
st.markdown('<div class="content">', unsafe_allow_html=True)

# FAQ Assistant Card
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('''
<div class="card-title">
    <i class="fas fa-comments icon"></i>
    FAQ Assistant
</div>
''', unsafe_allow_html=True)

# Chat display box
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for i, m in enumerate(st.session_state.messages):
        if m["role"] == "user":
            st.markdown(f'''
            <div class="message user-message">
                <div class="message-header">
                    <i class="fas fa-user icon"></i>
                    You
                </div>
                <div>{m["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown(f'''
            <div class="message assistant-message">
                <div class="message-header">
                    <i class="fas fa-robot icon"></i>
                    Assistant
                </div>
                <div>{m["content"]}</div>
            </div>
            ''', unsafe_allow_html=True)

    if st.session_state.is_streaming:
        st.info("Assistant is typing...")

    if st.session_state.sources:
        st.markdown("---")
        st.markdown("**Sources**")
        for s in st.session_state.sources:
            preview = s.get("preview", "")[:300]
            filename = s.get("filename", "unknown")
            st.markdown(f'''
            <div class="source-card">
                <div class="source-title">
                    <i class="fas fa-file-alt icon"></i>
                    {filename}
                </div>
                <div>{preview}...</div>
            </div>
            ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Question Input Card
st.markdown('<div class="card">', unsafe_allow_html=True)
with st.form("query_form", clear_on_submit=False):
    user_input = st.text_input("Ask a question about company policies, procedures, or documentation:", key="user_input")
    submitted = st.form_submit_button("Send Question")

if submitted and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.sources = []
    st.session_state.last_assistant = None
    st.session_state.is_streaming = True

    assistant_placeholder = st.empty()
    source_placeholder = st.empty()
    final_answer_parts = []

    try:
        url = f"{BACKEND_URL}/query_sse_memory/"
        data = {"query": user_input, "session_id": st.session_state.session_id}

        for event in sse_stream_post(url, json_data=data, timeout=300):
            t = event.get("type")
            if t == "token":
                token = event.get("value", "")
                final_answer_parts.append(token)
                joined = "".join(final_answer_parts)
                assistant_placeholder.markdown(
                    f'''
                    <div class="message assistant-message">
                        <div class="message-header">
                            <i class="fas fa-robot icon"></i>
                            Assistant
                        </div>
                        <div>{joined}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
            elif t == "sources":
                st.session_state.sources = event.get("value", [])
                src_md = "<b>Sources:</b><br>"
                for s in st.session_state.sources:
                    preview = s.get("preview", "")[:300]
                    filename = s.get("filename", "unknown")
                    src_md += f'''
                    <div class="source-card">
                        <div class="source-title">
                            <i class="fas fa-file-alt icon"></i>
                            {filename}
                        </div>
                        <div>{preview}...</div>
                    </div>
                    '''
                source_placeholder.markdown(src_md, unsafe_allow_html=True)
            elif t == "done":
                final_answer = "".join(final_answer_parts).strip()
                st.session_state.messages.append({"role": "assistant", "content": final_answer})
                st.session_state.last_assistant = final_answer
                st.session_state.is_streaming = False
                assistant_placeholder.markdown(
                    f'''
                    <div class="message assistant-message">
                        <div class="message-header">
                            <i class="fas fa-robot icon"></i>
                            Assistant
                        </div>
                        <div>{final_answer}</div>
                    </div>
                    ''',
                    unsafe_allow_html=True
                )
                break
    except Exception as e:
        st.session_state.is_streaming = False
        error_msg = str(e)
        if "quota exceeded" in error_msg.lower():
            st.error("Rate limit exceeded. Please wait a moment and try again.")
        else:
            st.error(f"Error during streaming: {e}")

st.markdown('</div>', unsafe_allow_html=True)

# Feedback UI
if st.session_state.last_assistant:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('''
    <div class="card-title">
        <i class="fas fa-thumbs-up icon"></i>
        Rate This Answer
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Helpful", key="positive_feedback"):
            try:
                payload = {
                    "query": st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "",
                    "answer": st.session_state.last_assistant,
                    "is_helpful": True,
                    "sources": st.session_state.sources,
                    "session_id": st.session_state.session_id
                }
                r = requests.post(f"{BACKEND_URL}/feedback/", json=payload, timeout=10)
                r.raise_for_status()
                st.success("Thanks for the feedback!")
            except Exception as e:
                st.error(f"Failed to send feedback: {e}")
    with col2:
        if st.button("Not helpful", key="negative_feedback"):
            try:
                payload = {
                    "query": st.session_state.messages[-2]["content"] if len(st.session_state.messages) >= 2 else "",
                    "answer": st.session_state.last_assistant,
                    "is_helpful": False,
                    "sources": st.session_state.sources,
                    "session_id": st.session_state.session_id
                }
                r = requests.post(f"{BACKEND_URL}/feedback/", json=payload, timeout=10)
                r.raise_for_status()
                st.info("Thanks for your feedback. We'll work to improve.")
            except Exception as e:
                st.error(f"Failed to send feedback: {e}")
    
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("💡 **Tip**: Upload company documents first, then ask questions about policies, procedures, or other documentation.")