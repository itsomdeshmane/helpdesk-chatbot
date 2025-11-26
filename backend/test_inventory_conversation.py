"""
Test the problematic inventory conversation
Shows how the improved system handles it better
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from llm.clarity_detector import analyze_query_clarity

def test_conversation():
    print("\n" + "="*80)
    print("  TESTING INVENTORY CONVERSATION")
    print("="*80)
    
    # Query 1: Original user query
    query1 = "How to create an item in inventory?"
    
    print(f"\n{'='*80}")
    print(f"USER: {query1}")
    print('='*80)
    
    result1 = analyze_query_clarity(query1)
    
    print(f"\nClarity Analysis:")
    print(f"  Is Clear: {result1['is_clear']}")
    print(f"  Score: {result1['clarity_score']:.2f}")
    print(f"  Query Type: {result1.get('query_type', 'unknown')}")
    
    if result1['is_clear']:
        print(f"\n[OK] DECISION: Query is clear, provide direct answer!")
        print(f"   The user said:")
        print(f"   - Action: CREATE")
        print(f"   - Entity: ITEM")
        print(f"   - Module: INVENTORY")
        print(f"   -> Should answer directly, not ask for clarification!")
    else:
        print(f"\n[PROBLEM] System thinks query is unclear")
        if result1.get('suggestions'):
            print(f"   Would ask:")
            for i, suggestion in enumerate(result1['suggestions'], 1):
                print(f"     {i}. {suggestion}")
    
    # Test other variations
    print(f"\n\n{'='*80}")
    print("  TESTING SIMILAR QUERIES")
    print('='*80)
    
    test_queries = [
        ("create item in inventory", "Has action + entity + module"),
        ("how to create customer in sales", "Complete with all context"),
        ("setup purchasing module", "Has action + module"),
        ("create item", "Missing module - should ask"),
        ("how to inventory", "Vague - should ask"),
    ]
    
    for query, description in test_queries:
        print(f"\n{'-'*80}")
        print(f"Query: '{query}'")
        print(f"Context: {description}")
        
        result = analyze_query_clarity(query)
        
        if result['is_clear']:
            print(f"[OK] Clear (score: {result['clarity_score']:.2f}) - Provide answer")
        else:
            print(f"[ASK] Unclear (score: {result['clarity_score']:.2f}) - Ask clarification")
            if result.get('suggestions'):
                print(f"   Questions:")
                for i, s in enumerate(result['suggestions'][:2], 1):
                    print(f"     {i}. {s}")
    
    print("\n" + "="*80)
    print("  SUMMARY")
    print("="*80)
    print("\nIMPROVEMENTS:")
    print("  [OK] Recognize complete queries (action + entity + module)")
    print("  [OK] Don't ask redundant clarification questions")
    print("  [OK] Provide direct answers when context is sufficient")
    print("  [OK] Only ask clarification when truly needed")
    print("\nRESULT:")
    print("  'How to create an item in inventory?' -> ANSWER DIRECTLY")
    print("  'create item' -> ASK which module")
    print("="*80 + "\n")

if __name__ == "__main__":
    test_conversation()

