from fastapi import APIRouter, Body
from llm.rag import search, generate_response, generate_response_with_module
from llm.classifier import detect_module
import asyncio
import time
import sys

router = APIRouter(tags=["Chat"])

@router.post("/query", summary="Send a chat query")
async def chat(query: str = Body(...), tenant_id: str = Body(...)):
    """
    Handle chat queries - now optimized to run module detection and search in parallel
    """
    start_time = time.time()
    print("\n" + "="*80, flush=True)
    print(f"🔵 NEW REQUEST RECEIVED", flush=True)
    print(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}", flush=True)
    print(f"   Tenant ID: {tenant_id}", flush=True)
    print(f"   Time: {time.strftime('%H:%M:%S')}", flush=True)
    print("="*80, flush=True)
    sys.stdout.flush()
    
    try:
        # Step 1: Search for relevant documents
        print("\n📚 STEP 1: Searching for relevant documents...", flush=True)
        sys.stdout.flush()
        search_start = time.time()
        docs_task = asyncio.create_task(asyncio.to_thread(search, query, tenant_id))
        
        # Get search results
        docs = await docs_task
        search_time = time.time() - search_start
        print(f"✅ Document search completed in {search_time:.2f}s", flush=True)
        print(f"   Found {len(docs)} document chunks", flush=True)
        for i, doc in enumerate(docs[:2], 1):
            preview = doc[:80].replace('\n', ' ')
            print(f"   Doc {i} preview: {preview}...", flush=True)
        sys.stdout.flush()
        
        context = "\n".join(docs)
        
        # Step 2: Generate response with module detection
        print("\n🤖 STEP 2: Generating AI response (with module detection)...", flush=True)
        sys.stdout.flush()
        generation_start = time.time()
        result = await asyncio.to_thread(generate_response_with_module, query, context, tenant_id)
        generation_time = time.time() - generation_start
        print(f"✅ Response generation completed in {generation_time:.2f}s", flush=True)
        print(f"   Module detected: {result.get('module', 'General')}", flush=True)
        print(f"   Response length: {len(result.get('response', ''))} characters", flush=True)
        sys.stdout.flush()
        
        total_time = time.time() - start_time
        print("\n" + "="*80, flush=True)
        print(f"✅ REQUEST COMPLETED SUCCESSFULLY", flush=True)
        print(f"   Total time: {total_time:.2f}s", flush=True)
        print(f"   Breakdown: Search={search_time:.2f}s, Generation={generation_time:.2f}s", flush=True)
        print("="*80 + "\n", flush=True)
        sys.stdout.flush()
        
        return {
            "module": result.get("module", "General"),
            "response": result.get("response", "")
        }
    except Exception as e:
        error_time = time.time() - start_time
        print("\n" + "="*80, flush=True)
        print(f"❌ ERROR IN REQUEST (after {error_time:.2f}s)", flush=True)
        print(f"   Error: {str(e)}", flush=True)
        print("="*80 + "\n", flush=True)
        sys.stdout.flush()
        return {
            "module": "General",
            "response": f"I apologize, but I encountered an error processing your request. Please make sure the backend services are properly configured."
        }