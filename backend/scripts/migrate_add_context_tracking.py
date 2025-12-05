"""
Database Migration: Add Context Tracking Tables
Adds AI-powered, generic context tracking for conversations
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager

def migrate_database():
    """
    Add context tracking tables for AI-powered conversation understanding
    """
    print("="*80)
    print("DATABASE MIGRATION: Adding AI-Powered Context Tracking")
    print("="*80)
    print("\nThis adds generic, dynamic context tracking that works for ANY conversation.")
    print("No more hardcoded patterns - uses AI to understand topics!")
    print("="*80)
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            print("\n📊 Step 1: Creating 'conversation_context' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_context (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    message_order INT NOT NULL COMMENT 'Which message this context is from',
                    
                    main_topic VARCHAR(500) DEFAULT NULL COMMENT 'Primary topic/entity discussed',
                    entities JSON DEFAULT NULL COMMENT 'All entities mentioned (JSON array)',
                    keywords JSON DEFAULT NULL COMMENT 'Important keywords (JSON array)',
                    
                    context_type VARCHAR(50) DEFAULT 'general' COMMENT 'module, entity, process, feature, etc.',
                    confidence FLOAT DEFAULT 0.0 COMMENT 'AI confidence score (0-1)',
                    
                    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    INDEX idx_conversation_order (conversation_id, message_order),
                    INDEX idx_main_topic (main_topic),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ 'conversation_context' table created")
            
            print("\n📊 Step 2: Creating 'context_resolution_cache' table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS context_resolution_cache (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    conversation_id INT NOT NULL,
                    
                    pronoun VARCHAR(100) NOT NULL COMMENT 'it, this, that, the module, etc.',
                    query_text TEXT NOT NULL COMMENT 'Full query containing the pronoun',
                    
                    resolved_entity VARCHAR(500) NOT NULL COMMENT 'What the pronoun refers to',
                    resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    expires_at TIMESTAMP DEFAULT NULL,
                    
                    INDEX idx_conversation_pronoun (conversation_id, pronoun),
                    INDEX idx_expires (expires_at),
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   ✅ 'context_resolution_cache' table created")
            
            conn.commit()
            
            print("\n" + "="*80)
            print("✅ MIGRATION COMPLETE!")
            print("="*80)
            print("\n📋 New Features:")
            print("   ✅ AI-powered topic extraction (works for ANY conversation)")
            print("   ✅ Generic pronoun resolution (not pattern-specific)")
            print("   ✅ Context tracking with confidence scores")
            print("   ✅ Resolution caching for performance")
            print("\n💡 How it works:")
            print("   • GPT extracts topics/entities from conversations dynamically")
            print("   • No hardcoded patterns - adapts to any domain")
            print("   • Resolves 'it', 'this', 'that' intelligently")
            print("   • Stores context for learning and improvement")
            print("\n🚀 Next steps:")
            print("   1. Restart your backend server")
            print("   2. Test with ANY conversation topic")
            print("   3. System will understand context automatically!")
            print("\n" + "="*80 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check MySQL is running")
        print("   2. Check database credentials in .env")
        print("   3. Ensure 'conversations' table exists (run previous migration first)")
        return False


def verify_migration():
    """
    Verify the migration was successful
    """
    print("\n🔍 Verifying migration...")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # Check conversation_context table
            cursor.execute("SHOW TABLES LIKE 'conversation_context'")
            if cursor.fetchone():
                print("   ✅ 'conversation_context' table exists")
            else:
                print("   ❌ 'conversation_context' table NOT found")
                return False
            
            # Check context_resolution_cache table
            cursor.execute("SHOW TABLES LIKE 'context_resolution_cache'")
            if cursor.fetchone():
                print("   ✅ 'context_resolution_cache' table exists")
            else:
                print("   ❌ 'context_resolution_cache' table NOT found")
                return False
            
            return True
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🔄 AI-Powered Context Tracking Migration")
    print("Generic, dynamic context understanding for ANY conversation")
    print("Safe to run multiple times (idempotent)")
    print()
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify
        verify_migration()
        print("\n✅ Migration successful! Restart your server to use AI-powered context tracking.\n")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the errors above.\n")
        sys.exit(1)

