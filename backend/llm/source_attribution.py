"""
Source Attribution Module - Production Ready
Provides citation and source tracking for answers
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
import hashlib


@dataclass
class Source:
    """Represents a source document/section"""
    filename: str
    section: Optional[str]
    chunk_id: Optional[int]
    relevance_score: float
    text_snippet: str
    page_number: Optional[int] = None
    module: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'filename': self.filename,
            'section': self.section,
            'chunk_id': self.chunk_id,
            'relevance_score': self.relevance_score,
            'text_snippet': self.text_snippet[:200] + '...' if len(self.text_snippet) > 200 else self.text_snippet,
            'page_number': self.page_number,
            'module': self.module
        }
    
    def to_citation(self) -> str:
        """Generate human-readable citation"""
        parts = [self.filename]
        
        if self.section:
            parts.append(f"Section: {self.section}")
        elif self.page_number:
            parts.append(f"Page {self.page_number}")
        
        return " - ".join(parts)


@dataclass
class AttributedResponse:
    """Response with source attribution"""
    response: str
    sources: List[Source]
    confidence_score: float
    citation_text: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'response': self.response,
            'sources': [s.to_dict() for s in self.sources],
            'confidence_score': self.confidence_score,
            'citation_text': self.citation_text
        }


class SourceAttributor:
    """
    Handles source attribution for generated responses.
    Tracks which documents were used to generate answers.
    """
    
    def __init__(self):
        """Initialize the source attributor"""
        self.min_snippet_length = 50
        self.max_sources = 5
    
    def extract_sources_from_search_results(
        self,
        search_results: List[Dict],
        query: str
    ) -> List[Source]:
        """
        Extract source information from search results.
        
        Args:
            search_results: List of search result dictionaries
            query: The user query (for relevance context)
        
        Returns:
            List of Source objects
        """
        sources = []
        seen_files = set()
        
        for result in search_results[:self.max_sources * 2]:  # Process more than needed
            filename = result.get('source', result.get('filename', 'Unknown'))
            
            # Skip duplicates from same file (keep highest scored)
            file_key = f"{filename}_{result.get('section', '')}"
            if file_key in seen_files:
                continue
            seen_files.add(file_key)
            
            source = Source(
                filename=filename,
                section=result.get('section', result.get('module')),
                chunk_id=result.get('chunk_id'),
                relevance_score=result.get('score', 0.0),
                text_snippet=result.get('text', '')[:500],
                page_number=result.get('page_number'),
                module=result.get('module', result.get('metadata', {}).get('module'))
            )
            
            sources.append(source)
        
        # Sort by relevance score
        sources.sort(key=lambda s: s.relevance_score, reverse=True)
        
        return sources[:self.max_sources]
    
    def create_attributed_response(
        self,
        response: str,
        sources: List[Source],
        include_inline_citations: bool = False
    ) -> AttributedResponse:
        """
        Create an attributed response with source citations.
        
        Args:
            response: The generated response text
            sources: List of Source objects
            include_inline_citations: Whether to add inline citation numbers
        
        Returns:
            AttributedResponse object
        """
        # Calculate overall confidence based on source relevance
        if sources:
            avg_relevance = sum(s.relevance_score for s in sources) / len(sources)
            confidence = min(avg_relevance, 1.0)
        else:
            confidence = 0.0
        
        # Generate citation text
        citation_text = self._generate_citation_text(sources)
        
        # Optionally add inline citations
        if include_inline_citations and sources:
            response = self._add_inline_citations(response, sources)
        
        return AttributedResponse(
            response=response,
            sources=sources,
            confidence_score=confidence,
            citation_text=citation_text
        )
    
    def _generate_citation_text(self, sources: List[Source]) -> str:
        """Generate formatted citation text"""
        if not sources:
            return ""
        
        # Group sources by filename
        by_file = {}
        for source in sources:
            if source.filename not in by_file:
                by_file[source.filename] = []
            by_file[source.filename].append(source)
        
        # Build citation string
        citations = []
        for filename, file_sources in by_file.items():
            sections = []
            for src in file_sources:
                if src.section:
                    sections.append(src.section)
                elif src.page_number:
                    sections.append(f"Page {src.page_number}")
            
            if sections:
                unique_sections = list(dict.fromkeys(sections))  # Preserve order, remove dupes
                citation = f"📄 {filename} ({', '.join(unique_sections[:3])})"
            else:
                citation = f"📄 {filename}"
            
            citations.append(citation)
        
        if len(citations) == 1:
            return f"\n\n**Source:** {citations[0]}"
        else:
            return f"\n\n**Sources:**\n" + "\n".join(f"• {c}" for c in citations)
    
    def _add_inline_citations(
        self,
        response: str,
        sources: List[Source]
    ) -> str:
        """Add inline citation numbers to response"""
        # Create source index map
        source_map = {i + 1: src for i, src in enumerate(sources)}
        
        # For each source, try to find relevant sentences and add citation
        sentences = re.split(r'(?<=[.!?])\s+', response)
        cited_sentences = []
        
        for sentence in sentences:
            citation_added = False
            sentence_lower = sentence.lower()
            
            for idx, source in source_map.items():
                # Check if sentence might be from this source
                source_keywords = set(re.findall(r'\b\w{4,}\b', source.text_snippet.lower()))
                sentence_keywords = set(re.findall(r'\b\w{4,}\b', sentence_lower))
                
                overlap = len(source_keywords & sentence_keywords)
                if overlap >= 3 and not citation_added:
                    # Add citation number
                    sentence = sentence.rstrip('.!?') + f" [{idx}]" + sentence[-1] if sentence[-1] in '.!?' else sentence + f" [{idx}]"
                    citation_added = True
                    break
            
            cited_sentences.append(sentence)
        
        return ' '.join(cited_sentences)
    
    def format_sources_for_display(
        self,
        sources: List[Source],
        format_type: str = "markdown"
    ) -> str:
        """
        Format sources for display in different formats.
        
        Args:
            sources: List of Source objects
            format_type: "markdown", "html", or "plain"
        
        Returns:
            Formatted source string
        """
        if not sources:
            return ""
        
        if format_type == "markdown":
            return self._format_markdown(sources)
        elif format_type == "html":
            return self._format_html(sources)
        else:
            return self._format_plain(sources)
    
    def _format_markdown(self, sources: List[Source]) -> str:
        """Format sources as markdown"""
        lines = ["", "---", "**📚 Sources:**", ""]
        
        for i, source in enumerate(sources, 1):
            relevance_bar = self._get_relevance_bar(source.relevance_score)
            line = f"{i}. **{source.filename}**"
            
            if source.section:
                line += f" - {source.section}"
            
            line += f" {relevance_bar}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _format_html(self, sources: List[Source]) -> str:
        """Format sources as HTML"""
        html = ['<div class="sources">', '<h4>📚 Sources</h4>', '<ul>']
        
        for source in sources:
            relevance_pct = int(source.relevance_score * 100)
            html.append(f'<li><strong>{source.filename}</strong>')
            if source.section:
                html.append(f' - {source.section}')
            html.append(f' <span class="relevance">({relevance_pct}% relevant)</span></li>')
        
        html.extend(['</ul>', '</div>'])
        return '\n'.join(html)
    
    def _format_plain(self, sources: List[Source]) -> str:
        """Format sources as plain text"""
        lines = ["", "Sources:", ""]
        
        for i, source in enumerate(sources, 1):
            line = f"  {i}. {source.filename}"
            if source.section:
                line += f" - {source.section}"
            lines.append(line)
        
        return "\n".join(lines)
    
    def _get_relevance_bar(self, score: float) -> str:
        """Generate a visual relevance indicator"""
        if score >= 0.8:
            return "🟢"  # High relevance
        elif score >= 0.5:
            return "🟡"  # Medium relevance
        else:
            return "🟠"  # Lower relevance


# Singleton instance
_source_attributor: Optional[SourceAttributor] = None


def get_source_attributor() -> SourceAttributor:
    """Get or create the singleton SourceAttributor instance"""
    global _source_attributor
    if _source_attributor is None:
        _source_attributor = SourceAttributor()
    return _source_attributor


def format_response_with_sources(
    response: str,
    search_results: List[Dict],
    query: str,
    include_citations: bool = True
) -> Dict:
    """
    Convenience function to format a response with source attribution.
    
    Args:
        response: The generated response
        search_results: Search results used to generate response
        query: User query
        include_citations: Whether to include source citations
    
    Returns:
        Dictionary with response, sources, and citation text
    """
    attributor = get_source_attributor()
    
    # Extract sources
    sources = attributor.extract_sources_from_search_results(search_results, query)
    
    # Create attributed response
    attributed = attributor.create_attributed_response(
        response,
        sources,
        include_inline_citations=False
    )
    
    result = {
        'response': attributed.response,
        'confidence': attributed.confidence_score,
    }
    
    if include_citations and sources:
        result['sources'] = [s.to_dict() for s in sources]
        result['citation_text'] = attributed.citation_text
    
    return result

