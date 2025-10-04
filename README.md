# Enterprise FAQ Assistant Platform

A professional Retrieval-Augmented Generation (RAG) platform designed specifically for enterprise FAQ management and assistance.

## Overview

This platform provides an intelligent FAQ assistant that can answer employee or customer questions based on company documentation. It combines the power of large language models with retrieval-augmented generation to provide accurate, context-aware responses.

## Features

- **Document Ingestion**: Upload and process various document formats (PDF, TXT, DOCX)
- **Intelligent Search**: Find relevant information across all company documents
- **Conversational Interface**: Natural chat interface for asking questions
- **Source Tracking**: See which documents informed each response
- **Feedback Collection**: Rate the helpfulness of answers to improve the system
- **Memory Management**: Context-aware conversations with session management
- **Professional UI**: Enterprise-grade interface with modern design principles

## Tech Stack

- **Frontend**: Streamlit for a responsive web interface
- **Backend**: FastAPI for RESTful API services
- **Database**: ChromaDB for vector storage and similarity search
- **AI/ML**: Langchain and Groq (Llama 3.1 8B) for natural language processing
- **Document Processing**: pdfplumber, python-docx for document parsing

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd enterprise-faq-platform
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   BACKEND_URL=http://localhost:8001
   ```

## Usage

1. Start the backend server:
   ```bash
   python start_backend.py
   ```

2. In a new terminal, start the frontend:
   ```bash
   streamlit run app.py
   ```

3. Access the application at `http://localhost:8503`

## Professional UI Features

The application now features a sophisticated, enterprise-grade interface with:

- **Professional Iconography**: SVG icon system replacing childish emojis
- **Corporate Color Scheme**: Professional blues and grays for enterprise appearance
- **Enhanced Typography**: Google Fonts (Inter and Roboto Slab) for improved readability
- **Dashboard Layout**: Organized sidebar and main content area
- **Card-Based Design**: Consistent card components with subtle shadows
- **Professional Components**: Custom-styled buttons, inputs, and interactive elements
- **Responsive Design**: Adapts to different screen sizes and devices
- **Accessibility Features**: Proper contrast ratios and keyboard navigation

For detailed information about the UI implementation, see:
- [Professional UI Guide](professional_ui_guide.md)
- [UI Transformation v2.0](ui_transformation_v2.md)

## API Endpoints

- `POST /ingest/` - Upload and process documents
- `POST /query/` - Ask questions about ingested documents
- `POST /query_sse_memory/` - Ask questions with streaming responses
- `POST /feedback/` - Provide feedback on answers
- `POST /reset_memory/` - Clear conversation history

## Examples

1. Upload company policy documents, employee handbooks, or product manuals
2. Ask questions like "What is the company's vacation policy?" or "How do I submit an expense report?"
3. Review the sources used to generate each answer
4. Provide feedback to improve future responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

MIT License - see LICENSE file for details