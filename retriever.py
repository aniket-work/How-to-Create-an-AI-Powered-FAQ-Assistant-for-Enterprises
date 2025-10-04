# retriever.py - Document retrieval for Enterprise FAQ Assistant
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import os
import time
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Tuple

# Load environment variables
load_dotenv()

# Get API key from environment
groq_api_key = os.getenv("GROQ_API_KEY")

# Initialize ChromaDB client and embeddings
chroma_client = chromadb.PersistentClient(path="./vector_store")

# Initialize embeddings (using HuggingFace as Groq doesn't provide embeddings)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Initialize LLM with Groq
llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.1-8b-instant",
    groq_api_key=groq_api_key
)

def query_docs_with_retry(query: str, k: int = 3, max_retries: int = 3) -> Tuple[str, List[dict]]:
    """Query documents with retry logic"""
    for attempt in range(max_retries):
        try:
            return query_docs(query, k)
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
    return "Failed to query documents after retries", []

def query_docs(query: str, k: int = 3) -> Tuple[str, List[dict]]:
    """Query documents and generate an answer using RAG"""
    try:
        # Get collection
        collection = chroma_client.get_collection(name="faq_documents")
        
        # Generate query embedding
        query_embedding = embeddings.embed_query(query)
        
        # Search for relevant documents
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k
        )
        
        # Extract documents and metadata
        documents = results['documents'][0] if results['documents'] else []
        metadatas = results['metadatas'][0] if results['metadatas'] else []
        
        # Format sources
        sources = []
        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            sources.append({
                "filename": meta.get("filename", "unknown"),
                "preview": doc[:300] + "..." if len(doc) > 300 else doc
            })
        
        # If no documents found, return a default response
        if not documents:
            return "I couldn't find any relevant information in the company documents. Please upload relevant documents or rephrase your question.", []
        
        # Create context from retrieved documents
        context = "\n\n".join(documents)
        
        # Create prompt for LLM
        template = """
        You are an enterprise FAQ assistant. Answer the question based on the provided context from company documents.
        If the context doesn't contain enough information to answer the question, say so politely.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        
        prompt = PromptTemplate(template=template, input_variables=["context", "question"])
        chain = LLMChain(llm=llm, prompt=prompt)
        
        # Generate answer
        answer = chain.run(context=context, question=query)
        
        return answer.strip(), sources
        
    except Exception as e:
        return f"Error querying documents: {str(e)}", []