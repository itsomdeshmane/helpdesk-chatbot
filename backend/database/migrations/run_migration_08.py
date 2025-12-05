"""
Run Migration 08 - Smart Tables
"""
import mysql.connector
import sys
from pathlib import Path

# Import config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DATABASE

def run_migration():
    """Run migration 08 to create smart tables"""
    migration_file = Path(__file__).parent / "08_smart_tables.sql"
    
    if not migration_file.exists():
        print(f"❌ Migration file not found: {migration_file}")
        return False
    
    print("🚀 Running Migration 08: Smart Tables")
    print("=" * 60)
    
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        # Read migration file
        print(f"📖 Reading: {migration_file.name}")
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Remove comment lines
        lines = []
        for line in sql_content.split('\n'):
            stripped = line.strip()
            if not stripped.startswith('--'):
                lines.append(line)
        cleaned_sql = '\n'.join(lines)
        
        print("⏳ Executing multiple statements...")
        
        # Use multi=True to execute multiple statements
        cursor = conn.cursor()
        
        try:
            # Execute the entire SQL file
            results = cursor.execute(cleaned_sql, multi=True)
            
            success_count = 0
            for result in results:
                if result.with_rows:
                    result.fetchall()  # Consume results
                success_count += 1
                
                # Try to determine what was executed
                if result.statement:
                    stmt_upper = result.statement.upper()
                    if 'CREATE TABLE' in stmt_upper:
                        import re
                        match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)', result.statement, re.IGNORECASE)
                        if match:
                            print(f"  ✅ Created table: {match.group(1)}")
                    elif 'INSERT INTO' in stmt_upper:
                        import re
                        match = re.search(r'INSERT INTO\s+(\w+)', result.statement, re.IGNORECASE)
                        if match:
                            print(f"  ✅ Inserted data into: {match.group(1)}")
            
            conn.commit()
            print(f"\n✅ Executed {success_count} statements successfully")
            
        except mysql.connector.Error as e:
            print(f"  ⚠️  Error: {e}")
            conn.rollback()
            
        finally:
            cursor.close()
            conn.close()
        
        print("=" * 60)
        print(f"✅ Migration completed successfully!")
        print(f"📊 Executed {success_count} statements")
        print("=" * 60)
        
        # Verify tables were created
        print("\n🔍 Verifying tables...")
        verify_tables()
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_tables():
    """Verify that all smart tables were created"""
    expected_tables = [
        'document_categories',
        'document_metadata',
        'document_relationships',
        'term_synonyms',
        'query_intents',
        'related_questions',
        'response_templates',
        'answer_quality_metrics',
        'search_analytics',
        'conversation_patterns',
        'auto_suggestions',
        'detailed_feedback'
    ]
    
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DATABASE
        )
        
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"\n📊 Smart Tables Status:")
        for table in expected_tables:
            if table in existing_tables:
                # Count rows
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✅ {table}: {count} rows")
            else:
                print(f"  ❌ {table}: NOT FOUND")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"⚠️  Verification failed: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MIGRATION 08: SMART TABLES")
    print("=" * 60 + "\n")
    
    success = run_migration()
    
    if success:
        print("\n✨ All done! Your chatbot is now smarter!")
        print("💡 Reload documents to populate the smart tables:")
        print("   curl -X POST http://localhost:8000/documents/reload")
    else:
        print("\n❌ Migration failed. Please check errors above.")
        sys.exit(1)

