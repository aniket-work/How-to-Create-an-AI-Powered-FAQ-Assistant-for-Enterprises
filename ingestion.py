# ingestion.py - Document ingestion for Enterprise FAQ Assistant
import os
import tempfile
import hashlib
import time
from typing import List
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings
import pdfplumber
import docx

# Load environment variables
load_dotenv()

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path="./vector_store")

# Get API key from environment
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize embeddings (using HuggingFace as Groq doesn't provide embeddings)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file content"""
    text = ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name
    
    try:
        with pdfplumber.open(tmp_file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    finally:
        os.unlink(tmp_file_path)
    
    return text

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file content"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp_file:
        tmp_file.write(file_content)
        tmp_file_path = tmp_file.name
    
    try:
        doc = docx.Document(tmp_file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    finally:
        os.unlink(tmp_file_path)
    
    return text

def extract_text_from_txt(file_content: bytes) -> str:
    """Extract text from TXT file content"""
    return file_content.decode('utf-8', errors='ignore')

def extract_text(file_content: bytes, filename: str) -> str:
    """Extract text from file based on its extension"""
    if filename.lower().endswith('.pdf'):
        return extract_text_from_pdf(file_content)
    elif filename.lower().endswith('.docx'):
        return extract_text_from_docx(file_content)
    elif filename.lower().endswith('.txt'):
        return extract_text_from_txt(file_content)
    else:
        raise ValueError(f"Unsupported file type: {filename}")

def ingest_document_with_retry(file_content: bytes, filename: str, max_retries: int = 3) -> str:
    """Ingest a document into the vector store with retry logic"""
    for attempt in range(max_retries):
        try:
            return ingest_document(file_content, filename)
        except Exception as e:
            if attempt < max_retries - 1:
                # Wait for a bit before retrying (exponential backoff)
                wait_time = 2 ** attempt
                print(f"Error occurred, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                continue
            else:
                # Re-raise the exception if we've exhausted retries
                raise e
    return "Failed to ingest document after retries"

def ingest_document(file_content: bytes, filename: str) -> str:
    """Ingest a document into the vector store for FAQ assistance"""
    try:
        # Extract text from file
        text = extract_text(file_content, filename)
        
        if not text.strip():
            return "No text extracted from document"
        
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        
        # Create or get collection
        collection_name = "faq_documents"
        try:
            collection = chroma_client.get_collection(name=collection_name)
        except:
            collection = chroma_client.create_collection(name=collection_name)
        
        # Generate unique IDs for chunks
        file_hash = hashlib.md5(filename.encode()).hexdigest()[:8]
        ids = [f"{file_hash}_chunk_{i}" for i in range(len(chunks))]
        
        # Add chunks to collection
        collection.add(
            documents=chunks,
            metadatas=[{"filename": filename, "chunk": i} for i in range(len(chunks))],
            ids=ids
        )
        
        return f"Successfully ingested {len(chunks)} chunks from {filename}"
        
    except Exception as e:
        return f"Error ingesting document: {str(e)}"