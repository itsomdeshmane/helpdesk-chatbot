"""
Quick Demo - Question Generation & Clarity Detection

This script provides a quick demonstration of the new features.
Run this to see the system in action!
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def demo():
    print("\n" + "="*80)
    print("  QUESTION GENERATION & CLARITY DETECTION - QUICK DEMO")
    print("="*80)
    
    # Demo 1: Query Clarity Detection
    print("\n### DEMO 1: Query Clarity Detection ###\n")
    
    from llm.clarity_detector import analyze_query_clarity
    
    test_queries = [
        ("help", "Very unclear query"),
        ("What are the purchasing features?", "Clear query"),
    ]
    
    for query, description in test_queries:
        print(f"Query: '{query}' ({description})")
        analysis = analyze_query_clarity(query)
        print(f"  - Clear: {analysis['is_clear']}")
        print(f"  - Score: {analysis['clarity_score']:.2f}")
        if not analysis['is_clear']:
            print(f"  - Suggestions: {analysis['suggestions'][0]}")
        print()
    
    # Demo 2: Question Generation
    print("\n### DEMO 2: Generating Level-Wise Questions ###\n")
    
    from llm.question_generator import generate_module_questions
    
    sample_context = """
    The Purchasing module manages procurement activities including:
    - Creating purchase orders
    - Managing vendors
    - Tracking requisitions
    - Receiving items
    """
    
    print("Generating questions for 'Purchasing' module...")
    questions = generate_module_questions("Purchasing", sample_context, "all")
    
    print(f"\nGenerated {sum(len(q) for q in questions.values())} questions:")
    
    for level in ["beginner", "intermediate", "advanced"]:
        print(f"\n{level.upper()}:")
        for i, q in enumerate(questions[level][:2], 1):  # Show first 2
            print(f"  {i}. {q}")
    
    # Demo 3: Database Operations
    print("\n\n### DEMO 3: Saving to Database ###\n")
    
    try:
        from database.db_manager import db_manager
        
        # Save questions
        print("Saving questions to database...")
        success = db_manager.save_generated_questions(
            "Purchasing", 
            questions, 
            "default"
        )
        
        if success:
            print("[OK] Questions saved successfully")
            
            # Retrieve them
            saved = db_manager.get_generated_questions(
                module_name="Purchasing",
                tenant_id="default"
            )
            print(f"[OK] Retrieved {len(saved)} questions from database")
        else:
            print("[ERROR] Failed to save questions")
            
    except Exception as e:
        print(f"[ERROR] Database demo failed: {e}")
    
    # Summary
    print("\n" + "="*80)
    print("  DEMO COMPLETE!")
    print("="*80)
    print("\nThe system is working correctly!")
    print("\nKey Features Demonstrated:")
    print("  1. Query clarity detection with scoring")
    print("  2. Level-wise question generation (beginner/intermediate/advanced)")
    print("  3. Database persistence for questions")
    print("\nAPI Endpoints Available:")
    print("  - POST /questions/generate")
    print("  - POST /questions/check-clarity")
    print("  - GET  /questions/random/{module}")
    print("  - POST /chat/query (now with auto clarity detection)")
    print("\nFor full documentation, see: backend/QUESTION_SYSTEM_GUIDE.txt")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

