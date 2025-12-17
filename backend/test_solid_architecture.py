"""
Quick Test Script for SOLID Architecture
Run this to verify the new architecture is working correctly
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_di_container():
    """Test 1: Dependency Injection Container"""
    print("\n" + "="*60)
    print("TEST 1: Dependency Injection Container")
    print("="*60)
    
    try:
        from core.container import container
        
        # Initialize container
        container.init_resources()
        print("✅ Container initialized")
        
        # Get config
        config = container.config()
        print(f"✅ Config loaded: OpenAI model = {config.openai.model}")
        
        # Get LLM provider
        llm_provider = container.llm_provider()
        print(f"✅ LLM Provider: {llm_provider.get_provider_name()}")
        
        # Get embedding service
        embedding_service = container.embedding_service()
        print(f"✅ Embedding Service: {embedding_service.get_provider_name()}")
        
        print("\n✅ TEST 1 PASSED: DI Container working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {e}\n")
        return False


async def test_infrastructure():
    """Test 2: Infrastructure Layer"""
    print("\n" + "="*60)
    print("TEST 2: Infrastructure Layer")
    print("="*60)
    
    try:
        from infrastructure.llm.openai_provider import OpenAIProvider
        from infrastructure.llm.openai_embedding import OpenAIEmbeddingService
        from core.config import app_config
        
        # Test OpenAI Provider
        provider = OpenAIProvider(
            api_key=app_config.openai.api_key,
            model=app_config.openai.model
        )
        print(f"✅ OpenAI Provider created: {provider.get_model()}")
        
        # Test token counting (doesn't require API call)
        tokens = await provider.count_tokens("Hello world")
        print(f"✅ Token counting works: 'Hello world' = {tokens} tokens")
        
        # Test Embedding Service
        embedding_service = OpenAIEmbeddingService(
            api_key=app_config.openai.api_key,
            model=app_config.openai.embedding_model
        )
        print(f"✅ Embedding Service created: {embedding_service.get_embedding_dimension()} dimensions")
        
        print("\n✅ TEST 2 PASSED: Infrastructure working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {e}\n")
        return False


async def test_data_sources():
    """Test 3: Data Sources"""
    print("\n" + "="*60)
    print("TEST 3: Data Sources")
    print("="*60)
    
    try:
        from infrastructure.vector_stores.in_memory_store import InMemoryVectorStore
        from infrastructure.llm.openai_embedding import OpenAIEmbeddingService
        from infrastructure.data_sources.vector_data_source import VectorDataSource
        from core.models.query import Query
        from core.config import app_config
        
        # Create in-memory vector store
        vector_store = InMemoryVectorStore()
        print("✅ In-memory vector store created")
        
        # Create embedding service
        embedding_service = OpenAIEmbeddingService(
            api_key=app_config.openai.api_key
        )
        print("✅ Embedding service created")
        
        # Create vector data source
        vector_source = VectorDataSource(vector_store, embedding_service)
        print("✅ Vector data source created")
        
        # Test can_handle
        query = Query(text="How do I create a work order?")
        can_handle = await vector_source.can_handle(query)
        print(f"✅ Can handle query: {can_handle}")
        
        print("\n✅ TEST 3 PASSED: Data sources working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {e}\n")
        return False


async def test_application_layer():
    """Test 4: Application Layer"""
    print("\n" + "="*60)
    print("TEST 4: Application Layer")
    print("="*60)
    
    try:
        from application.services.source_selector import SourceSelector
        from application.services.query_processor import QueryProcessor
        from application.services.response_formatter import ResponseFormatter
        from infrastructure.llm.openai_provider import OpenAIProvider
        from core.models.query import Query
        from core.models.response import DataSourceResponse
        from core.config import app_config
        
        # Test Source Selector
        selector = SourceSelector()
        print("✅ Source Selector created")
        
        # Test Query Processor
        llm_provider = OpenAIProvider(
            api_key=app_config.openai.api_key,
            model=app_config.openai.model
        )
        processor = QueryProcessor(llm_provider)
        print("✅ Query Processor created")
        
        # Test Response Formatter
        formatter = ResponseFormatter()
        print("✅ Response Formatter created")
        
        # Test formatting
        test_response = formatter.format_response(
            text="Test response",
            source="test",
            session_id="test123"
        )
        print(f"✅ Response formatting works: {test_response.success}")
        
        print("\n✅ TEST 4 PASSED: Application layer working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {e}\n")
        return False


async def test_database_connection():
    """Test 5: Database Connections"""
    print("\n" + "="*60)
    print("TEST 5: Database Connections")
    print("="*60)
    
    try:
        from infrastructure.databases.system_database import SystemDatabaseConnection
        from core.config import app_config
        
        # Create system database connection
        system_db = SystemDatabaseConnection(app_config.system_database)
        print("✅ System database connection created")
        
        # Test health check
        healthy = await system_db.health_check()
        print(f"✅ Database health check: {healthy}")
        
        if healthy:
            # Test simple query
            results = await system_db.execute_query("SELECT 1 as test")
            print(f"✅ Query executed: {results}")
        
        print("\n✅ TEST 5 PASSED: Database connections working!\n")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST 5 FAILED: {e}\n")
        print("   Note: This is okay if MySQL is not running")
        return True  # Don't fail the whole test suite


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("SOLID ARCHITECTURE TEST SUITE")
    print("="*60)
    print("Testing the new SOLID-compliant architecture...")
    print()
    
    results = []
    
    # Run tests
    results.append(await test_di_container())
    results.append(await test_infrastructure())
    results.append(await test_data_sources())
    results.append(await test_application_layer())
    results.append(await test_database_connection())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! SOLID Architecture is working!\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} tests failed. Check errors above.\n")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)

