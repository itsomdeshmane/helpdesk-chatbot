"""
Test script for enhanced response formatting
"""
import requests
import json

API_URL = "http://localhost:8000"

test_queries = [
    {
        "query": "What are the different types of inventory in the ERP system?",
        "expected_type": "list",
        "description": "Should return a bulleted or numbered list"
    },
    {
        "query": "How do I configure the sales module?",
        "expected_type": "step-by-step",
        "description": "Should return step-by-step instructions"
    },
    {
        "query": "What is an ERP system?",
        "expected_type": "definition",
        "description": "Should return a clear definition with explanation"
    },
    {
        "query": "What's the difference between FIFO and LIFO?",
        "expected_type": "comparison",
        "description": "Should return a comparison format"
    },
    {
        "query": "I'm getting an error when creating invoice",
        "expected_type": "troubleshooting",
        "description": "Should return troubleshooting steps"
    }
]

def test_chat_endpoint():
    """Test the enhanced chat responses"""
    print("="*80)
    print("TESTING ENHANCED RESPONSE FORMATTING")
    print("="*80 + "\n")
    
    for i, test in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {test['expected_type'].upper()}")
        print(f"{'='*80}")
        print(f"Query: {test['query']}")
        print(f"Expected: {test['description']}")
        print("-"*80)
        
        try:
            response = requests.post(
                f"{API_URL}/chat/query",
                json={
                    "query": test['query'],
                    "tenant_id": "test"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"\nModule: {data.get('module', 'N/A')}")
                print(f"\nResponse:\n{data.get('response', 'No response')}")
                print("\n✅ Test passed")
            else:
                print(f"\n❌ Error: Status {response.status_code}")
                print(response.text)
        
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        input("\nPress Enter to continue to next test...")

def test_faq_endpoint():
    """Test the FAQ endpoint"""
    print("\n" + "="*80)
    print("TESTING FAQ ENDPOINT")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/analytics/faq?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            faqs = data.get('faqs', [])
            print(f"\n✅ Found {len(faqs)} FAQ questions")
            
            for i, faq in enumerate(faqs[:5], 1):
                print(f"\n{i}. Q: {faq['question']}")
                print(f"   A: {faq['answer'][:100]}...")
                print(f"   Module: {faq['module']}, Popularity: {faq['popularity']}")
        else:
            print(f"❌ Error: Status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

def test_stats_endpoint():
    """Test the stats endpoint"""
    print("\n" + "="*80)
    print("TESTING STATS ENDPOINT")
    print("="*80)
    
    try:
        response = requests.get(f"{API_URL}/analytics/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print(f"\n✅ System Statistics:")
            print(f"   Total Interactions: {stats.get('total_interactions', 0)}")
            print(f"   Total FAQs: {stats.get('total_faqs', 0)}")
            print(f"   Average Response Time: {stats.get('average_response_time', 0)}s")
            
            print(f"\n   Popular Modules:")
            for module in stats.get('popular_modules', []):
                print(f"   - {module['module']}: {module['count']} queries")
        else:
            print(f"❌ Error: Status {response.status_code}")
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("\nMake sure the backend is running on http://localhost:8000\n")
    input("Press Enter to start testing...")
    
    # Test chat responses
    test_chat_endpoint()
    
    # Test FAQ endpoint
    test_faq_endpoint()
    
    # Test stats endpoint
    test_stats_endpoint()
    
    print("\n" + "="*80)
    print("ALL TESTS COMPLETED")
    print("="*80)





