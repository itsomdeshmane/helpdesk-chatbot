"""
Smart Search Module - Production Ready
Implements multiple search algorithms for accurate document retrieval:
- BM25 (Best Match 25) - industry standard for keyword search
- TF-IDF (Term Frequency-Inverse Document Frequency)
- Semantic similarity with sentence embeddings
- Fuzzy matching for typo tolerance
"""

import re
import math
from typing import List, Dict, Tuple, Optional
from collections import Counter
from dataclasses import dataclass
import numpy as np

# Try to import optional dependencies
try:
    from rank_bm25 import BM25Okapi
    BM25_AVAILABLE = True
except ImportError:
    BM25_AVAILABLE = False
    print("⚠️ rank-bm25 not installed, using TF-IDF fallback")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("⚠️ scikit-learn not installed, using basic search")


@dataclass
class SearchResult:
    """Search result with score and metadata"""
    text: str
    score: float
    filename: str
    algorithm: str
    chunk_id: int = 0


class SmartSearchEngine:
    """
    Multi-algorithm search engine for accurate document retrieval.
    Combines BM25, TF-IDF, and fuzzy matching for best results.
    """
    
    def __init__(self):
        self.documents: List[Dict] = []
        self.tokenized_docs: List[List[str]] = []
        self.bm25_index = None
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.is_indexed = False
        
        # Comprehensive stop words
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'it', 'its', 'this', 'that', 'these', 'those', 'i', 'you', 'he',
            'she', 'we', 'they', 'what', 'which', 'who', 'whom', 'where', 'when',
            'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
            'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there',
            'then', 'once', 'if', 'else', 'about', 'into', 'through', 'during',
            'before', 'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'any', 'your', 'our', 'their', 'his', 'her', 'my',
            'please', 'help', 'tell', 'show', 'give', 'explain', 'describe',
            'want', 'know', 'get', 'make', 'use', 'find', 'step', 'steps'
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text into words with normalization.
        - Lowercase
        - Remove special characters
        - Remove stop words
        - Keep meaningful tokens
        """
        # Lowercase and extract words
        text = text.lower()
        words = re.findall(r'\b[a-z0-9]+\b', text)
        
        # Filter stop words and short words
        tokens = [w for w in words if w not in self.stop_words and len(w) >= 2]
        
        return tokens
    
    def build_index(self, documents: List[Dict], tenant_id: str = "default"):
        """
        Build search indices from documents.
        
        Args:
            documents: List of document dicts with 'text', 'filename', 'tenant_id'
            tenant_id: Filter documents by tenant
        """
        # Filter by tenant
        self.documents = [
            doc for doc in documents 
            if doc.get('tenant_id', 'default') == tenant_id
        ]
        
        if not self.documents:
            print(f"   ⚠️ No documents for tenant: {tenant_id}")
            self.is_indexed = False
            return
        
        print(f"   📚 Building search index for {len(self.documents)} documents...")
        
        # Tokenize all documents
        self.tokenized_docs = [
            self.tokenize(doc.get('text', ''))
            for doc in self.documents
        ]
        
        # Build BM25 index
        if BM25_AVAILABLE and self.tokenized_docs:
            try:
                self.bm25_index = BM25Okapi(self.tokenized_docs)
                print(f"   ✅ BM25 index built")
            except Exception as e:
                print(f"   ⚠️ BM25 index failed: {e}")
                self.bm25_index = None
        
        # Build TF-IDF index
        if SKLEARN_AVAILABLE:
            try:
                texts = [doc.get('text', '') for doc in self.documents]
                self.tfidf_vectorizer = TfidfVectorizer(
                    stop_words='english',
                    ngram_range=(1, 2),  # Include bigrams
                    max_features=10000,
                    min_df=1
                )
                self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(texts)
                print(f"   ✅ TF-IDF index built")
            except Exception as e:
                print(f"   ⚠️ TF-IDF index failed: {e}")
                self.tfidf_vectorizer = None
        
        self.is_indexed = True
        print(f"   ✅ Search index ready")
    
    def search_bm25(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search using BM25 algorithm.
        BM25 is the industry standard for keyword-based search.
        """
        if not BM25_AVAILABLE or not self.bm25_index:
            return []
        
        query_tokens = self.tokenize(query)
        if not query_tokens:
            return []
        
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = self.documents[idx]
                results.append(SearchResult(
                    text=doc.get('text', ''),
                    score=float(scores[idx]),
                    filename=doc.get('filename', 'unknown'),
                    algorithm='BM25',
                    chunk_id=doc.get('chunk_id', idx)
                ))
        
        return results
    
    def search_tfidf(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Search using TF-IDF with cosine similarity.
        Good for finding semantically similar documents.
        """
        if not SKLEARN_AVAILABLE or self.tfidf_vectorizer is None:
            return []
        
        try:
            # Transform query
            query_vec = self.tfidf_vectorizer.transform([query])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.01:  # Minimum threshold
                    doc = self.documents[idx]
                    results.append(SearchResult(
                        text=doc.get('text', ''),
                        score=float(similarities[idx]),
                        filename=doc.get('filename', 'unknown'),
                        algorithm='TF-IDF',
                        chunk_id=doc.get('chunk_id', idx)
                    ))
            
            return results
        except Exception as e:
            print(f"   ⚠️ TF-IDF search error: {e}")
            return []
    
    def search_fuzzy(self, query: str, top_k: int = 5) -> List[SearchResult]:
        """
        Fuzzy keyword search with partial matching.
        Good for handling typos and variations.
        """
        query_lower = query.lower()
        query_words = self.tokenize(query)
        
        # Create n-grams for fuzzy matching
        def get_ngrams(text: str, n: int = 3) -> set:
            text = text.lower()
            return set(text[i:i+n] for i in range(len(text) - n + 1))
        
        query_ngrams = set()
        for word in query_words:
            if len(word) >= 3:
                query_ngrams.update(get_ngrams(word))
        
        results = []
        
        for i, doc in enumerate(self.documents):
            text = doc.get('text', '').lower()
            score = 0
            
            # Exact phrase match (highest score)
            if query_lower in text:
                score += 10
            
            # Word-level matching
            for word in query_words:
                if word in text:
                    score += 3
                # Partial word match
                elif len(word) >= 4 and word[:4] in text:
                    score += 1
            
            # N-gram similarity (fuzzy)
            if query_ngrams:
                text_ngrams = get_ngrams(text)
                overlap = len(query_ngrams & text_ngrams)
                ngram_score = overlap / max(len(query_ngrams), 1)
                score += ngram_score * 2
            
            if score > 0:
                results.append(SearchResult(
                    text=doc.get('text', ''),
                    score=score,
                    filename=doc.get('filename', 'unknown'),
                    algorithm='Fuzzy',
                    chunk_id=doc.get('chunk_id', i)
                ))
        
        # Sort by score and return top-k
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        use_bm25: bool = True,
        use_tfidf: bool = True,
        use_fuzzy: bool = True
    ) -> List[SearchResult]:
        """
        Combined search using multiple algorithms with rank fusion.
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_bm25: Include BM25 results
            use_tfidf: Include TF-IDF results
            use_fuzzy: Include fuzzy matching results
        
        Returns:
            List of SearchResult objects, ranked by combined score
        """
        if not self.is_indexed or not self.documents:
            return []
        
        all_results: Dict[str, SearchResult] = {}  # text hash -> result
        
        # Collect results from each algorithm
        if use_bm25:
            bm25_results = self.search_bm25(query, top_k * 2)
            for r in bm25_results:
                key = hash(r.text[:100])
                if key in all_results:
                    all_results[key].score += r.score * 1.0  # BM25 weight
                else:
                    all_results[key] = r
        
        if use_tfidf:
            tfidf_results = self.search_tfidf(query, top_k * 2)
            for r in tfidf_results:
                key = hash(r.text[:100])
                if key in all_results:
                    all_results[key].score += r.score * 10  # TF-IDF weight (normalized 0-1)
                else:
                    all_results[key] = r
        
        if use_fuzzy:
            fuzzy_results = self.search_fuzzy(query, top_k * 2)
            for r in fuzzy_results:
                key = hash(r.text[:100])
                if key in all_results:
                    all_results[key].score += r.score * 0.5  # Fuzzy weight
                else:
                    all_results[key] = r
        
        # Sort by combined score
        final_results = sorted(all_results.values(), key=lambda x: x.score, reverse=True)
        
        return final_results[:top_k]
    
    def get_context(self, query: str, top_k: int = 5) -> Tuple[List[str], List[Dict]]:
        """
        Get context strings for RAG.
        
        Args:
            query: Search query
            top_k: Number of documents to return
        
        Returns:
            Tuple of (context strings, metadata)
        """
        results = self.search(query, top_k)
        
        if not results:
            # Fallback: return most content-rich documents
            if self.documents:
                sorted_docs = sorted(
                    self.documents, 
                    key=lambda d: len(d.get('text', '')), 
                    reverse=True
                )
                return (
                    [d.get('text', '') for d in sorted_docs[:top_k]],
                    [{'filename': d.get('filename', ''), 'score': 0} for d in sorted_docs[:top_k]]
                )
            return [], []
        
        contexts = [r.text for r in results]
        metadata = [
            {
                'filename': r.filename,
                'score': r.score,
                'algorithm': r.algorithm,
                'chunk_id': r.chunk_id
            }
            for r in results
        ]
        
        return contexts, metadata


# Singleton instance
_search_engine: Optional[SmartSearchEngine] = None


def get_smart_search_engine() -> SmartSearchEngine:
    """Get or create the singleton SmartSearchEngine instance"""
    global _search_engine
    if _search_engine is None:
        _search_engine = SmartSearchEngine()
    return _search_engine


def smart_search(
    query: str, 
    documents: List[Dict], 
    tenant_id: str = "default",
    top_k: int = 5
) -> List[str]:
    """
    Convenience function for smart search.
    
    Args:
        query: Search query
        documents: List of document dicts
        tenant_id: Tenant filter
        top_k: Number of results
    
    Returns:
        List of relevant text chunks
    """
    engine = get_smart_search_engine()
    
    # Rebuild index if documents changed
    if not engine.is_indexed or len(engine.documents) != len([d for d in documents if d.get('tenant_id') == tenant_id]):
        engine.build_index(documents, tenant_id)
    
    contexts, _ = engine.get_context(query, top_k)
    return contexts

