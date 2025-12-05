"""
Fix Pinecone Index - Recreate with correct dimensions
Fixes the dimension mismatch error (1536 vs 3536)
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "erp-helpdesk")

def fix_pinecone_index():
    """
    Delete and recreate Pinecone index with correct dimensions
    """
    if not PINECONE_API_KEY:
        print("❌ PINECONE_API_KEY not found in .env file")
        return False
    
    print("="*80)
    print("🔧 Pinecone Index Fix - Dimension Mismatch")
    print("="*80)
    print(f"Index Name: {PINECONE_INDEX_NAME}")
    print(f"Required Dimension: 1536 (OpenAI text-embedding-ada-002)")
    print("="*80)
    
    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=PINECONE_API_KEY)
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        index_names = [index.name for index in existing_indexes]
        
        if PINECONE_INDEX_NAME in index_names:
            print(f"\n⚠️  Index '{PINECONE_INDEX_NAME}' already exists")
            
            # Get index details
            index_info = pc.describe_index(PINECONE_INDEX_NAME)
            current_dimension = index_info.dimension
            
            print(f"   Current dimension: {current_dimension}")
            print(f"   Required dimension: 1536")
            
            if current_dimension == 1536:
                print("\n✅ Index already has correct dimensions!")
                print("   No changes needed.")
                return True
            
            # Confirm deletion
            print("\n⚠️  WARNING: This will DELETE the existing index and all data!")
            response = input("   Type 'DELETE' to confirm: ")
            
            if response != "DELETE":
                print("\n❌ Operation cancelled")
                return False
            
            print(f"\n🗑️  Deleting index '{PINECONE_INDEX_NAME}'...")
            pc.delete_index(PINECONE_INDEX_NAME)
            print("   ✅ Index deleted")
            
            # Wait for deletion to complete
            import time
            print("   ⏳ Waiting for deletion to complete...")
            time.sleep(5)
        
        # Create new index with correct dimensions
        print(f"\n🔨 Creating new index '{PINECONE_INDEX_NAME}'...")
        print(f"   Dimension: 1536")
        print(f"   Metric: cosine")
        print(f"   Cloud: AWS")
        print(f"   Region: us-east-1")
        
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # CORRECT dimension for OpenAI embeddings
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        print(f"\n✅ Index '{PINECONE_INDEX_NAME}' created successfully!")
        print("\n" + "="*80)
        print("✅ PINECONE INDEX FIXED!")
        print("="*80)
        print("\nNext steps:")
        print("1. Restart your backend server")
        print("2. Upload your documents again:")
        print("   python scripts/reload_docs_to_pinecone.py")
        print("\n" + "="*80)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check your PINECONE_API_KEY in .env")
        print("2. Check your internet connection")
        print("3. Verify your Pinecone account is active")
        return False


if __name__ == "__main__":
    print("\n🔧 Pinecone Index Dimension Fix Utility")
    print("This will recreate your index with the correct dimensions (1536)")
    print()
    
    success = fix_pinecone_index()
    
    if not success:
        print("\n⚠️  Failed to fix index. Consider using in-memory mode:")
        print("   Set USE_PINECONE=false in your .env file")
    
    sys.exit(0 if success else 1)

