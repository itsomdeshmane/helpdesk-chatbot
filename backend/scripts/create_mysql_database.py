"""
MySQL Database Creation Script
Run this script to create the helpdesk database and all required tables
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import mysql.connector
from mysql.connector import Error
from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE
)

def create_database_and_tables():
    """Create database and all required tables"""
    connection = None
    
    try:
        # Step 1: Connect to MySQL server (without database)
        print("=" * 60)
        print("🔧 MySQL Database Setup")
        print("=" * 60)
        print(f"\n📡 Connecting to MySQL server at {MYSQL_HOST}:{MYSQL_PORT}...")
        
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        cursor = connection.cursor()
        print(f"✅ Connected successfully!\n")
        
        # Step 2: Create database
        print(f"🗄️  Creating database '{MYSQL_DATABASE}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ Database '{MYSQL_DATABASE}' created/verified\n")
        
        # Step 3: Use the database
        cursor.execute(f"USE {MYSQL_DATABASE}")
        print(f"📂 Using database '{MYSQL_DATABASE}'\n")
        
        # Step 4: Create chat_interactions table
        print("📊 Creating table 'chat_interactions'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_interactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tenant_id VARCHAR(255) NOT NULL,
                query TEXT NOT NULL,
                response TEXT NOT NULL,
                module VARCHAR(255) DEFAULT NULL,
                helpful INT DEFAULT 0 COMMENT 'User feedback: 1=helpful, 0=neutral, -1=not helpful',
                response_time FLOAT DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_tenant_created (tenant_id, created_at),
                INDEX idx_module (module)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Table 'chat_interactions' created")
        
        # Step 5: Create faq_questions table
        print("📚 Creating table 'faq_questions'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faq_questions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                category VARCHAR(255) DEFAULT NULL,
                module VARCHAR(255) DEFAULT NULL,
                source_document VARCHAR(500) DEFAULT NULL,
                popularity INT DEFAULT 0 COMMENT 'How often this is asked',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_faq_category (category),
                INDEX idx_faq_module (module)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Table 'faq_questions' created")
        
        # Step 6: Create response_patterns table
        print("🔄 Creating table 'response_patterns'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS response_patterns (
                id INT AUTO_INCREMENT PRIMARY KEY,
                query_type VARCHAR(255) NOT NULL COMMENT 'list, step-by-step, definition, etc.',
                pattern_template TEXT NOT NULL,
                success_rate FLOAT DEFAULT 0.0,
                usage_count INT DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """)
        print("✅ Table 'response_patterns' created\n")
        
        # Commit all changes
        connection.commit()
        
        # Step 7: Verify tables
        print("🔍 Verifying tables...")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   • {table_name}: {count} records")
        
        print("\n" + "=" * 60)
        print("🎉 Database setup completed successfully!")
        print("=" * 60)
        print(f"\n💡 Database Details:")
        print(f"   Host: {MYSQL_HOST}:{MYSQL_PORT}")
        print(f"   Database: {MYSQL_DATABASE}")
        print(f"   User: {MYSQL_USER}")
        print(f"   Tables: {len(tables)}")
        print("\n✅ Your application is ready to use MySQL!\n")
        
    except Error as e:
        print(f"\n❌ MySQL Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure MySQL server is running")
        print("   2. Verify credentials in .env file")
        print("   3. Check user permissions:")
        print(f"      GRANT ALL PRIVILEGES ON {MYSQL_DATABASE}.* TO '{MYSQL_USER}'@'localhost';")
        print("      FLUSH PRIVILEGES;")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False
        
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 Connection closed\n")
    
    return True

if __name__ == "__main__":
    success = create_database_and_tables()
    if success:
        print("👉 Next step: Run 'python test_mysql_connection.py' to test the connection")
    exit(0 if success else 1)

