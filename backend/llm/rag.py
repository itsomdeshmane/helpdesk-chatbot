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
        
        # Fallback: Use in-memory document storage with improved keyword matching
        print(f"   🔍 Using in-memory keyword search (Total docs: {len(in_memory_docs)})...")
        if in_memory_docs:
            # Enhanced keyword-based search
            query_lower = query.lower()
            matched_docs = []
            
            # Extract important keywords (longer than 3 chars, ignore common words)
            stop_words = {'what', 'where', 'when', 'which', 'who', 'how', 'give', 'show', 'tell', 'list', 'the', 'are', 'and', 'for', 'with'}
            query_words = [w for w in query_lower.split() if len(w) > 3 and w not in stop_words]
            
            # Also check for key phrases
            key_phrases = []
            if 'submodule' in query_lower or 'sub-module' in query_lower:
                key_phrases.append('submodule')
            if 'module' in query_lower:
                key_phrases.append('module')
            if 'purchasing' in query_lower:
                key_phrases.extend(['purchasing', 'purchase'])
            if 'inventory' in query_lower:
                key_phrases.append('inventory')
            
            search_start = time.time()
            for doc in in_memory_docs:
                if doc.get('tenant_id') == tenant_id:
                    text = doc.get('text', '').lower()
                    module = doc.get('module', '')
                    
                    # Count keyword matches
                    matches = sum(1 for word in query_words if word in text)
                    
                    # Count phrase matches (weighted higher)
                    phrase_matches = sum(2 for phrase in key_phrases if phrase in text)
                    
                    # Boost if from verax_system module
                    module_boost = 1 if module == 'verax_system' else 0
                    
                    total_score = matches + phrase_matches + module_boost
                    
                    if total_score > 0:
                        matched_docs.append((total_score, doc['text']))
            
            search_time = time.time() - search_start
            print(f"   ✅ Keyword search completed in {search_time:.3f}s")
            print(f"   📊 Scanned {len(in_memory_docs)} docs, found {len(matched_docs)} matches")
            
            # Sort by relevance and return top 5 for better context
            matched_docs.sort(reverse=True, key=lambda x: x[0])
            contexts = [doc[1] for doc in matched_docs[:5]]
            
            if contexts:
                print(f"   ✅ Returning top {len(contexts)} most relevant documents")
                return contexts
            else:
                print("   ⚠️  No matching documents found")
                return ["I don't have specific documentation loaded for this topic yet."]
        else:
            print("   ⚠️  No documents in memory")
            return ["No documentation has been loaded yet. Please load documentation first."]
            
    except Exception as e:
        print(f"   ❌ Search error: {e}")
        return ["I encountered an error searching the documentation. Please try rephrasing your question."]

def generate_response_with_module_with_context(query: str, context: str, tenant_id: str = "default", conversation_history: list = None):
    """
    Generate a response with conversation context support.
    Returns dict with 'response' and 'module' keys.
    
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
        
        # Detect query type and check if complex
        if enhanced_features_available:
            query_type = detect_query_type(query)
            is_complex, subquestions = is_complex_query(query)
            
            print(f"   📊 Query type: {query_type}", flush=True)
            
            # If query is too complex, suggest breaking it down
            if is_complex and subquestions:
                print(f"   ⚠️  Complex query detected, suggesting breakdown", flush=True)
                return {
                    "module": "General",
                    "response": f"""Your question covers multiple topics. To give you the best answer, let's break it down:

{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(subquestions))}

Which would you like me to answer first? Or feel free to ask about a specific part.""",
                    "needs_clarification": True
                }
            
            # Combine conversation context with document context
            full_context = conversation_context + context if conversation_context else context
            
            # Get enhanced prompts based on query type
            system_prompt, user_prompt = get_enhanced_prompt(query, full_context, query_type)
        else:
            # Fallback to basic prompt with conversation context
            query_type = "general"
            max_context_chars = 5000
            if len(context) > max_context_chars:
                context = context[:max_context_chars] + "\n... (context truncated for performance)"
            
            system_prompt = """You are a helpful AI assistant for the Verax ERP helpdesk system. 

CRITICAL CONTEXT RULES:
1. Pay CLOSE attention to the Previous Conversation section
2. When the user says "this module", "this feature", "it", "that", or "the module" - they are referring to topics from the previous conversation
3. ALWAYS resolve pronouns using conversation history FIRST before answering
4. If user asks "Who uses this?" and previous conversation was about "Workflow Module", answer about Workflow Module
5. Stay on the SAME topic from previous conversation unless user explicitly changes topics

🚨 STRICT RESPONSE RULES - MUST FOLLOW:
1. ONLY use information from the provided Documentation Context below
2. DO NOT use your general knowledge or training data about ERP systems
3. DO NOT make assumptions or add information not in the context
4. If the context doesn't contain the answer, respond with: "I don't have this information in the current documentation. Please contact support or check the complete documentation."
5. Extract ALL relevant information from the context
6. For lists (modules, submodules, features), include EVERYTHING mentioned in the context
7. Use bullet points and clear formatting
8. DO NOT hallucinate or make up information
9. At the end, add: MODULE: [module name from context]"""
            
            user_prompt = f"""{conversation_context}Documentation Context:
{context}

User Question: {query}

INSTRUCTIONS:
- If the user question contains pronouns like "this", "it", "that", "the module", look at the Previous Conversation above to understand what they are referring to
- Answer STRICTLY using ONLY the information from the Documentation Context above
- DO NOT use any external knowledge or general ERP information
- If the answer is not in the context, clearly state: "I don't have this information in the current documentation."
- Include all relevant details found in the context"""

        print(f"   📏 Prompt size: {len(system_prompt) + len(user_prompt)} characters", flush=True)
        print(f"   ⏳ Calling OpenAI API ({GPT_MODEL})...", flush=True)
        
        # Call OpenAI ChatGPT API with optimized settings
        # Low temperature (0.2) for factual, context-based responses
        api_start = time.time()
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,  # Low temperature for strict, factual responses
            max_tokens=400,
            timeout=25
        )
        api_time = time.time() - api_start
        print(f"   ✅ OpenAI API responded in {api_time:.2f}s", flush=True)
        
        content = response.choices[0].message.content
        print(f"   📝 Received response: {len(content)} characters", flush=True)
        
        # Parse the response to extract module and answer
        print("   🔍 Parsing module and answer...", flush=True)
        module = "General"
        answer = content
        
        # Try to extract MODULE from response
        if "MODULE:" in content:
            try:
                lines = content.split('\n')
                for line in lines:
                    if "MODULE:" in line:
                        module = line.replace("MODULE:", "").strip()
                        # Remove module line from answer
                        answer = content.replace(line, "").strip()
                        break
                print(f"   ✅ Successfully parsed - Module: {module}", flush=True)
            except:
                print("   ⚠️  Could not parse module, using default", flush=True)
        
        # Save interaction to database for training (without conversation context to avoid duplication)
        if enhanced_features_available:
            try:
                db_manager.save_interaction(
                    tenant_id=tenant_id,
                    query=query,
                    response=answer,
                    module=module,
                    response_time=api_time
                )
                print(f"   💾 Interaction saved to database", flush=True)
            except Exception as db_error:
                print(f"   ⚠️  Could not save to database: {db_error}", flush=True)
        
        return {
            "module": module,
            "response": answer,
            "query_type": query_type if 'query_type' in locals() else "general"
        }
    except Exception as e:
        print(f"   ❌ Error generating response: {str(e)}")
        error_msg = f"Error generating response: {str(e)}. Please check your OPENAI_API_KEY in the .env file."
        return {
            "module": "General",
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


def embed_chunks(chunks: list, module: str, tenant_id: str, filename: str):
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
                    "module": module,
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
                    "module": module,
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
                    "module": module,
                    "tenant_id": tenant_id,
                    "filename": filename,
                    "chunk_id": i
                }
                in_memory_docs.append(doc)
            print(f"      ✅ Stored {len(chunks)} chunks in memory as fallback")
        except Exception as fallback_error:
            print(f"      ❌ Could not store documents: {fallback_error}")