"""
Test Hybrid System - Database + Documentation Search
Verify that source intelligence works correctly
"""
import asyncio
import sys
sys.path.append('.')

from llm.source_intelligence import get_source_intelligence

async def test_source_detection():
    """Test the source intelligence service"""
    source_intel = get_source_intelligence()
    
    print("=" * 60)
    print("HYBRID SYSTEM TEST - Source Intelligence")
    print("=" * 60)
    print()
    
    # Test queries
    test_cases = [
        # Database queries
        ("show me all vendors", "database"),
        ("how many purchase orders in January 2025?", "database"),
        ("total sales for Rollins Group", "database"),
        ("list products where price > 100", "database"),
        ("count of orders between jan-2025 and dec-2025", "database"),
        
        # Documentation queries
        ("how do I create a purchase order?", "documents"),
        ("what is the approval process?", "documents"),
        ("explain authentication", "documents"),
        ("steps to configure database", "documents"),
        ("tell me about the vendor registration workflow", "documents"),
        
        # Follow-up queries
        ("add city to this", "followup"),
        ("show me more details", "followup"),
        ("what about the same data for last month?", "followup"),
        
        # Ambiguous queries
        ("vendor", "ambiguous"),
        ("data", "ambiguous"),
        ("help", "ambiguous"),
    ]
    
    print("Testing Database Queries:")
    print("-" * 60)
    for query, expected_type in test_cases[:5]:
        result = source_intel.detect_source(query)
        status = "✅" if result["source"] == "database" else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Detected: {result['source']} (confidence: {result['confidence']:.2f})")
        print(f"   Reason: {result['reason']}")
        print()
    
    print("\nTesting Documentation Queries:")
    print("-" * 60)
    for query, expected_type in test_cases[5:10]:
        result = source_intel.detect_source(query)
        status = "✅" if result["source"] == "documents" else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Detected: {result['source']} (confidence: {result['confidence']:.2f})")
        print(f"   Reason: {result['reason']}")
        print()
    
    print("\nTesting Follow-up Detection:")
    print("-" * 60)
    # Simulate conversation history
    conv_history = [
        {"query": "show vendors", "module": "Database", "response": "Found 100 vendors"}
    ]
    
    for query, expected_type in test_cases[10:13]:
        result = source_intel.detect_source(query, conversation_history=conv_history)
        status = "✅" if result["is_followup"] else "❌"
        print(f"{status} Query: '{query}'")
        print(f"   Is Follow-up: {result['is_followup']}")
        print(f"   Detected: {result['source']}")
        print(f"   Reason: {result['reason']}")
        print()
    
    print("\nTesting Ambiguous Queries:")
    print("-" * 60)
    for query, expected_type in test_cases[13:]:
        result = source_intel.detect_source(query)
        status = "✅" if result["source"] == "both" else "⚠️"
        print(f"{status} Query: '{query}'")
        print(f"   Detected: {result['source']} (confidence: {result['confidence']:.2f})")
        print(f"   Reason: {result['reason']}")
        print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_source_detection())

