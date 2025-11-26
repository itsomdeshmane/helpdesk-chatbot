"""
Markdown-aware chunking that preserves document structure.
Splits on sections/headings while keeping related content together.
"""
import re

def chunk_markdown(text: str, max_chunk_size: int = 1000, overlap: int = 100):
    """
    Split markdown text into chunks while preserving structure.
    Keeps sections, lists, code blocks, and tables together.
    
    Args:
        text: Markdown content to chunk
        max_chunk_size: Maximum words per chunk (default 1000)
        overlap: Number of words to overlap between chunks (default 100)
    
    Returns:
        List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Split by major sections (## headings and above)
    # This regex splits on lines starting with ## or # but keeps the heading with its content
    section_pattern = r'(?=^#{1,2}\s+.+$)'
    sections = re.split(section_pattern, text, flags=re.MULTILINE)
    
    # Filter out empty sections
    sections = [s.strip() for s in sections if s.strip()]
    
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for section in sections:
        section_words = section.split()
        section_size = len(section_words)
        
        # If a single section is larger than max_chunk_size, split it intelligently
        if section_size > max_chunk_size:
            # If we have a current chunk, save it first
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_size = 0
            
            # Split large section by subsections (### headings)
            subsections = split_large_section(section, max_chunk_size, overlap)
            chunks.extend(subsections)
        
        # If adding this section would exceed max size, save current chunk and start new one
        elif current_size + section_size > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from previous chunk
            if overlap > 0:
                words = current_chunk.split()
                overlap_text = " ".join(words[-overlap:]) if len(words) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + section
                current_size = len(overlap_text.split()) + section_size
            else:
                current_chunk = section
                current_size = section_size
        
        # Add section to current chunk
        else:
            if current_chunk:
                current_chunk += "\n\n" + section
            else:
                current_chunk = section
            current_size += section_size
    
    # Add the last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def split_large_section(section: str, max_chunk_size: int, overlap: int):
    """
    Split a large section by subsections (###) and preserve structure.
    """
    # Try splitting by ### headings
    subsection_pattern = r'(?=^#{3,}\s+.+$)'
    subsections = re.split(subsection_pattern, section, flags=re.MULTILINE)
    subsections = [s.strip() for s in subsections if s.strip()]
    
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for subsection in subsections:
        words = subsection.split()
        subsection_size = len(words)
        
        # If subsection is still too large, split by paragraphs
        if subsection_size > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_size = 0
            
            # Split by paragraphs
            para_chunks = split_by_paragraphs(subsection, max_chunk_size, overlap)
            chunks.extend(para_chunks)
        
        # If adding would exceed max, save current and start new
        elif current_size + subsection_size > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Add overlap
            if overlap > 0:
                chunk_words = current_chunk.split()
                overlap_text = " ".join(chunk_words[-overlap:]) if len(chunk_words) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + subsection
                current_size = len(overlap_text.split()) + subsection_size
            else:
                current_chunk = subsection
                current_size = subsection_size
        
        # Add to current chunk
        else:
            if current_chunk:
                current_chunk += "\n\n" + subsection
            else:
                current_chunk = subsection
            current_size += subsection_size
    
    # Add last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def split_by_paragraphs(text: str, max_chunk_size: int, overlap: int):
    """
    Split text by paragraphs when sections are too large.
    Preserves code blocks and lists together.
    """
    # Split by double newlines (paragraphs) but keep code blocks together
    paragraphs = re.split(r'\n\n+', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    
    chunks = []
    current_chunk = ""
    current_size = 0
    
    for para in paragraphs:
        words = para.split()
        para_size = len(words)
        
        # If paragraph itself is too large, force split by words
        if para_size > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
                current_size = 0
            
            # Force word-based split
            i = 0
            while i < len(words):
                chunk_words = words[i:i + max_chunk_size]
                chunks.append(" ".join(chunk_words))
                i += max_chunk_size - overlap
        
        # If adding would exceed max, save and start new
        elif current_size + para_size > max_chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Add overlap
            if overlap > 0:
                chunk_words = current_chunk.split()
                overlap_text = " ".join(chunk_words[-overlap:]) if len(chunk_words) > overlap else current_chunk
                current_chunk = overlap_text + "\n\n" + para
                current_size = len(overlap_text.split()) + para_size
            else:
                current_chunk = para
                current_size = para_size
        
        # Add to current chunk
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para
            current_size += para_size
    
    # Add last chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

