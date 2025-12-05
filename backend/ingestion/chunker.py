from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
import os

# Initialize semantic chunker with OpenAI embeddings
_semantic_chunker = None

def get_semantic_chunker():
    """
    Get or initialize the semantic chunker.
    Uses OpenAI embeddings to split text based on semantic similarity.
    """
    global _semantic_chunker
    if _semantic_chunker is None:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        _semantic_chunker = SemanticChunker(
            embeddings,
            breakpoint_threshold_type="percentile",  # Uses percentile-based splitting
            breakpoint_threshold_amount=85  # Split at top 15% of semantic differences
        )
    return _semantic_chunker


def chunk_text(text, size=800, overlap=150):
    """
    Split text into semantically meaningful chunks.
    Uses semantic similarity to determine optimal splitting points.
    
    Args:
        text: The text to chunk
        size: Target chunk size (used as guidance, not strict limit)
        overlap: Not used with semantic chunker but kept for API compatibility
    
    Returns:
        List of text chunks split at semantic boundaries
    """
    if not text or not text.strip():
        return []
    
    # Limit text length to avoid memory issues
    max_chars = 200000  # ~200k characters
    if len(text) > max_chars:
        print(f"   Warning: Text too long ({len(text)} chars), truncating to {max_chars} chars")
        text = text[:max_chars]
    
    try:
        # Use semantic chunker for intelligent splitting
        chunker = get_semantic_chunker()
        chunks = chunker.create_documents([text])
        
        # Extract text content from Document objects
        chunk_texts = [doc.page_content for doc in chunks]
        
        # If chunks are too large, split them further
        final_chunks = []
        for chunk in chunk_texts:
            if len(chunk.split()) > size * 1.5:  # If chunk is too large
                # Fall back to splitting by sentences
                sentences = chunk.split('. ')
                current_chunk = []
                current_length = 0
                
                for sentence in sentences:
                    sentence_words = len(sentence.split())
                    if current_length + sentence_words > size and current_chunk:
                        final_chunks.append('. '.join(current_chunk) + '.')
                        current_chunk = [sentence]
                        current_length = sentence_words
                    else:
                        current_chunk.append(sentence)
                        current_length += sentence_words
                
                if current_chunk:
                    final_chunks.append('. '.join(current_chunk))
            else:
                final_chunks.append(chunk)
        
        return [c for c in final_chunks if c.strip()]
    
    except Exception as e:
        print(f"   Warning: Semantic chunking failed ({str(e)}), falling back to simple chunking")
        # Fallback to simple word-based chunking
        words = text.split()
        chunks = []
        i = 0
        
        while i < len(words):
            chunk = " ".join(words[i:i+size])
            if chunk:
                chunks.append(chunk)
            i += size - overlap
        
        return chunks