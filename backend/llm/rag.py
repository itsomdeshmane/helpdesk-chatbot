from openai import OpenAI
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, GPT_MODEL
from functools import lru_cache
import hashlib
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Initialize OpenAI client with timeout
client = OpenAI(
    api_key=OPENAI_API_KEY,
    timeout=30.0,  # 30 second timeout
    max_retries=2  # Only retry twice
)

# In-memory document store (fallback when Pinecone is not configured)
in_memory_docs = []

# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

# Import database and prompt enhancer
try:
    from database.db_manager import db_manager
    from llm.prompt_enhancer import get_enhanced_prompt, detect_query_type, is_complex_query
    enhanced_features_available = True
except ImportError as e:
    print(f"Enhanced features not available: {e}", flush=True)
    enhanced_features_available = False

# Initialize Pinecone (if API key is provided)
pinecone_available = False
pinecone_index = None
if PINECONE_API_KEY:
    try:
        from pinecone import Pinecone
        # Initialize Pinecone with new API (v3.0+)
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pinecone_available = True
        # Cache the index connection
        if PINECONE_INDEX_NAME:
            try:
                pinecone_index = pc.Index(PINECONE_INDEX_NAME)
                print(f"✅ Connected to Pinecone index: {PINECONE_INDEX_NAME}")
            except Exception as e:
                print(f"⚠️  Could not connect to Pinecone index: {e}")
                print(f"📝 Using in-memory document storage as fallback")
    except Exception as e:
        print(f"⚠️  Could not initialize Pinecone: {e}")
        print(f"📝 Using in-memory document storage as fallback")
else:
    print(f"📝 Pinecone not configured. Using in-memory document storage.")

def search(query: str, tenant_id: str):
    """
    Search for relevant documents in the vector database or in-memory storage.
    Returns relevant context for the query.
    """
    import time
    try:
        # If Pinecone is configured, search there
        if pinecone_available and pinecone_index:
            print("   🔍 Using Pinecone vector search...")
            try:
                # Get embeddings from OpenAI
                print("   ⏳ Generating query embedding from OpenAI...")
                embed_start = time.time()
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=query
                )
                query_embedding = response.data[0].embedding
                embed_time = time.time() - embed_start
                print(f"   ✅ Embedding generated in {embed_time:.2f}s")
                
                # Search Pinecone using cached index
                print("   ⏳ Querying Pinecone index...")
                pinecone_start = time.time()
                results = pinecone_index.query(
                    vector=query_embedding,
                    filter={"tenant_id": tenant_id},
                    top_k=5,  # Increased to get more context for complete module info
                    include_metadata=True
                )
                pinecone_time = time.time() - pinecone_start
                print(f"   ✅ Pinecone query completed in {pinecone_time:.2f}s")
                
                # Access results using attributes (new Pinecone API v8.0+)
                matches = results.matches if hasattr(results, 'matches') else results.get('matches', [])
                
                if matches and len(matches) > 0:
                    print(f"   ✅ Found {len(matches)} matches in Pinecone")
                    # Access match attributes correctly for new API
                    contexts = []
                    for match in matches:
                        if hasattr(match, 'metadata'):
                            text = match.metadata.get('text', '')
                        else:
                            text = match.get('metadata', {}).get('text', '')
                        if text:
                            contexts.append(text)
                    return contexts if contexts else ["No relevant documents found."]
                else:
                    print("   ⚠️  No matches found in Pinecone")
                    return ["No relevant documents found in the knowledge base."]
            except Exception as e:
                print(f"   ❌ Pinecone search error: {e}")
                print("   🔄 Falling back to in-memory search...")
                # Fall through to in-memory search
        
        # Fallback: Use smart search engine (BM25 + TF-IDF + Fuzzy)
        print(f"   🔍 Using Smart Search Engine (Total docs: {len(in_memory_docs)})...")
        if in_memory_docs:
            search_start = time.time()
            
            try:
                # Use advanced multi-algorithm search
                from llm.smart_search import get_smart_search_engine
                
                engine = get_smart_search_engine()
                
                # Build/rebuild index if needed
                tenant_docs = [doc for doc in in_memory_docs if doc.get('tenant_id') == tenant_id]
                if not engine.is_indexed or len(engine.documents) != len(tenant_docs):
                    engine.build_index(in_memory_docs, tenant_id)
                
                # Perform multi-algorithm search
                contexts, metadata = engine.get_context(query, top_k=5)
                
                search_time = time.time() - search_start
                print(f"   ✅ Smart search completed in {search_time:.3f}s")
                
                if contexts:
                    print(f"   📊 Found {len(contexts)} relevant documents")
                    for i, meta in enumerate(metadata[:3]):
                        print(f"      #{i+1}: Score={meta.get('score', 0):.2f}, Algorithm={meta.get('algorithm', 'N/A')}, File={meta.get('filename', 'unknown')}")
                    return contexts
                elif tenant_docs:
                    # Fallback: return most content-rich docs
                    print(f"   ⚠️  No matches, returning content-rich documents")
                    sorted_docs = sorted(tenant_docs, key=lambda d: len(d.get('text', '')), reverse=True)
                    return [doc['text'] for doc in sorted_docs[:5]]
                else:
                    return ["No documentation has been loaded for your organization yet."]
                    
            except ImportError as e:
                print(f"   ⚠️  Smart search unavailable ({e}), using basic search...")
                # Basic fallback search
                return _basic_keyword_search(query, tenant_id, in_memory_docs)
            except Exception as e:
                print(f"   ❌ Smart search error: {e}")
                return _basic_keyword_search(query, tenant_id, in_memory_docs)
        else:
            print("   ⚠️  No documents in memory")
            return ["No documentation has been loaded yet. Please upload your documents first."]
            
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        return ["I encountered an error searching the documentation. Please try rephrasing your question."]


def _basic_keyword_search(query: str, tenant_id: str, docs: list) -> list:
    """Basic keyword search fallback"""
    query_lower = query.lower()
    query_words = [w for w in query_lower.split() if len(w) >= 3]
    
    tenant_docs = [doc for doc in docs if doc.get('tenant_id') == tenant_id]
    scored = []
    
    for doc in tenant_docs:
        text = doc.get('text', '').lower()
        score = sum(1 for w in query_words if w in text)
        if score > 0:
            scored.append((score, doc['text']))
    
    scored.sort(reverse=True, key=lambda x: x[0])
    
    if scored:
        return [s[1] for s in scored[:5]]
    elif tenant_docs:
        return [doc['text'] for doc in tenant_docs[:5]]
    return ["No matching documentation found."]


def generate_response_with_module_with_context(query: str, context: str, tenant_id: str = "default", conversation_history: list = None):
    """
    Generate a response with conversation context support.
    Returns dict with 'response' key.
    
    Args:
        query: Current user query
        context: Document context from search
        tenant_id: Tenant identifier
        conversation_history: List of previous messages in conversation
    """
    import time
    try:
        print("   🧠 Analyzing query with conversation context...", flush=True)
        
        # Build conversation context if available
        conversation_context = ""
        if conversation_history and len(conversation_history) > 0:
            print(f"   📜 Using {len(conversation_history)} previous messages for context", flush=True)
            conversation_context = "\n\nPrevious conversation:\n"
            for i, msg in enumerate(conversation_history[-3:], 1):  # Last 3 messages
                conversation_context += f"User: {msg['query']}\n"
                conversation_context += f"Assistant: {msg['response'][:150]}...\n\n"
            conversation_context += "Current question:\n"
        
        # Use simple query type detection
        query_type = "general"
        
        # Check if context is empty or not useful
        context_is_empty = (
            not context or 
            context.strip() == "" or
            "No relevant documents" in context or
            "No documentation has been loaded" in context or
            len(context.strip()) < 50
        )
        
        if context_is_empty:
            return {
                "response": "I don't have information about this in the loaded documentation. Please check if the relevant document has been uploaded or contact support."
            }
        
        # Truncate context if too long
        max_context_chars = 8000
        if len(context) > max_context_chars:
            context = context[:max_context_chars] + "\n... (context truncated)"
        
        system_prompt = """You are a helpdesk assistant that ONLY answers from the provided documentation.

CONTEXT RULES:
1. Pay attention to Previous Conversation to resolve pronouns ("this", "it", "that")
2. Stay on the SAME topic unless user explicitly changes it

🚨 ABSOLUTE RULES - YOU MUST FOLLOW:
1. ONLY use information EXPLICITLY written in the Documentation Context below
2. DO NOT use ANY external knowledge, training data, or general information
3. DO NOT make assumptions or infer anything not directly stated
4. DO NOT provide generic answers that could apply to any system
5. If the answer is NOT in the Documentation Context, respond EXACTLY with:
   "I don't have information about this in the loaded documentation. Please check if the relevant document has been uploaded or contact support."
6. Every single fact must come from the provided context
7. Use bullet points and clear formatting for lists
8. Be concise but complete

⚠️ NEVER MAKE UP OR GUESS INFORMATION - ONLY USE WHAT IS IN THE CONTEXT ⚠️"""
        
        user_prompt = f"""{conversation_context}Documentation Context (USE ONLY THIS - DO NOT ADD EXTERNAL INFO):
{context}

User Question: {query}

INSTRUCTIONS:
- Answer ONLY from the Documentation Context above
- If pronouns like "this", "it" are used, check Previous Conversation for context
- If the answer is NOT in the context, say "I don't have information about this in the loaded documentation"
- DO NOT add any external knowledge
- Format your response clearly with bullet points when listing steps or items"""

        print(f"   📏 Prompt size: {len(system_prompt) + len(user_prompt)} characters", flush=True)
        print(f"   ⏳ Calling OpenAI API ({GPT_MODEL})...", flush=True)
        
        # Call OpenAI ChatGPT API with optimized settings
        api_start = time.time()
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Low temperature for strict, factual responses
            max_tokens=600,   # Increased for detailed answers
            timeout=30
        )
        api_time = time.time() - api_start
        print(f"   ✅ OpenAI API responded in {api_time:.2f}s", flush=True)
        
        content = response.choices[0].message.content
        print(f"   📝 Received response: {len(content)} characters", flush=True)
        
        # Clean response - remove any MODULE: lines if present
        answer = content
        if "MODULE:" in content:
            lines = content.split('\n')
            answer = '\n'.join(line for line in lines if not line.strip().startswith("MODULE:"))
            answer = answer.strip()
        
        # Save interaction to database for training
        if enhanced_features_available:
            try:
                db_manager.save_interaction(
                    tenant_id=tenant_id,
                    query=query,
                    response=answer,
                    module="General",
                    response_time=api_time
                )
                print(f"   💾 Interaction saved to database", flush=True)
            except Exception as db_error:
                print(f"   ⚠️  Could not save to database: {db_error}", flush=True)
        
        return {
            "response": answer,
            "query_type": query_type
        }
    except Exception as e:
        print(f"   ❌ Error generating response: {str(e)}")
        error_msg = f"Error generating response: {str(e)}. Please check your OPENAI_API_KEY in the .env file."
        return {
            "response": error_msg
        }


def generate_response_with_module(query: str, context: str, tenant_id: str = "default"):
    """
    Generate a response AND detect the module in a single OpenAI call for better performance.
    Returns dict with 'response' and 'module' keys.
    Optimized to avoid blocking with enhanced formatting.
    
    NOTE: This is the legacy function. Use generate_response_with_module_with_context for conversation support.
    """
    return generate_response_with_module_with_context(query, context, tenant_id, None)

def check_file_exists_in_db(filename: str, tenant_id: str = "default"):
    """
    Check if data for a specific file already exists in Pinecone or in-memory storage.
    Returns True if the file has data uploaded, False otherwise.
    """
    try:
        if pinecone_available and pinecone_index:
            # Check Pinecone for any vectors with this filename
            # We'll check if the first chunk exists
            vector_id = f"{tenant_id}_{filename}_0"
            try:
                result = pinecone_index.fetch(ids=[vector_id])
                # Check if we got any results
                if hasattr(result, 'vectors') and result.vectors:
                    return len(result.vectors) > 0
                elif isinstance(result, dict) and 'vectors' in result:
                    return len(result['vectors']) > 0
                return False
            except Exception as e:
                # If fetch fails, assume file doesn't exist
                return False
        else:
            # Check in-memory storage
            for doc in in_memory_docs:
                if doc.get('filename') == filename and doc.get('tenant_id') == tenant_id:
                    return True
            return False
    except Exception as e:
        print(f"      ⚠️  Error checking file existence: {e}")
        return False


def clear_chunks_by_filename(filename: str, tenant_id: str = "default"):
    """
    Clear all chunks for a specific filename before reloading.
    This prevents duplicate/old chunks from remaining in the database.
    """
    try:
        if pinecone_available and pinecone_index:
            print(f"      🗑️  Clearing old chunks from Pinecone for: {filename}")
            try:
                # Delete vectors by metadata filter (if namespace supports it)
                # First, try to delete by filter
                try:
                    pinecone_index.delete(filter={"filename": filename, "tenant_id": tenant_id})
                    print(f"      ✅ Cleared old chunks using metadata filter")
                except Exception as filter_error:
                    # Fallback: Delete by ID prefix pattern
                    # Generate IDs that would have been created for this file
                    print(f"      ⚠️  Filter-based deletion not supported, using ID-based deletion")
                    # We'll delete up to 1000 possible chunk IDs (should cover most documents)
                    ids_to_delete = [f"{tenant_id}_{filename}_{i}" for i in range(1000)]
                    # Delete in batches of 100
                    for i in range(0, len(ids_to_delete), 100):
                        batch = ids_to_delete[i:i+100]
                        try:
                            pinecone_index.delete(ids=batch)
                        except:
                            pass  # Ignore errors for non-existent IDs
                    print(f"      ✅ Cleared potential duplicate chunks by ID")
            except Exception as e:
                print(f"      ⚠️  Could not clear Pinecone vectors: {e}")
                print(f"      💡 Vectors will be overwritten on next upsert with same IDs")
        else:
            # Clear from in-memory storage
            global in_memory_docs
            initial_count = len(in_memory_docs)
            in_memory_docs = [
                doc for doc in in_memory_docs 
                if not (doc.get('filename') == filename and doc.get('tenant_id') == tenant_id)
            ]
            removed_count = initial_count - len(in_memory_docs)
            print(f"      🗑️  Cleared {removed_count} old chunks from memory for: {filename}")
            print(f"      📊 Remaining in-memory docs: {len(in_memory_docs)}")
    except Exception as e:
        print(f"      ⚠️  Error clearing chunks: {e}")


def embed_chunks(chunks: list, tenant_id: str, filename: str):
    """
    Create embeddings for text chunks and store them in Pinecone or in-memory storage.
    """
    import time
    try:
        # Try Pinecone first
        if pinecone_available and pinecone_index:
            print(f"      🔗 Using Pinecone vector database...")
            index = pinecone_index
            
            # Create embeddings and upsert to Pinecone
            vectors = []
            print(f"      ⏳ Generating embeddings for {len(chunks)} chunks...")
            embed_start = time.time()
            
            for i, chunk in enumerate(chunks):
                # Show progress for large files
                if i > 0 and i % 10 == 0:
                    print(f"         Progress: {i}/{len(chunks)} chunks...")
                
                # Get embedding from OpenAI
                response = client.embeddings.create(
                    model="text-embedding-ada-002",
                    input=chunk
                )
                embedding = response.data[0].embedding
                
                # Prepare vector for upsert
                vector_id = f"{tenant_id}_{filename}_{i}"
                metadata = {
                    "text": chunk,
                    "tenant_id": tenant_id,
                    "filename": filename,
                    "chunk_id": i
                }
                vectors.append((vector_id, embedding, metadata))
            
            embed_time = time.time() - embed_start
            print(f"      ✅ Embeddings generated in {embed_time:.2f}s")
            
            # Upsert vectors to Pinecone
            if vectors:
                print(f"      ⏳ Uploading to Pinecone...")
                upsert_start = time.time()
                index.upsert(vectors=vectors)
                upsert_time = time.time() - upsert_start
                print(f"      ✅ Uploaded {len(vectors)} vectors to Pinecone in {upsert_time:.2f}s")
        else:
            # Fallback: Store in memory (without embeddings for simplicity)
            print(f"      📝 Pinecone not configured. Using in-memory storage...")
            for i, chunk in enumerate(chunks):
                doc = {
                    "text": chunk,
                    "tenant_id": tenant_id,
                    "filename": filename,
                    "chunk_id": i
                }
                in_memory_docs.append(doc)
            print(f"      ✅ Stored {len(chunks)} chunks in memory")
            print(f"      📊 Total in-memory docs: {len(in_memory_docs)}")
            
    except Exception as e:
        print(f"      ⚠️  Error embedding chunks: {e}")
        # Fallback to in-memory storage
        try:
            print(f"      🔄 Falling back to in-memory storage...")
            for i, chunk in enumerate(chunks):
                doc = {
                    "text": chunk,
                    "tenant_id": tenant_id,
                    "filename": filename,
                    "chunk_id": i
                }
                in_memory_docs.append(doc)
            print(f"      ✅ Stored {len(chunks)} chunks in memory as fallback")
        except Exception as fallback_error:
            print(f"      ❌ Could not store documents: {fallback_error}")