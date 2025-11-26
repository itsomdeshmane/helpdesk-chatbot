"""
Update database schema to add new tables
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import mysql.connector
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def update_schema():
    print("="*60)
    print("UPDATING DATABASE SCHEMA")
    print("="*60)
    
    try:
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        cursor = connection.cursor()
        
        # Create query_type_patterns table
        print("\nCreating query_type_patterns table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_type_patterns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_type VARCHAR(100) NOT NULL COMMENT 'Type: list, step-by-step, definition, etc.',
                keyword VARCHAR(255) NOT NULL COMMENT 'Keyword to match in query',
                priority INT DEFAULT 1 COMMENT 'Higher priority = checked first',
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_query_type (query_type),
                INDEX idx_active_priority (is_active, priority DESC),
                UNIQUE KEY unique_type_keyword (query_type, keyword)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("[OK] query_type_patterns table created")
        
        # Create erp_modules table
        print("\nCreating erp_modules table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS erp_modules (
                id INT AUTO_INCREMENT PRIMARY KEY,
                module_name VARCHAR(100) NOT NULL COMMENT 'Module name (e.g., Finance, HR, Sales)',
                module_code VARCHAR(50) NOT NULL COMMENT 'Short code for module',
                description TEXT COMMENT 'Description of the module',
                keywords TEXT COMMENT 'Keywords associated with this module (comma-separated)',
                is_active BOOLEAN DEFAULT TRUE,
                priority INT DEFAULT 1 COMMENT 'Display/matching priority',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_module_name (module_name),
                UNIQUE KEY unique_module_code (module_code),
                INDEX idx_active_priority (is_active, priority DESC)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("[OK] erp_modules table created")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n" + "="*60)
        print("[SUCCESS] Schema updated successfully!")
        print("="*60)
        print("\nNext step: Run seed script")
        print("  python scripts/seed_query_patterns.py")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    update_schema()

