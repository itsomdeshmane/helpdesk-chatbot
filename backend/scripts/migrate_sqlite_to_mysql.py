"""
Migration script to transfer data from SQLite to MySQL
Run this script to migrate existing chat history data to MySQL
"""
import sqlite3
import mysql.connector
from pathlib import Path
from config import (
    MYSQL_HOST,
    MYSQL_PORT,
    MYSQL_USER,
    MYSQL_PASSWORD,
    MYSQL_DATABASE
)

SQLITE_DB_PATH = Path(__file__).parent / "database" / "chat_history.db"

def migrate_data():
    """Migrate data from SQLite to MySQL"""
    
    # Check if SQLite database exists
    if not SQLITE_DB_PATH.exists():
        print("❌ SQLite database not found. Nothing to migrate.")
        print(f"   Expected path: {SQLITE_DB_PATH}")
        return
    
    print("🔄 Starting migration from SQLite to MySQL...")
    print(f"   Source: {SQLITE_DB_PATH}")
    print(f"   Target: {MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}")
    print()
    
    try:
        # Connect to SQLite
        sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
        sqlite_conn.row_factory = sqlite3.Row
        sqlite_cursor = sqlite_conn.cursor()
        
        # Connect to MySQL
        mysql_conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        mysql_cursor = mysql_conn.cursor()
        
        # Migrate chat_interactions
        print("📊 Migrating chat_interactions...")
        sqlite_cursor.execute("SELECT COUNT(*) FROM chat_interactions")
        count = sqlite_cursor.fetchone()[0]
        print(f"   Found {count} records to migrate")
        
        if count > 0:
            sqlite_cursor.execute("""
                SELECT tenant_id, query, response, module, helpful, response_time, created_at 
                FROM chat_interactions
            """)
            
            migrated = 0
            for row in sqlite_cursor:
                try:
                    mysql_cursor.execute("""
                        INSERT INTO chat_interactions 
                        (tenant_id, query, response, module, helpful, response_time, created_at) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        row['tenant_id'],
                        row['query'],
                        row['response'],
                        row['module'],
                        row['helpful'],
                        row['response_time'],
                        row['created_at']
                    ))
                    migrated += 1
                except Exception as e:
                    print(f"   ⚠️  Error migrating record: {e}")
            
            mysql_conn.commit()
            print(f"   ✅ Migrated {migrated}/{count} chat interactions")
        
        # Migrate faq_questions
        print("\n📚 Migrating faq_questions...")
        try:
            sqlite_cursor.execute("SELECT COUNT(*) FROM faq_questions")
            count = sqlite_cursor.fetchone()[0]
            print(f"   Found {count} records to migrate")
            
            if count > 0:
                sqlite_cursor.execute("""
                    SELECT question, answer, category, module, source_document, popularity, created_at 
                    FROM faq_questions
                """)
                
                migrated = 0
                for row in sqlite_cursor:
                    try:
                        mysql_cursor.execute("""
                            INSERT INTO faq_questions 
                            (question, answer, category, module, source_document, popularity, created_at) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (
                            row['question'],
                            row['answer'],
                            row['category'],
                            row['module'],
                            row['source_document'],
                            row['popularity'],
                            row['created_at']
                        ))
                        migrated += 1
                    except Exception as e:
                        print(f"   ⚠️  Error migrating record: {e}")
                
                mysql_conn.commit()
                print(f"   ✅ Migrated {migrated}/{count} FAQ questions")
        except sqlite3.OperationalError:
            print("   ⚠️  faq_questions table doesn't exist in SQLite, skipping...")
        
        # Migrate response_patterns
        print("\n🔄 Migrating response_patterns...")
        try:
            sqlite_cursor.execute("SELECT COUNT(*) FROM response_patterns")
            count = sqlite_cursor.fetchone()[0]
            print(f"   Found {count} records to migrate")
            
            if count > 0:
                sqlite_cursor.execute("""
                    SELECT query_type, pattern_template, success_rate, usage_count 
                    FROM response_patterns
                """)
                
                migrated = 0
                for row in sqlite_cursor:
                    try:
                        mysql_cursor.execute("""
                            INSERT INTO response_patterns 
                            (query_type, pattern_template, success_rate, usage_count) 
                            VALUES (%s, %s, %s, %s)
                        """, (
                            row['query_type'],
                            row['pattern_template'],
                            row['success_rate'],
                            row['usage_count']
                        ))
                        migrated += 1
                    except Exception as e:
                        print(f"   ⚠️  Error migrating record: {e}")
                
                mysql_conn.commit()
                print(f"   ✅ Migrated {migrated}/{count} response patterns")
        except sqlite3.OperationalError:
            print("   ⚠️  response_patterns table doesn't exist in SQLite, skipping...")
        
        # Close connections
        sqlite_conn.close()
        mysql_cursor.close()
        mysql_conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Verify the data in MySQL")
        print("   2. Backup your SQLite database if needed")
        print("   3. Restart your backend server")
        
    except sqlite3.Error as e:
        print(f"❌ SQLite error: {e}")
    except mysql.connector.Error as e:
        print(f"❌ MySQL error: {e}")
        print("\n💡 Troubleshooting:")
        print("   - Check if MySQL server is running")
        print("   - Verify database credentials in .env file")
        print("   - Ensure database exists (run backend server first to auto-create)")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    migrate_data()

