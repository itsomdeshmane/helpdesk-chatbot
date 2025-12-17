"""
Fix Database Settings Issue
This script adds the db_type column to user_database_connections table
and ensures the table structure is correct for multi-database support.
"""
import pymysql
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_USER, 
    MYSQL_PASSWORD, MYSQL_DATABASE
)

def get_connection():
    """Create database connection"""
    try:
        conn = pymysql.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        sys.exit(1)

def check_table_exists(conn):
    """Check if user_database_connections table exists"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'user_database_connections'
        """, (MYSQL_DATABASE,))
        result = cursor.fetchone()
        return result['count'] > 0

def check_column_exists(conn, column_name):
    """Check if a column exists in user_database_connections table"""
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = %s
            AND TABLE_NAME = 'user_database_connections'
            AND COLUMN_NAME = %s
        """, (MYSQL_DATABASE, column_name))
        result = cursor.fetchone()
        return result['count'] > 0

def create_table(conn):
    """Create user_database_connections table with all required columns"""
    print("\n📝 Creating user_database_connections table...")
    with conn.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_database_connections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                tenant_id VARCHAR(100) NOT NULL,
                db_type VARCHAR(20) DEFAULT 'mysql' NOT NULL COMMENT 'mysql, postgresql, sqlserver',
                host VARCHAR(255) NOT NULL,
                port INT NOT NULL DEFAULT 3306,
                database_name VARCHAR(100) NOT NULL,
                username VARCHAR(100) NOT NULL,
                encrypted_password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                
                INDEX idx_user_tenant (user_id, tenant_id),
                INDEX idx_tenant (tenant_id),
                INDEX idx_created_at (created_at),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_tenant_connection (user_id, tenant_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            COMMENT='Encrypted database connection credentials per user'
        """)
        conn.commit()
        print("✅ Table created successfully")

def add_db_type_column(conn):
    """Add db_type column to existing table"""
    print("\n📝 Adding db_type column to user_database_connections table...")
    with conn.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE user_database_connections 
            ADD COLUMN db_type VARCHAR(20) DEFAULT 'mysql' NOT NULL 
            COMMENT 'mysql, postgresql, sqlserver'
            AFTER tenant_id
        """)
        conn.commit()
        print("✅ db_type column added successfully")

def show_table_structure(conn):
    """Show the current table structure"""
    print("\n📋 Current table structure:")
    with conn.cursor() as cursor:
        cursor.execute("DESCRIBE user_database_connections")
        columns = cursor.fetchall()
        print("\n{:<20} {:<15} {:<10} {:<10}".format("Field", "Type", "Null", "Key"))
        print("-" * 60)
        for col in columns:
            print("{:<20} {:<15} {:<10} {:<10}".format(
                col['Field'], 
                col['Type'], 
                col['Null'], 
                col['Key'] or ''
            ))

def main():
    """Main function to fix database settings"""
    print("=" * 60)
    print("DATABASE SETTINGS FIX SCRIPT")
    print("=" * 60)
    print(f"\n🔍 Connecting to database: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    
    conn = get_connection()
    
    try:
        # Check if table exists
        table_exists = check_table_exists(conn)
        
        if not table_exists:
            print("\n⚠️  Table 'user_database_connections' does not exist")
            create_table(conn)
        else:
            print("\n✅ Table 'user_database_connections' exists")
            
            # Check if db_type column exists
            db_type_exists = check_column_exists(conn, 'db_type')
            
            if not db_type_exists:
                print("\n⚠️  Column 'db_type' does not exist")
                add_db_type_column(conn)
            else:
                print("\n✅ Column 'db_type' already exists")
        
        # Show final table structure
        show_table_structure(conn)
        
        print("\n" + "=" * 60)
        print("✅ DATABASE SETTINGS FIX COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Restart your backend server")
        print("2. Open the Settings UI in your frontend")
        print("3. Configure your database connection")
        print("4. Test and save the connection")
        print("\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()

