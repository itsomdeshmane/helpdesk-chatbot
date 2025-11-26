from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, documents, analytics
from ingestion.docs_loader import load_docs_from_folder, load_markdown_docs
import asyncio
import threading

app = FastAPI(
    title="AI Helpdesk Chatbot",
    description="AI-powered helpdesk chatbot with document search and Q&A",
    version="1.0.0"
)

# Flag to track if docs are loaded
docs_loaded = False

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # React dev server
        "http://localhost:3000",  # Fallback
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/chat")
app.include_router(documents.router, prefix="/documents")
app.include_router(analytics.router, prefix="/analytics")

def load_docs_background():
    """Load documents in background thread"""
    global docs_loaded
    import time
    
    print("\n" + "="*80, flush=True)
    print("AI HELPDESK CHATBOT - STARTING UP", flush=True)
    print("="*80, flush=True)
    print(f"Server: http://localhost:8000", flush=True)
    print(f"Docs: http://localhost:8000/docs", flush=True)
    print("="*80 + "\n", flush=True)
    
    print("Loading documentation in background...", flush=True)
    
    # Load regular documentation files (PDF, DOCX, etc.)
    load_docs_from_folder(tenant_id="default", module="general")
    
    # Load markdown documentation with structure-aware chunking
    print("\nLoading Verax markdown documentation...", flush=True)
    load_markdown_docs(tenant_id="default", module="verax_system")
    
    docs_loaded = True
    
    print("\n" + "="*80, flush=True)
    print("AI HELPDESK CHATBOT - READY!", flush=True)
    print("="*80, flush=True)
    print(f"Backend: http://localhost:8000", flush=True)
    print(f"Frontend: http://localhost:4200", flush=True)
    print(f"API Docs: http://localhost:8000/docs", flush=True)
    print("="*80 + "\n", flush=True)

@app.on_event("startup")
async def startup_event():
    """Start background document loading"""
    # Load docs in background thread so Swagger loads immediately
    thread = threading.Thread(target=load_docs_background, daemon=True)
    thread.start()
    print("FastAPI started - loading docs in background...", flush=True)

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    return {
        "status": "running",
        "message": "AI Helpdesk Running",
        "docs_loaded": docs_loaded,
        "version": "1.0.0"
    }

@app.get("/health", tags=["Health"])
def health():
    """Detailed health check"""
    from llm.rag import in_memory_docs
    return {
        "status": "healthy",
        "docs_loaded": docs_loaded,
        "document_count": len(in_memory_docs),
        "version": "1.0.0"
    }