"""
Database Migration: Add Conversations Table
Adds conversation session management tables to existing database
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_manager import db_manager

def migrate_database():
    """
    Add conversation tables to existing database
    """
    print("="*80)
    print("DATABASE MIGRATION: Adding Conversation Session Support")
    print("="*80)
    
    try:
        with db_manager.get_connection() as conn:
            print("\n📊 Step 1: Creating 'conversations' table...")
            
            # Create conversations table
            conn._conn.cursor().execute("""
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
            print("   ✅ 'conversations' table created")
            
            print("\n📊 Step 2: Checking if 'chat_interactions' needs update...")
            
            # Check if conversation_id column exists
            cursor = conn._conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'chat_interactions' 
                AND COLUMN_NAME = 'conversation_id'
            """)
            result = cursor.fetchone()
            
            if result[0] == 0:
                print("   Adding new columns to 'chat_interactions'...")
                
                # Add new columns
                cursor.execute("""
                    ALTER TABLE chat_interactions
                    ADD COLUMN conversation_id INT DEFAULT NULL AFTER id,
                    ADD COLUMN message_order INT DEFAULT 0 COMMENT 'Order of message in conversation',
                    ADD COLUMN context_used TEXT DEFAULT NULL COMMENT 'JSON: previous messages used as context'
                """)
                print("   ✅ Added: conversation_id, message_order, context_used")
                
                # Add index
                cursor.execute("""
                    ALTER TABLE chat_interactions
                    ADD INDEX idx_conversation (conversation_id),
                    ADD INDEX idx_message_order (conversation_id, message_order)
                """)
                print("   ✅ Added indexes")
                
                # Note: NOT adding foreign key constraint to allow NULL values for old data
                print("   ℹ️  Note: Old chat_interactions will have NULL conversation_id (that's OK)")
                
            else:
                print("   ℹ️  Columns already exist, skipping...")
            
            conn.commit()
            
            print("\n" + "="*80)
            print("✅ MIGRATION COMPLETE!")
            print("="*80)
            print("\n📋 Database now supports:")
            print("   ✅ Conversation sessions with UUID tracking")
            print("   ✅ Multi-turn conversations with context")
            print("   ✅ Session expiry management")
            print("   ✅ Message ordering within conversations")
            print("\n💡 Next steps:")
            print("   1. Restart your backend server")
            print("   2. Test conversation features")
            print("   3. Old chat data is preserved (no data loss)")
            print("\n" + "="*80 + "\n")
            
            return True
            
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check MySQL is running")
        print("   2. Check database credentials in .env")
        print("   3. Check user has ALTER table permissions")
        return False


def verify_migration():
    """
    Verify the migration was successful
    """
    print("\n🔍 Verifying migration...")
    
    try:
        with db_manager.get_connection() as conn:
            cursor = conn._conn.cursor()
            
            # Check conversations table
            cursor.execute("SHOW TABLES LIKE 'conversations'")
            if cursor.fetchone():
                print("   ✅ 'conversations' table exists")
            else:
                print("   ❌ 'conversations' table NOT found")
                return False
            
            # Check new columns in chat_interactions
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = DATABASE()
                AND TABLE_NAME = 'chat_interactions'
                AND COLUMN_NAME IN ('conversation_id', 'message_order', 'context_used')
            """)
            columns = [row[0] for row in cursor.fetchall()]
            
            if len(columns) == 3:
                print("   ✅ All new columns added to 'chat_interactions'")
            else:
                print(f"   ⚠️  Only {len(columns)}/3 columns found")
            
            return True
            
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


if __name__ == "__main__":
    print("\n🔄 Database Migration Script")
    print("This will add conversation session support to your database")
    print("Safe to run multiple times (idempotent)")
    print()
    
    # Run migration
    success = migrate_database()
    
    if success:
        # Verify
        verify_migration()
        print("\n✅ Migration successful! You can now restart your server.\n")
        sys.exit(0)
    else:
        print("\n❌ Migration failed. Please check the errors above.\n")
        sys.exit(1)

