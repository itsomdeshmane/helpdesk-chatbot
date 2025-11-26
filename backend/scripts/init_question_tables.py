"""
Initialize Question Generation Tables
Run this script to create the new tables for question generation and clarity detection
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import db_manager

def init_tables():
    """Initialize the new tables for question generation"""
    print("="*80)
    print("Initializing Question Generation Tables")
    print("="*80)
    
    try:
        with db_manager.get_connection() as conn:
            print("\n1. Creating generated_questions table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS generated_questions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    module_name VARCHAR(100) NOT NULL,
                    difficulty_level VARCHAR(20) NOT NULL COMMENT 'beginner, intermediate, advanced',
                    question TEXT NOT NULL,
                    tenant_id VARCHAR(255) DEFAULT 'default',
                    is_active BOOLEAN DEFAULT TRUE,
                    times_asked INT DEFAULT 0 COMMENT 'How many times this question was asked',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_module_level (module_name, difficulty_level),
                    INDEX idx_tenant (tenant_id),
                    INDEX idx_active (is_active)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   [OK] generated_questions table created")
            
            print("\n2. Creating query_clarifications table...")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_clarifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    tenant_id VARCHAR(255) NOT NULL,
                    original_query TEXT NOT NULL,
                    clarity_score FLOAT DEFAULT 0.0 COMMENT 'Clarity score 0-1',
                    issues TEXT COMMENT 'JSON array of clarity issues',
                    clarifying_questions TEXT COMMENT 'JSON array of questions asked',
                    user_clarification TEXT COMMENT 'User response to clarification',
                    was_resolved BOOLEAN DEFAULT FALSE COMMENT 'Whether user provided clarification',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_tenant_created (tenant_id, created_at),
                    INDEX idx_resolved (was_resolved)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("   [OK] query_clarifications table created")
            
            conn.commit()
            
            print("\n" + "="*80)
            print("[SUCCESS] All tables initialized successfully!")
            print("="*80)
            
            # Show table status
            print("\nTable Status:")
            cursor = conn.execute("""
                SELECT TABLE_NAME, TABLE_ROWS 
                FROM information_schema.TABLES 
                WHERE TABLE_SCHEMA = DATABASE() 
                AND TABLE_NAME IN ('generated_questions', 'query_clarifications')
            """)
            
            for row in cursor.fetchall():
                print(f"   - {row['TABLE_NAME']}: {row['TABLE_ROWS']} rows")
            
    except Exception as e:
        print(f"\n[ERROR] Error initializing tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = init_tables()
    sys.exit(0 if success else 1)

