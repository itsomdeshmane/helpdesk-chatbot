"""
Quick diagnostic script to check backend configuration
"""
import sys
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME

print("="*60)
print("BACKEND CONFIGURATION CHECK")
print("="*60)

# Check OpenAI API Key
if OPENAI_API_KEY:
    key_preview = OPENAI_API_KEY[:10] + "..." + OPENAI_API_KEY[-4:]
    print(f"[OK] OPENAI_API_KEY: Configured ({key_preview})")
else:
    print("[ERROR] OPENAI_API_KEY: NOT CONFIGURED")
    print("   -> Get your key from: https://platform.openai.com/api-keys")
    print("   -> Add to backend/.env file: OPENAI_API_KEY=sk-...")

# Check Pinecone API Key
if PINECONE_API_KEY:
    print(f"[OK] PINECONE_API_KEY: Configured")
    print(f"   Index: {PINECONE_INDEX_NAME}")
else:
    print("[WARN] PINECONE_API_KEY: Not configured (using in-memory storage)")

print("="*60)

# Try to import OpenAI client
try:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("[OK] OpenAI client initialized successfully")
except Exception as e:
    print(f"[ERROR] OpenAI client error: {e}")
    sys.exit(1)

# Check in-memory docs
try:
    from llm.rag import in_memory_docs
    print(f"[INFO] In-memory documents: {len(in_memory_docs)} chunks")
    if len(in_memory_docs) == 0:
        print("   [WARN] No documents loaded! Restart backend to load docs.")
except Exception as e:
    print(f"[WARN] Could not check documents: {e}")

print("="*60)
print("Configuration check complete!")
print("="*60)

