"""
Run Soft Delete Migration
Adds soft delete support to conversations table
"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager


def run_migration():
    """Run the soft delete migration"""
    print("🔧 Running soft delete migration...")
    
    try:
        with db_manager.get_connection() as conn:
            # Add soft delete columns
            print("   Adding deleted_by_user column...")
            try:
                conn.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN deleted_by_user BOOLEAN DEFAULT FALSE 
                    COMMENT 'User deleted this conversation (soft delete)'
                """)
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("   ⚠️  Column deleted_by_user already exists, skipping...")
                else:
                    raise
            
            print("   Adding deleted_at column...")
            try:
                conn.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN deleted_at TIMESTAMP NULL 
                    COMMENT 'When user deleted this conversation'
                """)
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("   ⚠️  Column deleted_at already exists, skipping...")
                else:
                    raise
            
            print("   Adding permanent_delete_after column...")
            try:
                conn.execute("""
                    ALTER TABLE conversations 
                    ADD COLUMN permanent_delete_after TIMESTAMP NULL 
                    COMMENT 'When to permanently delete (for compliance)'
                """)
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print("   ⚠️  Column permanent_delete_after already exists, skipping...")
                else:
                    raise
            
            print("   Adding index...")
            try:
                conn.execute("""
                    ALTER TABLE conversations
                    ADD INDEX idx_deleted_by_user (deleted_by_user, user_id)
                """)
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("   ⚠️  Index idx_deleted_by_user already exists, skipping...")
                else:
                    raise
            
            conn.commit()
            
        print("✅ Soft delete migration completed successfully!")
        print("\n📋 Summary:")
        print("   - Users can now 'delete' conversations (hidden from their view)")
        print("   - Deleted conversations kept for learning and analytics")
        print("   - Permanent deletion after 90 days (GDPR compliant)")
        print("   - Admin endpoint available to cleanup old data")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    success = run_migration()
    sys.exit(0 if success else 1)

