"""
Reload all documents into Pinecone vector database
Run this after setting up Pinecone to populate the index
"""
import os
os.environ["USE_PINECONE"] = "true"  # Force enable Pinecone

from ingestion.docs_loader import load_docs_from_folder, load_markdown_docs
from llm.rag import pinecone_available, pinecone_index

def main():
    print("\n" + "="*60)
    print("RELOAD DOCUMENTS TO PINECONE")
    print("="*60)
    
    # Check Pinecone status
    if not pinecone_available:
        print("\n❌ ERROR: Pinecone is not available!")
        print("\n💡 Please run setup_pinecone.py first to configure Pinecone")
        return
    
    if not pinecone_index:
        print("\n❌ ERROR: Pinecone index is not connected!")
        print("\n💡 Please check your PINECONE_INDEX_NAME in .env file")
        return
    
    print(f"\n✅ Pinecone is connected and ready!")
    print(f"   Using index: {pinecone_index._index_name if hasattr(pinecone_index, '_index_name') else 'unknown'}")
    
    # Get index stats before loading
    try:
        stats = pinecone_index.describe_index_stats()
        print(f"\n📊 Current index stats:")
        print(f"   - Total vectors: {stats.total_vector_count}")
    except:
        pass
    
    print("\n" + "="*60)
    print("Loading Documents to Pinecone")
    print("="*60)
    print("\nThis will:")
    print("  1. Load all DOCX/PDF/TXT files from docs folder")
    print("  2. Load VERAX_DOCUMENTATION.md")
    print("  3. Generate embeddings using OpenAI")
    print("  4. Store vectors in Pinecone")
    print("  5. Skip files that already exist (unless you force reload)")
    print("\n⚠️  This may take several minutes depending on document size.")
    
    print("\nOptions:")
    print("  1. Load only new files (skip existing)")
    print("  2. Force reload all files (overwrite existing)")
    
    choice = input("\nSelect option (1 or 2): ").strip()
    
    if choice not in ['1', '2']:
        print("\nInvalid choice. Cancelled.")
        return
    
    force_reload = (choice == '2')
    
    print("\n" + "="*60)
    print("Step 1: Loading Regular Documents")
    print("="*60)
    
    if force_reload:
        print("\n🔄 Force reload enabled - will overwrite existing files")
    else:
        print("\n✅ Smart mode - will skip files already in database")
    
    # Load regular documentation files
    load_docs_from_folder(tenant_id="default", module="general", force_reload=force_reload)
    
    print("\n" + "="*60)
    print("Step 2: Loading Markdown Documentation")
    print("="*60)
    
    # Load markdown documentation
    chunks_loaded = load_markdown_docs(tenant_id="default", module="verax_system", force_reload=force_reload)
    
    # Get final stats
    try:
        stats = pinecone_index.describe_index_stats()
        print("\n" + "="*60)
        print("✅ DOCUMENTS LOADED TO PINECONE!")
        print("="*60)
        print(f"\n📊 Final index stats:")
        print(f"   - Total vectors: {stats.total_vector_count}")
        print(f"   - Namespaces: {list(stats.namespaces.keys()) if hasattr(stats, 'namespaces') and stats.namespaces else 'default'}")
        print("\n💡 Your documents are now available in Pinecone!")
        print("   Restart your server to start using them.")
        print("\n" + "="*60 + "\n")
    except Exception as e:
        print(f"\n⚠️  Could not get final stats: {e}")
        print("\nBut documents should be loaded. Restart your server to use them.")

if __name__ == "__main__":
    main()


