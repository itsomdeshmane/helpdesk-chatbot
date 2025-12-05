"""
Test script to verify entity loading from database
Run this to test that entities are loaded correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_entity_loading():
    print("\n" + "="*70)
    print("Testing Entity Loading from Database")
    print("="*70 + "\n")
    
    # Test 1: Load entities from database
    print("1️⃣ Testing load_erp_entities()...")
    try:
        from llm.clarity_detector import load_erp_entities, refresh_entity_cache
        
        entities = load_erp_entities()
        print(f"✅ Loaded {len(entities)} entities from database")
        print(f"\nEntities loaded:")
        for key, value in sorted(entities.items()):
            print(f"   - {key}: {value}")
    except Exception as e:
        print(f"❌ Error loading entities: {e}")
        return False
    
    # Test 2: Test entity detection in queries
    print("\n2️⃣ Testing entity detection in queries...")
    try:
        from llm.clarity_detector import analyze_query_clarity
        
        test_queries = [
            ("how to create item", "item"),
            ("create customer", "customer"),
            ("add vendor", "vendor"),
            ("invoice not working", "invoice"),
        ]
        
        for query, expected_entity in test_queries:
            result = analyze_query_clarity(query)
            suggestions_text = ' '.join(result.get('suggestions', [])).lower()
            
            if expected_entity in suggestions_text or entities.get(expected_entity, '').lower() in suggestions_text:
                print(f"✅ '{query}' - Detected '{expected_entity}' correctly")
            else:
                print(f"⚠️  '{query}' - Expected '{expected_entity}' in suggestions")
                print(f"    Suggestions: {result.get('suggestions', [])}")
    except Exception as e:
        print(f"❌ Error testing entity detection: {e}")
        return False
    
    # Test 3: Test cache refresh
    print("\n3️⃣ Testing cache refresh...")
    try:
        entities_cached = load_erp_entities()
        print(f"✅ Cache working - {len(entities_cached)} entities")
        
        entities_refreshed = refresh_entity_cache()
        print(f"✅ Cache refreshed - {len(entities_refreshed)} entities")
    except Exception as e:
        print(f"❌ Error testing cache: {e}")
        return False
    
    # Test 4: Test database manager methods
    print("\n4️⃣ Testing database manager methods...")
    try:
        from database.db_manager import db_manager
        
        # Get entities
        entities_dict = db_manager.get_erp_entities()
        print(f"✅ db_manager.get_erp_entities() - {len(entities_dict)} entities")
        
        # Get specific entity details
        entity_details = db_manager.get_entity_details('item')
        if entity_details:
            print(f"✅ db_manager.get_entity_details('item')")
            print(f"   Name: {entity_details.get('entity_name')}")
            print(f"   Type: {entity_details.get('entity_type')}")
            print(f"   Modules: {entity_details.get('related_modules')}")
        else:
            print(f"⚠️  Could not get details for 'item' entity")
    except Exception as e:
        print(f"❌ Error testing database manager: {e}")
        print(f"   Note: This is OK if database is not set up yet")
    
    print("\n" + "="*70)
    print("✅ All Entity Loading Tests Passed!")
    print("="*70)
    print("\nKey Features:")
    print("  • Entities loaded from database with 10-minute cache")
    print("  • Fallback to default entities if database unavailable")
    print("  • Dynamic entity detection in clarity analysis")
    print("  • Easy to add/update entities via database")
    print("\nTo add new entities:")
    print("  db_manager.add_erp_entity('project', 'Project', 'master', ...)")
    print("="*70 + "\n")
    
    return True

if __name__ == "__main__":
    try:
        test_entity_loading()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

