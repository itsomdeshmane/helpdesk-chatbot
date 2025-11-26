"""
Setup and connect to Pinecone with correct configuration
"""
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, OPENAI_API_KEY
import os

def test_api_key():
    """Test if the Pinecone API key is valid"""
    print("\n" + "="*60)
    print("STEP 1: Testing Pinecone API Key")
    print("="*60)
    
    if not PINECONE_API_KEY:
        print("❌ ERROR: PINECONE_API_KEY not found in .env file")
        print("\n💡 Please add your API key to backend/.env:")
        print("   PINECONE_API_KEY=your-api-key-here")
        return False
    
    print(f"✓ API Key found: {PINECONE_API_KEY[:8]}...{PINECONE_API_KEY[-8:]}")
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        print("✅ API Key is valid!")
        return pc
    except Exception as e:
        print(f"❌ API Key is INVALID: {e}")
        print("\n💡 Please get a valid API key from: https://app.pinecone.io")
        print("   Go to API Keys section and create/copy a valid key")
        return False

def list_existing_indexes(pc):
    """List all existing indexes"""
    print("\n" + "="*60)
    print("STEP 2: Checking Existing Indexes")
    print("="*60)
    
    try:
        indexes = pc.list_indexes()
        
        if len(indexes) == 0:
            print("ℹ️  No indexes found. You'll need to create a new one.")
            return []
        
        print(f"✓ Found {len(indexes)} existing index(es):\n")
        
        for idx in indexes:
            print(f"📊 Index: {idx.name}")
            print(f"   - Dimension: {idx.dimension}")
            print(f"   - Metric: {idx.metric}")
            print(f"   - Cloud: {idx.cloud}")
            print(f"   - Region: {idx.region}")
            
            # Check if dimension is correct for OpenAI embeddings
            if idx.dimension == 1536:
                print(f"   ✅ Dimension is correct for OpenAI embeddings!")
            else:
                print(f"   ⚠️  Dimension {idx.dimension} is incompatible (need 1536)")
            print()
        
        return [idx.name for idx in indexes]
        
    except Exception as e:
        print(f"❌ Error listing indexes: {e}")
        return []

def create_new_index(pc):
    """Create a new index with correct dimensions"""
    print("\n" + "="*60)
    print("STEP 3: Create New Index")
    print("="*60)
    
    index_name = input("\nEnter name for new index (e.g., 'erp-helpdesk-v2'): ").strip()
    
    if not index_name:
        print("❌ Index name cannot be empty")
        return None
    
    print(f"\n⏳ Creating index: {index_name}")
    print(f"   - Dimension: 1536 (for OpenAI text-embedding-ada-002)")
    print(f"   - Metric: cosine")
    print(f"   - Cloud: aws")
    print(f"   - Region: us-east-1")
    
    try:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"\n✅ Index '{index_name}' created successfully!")
        return index_name
        
    except Exception as e:
        print(f"❌ Error creating index: {e}")
        
        if "already exists" in str(e).lower():
            print(f"💡 Index '{index_name}' already exists. You can use it.")
            return index_name
        
        print("\n💡 Alternative: Create index manually:")
        print("   1. Go to: https://app.pinecone.io")
        print("   2. Click 'Create Index'")
        print(f"   3. Name: {index_name}")
        print("   4. Dimensions: 1536")
        print("   5. Metric: cosine")
        
        return None

def connect_to_index(pc, index_name):
    """Connect to an index and test it"""
    print("\n" + "="*60)
    print("STEP 4: Connecting to Index")
    print("="*60)
    
    try:
        print(f"⏳ Connecting to index: {index_name}")
        index = pc.Index(index_name)
        
        # Get stats
        stats = index.describe_index_stats()
        print(f"✅ Successfully connected!")
        print(f"\n📊 Index Statistics:")
        print(f"   - Total vectors: {stats.total_vector_count}")
        if hasattr(stats, 'dimension'):
            print(f"   - Dimensions: {stats.dimension}")
        print(f"   - Namespaces: {list(stats.namespaces.keys()) if hasattr(stats, 'namespaces') and stats.namespaces else 'default'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to index: {e}")
        return False

def update_env_file(index_name):
    """Update .env file with the correct index name"""
    print("\n" + "="*60)
    print("STEP 5: Updating Configuration")
    print("="*60)
    
    try:
        env_path = ".env"
        
        # Read existing .env
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add PINECONE_INDEX_NAME and USE_PINECONE
        updated = False
        use_pinecone_updated = False
        new_lines = []
        
        for line in lines:
            if line.startswith('PINECONE_INDEX_NAME='):
                new_lines.append(f'PINECONE_INDEX_NAME={index_name}\n')
                updated = True
            elif line.startswith('USE_PINECONE='):
                new_lines.append('USE_PINECONE=true\n')
                use_pinecone_updated = True
            else:
                new_lines.append(line)
        
        # Add if not found
        if not updated:
            new_lines.append(f'PINECONE_INDEX_NAME={index_name}\n')
        if not use_pinecone_updated:
            new_lines.append('USE_PINECONE=true\n')
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Updated .env file:")
        print(f"   PINECONE_INDEX_NAME={index_name}")
        print(f"   USE_PINECONE=true")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("PINECONE DATABASE SETUP")
    print("="*60)
    print("\nThis script will help you:")
    print("  1. Verify your Pinecone API key")
    print("  2. Check/create an index with correct dimensions (1536)")
    print("  3. Update your configuration")
    print("\n" + "="*60)
    
    # Test API key
    pc = test_api_key()
    if not pc:
        return
    
    # List existing indexes
    existing_indexes = list_existing_indexes(pc)
    
    # Ask what to do
    print("\n" + "="*60)
    print("What would you like to do?")
    print("="*60)
    print("1. Use an existing index")
    print("2. Create a new index")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    index_name = None
    
    if choice == "1":
        if not existing_indexes:
            print("\n❌ No existing indexes. Please create a new one.")
            choice = "2"
        else:
            print("\nAvailable indexes:")
            for i, name in enumerate(existing_indexes, 1):
                print(f"{i}. {name}")
            
            idx_choice = input("\nSelect index number: ").strip()
            try:
                index_name = existing_indexes[int(idx_choice) - 1]
            except:
                print("❌ Invalid selection")
                return
    
    if choice == "2":
        index_name = create_new_index(pc)
        if not index_name:
            return
    
    if choice == "3":
        print("\nExiting...")
        return
    
    # Connect to the index
    if index_name:
        if connect_to_index(pc, index_name):
            update_env_file(index_name)
            
            print("\n" + "="*60)
            print("✅ PINECONE SETUP COMPLETE!")
            print("="*60)
            print("\n📋 Next steps:")
            print("   1. Restart your backend server")
            print("   2. Documents will be loaded to Pinecone automatically")
            print("   3. No more dimension mismatch errors!")
            print("\n💡 To restart the server:")
            print("   cd backend")
            print("   uvicorn app:app --reload --port 8000")
            print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()

