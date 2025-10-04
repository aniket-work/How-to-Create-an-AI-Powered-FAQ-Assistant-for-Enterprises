# app.py - Enterprise FAQ Assistant Platform
import streamlit as st
import requests
import uuid
import json
import os
from dotenv import load_dotenv

# ---------- CONFIG ----------
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
# ----------------------------

st.set_page_config(
    page_title="Enterprise FAQ Assistant", 
    layout="wide",
    page_icon="🏢"
)

# --- Custom CSS for professional UI ---
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .header-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .header-subtitle {
        font-size: 1.2rem;
        opacity: 0.9;
    }
    .chat-container {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #f9f9f9;
        height: 60vh;
        overflow-y: auto;
    }
    .user-message {
        background-color: #2196F3;
        color: white;
        padding: 12px 18px;
        border-radius: 20px;
        margin-bottom: 15px;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .assistant-message {
        background-color: #f1f1f1;
        color: #333;
        padding: 12px 18px;
        border-radius: 20px;
        margin-bottom: 15px;
        max-width: 80%;
        float: left;
        clear: both;
    }
    .source-card {
        background-color: #e3f2fd;
        border-left: 4px solid #2196F3;
        padding: 15px;
        border-radius: 5px;
        margin-top: 10px;
    }
    .feedback-section {
        background-color: #f5f5f5;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
    }
    .stButton>button {
        background-color: #2196F3;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #1976D2;
    }
    .upload-section {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
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
    <div class="header-title">Enterprise FAQ Assistant</div>
    <div class="header-subtitle">Intelligent answers to your company's most common questions</div>
</div>
""", unsafe_allow_html=True)

# --- Layout: left pane upload + controls, right pane chat display ---
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.header("📚 Document Management")
    upload_file = st.file_uploader("Upload Company Documents", type=["pdf", "txt", "docx"], accept_multiple_files=False)

    if st.button("📤 Upload & Process"):
        if upload_file is None:
            st.warning("Please select a file first.")
        else:
            try:
                files = {"file": (upload_file.name, upload_file.getvalue(), upload_file.type)}
                with st.spinner("Processing document..."):
                    r = requests.post(f"{BACKEND_URL}/ingest/", files=files, timeout=120)
                    r.raise_for_status()
                st.success("Document processed successfully ✅")
            except Exception as e:
                error_msg = str(e)
                if "quota exceeded" in error_msg.lower():
                    st.error("Rate limit exceeded during document processing. Please wait a moment and try again, or consider upgrading your Google AI API plan.")
                    st.info("For more information on quotas, visit: https://ai.google.dev/gemini-api/docs/rate-limits")
                else:
                    st.error(f"Upload failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.header("⚙️ Controls")
    if st.button("🗑️ Clear Conversation"):
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
            
            # Force rerun by modifying a dummy session_state key
            st.session_state._rerun = st.session_state.get("_rerun", 0) + 1

        except Exception as e:
            st.error(f"Reset failed: {e}")

    st.markdown("### 📊 System Info")
    st.write(f"Messages: {len(st.session_state.messages)}")
    st.write(f"Sources: {len(st.session_state.sources)}")

with col_right:
    st.header("💬 FAQ Assistant")

    # Chat display box
    chat_container = st.container()
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for i, m in enumerate(st.session_state.messages):
            if m["role"] == "user":
                st.markdown(f'<div class="user-message"><b>You:</b> {m["content"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message"><b>Assistant:</b> {m["content"]}</div><div style="clear: both;"></div>', unsafe_allow_html=True)

        if st.session_state.is_streaming:
            st.info("Assistant is typing...")

        if st.session_state.sources:
            st.markdown("---")
            st.markdown("**Sources**")
            for s in st.session_state.sources:
                preview = s.get("preview", "")[:300]
                filename = s.get("filename", "unknown")
                st.markdown(f'<div class="source-card"><b>{filename}</b><br>{preview}...</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Input
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
                        f'<div class="assistant-message"><b>Assistant:</b> {joined}</div><div style="clear: both;"></div>',
                        unsafe_allow_html=True
                    )
                elif t == "sources":
                    st.session_state.sources = event.get("value", [])
                    src_md = "<b>Sources:</b><br>"
                    for s in st.session_state.sources:
                        preview = s.get("preview", "")[:300]
                        filename = s.get("filename", "unknown")
                        src_md += f'<div class="source-card"><b>{filename}</b><br>{preview}...</div>'
                    source_placeholder.markdown(src_md, unsafe_allow_html=True)
                elif t == "done":
                    final_answer = "".join(final_answer_parts).strip()
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})
                    st.session_state.last_assistant = final_answer
                    st.session_state.is_streaming = False
                    assistant_placeholder.markdown(
                        f'<div class="assistant-message"><b>Assistant:</b> {final_answer}</div><div style="clear: both;"></div>',
                        unsafe_allow_html=True
                    )
                    break
        except Exception as e:
            st.session_state.is_streaming = False
            error_msg = str(e)
            if "quota exceeded" in error_msg.lower():
                st.error("Rate limit exceeded. Please wait a moment and try again, or consider upgrading your Google AI API plan.")
                st.info("For more information on quotas, visit: https://ai.google.dev/gemini-api/docs/rate-limits")
            else:
                st.error(f"Error during streaming: {e}")

    # Feedback UI
    if st.session_state.last_assistant:
        st.markdown('<div class="feedback-section">', unsafe_allow_html=True)
        st.markdown("### 📝 Rate This Answer")
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button("👍 Helpful"):
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
            if st.button("👎 Not helpful"):
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
                    st.success("Thanks for your feedback. We'll work to improve.")
                except Exception as e:
                    st.error(f"Failed to send feedback: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("💡 **Tip**: Upload company documents first, then ask questions about policies, procedures, or other documentation.")