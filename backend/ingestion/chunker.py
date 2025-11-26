def chunk_text(text, size=800, overlap=150):
    """
    Split text into overlapping chunks.
    Optimized for performance.
    """
    if not text or not text.strip():
        return []
    
    words = text.split()
    
    # Limit total words to avoid memory issues
    max_words = 50000  # ~200k characters
    if len(words) > max_words:
        print(f"   Warning: Text too long ({len(words)} words), truncating to {max_words} words")
        words = words[:max_words]
    
    chunks = []
    i = 0
    
    while i < len(words):
        chunk = " ".join(words[i:i+size])
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)
        i += size - overlap
    
    return chunks