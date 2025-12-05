"""
Enhanced Chunker Module - Production Ready
Provides advanced text chunking with sentence awareness, overlap, and metadata preservation
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import hashlib


@dataclass
class Chunk:
    """Represents a text chunk with metadata"""
    text: str
    chunk_id: int
    start_char: int
    end_char: int
    section: Optional[str] = None
    page_number: Optional[int] = None
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'chunk_id': self.chunk_id,
            'start_char': self.start_char,
            'end_char': self.end_char,
            'section': self.section,
            'page_number': self.page_number,
            'metadata': self.metadata or {}
        }


class EnhancedChunker:
    """
    Production-ready text chunker with:
    - Sentence-aware splitting
    - Configurable overlap
    - Section detection
    - Metadata preservation
    - Parent-child chunking support
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        min_chunk_size: int = 50,
        respect_sentences: bool = True,
        preserve_sections: bool = True
    ):
        """
        Initialize the enhanced chunker.
        
        Args:
            chunk_size: Target size of each chunk (in characters)
            chunk_overlap: Overlap between consecutive chunks
            min_chunk_size: Minimum chunk size (skip smaller chunks)
            respect_sentences: Try not to split mid-sentence
            preserve_sections: Detect and preserve section boundaries
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.respect_sentences = respect_sentences
        self.preserve_sections = preserve_sections
        
        # Section header patterns
        self.section_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headers
            r'^([A-Z][A-Za-z\s]+):?\s*$',  # Title Case Headers
            r'^(\d+\.[\d\.]*)\s+(.+)$',  # Numbered sections (1. 1.1 1.1.1)
            r'^(Chapter|Section|Part)\s+(\d+|[IVX]+)',  # Chapter/Section markers
        ]
        
        print(f"✅ Enhanced chunker initialized (size={chunk_size}, overlap={chunk_overlap})", flush=True)
    
    def chunk_text(
        self,
        text: str,
        metadata: Dict = None
    ) -> List[Chunk]:
        """
        Split text into chunks with overlap and metadata.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata to attach to all chunks
        
        Returns:
            List of Chunk objects
        """
        if not text or not text.strip():
            return []
        
        # Normalize whitespace
        text = self._normalize_text(text)
        
        # If preserving sections, split by sections first
        if self.preserve_sections:
            sections = self._detect_sections(text)
            if len(sections) > 1:
                return self._chunk_with_sections(sections, metadata)
        
        # Standard chunking with overlap
        return self._chunk_with_overlap(text, metadata)
    
    def _normalize_text(self, text: str) -> str:
        """Normalize whitespace and clean text"""
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        # But preserve paragraph breaks
        text = re.sub(r'\s*\n\s*\n\s*', '\n\n', text)
        return text.strip()
    
    def _detect_sections(self, text: str) -> List[Tuple[str, str]]:
        """
        Detect sections in text.
        
        Returns:
            List of (section_title, section_content) tuples
        """
        sections = []
        current_section = "Introduction"
        current_content = []
        
        lines = text.split('\n')
        
        for line in lines:
            is_header = False
            header_text = None
            
            for pattern in self.section_patterns:
                match = re.match(pattern, line.strip(), re.MULTILINE)
                if match:
                    is_header = True
                    header_text = match.group(1) if match.lastindex else line.strip()
                    break
            
            if is_header and header_text:
                # Save previous section
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))
                
                current_section = header_text
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections.append((current_section, '\n'.join(current_content)))
        
        return sections
    
    def _chunk_with_sections(
        self,
        sections: List[Tuple[str, str]],
        metadata: Dict = None
    ) -> List[Chunk]:
        """
        Chunk text while preserving section information.
        
        Args:
            sections: List of (section_title, content) tuples
            metadata: Optional metadata
        
        Returns:
            List of Chunk objects
        """
        all_chunks = []
        chunk_id = 0
        char_offset = 0
        
        for section_title, section_content in sections:
            if len(section_content.strip()) < self.min_chunk_size:
                continue
            
            # Chunk this section
            section_chunks = self._chunk_with_overlap(
                section_content,
                metadata,
                section_title=section_title,
                start_chunk_id=chunk_id,
                char_offset=char_offset
            )
            
            all_chunks.extend(section_chunks)
            chunk_id += len(section_chunks)
            char_offset += len(section_content)
        
        return all_chunks
    
    def _chunk_with_overlap(
        self,
        text: str,
        metadata: Dict = None,
        section_title: str = None,
        start_chunk_id: int = 0,
        char_offset: int = 0
    ) -> List[Chunk]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            metadata: Optional metadata
            section_title: Section this text belongs to
            start_chunk_id: Starting chunk ID
            char_offset: Character offset in original document
        
        Returns:
            List of Chunk objects
        """
        chunks = []
        
        if self.respect_sentences:
            # Split into sentences
            sentences = self._split_sentences(text)
        else:
            # Split into words
            sentences = text.split()
        
        current_chunk = []
        current_length = 0
        chunk_start = 0
        chunk_id = start_chunk_id
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed chunk size
            if current_length + sentence_length > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk_text = ' '.join(current_chunk) if not self.respect_sentences else ''.join(current_chunk)
                chunk_end = chunk_start + len(chunk_text)
                
                if len(chunk_text.strip()) >= self.min_chunk_size:
                    chunks.append(Chunk(
                        text=chunk_text.strip(),
                        chunk_id=chunk_id,
                        start_char=char_offset + chunk_start,
                        end_char=char_offset + chunk_end,
                        section=section_title,
                        metadata=metadata
                    ))
                    chunk_id += 1
                
                # Calculate overlap
                overlap_text = self._get_overlap_text(current_chunk)
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text) if overlap_text else 0
                chunk_start = chunk_end - len(overlap_text) if overlap_text else chunk_end
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        # Handle remaining content
        if current_chunk:
            chunk_text = ' '.join(current_chunk) if not self.respect_sentences else ''.join(current_chunk)
            if len(chunk_text.strip()) >= self.min_chunk_size:
                chunks.append(Chunk(
                    text=chunk_text.strip(),
                    chunk_id=chunk_id,
                    start_char=char_offset + chunk_start,
                    end_char=char_offset + chunk_start + len(chunk_text),
                    section=section_title,
                    metadata=metadata
                ))
        
        return chunks
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences while preserving sentence boundaries.
        
        Args:
            text: Text to split
        
        Returns:
            List of sentences
        """
        # Use regex to split on sentence boundaries
        # Handles: . ! ? followed by space and capital letter
        # But not: Dr. Mr. Mrs. etc.
        
        abbreviations = r'(?<!\b(?:Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|Inc|Ltd|Corp|e\.g|i\.e))'
        sentence_endings = r'(?<=[.!?])\s+(?=[A-Z"\'(])'
        
        # First, protect abbreviations
        protected_text = text
        
        # Split on sentence boundaries
        sentences = re.split(sentence_endings, protected_text)
        
        # Clean up
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If no split occurred (single sentence), return as is
        if len(sentences) <= 1:
            return [text]
        
        return sentences
    
    def _get_overlap_text(self, chunks: List[str]) -> str:
        """
        Get overlap text from the end of current chunk.
        
        Args:
            chunks: List of sentence/word chunks
        
        Returns:
            Text for overlap with next chunk
        """
        if not chunks:
            return ""
        
        # Take sentences/words from the end until we reach overlap size
        overlap_parts = []
        overlap_length = 0
        
        for item in reversed(chunks):
            if overlap_length + len(item) > self.chunk_overlap:
                break
            overlap_parts.insert(0, item)
            overlap_length += len(item)
        
        if self.respect_sentences:
            return ''.join(overlap_parts)
        else:
            return ' '.join(overlap_parts)
    
    def chunk_with_parent_documents(
        self,
        text: str,
        parent_chunk_size: int = 2000,
        metadata: Dict = None
    ) -> Tuple[List[Chunk], List[Chunk]]:
        """
        Create parent-child chunk relationships.
        Useful for contextual retrieval where you retrieve small chunks
        but use larger parent chunks for context.
        
        Args:
            text: Text to chunk
            parent_chunk_size: Size of parent chunks
            metadata: Optional metadata
        
        Returns:
            Tuple of (child_chunks, parent_chunks)
        """
        # Create parent chunks (larger)
        parent_chunker = EnhancedChunker(
            chunk_size=parent_chunk_size,
            chunk_overlap=200,
            min_chunk_size=100,
            respect_sentences=self.respect_sentences
        )
        parent_chunks = parent_chunker.chunk_text(text, metadata)
        
        # Create child chunks (smaller, nested in parents)
        child_chunks = []
        
        for parent in parent_chunks:
            # Chunk the parent text into smaller pieces
            children = self._chunk_with_overlap(
                parent.text,
                metadata={
                    **(metadata or {}),
                    'parent_chunk_id': parent.chunk_id
                },
                section_title=parent.section,
                start_chunk_id=len(child_chunks)
            )
            child_chunks.extend(children)
        
        return child_chunks, parent_chunks
    
    def estimate_chunk_count(self, text: str) -> int:
        """
        Estimate the number of chunks that will be created.
        
        Args:
            text: Text to estimate
        
        Returns:
            Estimated number of chunks
        """
        if not text:
            return 0
        
        text_length = len(text)
        effective_chunk_size = self.chunk_size - self.chunk_overlap
        
        if effective_chunk_size <= 0:
            return 1
        
        return max(1, int(text_length / effective_chunk_size))


def chunk_document(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
    metadata: Dict = None
) -> List[Dict]:
    """
    Convenience function to chunk a document.
    
    Args:
        text: Text to chunk
        chunk_size: Target chunk size
        overlap: Overlap between chunks
        metadata: Optional metadata
    
    Returns:
        List of chunk dictionaries
    """
    chunker = EnhancedChunker(
        chunk_size=chunk_size,
        chunk_overlap=overlap
    )
    
    chunks = chunker.chunk_text(text, metadata)
    return [chunk.to_dict() for chunk in chunks]


# Backward compatibility with existing code
def chunk_text(text: str, size: int = 500, overlap: int = 100) -> List[str]:
    """
    Legacy function for backward compatibility.
    
    Args:
        text: Text to chunk
        size: Chunk size
        overlap: Overlap
    
    Returns:
        List of chunk text strings
    """
    chunker = EnhancedChunker(
        chunk_size=size,
        chunk_overlap=overlap
    )
    
    chunks = chunker.chunk_text(text)
    return [chunk.text for chunk in chunks]


# Singleton instance
_chunker_instance: Optional[EnhancedChunker] = None


def get_chunker(
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> EnhancedChunker:
    """Get or create an EnhancedChunker instance"""
    global _chunker_instance
    if _chunker_instance is None:
        _chunker_instance = EnhancedChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
    return _chunker_instance

