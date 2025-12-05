"""
Configuration Module - Production Ready
Centralized configuration management with environment variable support
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =============================================================================
# VECTOR DATABASE CONFIGURATION
# =============================================================================

# Set to "false" to temporarily disable Pinecone and use in-memory storage
USE_PINECONE = os.getenv("USE_PINECONE", "false").lower() == "true"

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY") if USE_PINECONE else None
# NOTE: Index must have 1536 dimensions for OpenAI text-embedding-3-small
# If you get dimension mismatch error, create new index with 1536 dimensions
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "erp-helpdesk")

# =============================================================================
# OPENAI CONFIGURATION
# =============================================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI Model Configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# Model parameters
GPT_TEMPERATURE = float(os.getenv("GPT_TEMPERATURE", "0.2"))
GPT_MAX_TOKENS = int(os.getenv("GPT_MAX_TOKENS", "500"))

# =============================================================================
# DATABASE CONFIGURATION
# =============================================================================

# MySQL Database Configuration
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "helpdesk_db")

# =============================================================================
# REDIS CACHE CONFIGURATION (Optional - falls back to in-memory)
# =============================================================================

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))

# Cache TTL settings (in seconds)
CACHE_EMBEDDING_TTL = int(os.getenv("CACHE_EMBEDDING_TTL", "86400"))  # 24 hours
CACHE_SEARCH_TTL = int(os.getenv("CACHE_SEARCH_TTL", "3600"))  # 1 hour
CACHE_RESPONSE_TTL = int(os.getenv("CACHE_RESPONSE_TTL", "1800"))  # 30 minutes

# =============================================================================
# SEARCH CONFIGURATION
# =============================================================================

# Enable hybrid search (BM25 + Vector)
USE_HYBRID_SEARCH = os.getenv("USE_HYBRID_SEARCH", "true").lower() == "true"

# Hybrid search weight (0.0 = all BM25, 1.0 = all vector)
HYBRID_SEARCH_ALPHA = float(os.getenv("HYBRID_SEARCH_ALPHA", "0.6"))

# Enable query rewriting
USE_QUERY_REWRITING = os.getenv("USE_QUERY_REWRITING", "true").lower() == "true"

# Search result count
SEARCH_TOP_K = int(os.getenv("SEARCH_TOP_K", "5"))

# =============================================================================
# CHUNKING CONFIGURATION
# =============================================================================

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
MIN_CHUNK_SIZE = int(os.getenv("MIN_CHUNK_SIZE", "50"))

# =============================================================================
# FEATURE FLAGS
# =============================================================================

# Enable streaming responses
ENABLE_STREAMING = os.getenv("ENABLE_STREAMING", "true").lower() == "true"

# Enable source attribution
ENABLE_SOURCE_ATTRIBUTION = os.getenv("ENABLE_SOURCE_ATTRIBUTION", "true").lower() == "true"

# Enable answer quality scoring
ENABLE_QUALITY_SCORING = os.getenv("ENABLE_QUALITY_SCORING", "true").lower() == "true"

# Enable suggested questions
ENABLE_SUGGESTIONS = os.getenv("ENABLE_SUGGESTIONS", "true").lower() == "true"

# Enable feedback collection
ENABLE_FEEDBACK = os.getenv("ENABLE_FEEDBACK", "true").lower() == "true"

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")  # "json" or "text"
LOG_FILE = os.getenv("LOG_FILE", "logs/helpdesk.log")

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

# CORS Configuration
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:3000").split(",")

# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not OPENAI_API_KEY:
        errors.append("OPENAI_API_KEY is required")
    
    if USE_PINECONE and not PINECONE_API_KEY:
        errors.append("PINECONE_API_KEY is required when USE_PINECONE=true")
    
    if errors:
        print("⚠️ Configuration errors:")
        for error in errors:
            print(f"   - {error}")
        return False
    
    return True

# Run validation on import
if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors")
