"""
Hybrid Search Module - Production Ready
Combines BM25 keyword search with vector semantic search using Reciprocal Rank Fusion (RRF)
"""

import hashlib
import pickle
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from rank_bm25 import BM25Okapi
import numpy as np
from functools import lru_cache
import re
import threading
from datetime import datetime, timedelta

# Thread-safe lock for BM25 index updates
_bm25_lock = threading.Lock()


@dataclass
class SearchResult:
    """Represents a single search result with metadata"""
    text: str
    score: float
    source: str
    section: Optional[str] = None
    chunk_id: Optional[int] = None
    search_type: str = "hybrid"  # "vector", "bm25", or "hybrid"
    metadata: Optional[Dict] = None


class HybridSearchEngine:
    """
    Production-ready Hybrid Search Engine combining:
    - BM25 (Best Match 25) for keyword/lexical search
    - Vector embeddings for semantic search
    - Reciprocal Rank Fusion (RRF) for combining results
    """
    
    def __init__(self, cache_dir: str = None):
        """Initialize the hybrid search engine"""
        self.bm25_index: Optional[BM25Okapi] = None
        self.document_store: List[Dict] = []
        self.tokenized_corpus: List[List[str]] = []
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "cache")
        self._ensure_cache_dir()
        
        # Stopwords for tokenization
        self.stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
            'dare', 'ought', 'used', 'it', 'its', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'we', 'they', 'what', 'which', 'who', 'whom',
            'where', 'when', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
            'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only',
            'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also'
        }
        
        print("✅ Hybrid Search Engine initialized", flush=True)
    
    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text for BM25 indexing
        - Lowercase
        - Remove special characters
        - Remove stopwords
        - Keep alphanumeric tokens of length > 2
        """
        if not text:
            return []
        
        # Lowercase and remove special characters
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split and filter
        tokens = text.split()
        tokens = [
            token for token in tokens 
            if len(token) > 2 and token not in self.stopwords and token.isalnum()
        ]
        
        return tokens
    
    def build_bm25_index(self, documents: List[Dict], tenant_id: str = "default"):
        """
        Build or rebuild BM25 index from documents
        
        Args:
            documents: List of document dicts with 'text', 'filename', 'module', etc.
            tenant_id: Tenant identifier for multi-tenant support
        """
        with _bm25_lock:
            print(f"   🔨 Building BM25 index for {len(documents)} documents...", flush=True)
            
            # Filter documents for tenant
            tenant_docs = [
                doc for doc in documents 
                if doc.get('tenant_id', 'default') == tenant_id
            ]
            
            if not tenant_docs:
                print(f"   ⚠️ No documents found for tenant: {tenant_id}", flush=True)
                return
            
            # Store documents
            self.document_store = tenant_docs
            
            # Tokenize corpus
            self.tokenized_corpus = [
                self.tokenize(doc.get('text', '')) 
                for doc in tenant_docs
            ]
            
            # Build BM25 index
            self.bm25_index = BM25Okapi(self.tokenized_corpus)
            
            # Cache the index
            self._save_index_cache(tenant_id)
            
            print(f"   ✅ BM25 index built with {len(tenant_docs)} documents", flush=True)
    
    def _save_index_cache(self, tenant_id: str):
        """Save BM25 index to cache file"""
        try:
            cache_file = os.path.join(self.cache_dir, f"bm25_index_{tenant_id}.pkl")
            cache_data = {
                'document_store': self.document_store,
                'tokenized_corpus': self.tokenized_corpus,
                'timestamp': datetime.now().isoformat()
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print(f"   💾 BM25 index cached for tenant: {tenant_id}", flush=True)
        except Exception as e:
            print(f"   ⚠️ Failed to cache BM25 index: {e}", flush=True)
    
    def _load_index_cache(self, tenant_id: str) -> bool:
        """Load BM25 index from cache file"""
        try:
            cache_file = os.path.join(self.cache_dir, f"bm25_index_{tenant_id}.pkl")
            if not os.path.exists(cache_file):
                return False
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            self.document_store = cache_data['document_store']
            self.tokenized_corpus = cache_data['tokenized_corpus']
            self.bm25_index = BM25Okapi(self.tokenized_corpus)
            
            print(f"   📂 BM25 index loaded from cache for tenant: {tenant_id}", flush=True)
            return True
        except Exception as e:
            print(f"   ⚠️ Failed to load BM25 cache: {e}", flush=True)
            return False
    
    def bm25_search(self, query: str, top_k: int = 10) -> List[SearchResult]:
        """
        Perform BM25 keyword search
        
        Args:
            query: Search query
            top_k: Number of results to return
        
        Returns:
            List of SearchResult objects
        """
        if not self.bm25_index or not self.document_store:
            return []
        
        # Tokenize query
        query_tokens = self.tokenize(query)
        
        if not query_tokens:
            return []
        
        # Get BM25 scores
        scores = self.bm25_index.get_scores(query_tokens)
        
        # Get top-k indices
        top_indices = np.argsort(scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                doc = self.document_store[idx]
                results.append(SearchResult(
                    text=doc.get('text', ''),
                    score=float(scores[idx]),
                    source=doc.get('filename', 'unknown'),
                    section=doc.get('section', doc.get('module', '')),
                    chunk_id=doc.get('chunk_id'),
                    search_type="bm25",
                    metadata={
                        'module': doc.get('module', ''),
                        'tenant_id': doc.get('tenant_id', 'default')
                    }
                ))
        
        return results
    
    def reciprocal_rank_fusion(
        self,
        vector_results: List[SearchResult],
        bm25_results: List[SearchResult],
        k: int = 60,
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """
        Combine vector and BM25 results using Reciprocal Rank Fusion (RRF)
        
        RRF Score = Σ (1 / (k + rank))
        
        Args:
            vector_results: Results from vector/semantic search
            bm25_results: Results from BM25 keyword search
            k: RRF constant (default 60, higher = more weight to lower ranks)
            alpha: Weight for vector results (1-alpha for BM25)
        
        Returns:
            Combined and re-ranked results
        """
        # Create score dictionaries using text hash as key
        rrf_scores: Dict[str, float] = {}
        result_map: Dict[str, SearchResult] = {}
        
        # Process vector results
        for rank, result in enumerate(vector_results, 1):
            text_hash = hashlib.md5(result.text.encode()).hexdigest()
            rrf_scores[text_hash] = alpha * (1.0 / (k + rank))
            result_map[text_hash] = result
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results, 1):
            text_hash = hashlib.md5(result.text.encode()).hexdigest()
            bm25_contribution = (1 - alpha) * (1.0 / (k + rank))
            
            if text_hash in rrf_scores:
                # Document found in both - boost score
                rrf_scores[text_hash] += bm25_contribution
                # Mark as hybrid
                if text_hash in result_map:
                    result_map[text_hash].search_type = "hybrid"
            else:
                rrf_scores[text_hash] = bm25_contribution
                result_map[text_hash] = result
        
        # Sort by RRF score
        sorted_hashes = sorted(rrf_scores.keys(), key=lambda h: rrf_scores[h], reverse=True)
        
        # Build final results
        final_results = []
        for text_hash in sorted_hashes:
            result = result_map[text_hash]
            result.score = rrf_scores[text_hash]
            final_results.append(result)
        
        return final_results
    
    def hybrid_search(
        self,
        query: str,
        vector_results: List[Dict],
        tenant_id: str = "default",
        top_k: int = 5,
        alpha: float = 0.5,
        rebuild_index: bool = False
    ) -> List[SearchResult]:
        """
        Perform hybrid search combining vector and BM25 results
        
        Args:
            query: Search query
            vector_results: Results from vector search (list of dicts with 'text', 'score', etc.)
            tenant_id: Tenant identifier
            top_k: Number of final results to return
            alpha: Weight for vector results (0.0-1.0)
            rebuild_index: Force rebuild BM25 index
        
        Returns:
            Combined and ranked SearchResult list
        """
        # Convert vector results to SearchResult objects
        vector_search_results = [
            SearchResult(
                text=r.get('text', ''),
                score=r.get('score', 0.0),
                source=r.get('source', r.get('filename', 'unknown')),
                section=r.get('section', r.get('module', '')),
                chunk_id=r.get('chunk_id'),
                search_type="vector",
                metadata=r.get('metadata', {})
            )
            for r in vector_results
        ]
        
        # Check if BM25 index needs to be loaded/built
        if rebuild_index or not self.bm25_index:
            if not self._load_index_cache(tenant_id):
                # No cache, need documents to build index
                # Return vector-only results
                return vector_search_results[:top_k]
        
        # Perform BM25 search
        bm25_results = self.bm25_search(query, top_k=top_k * 2)
        
        # If no BM25 results, return vector results
        if not bm25_results:
            return vector_search_results[:top_k]
        
        # Combine using RRF
        combined_results = self.reciprocal_rank_fusion(
            vector_search_results,
            bm25_results,
            alpha=alpha
        )
        
        return combined_results[:top_k]
    
    def update_index_with_document(self, document: Dict, tenant_id: str = "default"):
        """
        Incrementally add a document to the BM25 index
        
        Args:
            document: Document dict with 'text', 'filename', etc.
            tenant_id: Tenant identifier
        """
        with _bm25_lock:
            document['tenant_id'] = tenant_id
            self.document_store.append(document)
            
            tokens = self.tokenize(document.get('text', ''))
            self.tokenized_corpus.append(tokens)
            
            # Rebuild index with new document
            self.bm25_index = BM25Okapi(self.tokenized_corpus)
            
            # Update cache
            self._save_index_cache(tenant_id)
    
    def clear_index(self, tenant_id: str = "default"):
        """Clear the BM25 index for a tenant"""
        with _bm25_lock:
            self.document_store = []
            self.tokenized_corpus = []
            self.bm25_index = None
            
            # Remove cache file
            cache_file = os.path.join(self.cache_dir, f"bm25_index_{tenant_id}.pkl")
            if os.path.exists(cache_file):
                os.remove(cache_file)
            
            print(f"   🗑️ BM25 index cleared for tenant: {tenant_id}", flush=True)


# Singleton instance
_hybrid_search_engine: Optional[HybridSearchEngine] = None


def get_hybrid_search_engine() -> HybridSearchEngine:
    """Get or create the singleton HybridSearchEngine instance"""
    global _hybrid_search_engine
    if _hybrid_search_engine is None:
        _hybrid_search_engine = HybridSearchEngine()
    return _hybrid_search_engine

