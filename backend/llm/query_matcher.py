"""
Query Matcher - Machine Learning Based Query Matching
Uses TF-IDF and Sentence Embeddings to match user queries with historical data
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder
import pickle
import os
from datetime import datetime, timedelta
import re

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️  sentence-transformers not installed. Semantic search will be unavailable.")


class QueryMatcher:
    """
    Machine Learning based query matcher
    Trains on historical queries to find similar questions and predict intent
    """
    
    def __init__(self, use_semantic=True):
        """
        Initialize the query matcher
        
        Args:
            use_semantic: Whether to use semantic embeddings (requires sentence-transformers)
        """
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.intent_classifier = None
        self.intent_encoder = None
        self.semantic_model = None
        self.semantic_embeddings = None
        
        self.training_queries = []
        self.training_intents = []
        self.training_modules = []
        self.training_responses = []
        
        self.is_trained = False
        self.last_training_time = None
        
        # Initialize semantic model if available
        if use_semantic and SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                print("🔄 Loading sentence-transformers model...")
                self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("✅ Semantic model loaded")
            except Exception as e:
                print(f"⚠️  Could not load semantic model: {e}")
                self.semantic_model = None
    
    def train(self, queries, intents=None, modules=None, responses=None):
        """
        Train the matcher on historical data
        
        Args:
            queries: List of user queries
            intents: List of query intents (optional)
            modules: List of modules (optional)
            responses: List of responses (optional)
        """
        print(f"\n🎓 Training Query Matcher on {len(queries)} queries...")
        
        if len(queries) == 0:
            print("⚠️  No training data provided")
            return False
        
        self.training_queries = queries
        self.training_intents = intents or []
        self.training_modules = modules or []
        self.training_responses = responses or []
        
        # Train TF-IDF vectorizer
        print("   Training TF-IDF vectorizer...")
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 3),
            stop_words='english',
            min_df=1,
            max_df=0.8
        )
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(queries)
        print(f"   ✓ TF-IDF matrix shape: {self.tfidf_matrix.shape}")
        
        # Train intent classifier if intents provided
        if intents and len(intents) == len(queries):
            print("   Training intent classifier...")
            self.intent_encoder = LabelEncoder()
            encoded_intents = self.intent_encoder.fit_transform(intents)
            
            self.intent_classifier = MultinomialNB()
            self.intent_classifier.fit(self.tfidf_matrix, encoded_intents)
            print(f"   ✓ Intent classifier trained ({len(set(intents))} classes)")
        
        # Generate semantic embeddings if model available
        if self.semantic_model:
            print("   Generating semantic embeddings...")
            self.semantic_embeddings = self.semantic_model.encode(
                queries,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            print(f"   ✓ Embeddings shape: {self.semantic_embeddings.shape}")
        
        self.is_trained = True
        self.last_training_time = datetime.now()
        print(f"✅ Training complete!\n")
        return True
    
    def find_similar_queries(self, query, top_k=5, method='tfidf'):
        """
        Find similar queries from training data
        
        Args:
            query: User query string
            top_k: Number of similar queries to return
            method: 'tfidf' or 'semantic'
        
        Returns:
            List of tuples: (similar_query, similarity_score, index)
        """
        if not self.is_trained:
            return []
        
        if method == 'semantic' and self.semantic_embeddings is not None:
            # Use semantic embeddings
            query_embedding = self.semantic_model.encode([query], convert_to_numpy=True)
            similarities = cosine_similarity(query_embedding, self.semantic_embeddings)[0]
        else:
            # Use TF-IDF
            query_vector = self.tfidf_vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
        
        # Get top K indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Minimum threshold
                results.append({
                    'query': self.training_queries[idx],
                    'similarity': float(similarities[idx]),
                    'index': int(idx),
                    'response': self.training_responses[idx] if idx < len(self.training_responses) else None,
                    'module': self.training_modules[idx] if idx < len(self.training_modules) else None
                })
        
        return results
    
    def predict_intent(self, query):
        """
        Predict the intent of a query
        
        Args:
            query: User query string
        
        Returns:
            dict: {'intent': str, 'confidence': float}
        """
        if not self.is_trained or not self.intent_classifier:
            return {'intent': 'unknown', 'confidence': 0.0}
        
        query_vector = self.tfidf_vectorizer.transform([query])
        
        # Predict intent
        intent_encoded = self.intent_classifier.predict(query_vector)[0]
        intent = self.intent_encoder.inverse_transform([intent_encoded])[0]
        
        # Get probability
        probabilities = self.intent_classifier.predict_proba(query_vector)[0]
        confidence = float(max(probabilities))
        
        return {
            'intent': intent,
            'confidence': confidence
        }
    
    def get_best_response(self, query, method='semantic', similarity_threshold=0.6):
        """
        Get the best response for a query based on historical data
        
        Args:
            query: User query string
            method: 'tfidf' or 'semantic'
            similarity_threshold: Minimum similarity to return a match
        
        Returns:
            dict: Best matching response with metadata
        """
        similar_queries = self.find_similar_queries(query, top_k=3, method=method)
        
        if not similar_queries:
            return None
        
        best_match = similar_queries[0]
        
        if best_match['similarity'] < similarity_threshold:
            return None
        
        return {
            'matched_query': best_match['query'],
            'response': best_match['response'],
            'similarity_score': best_match['similarity'],
            'module': best_match['module'],
            'confidence': 'high' if best_match['similarity'] > 0.8 else 'medium'
        }
    
    def save_model(self, filepath='models/query_matcher.pkl'):
        """Save trained model to disk"""
        if not self.is_trained:
            print("⚠️  Model not trained yet")
            return False
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Don't save the semantic model (too large), just the embeddings
        model_data = {
            'tfidf_vectorizer': self.tfidf_vectorizer,
            'tfidf_matrix': self.tfidf_matrix,
            'intent_classifier': self.intent_classifier,
            'intent_encoder': self.intent_encoder,
            'semantic_embeddings': self.semantic_embeddings,
            'training_queries': self.training_queries,
            'training_intents': self.training_intents,
            'training_modules': self.training_modules,
            'training_responses': self.training_responses,
            'last_training_time': self.last_training_time
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"✅ Model saved to {filepath}")
        return True
    
    def load_model(self, filepath='models/query_matcher.pkl'):
        """Load trained model from disk"""
        if not os.path.exists(filepath):
            print(f"⚠️  Model file not found: {filepath}")
            return False
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.tfidf_vectorizer = model_data['tfidf_vectorizer']
        self.tfidf_matrix = model_data['tfidf_matrix']
        self.intent_classifier = model_data['intent_classifier']
        self.intent_encoder = model_data['intent_encoder']
        self.semantic_embeddings = model_data['semantic_embeddings']
        self.training_queries = model_data['training_queries']
        self.training_intents = model_data['training_intents']
        self.training_modules = model_data['training_modules']
        self.training_responses = model_data['training_responses']
        self.last_training_time = model_data['last_training_time']
        
        self.is_trained = True
        
        # Reload semantic model if embeddings exist
        if self.semantic_embeddings is not None and SENTENCE_TRANSFORMERS_AVAILABLE:
            self.semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print(f"✅ Model loaded from {filepath}")
        print(f"   Training date: {self.last_training_time}")
        print(f"   Queries: {len(self.training_queries)}")
        return True
    
    def get_training_stats(self):
        """Get statistics about the trained model"""
        if not self.is_trained:
            return None
        
        return {
            'num_queries': len(self.training_queries),
            'vocabulary_size': len(self.tfidf_vectorizer.vocabulary_),
            'num_intents': len(set(self.training_intents)) if self.training_intents else 0,
            'has_semantic': self.semantic_embeddings is not None,
            'last_trained': self.last_training_time.isoformat() if self.last_training_time else None
        }


def train_from_database(tenant_id='default'):
    """
    Train the query matcher from database
    
    Args:
        tenant_id: Tenant ID to fetch queries for
    
    Returns:
        QueryMatcher: Trained matcher instance
    """
    from database.db_manager import db_manager
    
    print("\n📚 Loading training data from database...")
    
    # Fetch all queries
    try:
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                """SELECT query, response, module, created_at 
                   FROM chat_interactions 
                   WHERE tenant_id = %s 
                   AND CHAR_LENGTH(query) > 10
                   ORDER BY created_at DESC""",
                (tenant_id,)
            )
            results = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error fetching from database: {e}")
        return None
    
    if len(results) == 0:
        print("⚠️  No queries found in database")
        return None
    
    print(f"✅ Loaded {len(results)} queries from database")
    
    # Extract data
    queries = [row['query'] for row in results]
    responses = [row['response'] for row in results]
    modules = [row['module'] for row in results]
    
    # Detect intents (simple rule-based for now)
    from llm.clarity_detector import _detect_query_type
    intents = [_detect_query_type(q) for q in queries]
    
    # Train matcher
    matcher = QueryMatcher(use_semantic=SENTENCE_TRANSFORMERS_AVAILABLE)
    success = matcher.train(queries, intents, modules, responses)
    
    if success:
        # Save model
        model_path = os.path.join(
            os.path.dirname(__file__),
            '..',
            'models',
            'query_matcher.pkl'
        )
        matcher.save_model(model_path)
    
    return matcher


if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("🤖 Query Matcher - Training Module")
    print("="*80)
    
    matcher = train_from_database()
    
    if matcher:
        stats = matcher.get_training_stats()
        print(f"\n📊 Training Statistics:")
        print(f"   Queries: {stats['num_queries']}")
        print(f"   Vocabulary: {stats['vocabulary_size']} words")
        print(f"   Intents: {stats['num_intents']}")
        print(f"   Semantic Search: {'Yes' if stats['has_semantic'] else 'No'}")
        print(f"\n✅ Training complete!")









