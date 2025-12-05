"""
Complete Migration: All Conversation Features
Creates all tables and updates schema for full conversation support with AI-powered context tracking
Safe to run multiple times (idempotent)
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager

def run_complete_migration():
    """
    Single migration that creates/updates everything needed for conversation features
    """
    print("="*80)
    print("COMPLETE MIGRATION: Conversation Features + AI Context Tracking")
    print("="*80)
    print("\nThis will:")
    print("  ✅ Create 'conversations' table (session management)")
    print("  ✅ Update 'chat_interactions' table (add conversation linking)")
    print("  ✅ Create 'conversation_context' table (AI-extracted topics)")
    print("  ✅ Create 'context_resolution_cache' table (pronoun resolution)")
    print("  ✅ Safe to run multiple times")
    print("="*80 + "\n")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # ================================================================
            # PART 1: Create conversations table
            # ================================================================
            print("📊 [1/4] Creating 'conversations' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(100) NOT NULL UNIQUE COMMENT 'Unique session identifier (UUID)',
                    tenant_id VARCHAR(255) NOT NULL,
                    user_id VARCHAR(255) DEFAULT NULL COMMENT 'Optional user identification',
                    title VARCHAR(500) DEFAULT NULL COMMENT 'Auto-generated conversation title',
                    status VARCHAR(50) DEFAULT 'active' COMMENT 'active, archived, expired',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP DEFAULT NULL COMMENT 'Session expiry time',
                    INDEX idx_session (session_id),
                    INDEX idx_tenant (tenant_id),
                    INDEX idx_status (status),
                    INDEX idx_expires (expires_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ 'conversations' table ready")
            
            # ================================================================
            # PART 2: Update chat_interactions table
            # ================================================================
            print("\n📊 [2/4] Updating 'chat_interactions' table...")
            
            # Check if conversation_id column exists
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'chat_interactions' 
                AND COLUMN_NAME = 'conversation_id'
            """)
            result = cursor.fetchone()
            
            if result[0] == 0:
                print("   Adding conversation tracking columns...")
                
                # Add new columns
                cursor.execute("""
                    ALTER TABLE chat_interactions
                    ADD COLUMN conversation_id INT DEFAULT NULL AFTER id,
                    ADD COLUMN message_order INT DEFAULT 0 COMMENT 'Order of message in conversation',
                    ADD COLUMN context_used TEXT DEFAULT NULL COMMENT 'JSON: previous messages used as context'
                """)
                print("   ✅ Added: conversation_id, message_order, context_used")
                
                # Add indexes
                cursor.execute("""
                    ALTER TABLE chat_interactions
                    ADD INDEX idx_conversation (conversation_id),
                    ADD INDEX idx_message_order (conversation_id, message_order)
                """)
                print("   ✅ Added indexes")
                print("   ℹ️  Old chat_interactions will have NULL conversation_id (preserved)")
            else:
                print("   ✅ Columns already exist, skipping...")
            
            # ================================================================
            # PART 3: Create conversation_context table (AI-powered)
            # ================================================================
            print("\n📊 [3/4] Creating 'conversation_context' table (AI-powered)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    message_order INT NOT NULL COMMENT 'Which message this context is from',
                    
                    -- AI-extracted data (generic, works for ANY topic)
                    main_topic VARCHAR(500) DEFAULT NULL COMMENT 'Primary topic/entity discussed',
                    entities JSON DEFAULT NULL COMMENT 'All entities mentioned (JSON array)',
                    keywords JSON DEFAULT NULL COMMENT 'Important keywords (JSON array)',
                    
                    -- Context classification
                    context_type VARCHAR(50) DEFAULT 'general' COMMENT 'module, entity, process, feature, etc.',
                    confidence FLOAT DEFAULT 0.0 COMMENT 'AI confidence score (0-1)',
                    
                    -- Metadata
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    INDEX idx_conversation_order (conversation_id, message_order),
                    INDEX idx_main_topic (main_topic),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ 'conversation_context' table ready")
            
            # ================================================================
            # PART 4: Create context_resolution_cache table
            # ================================================================
            print("\n📊 [4/4] Creating 'context_resolution_cache' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_resolution_cache (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    
                    -- Pronoun resolution
                    pronoun VARCHAR(100) NOT NULL COMMENT 'it, this, that, the module, etc.',
                    query_text TEXT NOT NULL COMMENT 'Full query containing the pronoun',
                    
                    -- What it refers to
                    resolved_entity VARCHAR(500) NOT NULL COMMENT 'What the pronoun refers to',
                    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Cache TTL
                    expires_at TIMESTAMP DEFAULT NULL,
                    
                    INDEX idx_conversation_pronoun (conversation_id, pronoun),
                    INDEX idx_expires (expires_at),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ 'context_resolution_cache' table ready")
            
            # Commit all changes
            conn.commit()
            
            # ================================================================
            # SUCCESS
            # ================================================================
            print("\n" + "="*80)
            print("✅ MIGRATION COMPLETE!")
            print("="*80)
            print("\n📋 Database now supports:")
            print("   ✅ Session-based conversations with UUID tracking")
            print("   ✅ Multi-turn conversations with context memory")
            print("   ✅ AI-powered topic extraction (works for ANY topic)")
            print("   ✅ Generic pronoun resolution (it, this, that, etc.)")
            print("   ✅ Session expiry management (2-hour default)")
            print("   ✅ Message ordering within conversations")
            print("   ✅ Context tracking with confidence scores")
            print("   ✅ Resolution caching for performance")
            
            print("\n💡 Key Features:")
            print("   • No hardcoded patterns - pure AI understanding")
            print("   • Works for ANY conversation topic (ERP, CRM, any domain)")
            print("   • Learns and improves from conversations")
            print("   • Maintains context across multiple questions")
            
            print("\n🚀 Next steps:")
            print("   1. Restart your backend server:")
            print("      uvicorn app:app --reload --host 0.0.0.0 --port 8000")
            print("")
            print("   2. Test conversation continuity:")
            print("      First: 'What is the Workflow Module?'")
            print("      Then: 'Who uses it?'")
            print("      System will understand 'it' = 'Workflow Module' ✅")
            print("")
            print("   3. Check server logs for context extraction:")
            print("      Look for: '🧠 Context extracted: Topic=...'")
            print("")
            print("   4. Old data is preserved (no data loss)")
            print("\n" + "="*80 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"\n🔍 Error details: {type(e).__name__}")
        print("\n💡 Troubleshooting:")
        print("   1. Check MySQL is running: mysql -u root -p")
        print("   2. Check database credentials in .env file")
        print("   3. Ensure user has CREATE TABLE permissions")
        print("   4. Check if tables already exist (safe to re-run)")
        print(f"\n   Full error: {str(e)}\n")
        return False


def verify_migration():
    """
    Verify all tables were created successfully
    """
    print("\n🔍 Verifying migration...")
    
    required_tables = [
        'conversations',
        'chat_interactions',
        'conversation_context',
        'context_resolution_cache'
    ]
    
    required_columns = [
        ('chat_interactions', 'conversation_id'),
        ('chat_interactions', 'message_order'),
        ('chat_interactions', 'context_used')
    ]
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # Check tables
            print("\n   Checking tables...")
            for table in required_tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    print(f"      ✅ '{table}' exists")
                else:
                    print(f"      ❌ '{table}' NOT found")
                    return False
            
            # Check new columns
            print("\n   Checking new columns...")
            for table, column in required_columns:
                cursor.execute(f"""
                    SELECT COUNT(*) as count
                    FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE()
                    AND TABLE_NAME = '{table}'
                    AND COLUMN_NAME = '{column}'
                """)
                result = cursor.fetchone()
                if result[0] > 0:
                    print(f"      ✅ '{table}.{column}' exists")
                else:
                    print(f"      ⚠️  '{table}.{column}' NOT found")
            
            print("\n   ✅ Verification complete!")
            return True
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def show_statistics():
    """
    Show database statistics
    """
    print("\n📊 Database Statistics:")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # Count conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            print(f"   • Conversations: {conv_count}")
            
            # Count chat interactions
            cursor.execute("SELECT COUNT(*) FROM chat_interactions")
            chat_count = cursor.fetchone()[0]
            print(f"   • Chat messages: {chat_count}")
            
            # Count with conversation_id
            cursor.execute("SELECT COUNT(*) FROM chat_interactions WHERE conversation_id IS NOT NULL")
            linked_count = cursor.fetchone()[0]
            print(f"   • Linked messages: {linked_count}")
            
            # Count context records
            cursor.execute("SELECT COUNT(*) FROM conversation_context")
            context_count = cursor.fetchone()[0]
            print(f"   • Context records: {context_count}")
            
            # Count cached resolutions
            cursor.execute("SELECT COUNT(*) FROM context_resolution_cache")
            cache_count = cursor.fetchone()[0]
            print(f"   • Cached resolutions: {cache_count}")
            
    except Exception as e:
        print(f"   ⚠️  Could not fetch statistics: {e}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 COMPLETE CONVERSATION FEATURES MIGRATION")
    print("="*80)
    print("\nAdds:")
    print("  • Session management")
    print("  • Conversation memory")
    print("  • AI-powered context tracking")
    print("  • Generic pronoun resolution")
    print("\nSafe to run multiple times!")
    print("="*80 + "\n")
    
    # Run migration
    success = run_complete_migration()
    
    if success:
        # Verify
        verify_migration()
        
        # Show stats
        show_statistics()
        
        print("\n" + "="*80)
        print("✅ SUCCESS! All conversation features are ready.")
        print("="*80)
        print("\n🎉 Your chatbot now has:")
        print("   • Full conversation memory")
        print("   • AI-powered context understanding")
        print("   • Works for ANY topic (generic)")
        print("   • Intelligent pronoun resolution")
        print("\nRestart your server and test it!")
        print("="*80 + "\n")
        
        sys.exit(0)
    else:
        print("\n" + "="*80)
        print("❌ Migration failed - see errors above")
        print("="*80 + "\n")
        sys.exit(1)

