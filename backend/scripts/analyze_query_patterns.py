"""
Analyze User Query Patterns from Database
Extracts keywords, patterns, and provides training algorithm recommendations
"""
import sys
import os
from collections import Counter, defaultdict
from datetime import datetime
import re
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager


class QueryPatternAnalyzer:
    """Analyze user queries and extract patterns for training"""
    
    def __init__(self):
        self.queries = []
        self.keywords = Counter()
        self.bigrams = Counter()
        self.trigrams = Counter()
        self.query_types = Counter()
        self.entities_mentioned = Counter()
        self.modules = Counter()
        
        # Common stop words to filter out
        self.stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'could', 'may', 'might', 'must', 'can', 'i', 'you', 'we', 'they',
            'this', 'that', 'these', 'those', 'it', 'its', 'to', 'from', 'in',
            'on', 'at', 'by', 'for', 'with', 'about', 'as', 'of', 'and', 'or',
            'but', 'if', 'then', 'than', 'so', 'my', 'your', 'our', 'their'
        }
        
        # Action verbs for intent classification
        self.action_verbs = {
            'create': ['create', 'add', 'new', 'make', 'insert', 'setup', 'configure'],
            'read': ['view', 'see', 'show', 'display', 'find', 'search', 'get', 'list'],
            'update': ['update', 'edit', 'modify', 'change', 'alter', 'revise'],
            'delete': ['delete', 'remove', 'cancel', 'deactivate'],
            'help': ['how', 'what', 'why', 'when', 'where', 'help', 'explain', 'tell']
        }
    
    def fetch_all_queries(self, tenant_id='default'):
        """Fetch all queries from the database"""
        print("\n📊 Fetching queries from database...")
        
        try:
            with db_manager.get_connection() as conn:
                cursor = conn.execute(
                    """SELECT query, module, created_at 
                       FROM chat_interactions 
                       WHERE tenant_id = %s 
                       ORDER BY created_at DESC""",
                    (tenant_id,)
                )
                results = cursor.fetchall()
                
                self.queries = results
                print(f"✅ Fetched {len(self.queries)} queries")
                return results
        except Exception as e:
            print(f"❌ Error fetching queries: {e}")
            return []
    
    def extract_keywords(self, text):
        """Extract keywords from text (single words)"""
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter stop words and short words
        keywords = [w for w in words if w not in self.stop_words and len(w) > 2]
        
        return keywords
    
    def extract_ngrams(self, text, n=2):
        """Extract n-grams from text"""
        words = self.extract_keywords(text)
        
        if len(words) < n:
            return []
        
        ngrams = []
        for i in range(len(words) - n + 1):
            ngrams.append(' '.join(words[i:i+n]))
        
        return ngrams
    
    def detect_query_intent(self, query):
        """Detect the intent of the query"""
        query_lower = query.lower()
        
        # Check for action verbs
        for action, verbs in self.action_verbs.items():
            for verb in verbs:
                if verb in query_lower:
                    return action
        
        # Default to 'help' if no specific action detected
        return 'general'
    
    def detect_entities(self, query):
        """Detect ERP entities mentioned in query"""
        entities = db_manager.get_erp_entities()
        query_lower = query.lower()
        
        mentioned = []
        for entity_key, entity_name in entities.items():
            if entity_key in query_lower:
                mentioned.append(entity_key)
        
        return mentioned
    
    def analyze_all_queries(self):
        """Analyze all queries and extract patterns"""
        print("\n🔍 Analyzing query patterns...")
        
        for row in self.queries:
            query = row['query']
            module = row['module']
            
            # Extract keywords
            keywords = self.extract_keywords(query)
            self.keywords.update(keywords)
            
            # Extract bigrams
            bigrams = self.extract_ngrams(query, n=2)
            self.bigrams.update(bigrams)
            
            # Extract trigrams
            trigrams = self.extract_ngrams(query, n=3)
            self.trigrams.update(trigrams)
            
            # Detect intent
            intent = self.detect_query_intent(query)
            self.query_types[intent] += 1
            
            # Detect entities
            entities = self.detect_entities(query)
            self.entities_mentioned.update(entities)
            
            # Count modules
            if module:
                self.modules[module] += 1
        
        print(f"✅ Analysis complete!")
        print(f"   - Total unique keywords: {len(self.keywords)}")
        print(f"   - Total unique bigrams: {len(self.bigrams)}")
        print(f"   - Total unique trigrams: {len(self.trigrams)}")
    
    def print_statistics(self):
        """Print comprehensive statistics"""
        print("\n" + "="*80)
        print("📈 QUERY PATTERN ANALYSIS REPORT")
        print("="*80)
        
        # Total queries
        print(f"\n📊 Total Queries Analyzed: {len(self.queries)}")
        
        # Top keywords
        print("\n🔑 Top 20 Keywords Used by Users:")
        print("-" * 60)
        for keyword, count in self.keywords.most_common(20):
            print(f"   {keyword:20s} - {count:4d} times")
        
        # Top bigrams (2-word phrases)
        print("\n🔗 Top 15 Two-Word Phrases:")
        print("-" * 60)
        for bigram, count in self.bigrams.most_common(15):
            print(f"   {bigram:30s} - {count:4d} times")
        
        # Top trigrams (3-word phrases)
        print("\n🔗 Top 10 Three-Word Phrases:")
        print("-" * 60)
        for trigram, count in self.trigrams.most_common(10):
            print(f"   {trigram:40s} - {count:4d} times")
        
        # Query intents
        print("\n🎯 Query Intent Distribution:")
        print("-" * 60)
        for intent, count in self.query_types.most_common():
            percentage = (count / len(self.queries)) * 100
            print(f"   {intent:15s} - {count:4d} queries ({percentage:5.1f}%)")
        
        # Entities mentioned
        print("\n🏢 Most Referenced ERP Entities:")
        print("-" * 60)
        for entity, count in self.entities_mentioned.most_common(15):
            print(f"   {entity:20s} - {count:4d} times")
        
        # Modules
        print("\n📦 Most Queried Modules:")
        print("-" * 60)
        for module, count in self.modules.most_common():
            percentage = (count / sum(self.modules.values())) * 100
            print(f"   {module:25s} - {count:4d} queries ({percentage:5.1f}%)")
    
    def export_patterns_to_json(self, filename='query_patterns_analysis.json'):
        """Export analysis results to JSON file"""
        print(f"\n💾 Exporting patterns to {filename}...")
        
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
        os.makedirs(output_dir, exist_ok=True)
        
        filepath = os.path.join(output_dir, filename)
        
        data = {
            'metadata': {
                'total_queries': len(self.queries),
                'analysis_date': datetime.now().isoformat(),
                'unique_keywords': len(self.keywords),
                'unique_bigrams': len(self.bigrams)
            },
            'top_keywords': dict(self.keywords.most_common(50)),
            'top_bigrams': dict(self.bigrams.most_common(30)),
            'top_trigrams': dict(self.trigrams.most_common(20)),
            'query_intents': dict(self.query_types),
            'entities_mentioned': dict(self.entities_mentioned),
            'modules': dict(self.modules)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported to {filepath}")
    
    def generate_training_recommendations(self):
        """Generate recommendations for training the system"""
        print("\n" + "="*80)
        print("🤖 TRAINING ALGORITHM RECOMMENDATIONS")
        print("="*80)
        
        print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    RECOMMENDED TRAINING APPROACH                           ║
╚════════════════════════════════════════════════════════════════════════════╝

Based on the analysis of your user queries, here are the recommended algorithms
and approaches for training your chatbot system:

┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. TF-IDF (Term Frequency-Inverse Document Frequency)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Identify important keywords in queries                            │
│  Algorithm: TF-IDF with scikit-learn                                        │
│  Use Case: Query classification and similarity matching                     │
│                                                                              │
│  Implementation:                                                             │
│    - Build TF-IDF vectors for all historical queries                        │
│    - Calculate cosine similarity for new queries                            │
│    - Match similar queries to retrieve best responses                       │
│                                                                              │
│  Complexity: O(n*m) where n=queries, m=vocabulary size                      │
│  Training Time: Fast (< 1 minute for 10K queries)                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. Intent Classification with Machine Learning                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Classify user intent (create, read, update, delete, help)        │
│  Algorithm: Naive Bayes or Logistic Regression                             │
│  Use Case: Route queries to appropriate handlers                            │
│                                                                              │
│  Implementation:                                                             │
│    - Label queries with intents (CRUD operations + help)                    │
│    - Train classifier on historical data                                    │
│    - Predict intent for new queries                                         │
│                                                                              │
│  Accuracy: 85-95% with sufficient training data                             │
│  Training Time: Fast (< 5 minutes)                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. Named Entity Recognition (NER) - Custom Model                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Extract ERP entities (item, customer, vendor, etc.)              │
│  Algorithm: spaCy NER or BERT-based NER                                    │
│  Use Case: Identify what entities user is asking about                      │
│                                                                              │
│  Implementation:                                                             │
│    - Use existing entity dictionary as training data                        │
│    - Train custom spaCy NER model with your entities                        │
│    - Extract entities from new queries in real-time                         │
│                                                                              │
│  Accuracy: 90-95% for known entities                                        │
│  Training Time: Medium (10-30 minutes)                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. Sentence Embeddings with Semantic Search                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Find semantically similar queries                                 │
│  Algorithm: sentence-transformers (SBERT)                                   │
│  Use Case: FAQ matching and semantic query understanding                    │
│                                                                              │
│  Implementation:                                                             │
│    - Generate embeddings for all historical queries                         │
│    - Store embeddings in vector database (Pinecone/FAISS)                   │
│    - For new query, find top-K similar historical queries                   │
│                                                                              │
│  Accuracy: 88-93% semantic similarity matching                              │
│  Training Time: Pre-trained model (no training needed)                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. N-gram Language Model for Auto-completion                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Suggest query completions as user types                          │
│  Algorithm: Trigram model with smoothing                                    │
│  Use Case: Help users formulate better queries                              │
│                                                                              │
│  Implementation:                                                             │
│    - Build trigram model from historical queries                            │
│    - Calculate probabilities for next word predictions                      │
│    - Suggest top-3 completions in real-time                                 │
│                                                                              │
│  Accuracy: Depends on training data coverage                                │
│  Training Time: Fast (< 2 minutes)                                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. Reinforcement Learning from User Feedback                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  Purpose: Improve responses based on user feedback                          │
│  Algorithm: Contextual Bandits or Q-Learning                                │
│  Use Case: Learn which responses users find helpful                         │
│                                                                              │
│  Implementation:                                                             │
│    - Track 'helpful' feedback for each response                             │
│    - Reward responses with positive feedback                                │
│    - Adjust response ranking over time                                       │
│                                                                              │
│  Improvement: Continuous learning from user interactions                    │
│  Training Time: Ongoing (updates with each interaction)                     │
└─────────────────────────────────────────────────────────────────────────────┘

╔════════════════════════════════════════════════════════════════════════════╗
║                      RECOMMENDED IMPLEMENTATION PLAN                        ║
╚════════════════════════════════════════════════════════════════════════════╝

Phase 1 (Immediate - 1-2 days):
  ✓ Implement TF-IDF for query similarity matching
  ✓ Add intent classification with Naive Bayes
  ✓ Build keyword extraction system

Phase 2 (Short-term - 1 week):
  ✓ Integrate sentence embeddings (SBERT) for semantic search
  ✓ Train custom NER model for entity extraction
  ✓ Create FAQ auto-matching system

Phase 3 (Medium-term - 2 weeks):
  ✓ Implement reinforcement learning from feedback
  ✓ Add query auto-completion with n-gram models
  ✓ Build analytics dashboard for pattern monitoring

Phase 4 (Long-term - ongoing):
  ✓ Continuous model retraining with new data
  ✓ A/B testing different response strategies
  ✓ Fine-tune models based on performance metrics

╔════════════════════════════════════════════════════════════════════════════╗
║                        KEY PERFORMANCE METRICS                             ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
        
        # Calculate some metrics
        total_queries = len(self.queries)
        avg_query_length = sum(len(q['query'].split()) for q in self.queries) / total_queries if total_queries > 0 else 0
        
        print(f"""
  📊 Current System Stats:
     • Total training queries available: {total_queries}
     • Average query length: {avg_query_length:.1f} words
     • Unique vocabulary size: {len(self.keywords)}
     • Query diversity score: {len(self.keywords) / total_queries:.2f}
     
  🎯 Target Metrics After Training:
     • Query classification accuracy: > 90%
     • Entity extraction accuracy: > 95%
     • Response relevance score: > 85%
     • Average response time: < 2 seconds
     • User satisfaction rate: > 80%
""")
        
        print("="*80 + "\n")


def main():
    """Main function to run the analysis"""
    print("\n" + "="*80)
    print("🚀 QUERY PATTERN ANALYZER - Training Data Extraction")
    print("="*80)
    
    analyzer = QueryPatternAnalyzer()
    
    # Step 1: Fetch all queries
    queries = analyzer.fetch_all_queries(tenant_id='default')
    
    if len(queries) == 0:
        print("\n⚠️  No queries found in database.")
        print("   Please ensure you have chat interactions logged.")
        return
    
    # Step 2: Analyze patterns
    analyzer.analyze_all_queries()
    
    # Step 3: Print statistics
    analyzer.print_statistics()
    
    # Step 4: Export to JSON
    analyzer.export_patterns_to_json()
    
    # Step 5: Generate training recommendations
    analyzer.generate_training_recommendations()
    
    print("✅ Analysis complete! Check the logs folder for exported data.\n")


if __name__ == "__main__":
    main()














