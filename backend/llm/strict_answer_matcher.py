"""
Strict Answer Matcher - Returns answers ONLY from database without LLM generation
This ensures no common knowledge or hallucinations are added
"""
import logging
from typing import Optional, Dict, List
from functools import lru_cache

logger = logging.getLogger(__name__)


class StrictAnswerMatcher:
    """
    Matches user queries with historical Q&A pairs from database
    Returns answers ONLY if high similarity match is found
    Does NOT use LLM to generate new answers
    """
    
    def __init__(self, tenant_id: str = "default"):
        self.tenant_id = tenant_id
        self.matcher = None
        self.is_initialized = False
    
    def _initialize(self):
        """Lazy initialization of the query matcher"""
        if self.is_initialized:
            return True
        
        try:
            from llm.query_matcher import QueryMatcher, SENTENCE_TRANSFORMERS_AVAILABLE
            from database.db_manager import db_manager
            
            logger.info(f"🔍 Initializing strict matcher for tenant: {self.tenant_id}")
            
            # Load training data from database
            with db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT query, response, module, created_at, helpful
                       FROM chat_interactions 
                       WHERE tenant_id = %s 
                       AND CHAR_LENGTH(query) > 10
                       AND CHAR_LENGTH(response) > 20
                       ORDER BY created_at DESC
                       LIMIT 5000""",  # Limit for performance
                    (self.tenant_id,)
                )
                results = cursor.fetchall()
            
            if len(results) == 0:
                logger.warning(f"⚠️  No historical data found for tenant: {self.tenant_id}")
                return False
            
            logger.info(f"✅ Loaded {len(results)} historical Q&A pairs")
            
            # Extract data
            queries = [row['query'] for row in results]
            responses = [row['response'] for row in results]
            modules = [row['module'] for row in results]
            
            # Filter out "don't have" responses - we don't want to match against failed responses
            filtered_data = []
            for i, response in enumerate(responses):
                if not any(phrase in response.lower() for phrase in [
                    "don't have information",
                    "no information",
                    "no documentation",
                    "not found",
                    "please check if the relevant document"
                ]):
                    filtered_data.append({
                        'query': queries[i],
                        'response': responses[i],
                        'module': modules[i]
                    })
            
            if len(filtered_data) == 0:
                logger.warning(f"⚠️  No valid responses found after filtering")
                return False
            
            logger.info(f"📊 Using {len(filtered_data)} valid Q&A pairs after filtering")
            
            # Train matcher
            self.matcher = QueryMatcher(use_semantic=SENTENCE_TRANSFORMERS_AVAILABLE)
            
            filtered_queries = [d['query'] for d in filtered_data]
            filtered_responses = [d['response'] for d in filtered_data]
            filtered_modules = [d['module'] for d in filtered_data]
            
            success = self.matcher.train(
                filtered_queries,
                intents=None,
                modules=filtered_modules,
                responses=filtered_responses
            )
            
            if success:
                self.is_initialized = True
                logger.info(f"✅ Strict matcher initialized successfully")
                return True
            else:
                logger.error(f"❌ Failed to train matcher")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error initializing strict matcher: {e}")
            return False
    
    def find_exact_match(
        self, 
        query: str,
        similarity_threshold: float = 0.85,
        use_semantic: bool = True
    ) -> Optional[Dict]:
        """
        Find exact or highly similar match from database
        
        Args:
            query: User query
            similarity_threshold: Minimum similarity (0.85 = 85% match)
            use_semantic: Use semantic search if available
        
        Returns:
            Dict with matched response or None if no match found
        """
        # Initialize if needed
        if not self._initialize():
            logger.warning("⚠️  Matcher not initialized, cannot find matches")
            return None
        
        try:
            # Use semantic search if available, otherwise TF-IDF
            method = 'semantic' if (use_semantic and self.matcher.semantic_model) else 'tfidf'
            
            logger.info(f"🔍 Searching for match using {method} (threshold: {similarity_threshold})")
            
            # Find best matching response
            best_match = self.matcher.get_best_response(
                query,
                method=method,
                similarity_threshold=similarity_threshold
            )
            
            if best_match:
                logger.info(f"✅ Found match! Similarity: {best_match['similarity_score']:.3f}")
                logger.info(f"   Matched query: {best_match['matched_query'][:80]}...")
                logger.info(f"   Module: {best_match['module']}")
                
                return {
                    'success': True,
                    'response': best_match['response'],
                    'matched_query': best_match['matched_query'],
                    'similarity_score': best_match['similarity_score'],
                    'module': best_match['module'],
                    'confidence': best_match['confidence'],
                    'source': 'database_exact_match'
                }
            else:
                logger.info(f"❌ No match found above threshold {similarity_threshold}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error finding match: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get statistics about the matcher"""
        if not self._initialize():
            return {'initialized': False}
        
        stats = self.matcher.get_training_stats()
        stats['initialized'] = True
        stats['tenant_id'] = self.tenant_id
        return stats


# Singleton cache for matchers per tenant
_matcher_cache = {}


def get_strict_matcher(tenant_id: str = "default") -> StrictAnswerMatcher:
    """
    Get or create strict matcher for a tenant
    
    Args:
        tenant_id: Tenant identifier
    
    Returns:
        StrictAnswerMatcher instance
    """
    if tenant_id not in _matcher_cache:
        _matcher_cache[tenant_id] = StrictAnswerMatcher(tenant_id)
    
    return _matcher_cache[tenant_id]


def clear_matcher_cache():
    """Clear the matcher cache (useful after new data is added)"""
    global _matcher_cache
    _matcher_cache = {}
    logger.info("🗑️  Matcher cache cleared")


if __name__ == "__main__":
    # Test the strict matcher
    print("="*80)
    print("🔒 Strict Answer Matcher - Test")
    print("="*80)
    
    matcher = get_strict_matcher("default")
    
    # Test queries
    test_queries = [
        "How do I reset my password?",
        "What is the capital of France?",  # Should NOT match (general knowledge)
        "How to create a new user?"
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        result = matcher.find_exact_match(query, similarity_threshold=0.75)
        
        if result:
            print(f"✅ Match found (similarity: {result['similarity_score']:.2f})")
            print(f"   Response: {result['response'][:200]}...")
        else:
            print(f"❌ No match found in database")
    
    # Show stats
    print(f"\n📊 Matcher Statistics:")
    stats = matcher.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

