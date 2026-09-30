# AI Document Chatbot (RAG-based)

A ChatGPT-like web app to upload documents (PDF/TXT/DOCX) and ask questions about them using RAG (Retrieval-Augmented Generation).

## Tech Stack
- Backend: Python, FastAPI
- Embeddings: Sentence Transformers (all-MiniLM-L6-v2)
- Vector DB: ChromaDB
- LLM: Ollama (llama3.2)
- Chat history: SQLite
- Frontend: HTML/CSS/JavaScript

## Setup Instructions

1. Install Python 3.10+ and create a virtual environment:
python -m venv venv
   venv\Scripts\activate

2. Install dependencies:
   pip install -r requirements.txt

3. Install Ollama (https://ollama.com) and pull the model:
   ollama pull llama3.2

4. Run the server:
   uvicorn app.main:app

5. Open the app: http://127.0.0.1:8000

## Features
- Upload PDF, TXT, DOCX files
- Automatic text extraction and chunking
- Embeddings generated with Sentence Transformers, stored in ChromaDB
- Duplicate file detection using file hash
- RAG-based question answering with source (filename + page) shown
- Chat history stored in SQLite (GET /history)
- Basic error handling and logging

## API Endpoints
- POST /upload - Upload a document
- POST /chat - Ask a question ({"question": "..."})
- GET /history - View past questions/answers
- GET /status - Health check

## Known Limitations
- When multiple documents are uploaded, a general question without naming a document may retrieve chunks from the wrong file. Mentioning the filename in the question improves accuracy.
- First response after starting the server may be slower as the embedding model loads.