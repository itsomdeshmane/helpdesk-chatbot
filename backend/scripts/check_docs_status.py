"""
Debug script to check what documentation is loaded and test retrieval.
"""
from llm.rag import in_memory_docs, search
from pathlib import Path

def check_documentation_status():
    """Check what documentation is currently loaded"""
    print("\n" + "="*60)
    print("DOCUMENTATION STATUS CHECK")
    print("="*60)
    
    # Check if docs are loaded
    if not in_memory_docs:
        print("\n❌ NO DOCUMENTS LOADED!")
        print("Please run: python reload_verax_docs.py")
        return
    
    print(f"\n✅ Total documents in memory: {len(in_memory_docs)}")
    
    # Count by module
    modules = {}
    for doc in in_memory_docs:
        module = doc.get('module', 'unknown')
        modules[module] = modules.get(module, 0) + 1
    
    print("\n📊 Documents by module:")
    for module, count in sorted(modules.items()):
        print(f"   • {module}: {count} chunks")
    
    # Check for Verax documentation
    verax_docs = [doc for doc in in_memory_docs if doc.get('module') == 'verax_system']
    if verax_docs:
        print(f"\n✅ Verax documentation loaded: {len(verax_docs)} chunks")
        
        # Show sample of first chunk
        if verax_docs:
            sample = verax_docs[0].get('text', '')[:200]
            print(f"\n📄 Sample from first chunk:")
            print(f"   {sample}...")
    else:
        print("\n⚠️  Verax documentation NOT loaded!")
        print("Please run: python reload_verax_docs.py")
    
    # Check for VERAX_DOCUMENTATION.md file
    backend_dir = Path(__file__).parent
    verax_doc_path = backend_dir.parent / "docs" / "VERAX_DOCUMENTATION.md"
    
    print(f"\n📁 Documentation file check:")
    if verax_doc_path.exists():
        size_kb = verax_doc_path.stat().st_size / 1024
        print(f"   ✅ VERAX_DOCUMENTATION.md found ({size_kb:.1f} KB)")
    else:
        print(f"   ❌ VERAX_DOCUMENTATION.md NOT found at: {verax_doc_path}")
    
    print("\n" + "="*60)


def test_search_query(query: str):
    """Test a search query"""
    print(f"\n🔍 Testing query: '{query}'")
    print("-" * 60)
    
    try:
        results = search(query, tenant_id="default")
        
        if results:
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                preview = result[:150].replace('\n', ' ')
                print(f"\n   Result {i}: {preview}...")
        else:
            print("❌ No results found")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("-" * 60)


if __name__ == "__main__":
    # Check documentation status
    check_documentation_status()
    
    # Test some queries
    print("\n" + "="*60)
    print("TESTING SEARCH QUERIES")
    print("="*60)
    
    test_queries = [
        "What are all the modules?",
        "Give me the submodule list of purchasing module",
        "purchasing submodules"
    ]
    
    for query in test_queries:
        test_search_query(query)
    
    print("\n" + "="*60)
    print("✅ Check complete!")
    print("="*60 + "\n")

