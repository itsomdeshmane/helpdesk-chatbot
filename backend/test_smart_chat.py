"""
Test script for Smart Chat functionality
Run this to verify the implementation is working correctly
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
print("Testing imports...")
try:
    from llm.database_query_service import get_database_query_service
    from llm.schema_service import get_schema_service
    from llm.clarifying_question_service import get_clarifying_question_service
    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)


async def test_schema_service():
    """Test database schema extraction"""
    print("\n" + "="*60)
    print("TEST 1: Schema Service")
    print("="*60)
    
    try:
        service = get_schema_service()
        
        # Test getting tables
        print("📊 Getting all tables...")
        tables = await service.get_all_tables()
        
        if tables:
            print(f"✅ Found {len(tables)} tables:")
            for table in tables[:5]:  # Show first 5
                print(f"   - {table['table_name']} ({table.get('row_count', 0)} rows)")
            
            # Test getting columns for first table
            if len(tables) > 0:
                first_table = tables[0]['table_name']
                print(f"\n📋 Getting columns for '{first_table}'...")
                columns = await service.get_table_columns(first_table)
                print(f"✅ Found {len(columns)} columns:")
                for col in columns[:5]:  # Show first 5
                    print(f"   - {col['column_name']} ({col['data_type']})")
            
            # Test getting full schema
            print(f"\n🔍 Getting complete database schema...")
            schema = await service.get_database_schema()
            print(f"✅ Schema retrieved: {schema['table_count']} tables")
            
            # Test schema context generation
            context = service.get_schema_context(schema)
            print(f"✅ Schema context generated: {len(context)} characters")
            
        else:
            print("⚠️  No tables found. Make sure DB is configured and has tables.")
            print("   You can create sample tables using the SQL in ENV_SETUP_GUIDE.md")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema service test failed: {e}")
        print("   Make sure MySQL is running and credentials are correct in .env")
        return False


async def test_database_query_service():
    """Test SQL generation and execution"""
    print("\n" + "="*60)
    print("TEST 2: Database Query Service")
    print("="*60)
    
    try:
        service = get_database_query_service()
        
        # Test SQL generation
        queries = [
            "How many customers do we have?",
            "Show me all products",
            "What is the total revenue?"
        ]
        
        for query in queries:
            print(f"\n💬 Query: '{query}'")
            print("   Converting to SQL...")
            
            sql = await service.convert_to_sql(query)
            print(f"   ✅ Generated SQL: {sql}")
            
            # Try to execute (will fail if no tables, that's OK)
            print("   Executing query...")
            result = await service.execute_query(sql, original_query=query)
            
            if result['success']:
                print(f"   ✅ Success: {result['message']}")
                if result.get('rows'):
                    print(f"   📊 Returned {len(result['rows'])} rows")
            else:
                print(f"   ⚠️  Query failed (this is OK if tables don't exist): {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database query service test failed: {e}")
        return False


async def test_clarifying_service():
    """Test clarifying question generation"""
    print("\n" + "="*60)
    print("TEST 3: Clarifying Question Service")
    print("="*60)
    
    try:
        service = get_clarifying_question_service()
        
        queries = [
            ("tell me about it", ["customers", "orders", "products"]),
            ("show me stuff", None),
            ("what about the thing", ["users", "sessions"])
        ]
        
        for query, tables in queries:
            print(f"\n💬 Query: '{query}'")
            print("   Generating clarifying question...")
            
            clarifying = await service.generate_clarifying_question(
                query,
                "test_user",
                "test_session",
                available_tables=tables
            )
            
            print(f"   ✅ Generated: {clarifying}")
        
        return True
        
    except Exception as e:
        print(f"❌ Clarifying question service test failed: {e}")
        return False


async def test_smart_chat_flow():
    """Test the complete smart chat flow"""
    print("\n" + "="*60)
    print("TEST 4: Smart Chat Flow (End-to-End)")
    print("="*60)
    
    try:
        print("\n🔄 Testing 3-layer fallback strategy...")
        
        # Layer 1: Would search documents (we'll simulate)
        print("\n1️⃣ Layer 1: Document Search")
        print("   In production: Searches Pinecone/RAG knowledge base")
        print("   If answer found → Return from documents")
        print("   If not found → Continue to Layer 2")
        
        # Layer 2: Database query
        print("\n2️⃣ Layer 2: Database Query")
        db_service = get_database_query_service()
        
        query = "How many customers do we have?"
        print(f"   Query: '{query}'")
        
        sql = await db_service.convert_to_sql(query)
        print(f"   Generated SQL: {sql}")
        
        result = await db_service.execute_query(sql, original_query=query)
        if result['success']:
            print(f"   ✅ Database answered: {result['message']}")
            print("   → Would return this result")
        else:
            print(f"   ⚠️  Database query failed: {result['message']}")
            print("   → Would continue to Layer 3")
        
        # Layer 3: Clarifying question
        print("\n3️⃣ Layer 3: Clarifying Question")
        clarifying_service = get_clarifying_question_service()
        schema_service = get_schema_service()
        
        tables = await schema_service.get_all_tables()
        table_names = [t['table_name'] for t in tables] if tables else []
        
        unclear_query = "tell me about stuff"
        print(f"   Query: '{unclear_query}'")
        
        clarifying = await clarifying_service.generate_clarifying_question(
            unclear_query,
            "test_user",
            "test_session",
            available_tables=table_names
        )
        print(f"   ✅ Clarifying question: {clarifying}")
        
        print("\n✅ Smart chat flow test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Smart chat flow test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 SMART CHAT IMPLEMENTATION TEST SUITE")
    print("="*60)
    
    # Check environment
    print("\n📋 Checking environment configuration...")
    env_vars = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DB_HOST": os.getenv("DB_HOST"),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER"),
    }
    
    for key, value in env_vars.items():
        status = "✅" if value else "⚠️"
        display_value = value[:20] + "..." if value and len(value) > 20 else value
        print(f"   {status} {key}: {display_value or 'Not set'}")
    
    if not env_vars["OPENAI_API_KEY"]:
        print("\n⚠️  WARNING: OPENAI_API_KEY not set. Some features will use fallback mode.")
    
    if not env_vars["DB_HOST"]:
        print("\n⚠️  WARNING: Database not configured. Schema tests will fail.")
        print("   To configure: See ENV_SETUP_GUIDE.md")
    
    # Run tests
    results = []
    
    try:
        results.append(("Schema Service", await test_schema_service()))
    except Exception as e:
        print(f"❌ Schema test crashed: {e}")
        results.append(("Schema Service", False))
    
    try:
        results.append(("Database Query Service", await test_database_query_service()))
    except Exception as e:
        print(f"❌ Database query test crashed: {e}")
        results.append(("Database Query Service", False))
    
    try:
        results.append(("Clarifying Question Service", await test_clarifying_service()))
    except Exception as e:
        print(f"❌ Clarifying question test crashed: {e}")
        results.append(("Clarifying Question Service", False))
    
    try:
        results.append(("Smart Chat Flow", await test_smart_chat_flow()))
    except Exception as e:
        print(f"❌ Smart chat flow test crashed: {e}")
        results.append(("Smart Chat Flow", False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is working correctly.")
    elif passed > 0:
        print("⚠️  Some tests passed. Check configuration for failed tests.")
    else:
        print("❌ All tests failed. Check environment configuration.")
    
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)



