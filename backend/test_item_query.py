"""Quick test for 'how to create item' query"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.clarity_detector import analyze_query_clarity

def test_item_query():
    query = "how to create item"
    
    print("\n" + "="*70)
    print("Testing: 'how to create item'")
    print("="*70)
    
    result = analyze_query_clarity(query)
    
    print(f"\nQuery: '{query}'")
    print(f"Is Clear: {result['is_clear']}")
    print(f"Clarity Score: {result['clarity_score']:.2f}")
    print(f"Query Type: {result.get('query_type', 'unknown')}")
    
    if result.get('issues'):
        print(f"Issues: {', '.join(result['issues'])}")
    
    if result.get('suggestions'):
        print(f"\nClarifying Questions:")
        for i, suggestion in enumerate(result['suggestions'], 1):
            print(f"  {i}. {suggestion}")
    
    print("\n" + "="*70)
    
    # Verify improvement
    suggestions_text = ' '.join(result.get('suggestions', [])).lower()
    
    if 'item' in suggestions_text or 'items' in suggestions_text:
        print("[SUCCESS] Context maintained - 'item' mentioned in questions")
    else:
        print("[WARNING] Context may be lost - 'item' not in questions")
    
    if 'this topic' in suggestions_text:
        print("[WARNING] Generic 'this topic' used instead of specific entity")
    else:
        print("[SUCCESS] No generic 'this topic' - specific context used")
    
    print("="*70 + "\n")

if __name__ == "__main__":
    test_item_query()

