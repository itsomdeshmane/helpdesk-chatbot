from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import chat, documents, analytics, auth
from routers import feedback, streaming, smart_chat, settings
from routers import user_conversations, global_analytics  # NEW: User-specific and global analytics
from routers import keyword_training  # NEW: Keyword learning system
from routers import metadata_management  # NEW: Metadata learning and management
from routers import smart_chat_v2  # NEW: SOLID-compliant router
from utils.observability import get_logger, generate_request_id
from utils.rate_limiter import rate_limiter
import asyncio
import time

# Initialize logger
logger = get_logger()

# ============================================================================
# SOLID REFACTORING: Dependency Injection Container
# ============================================================================
from core.container import AppContainer

# Initialize DI container
container = AppContainer()

# Wire container with FastAPI (enables dependency injection)
container.wire(modules=[
    "routers.smart_chat_v2",  # New SOLID router
    __name__  # Current module (app.py)
])

logger.info("✅ Dependency Injection Container initialized and wired")

# Initialize legacy bridge (for backward compatibility during migration)
from utils.legacy_bridge import LegacyBridge
LegacyBridge.set_container(container)
logger.info("✅ Legacy bridge initialized")
# ============================================================================

app = FastAPI(
    title="AI Helpdesk Chatbot",
    description="AI-powered helpdesk chatbot with document search, Q&A, streaming, and feedback - Now with SOLID architecture!",
    version="2.1.0"  # Incremented version for SOLID architecture
)

# Configure CORS - MUST be added before other middleware
# Secure: Uses environment-based configuration, NO wildcards in production
from config import CORS_ORIGINS, ENVIRONMENT

print(f"🔒 CORS configured for {ENVIRONMENT} environment")
print(f"   Allowed origins: {', '.join(CORS_ORIGINS)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Environment-based, no wildcards
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Session-ID", "X-RateLimit-Limit-Minute", "X-RateLimit-Remaining-Minute"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Rate limiting middleware - protect against abuse
app.middleware("http")(rate_limiter)

# Request logging middleware - skip OPTIONS requests to avoid interference with CORS
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    # Skip logging for OPTIONS preflight requests
    if request.method == "OPTIONS":
        return await call_next(request)
    
    request_id = generate_request_id()
    start_time = time.time()
    
    # Add request ID to state
    request.state.request_id = request_id
    
    try:
        # Log request start
        print(f"📥 {request.method} {request.url.path} [Request ID: {request_id}]", flush=True)
        
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000
        print(f"📤 {request.method} {request.url.path} -> {response.status_code} ({duration_ms:.0f}ms)", flush=True)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
    except Exception as e:
        print(f"❌ Error in request: {e}", flush=True)
        raise


# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(chat.router, prefix="/chat")
app.include_router(streaming.router, prefix="/chat")  # Streaming under /chat

# ============================================================================
# SMART CHAT ROUTERS: Both old and new for gradual migration
# ============================================================================
# OLD: Legacy router (kept for backward compatibility)
app.include_router(smart_chat.router, prefix="/chat", tags=["Smart Chat (Legacy)"])

# NEW: SOLID-compliant router with dependency injection
app.include_router(smart_chat_v2.router, prefix="/chat", tags=["Smart Chat V2 (SOLID)"])
# 
# Migration Strategy:
# 1. Both routers are available simultaneously
# 2. New endpoints at /chat/smart/v2/* use SOLID architecture
# 3. Old endpoints at /chat/smart/* still work (legacy)
# 4. Backward compatible endpoint at /chat/smart/query uses new implementation
# 5. After validation, can remove legacy router
# ============================================================================

app.include_router(documents.router, prefix="/documents")
app.include_router(analytics.router, prefix="/analytics")
app.include_router(feedback.router, prefix="/feedback")

# NEW: User-specific conversation history (isolated per user)
app.include_router(user_conversations.router, prefix="/conversations")

# NEW: Global analytics and learning (aggregated from all users for system improvement)
app.include_router(global_analytics.router, prefix="/analytics/global")

# Settings management
app.include_router(settings.router)

# Keyword training (AI learning system - ZERO HARDCODED)
app.include_router(keyword_training.router)

# Metadata management (Column/table descriptions and auto-learning)
app.include_router(metadata_management.router, prefix="/metadata")

@app.on_event("startup")
async def startup_event():
    """Startup event - display information"""
    print("\n" + "="*80, flush=True)
    print("AI HELPDESK CHATBOT - STARTING UP", flush=True)
    print("="*80, flush=True)
    print(f"Server: http://localhost:8000", flush=True)
    print(f"Docs: http://localhost:8000/docs", flush=True)
    print("="*80 + "\n", flush=True)
    
    print("ℹ️  Documents are NOT loaded automatically on startup.", flush=True)
    print("ℹ️  To load/reload documents, use these endpoints:", flush=True)
    print("   • POST /documents/upload - Upload a single file", flush=True)
    print("   • POST /documents/reload - Reload ALL files (PDF, DOCX, XLSX, TXT, MD)", flush=True)
    print("   • POST /documents/reload-markdown - Reload only markdown files", flush=True)
    print("", flush=True)
    print("💡 If documents are already in Pinecone, they will be queried automatically.", flush=True)
    
    print("\n" + "="*80, flush=True)
    print("🎉 SOLID REFACTORING ACTIVE!", flush=True)
    print("="*80, flush=True)
    print("✅ Dependency Injection: Enabled", flush=True)
    print("✅ SOLID Architecture: Active", flush=True)
    print("✅ New Endpoints: /chat/smart/v2/* (SOLID-compliant)", flush=True)
    print("✅ Legacy Endpoints: /chat/smart/* (backward compatible)", flush=True)
    print("="*80 + "\n", flush=True)
    
    print("\n" + "="*80, flush=True)
    print("AI HELPDESK CHATBOT - READY!", flush=True)
    print("="*80, flush=True)
    print(f"Backend: http://localhost:8000", flush=True)
    print(f"Frontend: http://localhost:4200", flush=True)
    print(f"API Docs: http://localhost:8000/docs", flush=True)
    print("="*80 + "\n", flush=True)

@app.get("/", tags=["Health"])
def root():
    """Health check endpoint"""
    from llm.rag import in_memory_docs
    
    return {
        "status": "running",
        "message": "AI Helpdesk Running",
        "in_memory_docs": len(in_memory_docs),
        "version": "2.0.0"
    }

@app.get("/health", tags=["Health"])
def health():
    """Detailed health check"""
    from llm.rag import in_memory_docs
    from llm.cache_manager import get_cache_manager
    
    cache_stats = {}
    try:
        cache_stats = get_cache_manager().get_stats()
    except:
        pass
    
    return {
        "status": "healthy",
        "in_memory_docs_count": len(in_memory_docs),
        "document_count": len(in_memory_docs),
        "version": "2.0.0",
        "features": {
            "hybrid_search": True,
            "streaming": True,
            "feedback": True,
            "source_attribution": True,
            "quality_scoring": True
        },
        "cache_stats": cache_stats
    }


@app.get("/metrics", tags=["Health"])
def metrics():
    """Get system metrics"""
    from utils.observability import get_logger
    return get_logger().get_metrics()