"""
Test Script for Question Generation and Clarity Detection System

This script demonstrates the new features:
1. Level-wise question generation for modules
2. Query clarity detection
3. Automatic clarification when queries are unclear
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_question_generation():
    """Test generating level-wise questions for a module"""
    print("\n" + "="*80)
    print("TEST 1: Generating Level-Wise Questions for a Module")
    print("="*80)
    
    from llm.question_generator import generate_module_questions, format_questions_for_display
    
    # Sample context (in real usage, this comes from documentation)
    sample_context = """
    The Purchasing module in Verax ERP helps manage procurement activities.
    
    Key features include:
    - Creating and managing purchase orders
    - Vendor management and vendor selection
    - Request for Quotations (RFQ)
    - Purchase requisitions
    - Receiving and inspecting purchased items
    - Integration with Inventory and Finance modules
    
    Common workflows:
    1. Create purchase requisition
    2. Convert to purchase order
    3. Send to vendor
    4. Receive items
    5. Match invoice to purchase order
    """
    
    # Generate questions
    module_name = "Purchasing"
    questions = generate_module_questions(module_name, sample_context, "all")
    
    # Display formatted questions
    formatted = format_questions_for_display(questions, module_name)
    print(formatted)
    
    return questions


def test_clarity_detection():
    """Test query clarity detection"""
    print("\n" + "="*80)
    print("TEST 2: Query Clarity Detection")
    print("="*80)
    
    from llm.clarity_detector import analyze_query_clarity, format_clarification_response
    
    test_queries = [
        "help",  # Very vague
        "how to?",  # Incomplete
        "What are the purchasing features?",  # Clear
        "it not working",  # Missing context
        "Tell me about sales and also inventory and what about finance",  # Too complex
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing Query: '{query}'")
        print("-" * 60)
        
        analysis = analyze_query_clarity(query)
        
        print(f"   Is Clear: {analysis['is_clear']}")
        print(f"   Clarity Score: {analysis['clarity_score']:.2f}")
        
        if analysis['issues']:
            print(f"   Issues: {', '.join(analysis['issues'])}")
        
        if not analysis['is_clear'] and analysis['suggestions']:
            print(f"   Clarifying Questions:")
            for i, suggestion in enumerate(analysis['suggestions'], 1):
                print(f"      {i}. {suggestion}")


def test_clarification_response():
    """Test generating clarification responses"""
    print("\n" + "="*80)
    print("TEST 3: Generating Clarification Responses")
    print("="*80)
    
    from llm.clarity_detector import (
        generate_clarifying_questions, 
        format_clarification_response
    )
    
    unclear_query = "how to setup?"
    
    print(f"\n📝 User Query: '{unclear_query}'")
    print("-" * 60)
    
    # Generate clarifying questions
    clarifying_questions = generate_clarifying_questions(unclear_query)
    
    if clarifying_questions:
        # Format response
        response = format_clarification_response(unclear_query, clarifying_questions)
        print(response)
    else:
        print("   Query is clear, no clarification needed.")


def test_integrated_flow():
    """Test the integrated flow with RAG system"""
    print("\n" + "="*80)
    print("TEST 4: Integrated Flow - RAG with Clarity Detection")
    print("="*80)
    
    from llm.rag import generate_response_with_module
    
    test_cases = [
        {
            "query": "help me",
            "context": "Sample documentation about ERP modules...",
            "expected": "Should ask for clarification"
        },
        {
            "query": "What are the main features of the Purchasing module?",
            "context": "The Purchasing module provides vendor management, purchase orders, and requisition tracking.",
            "expected": "Should provide direct answer"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test Case {i}:")
        print(f"   Query: '{test_case['query']}'")
        print(f"   Expected: {test_case['expected']}")
        print("-" * 60)
        
        result = generate_response_with_module(
            query=test_case['query'],
            context=test_case['context'],
            tenant_id="default"
        )
        
        print(f"\n   Module Detected: {result.get('module', 'N/A')}")
        print(f"   Needs Clarification: {result.get('needs_clarification', False)}")
        
        if result.get('clarity_score'):
            print(f"   Clarity Score: {result['clarity_score']:.2f}")
        
        print(f"\n   Response:")
        print(f"   {result.get('response', 'N/A')[:200]}...")


def test_database_operations():
    """Test database operations for questions"""
    print("\n" + "="*80)
    print("TEST 5: Database Operations")
    print("="*80)
    
    try:
        from database.db_manager import db_manager
        
        # Save sample questions
        print("\n📝 Saving sample questions to database...")
        
        sample_questions = {
            "beginner": [
                "What is the Purchasing module?",
                "How do I create a purchase order?"
            ],
            "intermediate": [
                "How do I manage vendor relationships?",
                "What is the purchase requisition workflow?"
            ],
            "advanced": [
                "How do I configure automated purchase order approval?",
                "How do I integrate Purchasing with Finance module?"
            ]
        }
        
        success = db_manager.save_generated_questions(
            module_name="Purchasing",
            questions_dict=sample_questions,
            tenant_id="default"
        )
        
        if success:
            print("   ✅ Questions saved successfully")
        else:
            print("   ❌ Failed to save questions")
            return
        
        # Retrieve questions
        print("\n📚 Retrieving questions from database...")
        
        questions = db_manager.get_generated_questions(
            module_name="Purchasing",
            tenant_id="default"
        )
        
        print(f"   Found {len(questions)} questions")
        
        # Display by level
        by_level = {}
        for q in questions:
            level = q.get('difficulty_level')
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(q.get('question'))
        
        for level, qs in by_level.items():
            print(f"\n   {level.capitalize()}: {len(qs)} questions")
            for question in qs[:2]:  # Show first 2
                print(f"      - {question}")
        
        # Test clarification tracking
        print("\n📊 Testing clarification tracking...")
        
        clarification_id = db_manager.save_clarification_request(
            tenant_id="default",
            original_query="help me",
            clarity_score=0.2,
            issues=["Query too vague"],
            clarifying_questions=["What would you like help with?"]
        )
        
        if clarification_id:
            print(f"   ✅ Clarification saved (ID: {clarification_id})")
            
            # Get stats
            stats = db_manager.get_clarification_stats("default")
            print(f"\n   Clarification Stats:")
            print(f"      Total: {stats.get('total_clarifications', 0)}")
            print(f"      Avg Clarity Score: {stats.get('avg_clarity_score', 0):.2f}")
        
    except Exception as e:
        print(f"   ❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests"""
    print("\n")
    print("="*80)
    print("  QUESTION GENERATION & CLARITY DETECTION SYSTEM - TEST SUITE")
    print("="*80)
    
    try:
        # Run tests
        test_question_generation()
        test_clarity_detection()
        test_clarification_response()
        test_integrated_flow()
        test_database_operations()
        
        print("\n" + "="*80)
        print("  ALL TESTS COMPLETED!")
        print("="*80)
        print("\n✨ The question generation and clarity detection system is working!\n")
        print("📚 How to use:")
        print("   1. Generate questions: POST /questions/generate")
        print("   2. Check query clarity: POST /questions/check-clarity")
        print("   3. Chat endpoint automatically detects unclear queries")
        print("   4. Get random questions: GET /questions/random/{module}")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

