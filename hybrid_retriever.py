# hybrid_retriever.py - Hybrid document retrieval for Enterprise FAQ Assistant
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import os
import time
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from rank_bm25 import BM25Okapi
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

def query_hybrid_with_retry(query: str, k: int = 3, max_retries: int = 3) -> Tuple[str, List[dict]]:
    """Query documents using hybrid search with retry logic"""
    for attempt in range(max_retries):
        try:
            return query_hybrid(query, k)
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

def query_hybrid(query: str, k: int = 3) -> Tuple[str, List[dict]]:
    """Query documents using hybrid search (vector + BM25)"""
    try:
        # Get collection
        collection = chroma_client.get_collection(name="faq_documents")
        
        # Vector search
        query_embedding = embeddings.embed_query(query)
        vector_results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k*2
        )
        
        # BM25 search
        all_documents = collection.get()
        if not all_documents['documents']:
            return "No documents available.", []
        
        # Tokenize documents for BM25
        tokenized_docs = [doc.split() for doc in all_documents['documents']]
        bm25 = BM25Okapi(tokenized_docs)
        tokenized_query = query.split()
        bm25_scores = bm25.get_scores(tokenized_query)
        
        # Combine results (simple combination)
        doc_scores = {}
        for i, doc_id in enumerate(all_documents['ids']):
            doc_scores[doc_id] = {
                'document': all_documents['documents'][i],
                'metadata': all_documents['metadatas'][i],
                'vector_score': 0,
                'bm25_score': bm25_scores[i]
            }
        
        # Add vector scores
        if vector_results['ids'] and vector_results['ids'][0]:
            for i, doc_id in enumerate(vector_results['ids'][0]):
                if doc_id in doc_scores:
                    doc_scores[doc_id]['vector_score'] = vector_results['distances'][0][i]
        
        # Sort by combined score (simple average)
        sorted_docs = sorted(
            doc_scores.items(), 
            key=lambda x: (x[1]['vector_score'] + x[1]['bm25_score']), 
            reverse=True
        )
        
        # Take top k results
        top_docs = sorted_docs[:k]
        
        # Format sources
        sources = []
        documents_for_context = []
        for doc_id, doc_data in top_docs:
            sources.append({
                "filename": doc_data['metadata'].get("filename", "unknown"),
                "preview": doc_data['document'][:300] + "..." if len(doc_data['document']) > 300 else doc_data['document']
            })
            documents_for_context.append(doc_data['document'])
        
        # If no documents found, return a default response
        if not documents_for_context:
            return "I couldn't find any relevant information in the company documents. Please upload relevant documents or rephrase your question.", []
        
        # Create context from retrieved documents
        context = "\n\n".join(documents_for_context)
        
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
        return f"Error in hybrid search: {str(e)}", []