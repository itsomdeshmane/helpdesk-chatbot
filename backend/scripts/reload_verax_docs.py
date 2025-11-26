"""
Simple script to reload the Verax markdown documentation.
This will clear old chunks and load with the new structure-aware chunking.
"""
from ingestion.docs_loader import load_markdown_docs

if __name__ == "__main__":
    print("\n" + "="*60)
    print("RELOADING VERAX DOCUMENTATION")
    print("="*60)
    print("\nThis will:")
    print("  1. Check if VERAX_DOCUMENTATION.md already exists in database")
    print("  2. Load with new structure-aware chunking")
    print("  3. Preserve module lists and hierarchical content\n")
    
    print("Options:")
    print("  1. Load only if not already in database (skip if exists)")
    print("  2. Force reload (overwrite existing)")
    
    choice = input("\nSelect option (1 or 2, default 2): ").strip()
    
    if not choice:
        choice = '2'  # Default to force reload for backward compatibility
    
    if choice not in ['1', '2']:
        print("\nInvalid choice. Cancelled.")
        exit(1)
    
    force_reload = (choice == '2')
    
    chunks_loaded = load_markdown_docs(tenant_id="default", module="verax_system", force_reload=force_reload)
    
    if chunks_loaded > 0:
        print("\n✅ SUCCESS! Verax documentation reloaded successfully!")
        print(f"✅ {chunks_loaded} chunks are now ready for queries.")
        print("\n💡 Try asking: 'Give me all module list' or 'What are all the modules?'")
    else:
        print("\n❌ FAILED! Could not reload documentation.")
        print("Please check that docs/VERAX_DOCUMENTATION.md exists.")
    
    print("\n" + "="*60 + "\n")

