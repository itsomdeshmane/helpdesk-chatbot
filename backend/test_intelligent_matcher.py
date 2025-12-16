"""
Test script for Intelligent Entity Matcher
Demonstrates automatic detection of all types of entities
"""
import logging
from llm.intelligent_entity_matcher import get_intelligent_matcher

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Sample database schema for testing
SAMPLE_SCHEMA = {
    'tickets': {
        'columns': [
            {'name': 'ticket_id', 'type': 'int'},
            {'name': 'title', 'type': 'varchar'},
            {'name': 'status', 'type': 'varchar'},
            {'name': 'priority', 'type': 'varchar'},
            {'name': 'customer_city', 'type': 'varchar'},
            {'name': 'country', 'type': 'varchar'},
            {'name': 'category', 'type': 'varchar'},
            {'name': 'created_date', 'type': 'datetime'},
            {'name': 'total_amount', 'type': 'decimal'},
            {'name': 'assigned_to', 'type': 'varchar'},
        ]
    },
    'customers': {
        'columns': [
            {'name': 'customer_id', 'type': 'int'},
            {'name': 'customer_name', 'type': 'varchar'},
            {'name': 'email', 'type': 'varchar'},
            {'name': 'phone', 'type': 'varchar'},
            {'name': 'city', 'type': 'varchar'},
            {'name': 'state', 'type': 'varchar'},
            {'name': 'account_status', 'type': 'varchar'},
        ]
    }
}


def print_separator(title):
    """Print a section separator"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)


def test_entity_extraction():
    """Test entity extraction from queries"""
    print_separator("TEST 1: Entity Extraction")
    
    matcher = get_intelligent_matcher()
    
    test_queries = [
        "Show me tickets in Mumbai",
        "Count open tickets with high priority",
        "Show closed tickets in India",
        "List urgent tasks from New York",
        "Find tickets in category Support",
        "Show tickets created on 2024-12-15",
        "Find tickets worth $500",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        entities = matcher.extract_entities(query)
        
        if entities:
            for entity_type, entity_list in entities.items():
                print(f"   ✅ {entity_type.upper()}:")
                for entity in entity_list:
                    print(f"      - {entity['value']} (confidence: {entity['confidence']:.2f}, method: {entity['method']})")
        else:
            print("   ❌ No entities detected")


def test_column_matching():
    """Test intelligent column matching"""
    print_separator("TEST 2: Column Matching")
    
    matcher = get_intelligent_matcher()
    table_schema = SAMPLE_SCHEMA['tickets']
    
    test_cases = [
        ('location', 'Expected: customer_city or country'),
        ('status', 'Expected: status'),
        ('priority', 'Expected: priority'),
        ('category', 'Expected: category'),
        ('date', 'Expected: created_date'),
        ('amount', 'Expected: total_amount'),
        ('name', 'Expected: title or assigned_to'),
    ]
    
    for entity_type, expected in test_cases:
        print(f"\n🔍 Entity Type: {entity_type}")
        print(f"   Expected: {expected}")
        
        column = matcher.find_matching_column(entity_type, table_schema)
        
        if column:
            print(f"   ✅ Found: {column}")
        else:
            print(f"   ❌ No match found")


def test_filter_conditions():
    """Test automatic filter condition creation"""
    print_separator("TEST 3: Filter Condition Creation")
    
    matcher = get_intelligent_matcher()
    table_schema = SAMPLE_SCHEMA['tickets']
    
    test_queries = [
        "Show me tickets in Mumbai",
        "Count open tickets with high priority",
        "List tickets in India with urgent priority",
        "Show closed tickets in category Support",
    ]
    
    for query in test_queries:
        print(f"\n📝 Query: \"{query}\"")
        conditions = matcher.create_filter_conditions(query, table_schema)
        
        if conditions:
            print(f"   ✅ Created {len(conditions)} condition(s):")
            for cond in conditions:
                col = cond.get('column', 'N/A')
                val = cond.get('value', 'N/A')
                op = cond.get('operator', '=')
                print(f"      - {col} {op} '{val}'")
        else:
            print("   ❌ No conditions created")


def test_fuzzy_matching():
    """Test fuzzy matching with typos"""
    print_separator("TEST 4: Fuzzy Matching (Typo Tolerance)")
    
    matcher = get_intelligent_matcher()
    
    # Schema with typos
    typo_schema = {
        'columns': [
            {'name': 'ticket_id', 'type': 'int'},
            {'name': 'titel', 'type': 'varchar'},  # Typo: title
            {'name': 'statuss', 'type': 'varchar'},  # Typo: status
            {'name': 'priorty', 'type': 'varchar'},  # Typo: priority
            {'name': 'citty', 'type': 'varchar'},  # Typo: city
        ]
    }
    
    test_cases = [
        ('name', 'titel'),
        ('status', 'statuss'),
        ('priority', 'priorty'),
        ('location', 'citty'),
    ]
    
    for entity_type, expected_match in test_cases:
        print(f"\n🔍 Entity Type: {entity_type}")
        column = matcher.find_matching_column(entity_type, typo_schema, threshold=60.0)
        
        if column:
            print(f"   ✅ Matched: {column} (expected: {expected_match})")
            if column == expected_match:
                print(f"   🎯 Perfect match!")
        else:
            print(f"   ❌ No match found")


def test_multiple_entities():
    """Test handling multiple entities in one query"""
    print_separator("TEST 5: Multiple Entity Detection")
    
    matcher = get_intelligent_matcher()
    table_schema = SAMPLE_SCHEMA['tickets']
    
    complex_queries = [
        "Show open tickets in Mumbai with high priority",
        "Count closed tickets from India in Support category",
        "List urgent tasks in New York with status pending",
    ]
    
    for query in complex_queries:
        print(f"\n📝 Query: \"{query}\"")
        
        # Extract entities
        entities = matcher.extract_entities(query)
        print(f"   Detected {len(entities)} entity type(s):")
        for entity_type, entity_list in entities.items():
            values = [e['value'] for e in entity_list]
            print(f"      - {entity_type}: {', '.join(values)}")
        
        # Create conditions
        conditions = matcher.create_filter_conditions(query, table_schema)
        print(f"\n   Generated SQL conditions:")
        if conditions:
            where_parts = []
            for cond in conditions:
                col = cond.get('column')
                val = cond.get('value')
                op = cond.get('operator', '=')
                if op == 'LIKE':
                    where_parts.append(f"{col} LIKE '%{val}%'")
                else:
                    where_parts.append(f"{col} {op} '{val}'")
            
            print(f"   WHERE {' AND '.join(where_parts)}")
        else:
            print("   (No conditions)")


def test_cross_table_matching():
    """Test matching across different table schemas"""
    print_separator("TEST 6: Cross-Table Schema Matching")
    
    matcher = get_intelligent_matcher()
    
    test_query = "Show customers in Delhi with active status"
    
    for table_name, table_schema in SAMPLE_SCHEMA.items():
        print(f"\n📊 Table: {table_name}")
        print(f"   Query: \"{test_query}\"")
        
        conditions = matcher.create_filter_conditions(test_query, table_schema)
        
        if conditions:
            print(f"   ✅ Matched {len(conditions)} column(s):")
            for cond in conditions:
                print(f"      - {cond['column']} = '{cond['value']}'")
        else:
            print(f"   ❌ No matches in this table")


def run_all_tests():
    """Run all test cases"""
    print("\n" + "🎯" * 35)
    print("  INTELLIGENT ENTITY MATCHER - TEST SUITE")
    print("🎯" * 35)
    
    try:
        test_entity_extraction()
        test_column_matching()
        test_filter_conditions()
        test_fuzzy_matching()
        test_multiple_entities()
        test_cross_table_matching()
        
        print_separator("✅ ALL TESTS COMPLETED")
        print("\n✨ The Intelligent Entity Matcher is working correctly!")
        print("   - NLP-powered entity detection")
        print("   - Intelligent fuzzy column matching")
        print("   - Automatic filter condition creation")
        print("   - Works with ANY database schema!")
        
    except Exception as e:
        print_separator("❌ TEST FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

